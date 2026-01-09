import httpx
import asyncio

async def test_user_flow():
    base_url = "http://localhost:8003/v1"
    
    async with httpx.AsyncClient() as client:
        # 1. Register
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword"
        }
        print("Registering user...")
        resp = await client.post(f"{base_url}/auth/register", json=user_data)
        if resp.status_code == 400 and "already registered" in resp.text:
            print("User already exists, proceeding to login.")
        else:
            assert resp.status_code == 200, f"Register failed: {resp.text}"
            print("Registration successful.")

        # 2. Login
        print("Logging in...")
        login_data = {
            "username": "testuser",
            "password": "testpassword"
        }
        resp = await client.post(f"{base_url}/auth/login", data=login_data)
        assert resp.status_code == 200, f"Login failed: {resp.text}"
        token = resp.json()["access_token"]
        print("Login successful.")

        # 3. Get Me
        print("Fetching profile...")
        headers = {"Authorization": f"Bearer {token}"}
        resp = await client.get(f"{base_url}/users/me", headers=headers)
        assert resp.status_code == 200, f"Get me failed: {resp.text}"
        user = resp.json()
        assert user["username"] == "testuser"
        print(f"Profile fetched successfully: {user['email']}")

if __name__ == "__main__":
    asyncio.run(test_user_flow())
