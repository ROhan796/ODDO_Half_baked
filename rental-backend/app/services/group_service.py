# app/services/group_service.py
from uuid import UUID
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.group import (
    Group,
    GroupMember,
    GroupMemberRole,
    GroupMemberStatus,
    GroupVote,
    GroupVoteRecord,
    GroupVoteType,
    GroupVoteStatus,
    VoteChoice,
    GroupStatus,
)
from app.models.user import User


class GroupService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_group(self, data: dict, leader_id: UUID) -> Group:
        user = await self.db.get(User, leader_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leader user not found",
            )

        group = Group(
            name=data["name"],
            description=data.get("description"),
            leader_id=leader_id,
            max_members=data.get("max_members", 20),
            joint_liability=data.get("joint_liability", True),
            status=GroupStatus.ACTIVE,
        )
        self.db.add(group)
        await self.db.flush()

        leader_member = GroupMember(
            group_id=group.id,
            user_id=leader_id,
            role=GroupMemberRole.LEADER,
            status=GroupMemberStatus.ACTIVE,
            trust_score_at_join=user.trust_score or 0,
            joined_at=datetime.now(timezone.utc),
        )
        self.db.add(leader_member)
        await self.db.flush()
        await self.db.refresh(group)

        return group

    async def get_group(self, group_id: UUID) -> dict:
        result = await self.db.execute(
            select(Group).where(Group.id == group_id)
        )
        group = result.scalar_one_or_none()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found",
            )

        members_result = await self.db.execute(
            select(GroupMember).where(GroupMember.group_id == group_id)
        )
        members = members_result.scalars().all()

        return {"group": group, "members": members}

    async def list_groups(
        self, page: int = 1, limit: int = 20, user_id: UUID = None
    ) -> dict:
        query = select(Group)

        if user_id:
            member_subq = select(GroupMember.group_id).where(
                GroupMember.user_id == user_id
            )
            query = query.where(Group.id.in_(member_subq))

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(Group.created_at.desc())
        query = query.offset((page - 1) * limit).limit(limit)
        result = await self.db.execute(query)
        groups = result.scalars().all()

        return {
            "items": groups,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
        }

    async def add_member(
        self, group_id: UUID, data: dict, added_by: UUID
    ) -> GroupMember:
        result = await self.db.execute(
            select(Group).where(Group.id == group_id)
        )
        group = result.scalar_one_or_none()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found",
            )

        member_count_result = await self.db.execute(
            select(func.count()).select_from(GroupMember).where(
                GroupMember.group_id == group_id
            )
        )
        current_count = member_count_result.scalar()

        if current_count >= group.max_members:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Group has reached maximum members",
            )

        existing_member = await self.db.execute(
            select(GroupMember).where(
                GroupMember.group_id == group_id,
                GroupMember.user_id == data["user_id"],
            )
        )
        if existing_member.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User is already a member of this group",
            )

        user = await self.db.get(User, data["user_id"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        member = GroupMember(
            group_id=group_id,
            user_id=data["user_id"],
            role=GroupMemberRole(data.get("role", "member")),
            status=GroupMemberStatus.INVITED,
            trust_score_at_join=user.trust_score or 0,
            deposit_share_pct=Decimal(str(data.get("deposit_share_pct", 0))),
            deposit_share_amount=Decimal(str(data.get("deposit_share_amount", 0))),
        )
        self.db.add(member)
        group.current_member_count = current_count + 1

        await self.db.flush()
        await self.db.refresh(member)
        return member

    async def remove_member(
        self, group_id: UUID, user_id: UUID, removed_by: UUID
    ) -> dict:
        result = await self.db.execute(
            select(GroupMember).where(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id,
            )
        )
        member = result.scalar_one_or_none()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found in group",
            )

        if member.role == GroupMemberRole.LEADER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove group leader",
            )

        member.status = GroupMemberStatus.REMOVED
        member.removed_at = datetime.now(timezone.utc)
        member.removed_by = removed_by

        group_result = await self.db.execute(
            select(Group).where(Group.id == group_id)
        )
        group = group_result.scalar_one_or_none()
        if group:
            group.current_member_count = max(group.current_member_count - 1, 0)

        await self.db.flush()
        return {"message": "Member removed successfully"}

    async def create_vote(
        self, group_id: UUID, data: dict, requested_by: UUID
    ) -> GroupVote:
        result = await self.db.execute(
            select(Group).where(Group.id == group_id)
        )
        group = result.scalar_one_or_none()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found",
            )

        vote = GroupVote(
            group_id=group_id,
            rental_id=data.get("rental_id"),
            vote_type=GroupVoteType(data["vote_type"]),
            requested_by=requested_by,
            reason=data.get("reason"),
            status=GroupVoteStatus.PENDING,
            expires_at=data.get(
                "expires_at",
                datetime.now(timezone.utc) + timedelta(days=3),
            ),
        )
        self.db.add(vote)
        await self.db.flush()
        await self.db.refresh(vote)
        return vote

    async def cast_vote(
        self, vote_id: UUID, data: dict, user_id: UUID
    ) -> GroupVoteRecord:
        result = await self.db.execute(
            select(GroupVote).where(GroupVote.id == vote_id)
        )
        vote = result.scalar_one_or_none()
        if not vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vote not found",
            )

        if vote.status != GroupVoteStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vote is no longer open",
            )

        if vote.expires_at < datetime.now(timezone.utc):
            vote.status = GroupVoteStatus.EXPIRED
            await self.db.flush()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vote has expired",
            )

        member_result = await self.db.execute(
            select(GroupMember).where(
                GroupMember.group_id == vote.group_id,
                GroupMember.user_id == user_id,
                GroupMember.status == GroupMemberStatus.ACTIVE,
            )
        )
        member = member_result.scalar_one_or_none()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not an active member of this group",
            )

        existing_vote = await self.db.execute(
            select(GroupVoteRecord).where(
                GroupVoteRecord.vote_id == vote_id,
                GroupVoteRecord.user_id == user_id,
            )
        )
        if existing_vote.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User has already voted",
            )

        vote_choice = VoteChoice(data["vote"])
        record = GroupVoteRecord(
            vote_id=vote_id,
            user_id=user_id,
            vote=vote_choice,
            voted_at=datetime.now(timezone.utc),
        )
        self.db.add(record)

        if vote_choice == VoteChoice.APPROVE:
            vote.votes_for = (vote.votes_for or 0) + 1
        else:
            vote.votes_against = (vote.votes_against or 0) + 1

        await self.db.flush()
        await self.db.refresh(record)
        return record

    async def resolve_vote(self, vote_id: UUID) -> GroupVote:
        result = await self.db.execute(
            select(GroupVote).where(GroupVote.id == vote_id)
        )
        vote = result.scalar_one_or_none()
        if not vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vote not found",
            )

        if vote.status != GroupVoteStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vote already resolved",
            )

        member_count_result = await self.db.execute(
            select(func.count()).select_from(GroupMember).where(
                GroupMember.group_id == vote.group_id,
                GroupMember.status == GroupMemberStatus.ACTIVE,
            )
        )
        total_members = member_count_result.scalar()
        total_votes = (vote.votes_for or 0) + (vote.votes_against or 0)

        if total_votes < (total_members / 2):
            vote.status = GroupVoteStatus.EXPIRED
        elif (vote.votes_for or 0) > (vote.votes_against or 0):
            vote.status = GroupVoteStatus.APPROVED
        else:
            vote.status = GroupVoteStatus.REJECTED

        vote.resolved_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(vote)
        return vote
