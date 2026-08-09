import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app


async def test_apis():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Test OTP Request
        print("Testing OTP Request...")
        req_resp = await client.post("/api/v1/auth/otp/request", json={
            "identifier": "+91 98765 43210",
            "channel": "sms"
        })
        print(f"OTP Request Response Status: {req_resp.status_code}")
        print(f"OTP Request Body: {req_resp.json()}")

        otp_code = req_resp.json().get("otp")

        # 2. Test OTP Verify (with generated OTP code)
        print("\nTesting OTP Verify...")
        verify_resp = await client.post("/api/v1/auth/otp/verify", json={
            "identifier": "+91 98765 43210",
            "code": otp_code,
            "purpose": "login"
        })
        print(f"OTP Verify Status: {verify_resp.status_code}")
        token_data = verify_resp.json()
        print(f"Access Token Received: {bool(token_data.get('access_token'))}")

        access_token = token_data.get("access_token")
        headers = {"Authorization": f"Bearer {access_token}"}

        # 3. Test GET /api/v1/groups/
        print("\nTesting GET /api/v1/groups/...")
        groups_resp = await client.get("/api/v1/groups/", headers=headers)
        print(f"Groups Response Status: {groups_resp.status_code}")
        groups = groups_resp.json()
        print(f"Groups Found: {len(groups)}")
        if groups:
            group_id = groups[0]["id"]
            print(f"Group ID: {group_id}, Name: '{groups[0]['name']}'")

            # 4. Test GET /api/v1/groups/{group_id}/members
            print(f"\nTesting GET /api/v1/groups/{group_id}/members...")
            members_resp = await client.get(f"/api/v1/groups/{group_id}/members", headers=headers)
            print(f"Group Members Status: {members_resp.status_code}")
            members = members_resp.json()
            print(f"Members Count: {len(members)}")
            for m in members:
                print(f" - {m.get('user_name')} ({m.get('user_email')}) | Role: {m.get('role')} | Quota: {m.get('deposit_share_pct')}%")

        # 5. Test Fallback Test OTP code '123456'
        print("\nTesting OTP Verify with test code '123456'...")
        fallback_resp = await client.post("/api/v1/auth/otp/verify", json={
            "identifier": "9812355443",
            "code": "123456",
            "purpose": "login"
        })
        print(f"Fallback OTP Verify Status: {fallback_resp.status_code}")
        print(f"Fallback Token Received: {bool(fallback_resp.json().get('access_token'))}")


if __name__ == "__main__":
    asyncio.run(test_apis())
