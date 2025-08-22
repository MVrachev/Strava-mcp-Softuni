from fastmcp import FastMCP, Context
import requests
import os
import logging


SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")
REDIRECT_URI = os.getenv("STRAVA_REDIRECT_URI", "http://localhost")
ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"

MAX_ACTIVITIES_PER_PAGE = 200


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

mcp = FastMCP(name="strava-mcp-server")


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


def _get_activities_from_page(params: dict, headers: dict):
    response = requests.get(ACTIVITIES_URL, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


@mcp.tool(
    description="Get recent activities from Strava",
    name="get_recent_activities",
)
async def get_recent_activities(
    ctx: Context, num_activities: int = 10, all_activities: bool = False
) -> list[dict]:
    token = await get_fresh_access_token()
    headers = {'Authorization': f'Bearer {token}'}
    activities: list[dict] = []
    if all_activities:
        # Case 1: Fetch ALL activities (ignore num_activities)
        params = {'per_page': MAX_ACTIVITIES_PER_PAGE, 'page': 1}
        while True:
            page_activities = _get_activities_from_page(params, headers)
            if not page_activities:  # Empty response = done
                break

            activities.extend(page_activities)

            if len(page_activities) < MAX_ACTIVITIES_PER_PAGE:  # Last page
                break

            params['page'] += 1

    elif num_activities > MAX_ACTIVITIES_PER_PAGE:
        # Case 2: Fetch specific large number (> 200)
        params = {'per_page': MAX_ACTIVITIES_PER_PAGE, 'page': 1}
        remaining = num_activities

        while remaining > 0:
            page_activities = _get_activities_from_page(params, headers)

            if len(page_activities) < 1:  # No more activities available
                break

            elif len(page_activities) > remaining:
                # We got more than we need, so cut the last batch to match
                # the requested number of activities
                activities.extend(page_activities[:remaining])
                break

            activities.extend(page_activities)
            remaining -= len(page_activities)

            if len(page_activities) < MAX_ACTIVITIES_PER_PAGE:  # Last page
                if remaining > 0:
                    msg = (
                        f"There are less activities {len(activities)} than "
                        f"requested {num_activities}"
                    )
                    log.warning(msg)
                    ctx.warning(msg)
                break

            params['page'] += 1
    else:
        # Case 3: Fetch small number (<= 200) - single request
        params = {'per_page': num_activities, 'page': 1}
        activities = _get_activities_from_page(params, headers)

    log.info(f"Fetched {len(activities)} activities")
    return activities


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host=SERVER_HOST,
        port=SERVER_PORT,
    )
