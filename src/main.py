from fastmcp import FastMCP
import requests
import os

SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REDIRECT_URI = os.getenv("STRAVA_REDIRECT_URI", "http://localhost")
REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")
SCOPES = os.getenv("STRAVA_SCOPES", "read_all,activity:read_all,profile:read_all")

ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"

MAX_ACTIVITIES_PER_PAGE = 200


async def get_fresh_access_token():
    """
    Automatically get a fresh access token using stored refresh token.
    """
    if not REFRESH_TOKEN:
        raise Exception("STRAVA_REFRESH_TOKEN not set. Run setup_once.py first!")

    if not CLIENT_ID or not CLIENT_SECRET:
        raise Exception("STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET must be set")

    token_url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token"
    }

    response = requests.post(token_url, data=payload)
    response.raise_for_status()
    data = response.json()

    return data['access_token']


mcp = FastMCP(name="strava-mcp-server")

@mcp.tool(
    name="get_activities",
    description="Get activities from Strava",
)
async def get_activities(num_activities: int):
    """
    Get activities from Strava.
    """
    access_token = await get_fresh_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"page": 1, "per_page": num_activities}
    response = requests.get(ACTIVITIES_URL, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host=SERVER_HOST,
        port=SERVER_PORT,
    )
