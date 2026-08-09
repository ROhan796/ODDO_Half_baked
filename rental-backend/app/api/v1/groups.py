# app/api/v1/groups.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.utils.database import get_read_db, get_db
from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.models.group import Group, GroupMember, GroupVote
from app.schemas.group import (
    GroupCreate,
    GroupResponse,
    GroupMemberAdd,
    GroupMemberResponse,
    GroupVoteCreate,
    GroupVoteResponse,
    GroupVoteCast,
)

router = APIRouter()


@router.get("/", response_model=list[GroupResponse])
async def list_groups(
    db: AsyncSession = Depends(get_read_db),
    current_user: User = Depends(get_current_user),
):
    """List groups."""
    query = select(Group)

    # Portal users can only see their groups
    if current_user.role == "portal_user":
        query = query.join(GroupMember).where(GroupMember.user_id == current_user.id)

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=GroupResponse, status_code=201)
async def create_group(
    data: GroupCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new group."""
    group = Group(
        name=data.name,
        description=data.description,
        leader_id=current_user.id,
        max_members=data.max_members,
        joint_liability=data.joint_liability,
    )
    db.add(group)
    await db.flush()

    # Add creator as leader
    member = GroupMember(
        group_id=group.id,
        user_id=current_user.id,
        role="leader",
        status="active",
        trust_score_at_join=current_user.trust_score,
    )
    db.add(member)

    return group


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: uuid.UUID,
    db: AsyncSession = Depends(get_read_db),
    current_user: User = Depends(get_current_user),
):
    """Get group by ID."""
    group = await db.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group


@router.get("/{group_id}/members", response_model=list[GroupMemberResponse])
async def list_group_members(
    group_id: uuid.UUID,
    db: AsyncSession = Depends(get_read_db),
    current_user: User = Depends(get_current_user),
):
    """List members of a group with user profile details and quotas."""
    group = await db.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    result = await db.execute(
        select(GroupMember, User)
        .join(User, GroupMember.user_id == User.id)
        .where(GroupMember.group_id == group_id)
    )
    rows = result.all()

    response_items = []
    for member, user in rows:
        resp = GroupMemberResponse.model_validate(member)
        resp.user_name = user.name
        resp.user_email = user.email
        resp.user_phone = user.phone
        resp.user_role = user.role.value if hasattr(user.role, 'value') else str(user.role)
        resp.profile_photo_url = user.profile_photo_url
        response_items.append(resp)

    return response_items


@router.post("/{group_id}/members", response_model=GroupMemberResponse)
async def add_member(
    group_id: uuid.UUID,
    data: GroupMemberAdd,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add member to group."""
    group = await db.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Check if user is leader
    result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == current_user.id,
            GroupMember.role == "leader",
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Only group leader can add members")

    # Check member limit
    if group.current_member_count >= group.max_members:
        raise HTTPException(status_code=400, detail="Group is full")

    member = GroupMember(
        group_id=group_id,
        user_id=data.user_id,
        deposit_share_pct=data.deposit_share_pct,
        trust_score_at_join=0,
    )
    db.add(member)

    group.current_member_count += 1
    await db.commit()

    return member


@router.post("/{group_id}/votes", response_model=GroupVoteResponse)
async def create_vote(
    group_id: uuid.UUID,
    data: GroupVoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a group vote."""
    from datetime import datetime, timedelta, timezone

    vote = GroupVote(
        group_id=group_id,
        rental_id=data.rental_id,
        vote_type=data.vote_type,
        requested_by=current_user.id,
        reason=data.reason,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )
    db.add(vote)
    return vote


@router.post("/{group_id}/votes/{vote_id}/cast")
async def cast_vote(
    group_id: uuid.UUID,
    vote_id: uuid.UUID,
    data: GroupVoteCast,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cast a vote."""
    # TODO: Implement voting logic
    return {"message": "Vote cast successfully"}
