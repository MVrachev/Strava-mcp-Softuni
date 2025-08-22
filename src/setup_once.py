import requests
import webbrowser
import os
from urllib.parse import urlparse, parse_qs
import logging


SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REDIRECT_URI = os.getenv("STRAVA_REDIRECT_URI", "http://localhost")
REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")
SCOPES = os.getenv("STRAVA_SCOPES", "read_all,activity:read_all,profile:read_all")


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)


def get_proper_refresh_token():
    """
    Get a proper refresh token with activity:read_all scope
    Following the forum approach: use client ID/secret to get code, then exchange for refresh token
    """
    if not CLIENT_ID or not CLIENT_SECRET:
        raise Exception("❌ Error: Set STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET environment variables")

    print("🚀 Getting proper refresh token with activity:read_all scope")
    print(f"🔑 Scopes requested: {SCOPES}")

    # Step 1: Get authorization code with desired scopes
    auth_url = (
        f"https://www.strava.com/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&approval_prompt=force"  # Force re-approval to ensure we get the right scopes
        f"&scope={SCOPES}"
    )

    print("📋 STEP 1: Get authorization code")
    print("=" * 50)
    print("🌐 Opening browser for authorization...")
    print("⚠️  IMPORTANT: Approve 'View data about your activities'")
    print()
    print("If browser doesn't open automatically, copy this URL:")
    print(auth_url)
    print()

    webbrowser.open(auth_url)

    print("After clicking 'Authorize', you'll be redirected to something like:")
    print(f"{REDIRECT_URI}/?state=&code=XXXXXXXXX&scope=read,activity:read_all")
    print()
    while True:
        redirect_url = input("📥 Paste the complete redirect URL here: ").strip()
        if redirect_url:
            break

    try:
        parsed_url = urlparse(redirect_url)
        query_params = parse_qs(parsed_url.query)

        if 'code' not in query_params:
            print("❌ Error: No 'code' found in URL. Make sure you copied the complete redirect URL")
            return

        code = query_params['code'][0]
        print(f"✅ Extracted authorization code: {code[:10]}...")

        if 'scope' in query_params:
            granted_scopes = query_params['scope'][0]
            print(f"✅ Granted scopes: {granted_scopes}")
            if 'activity:read_all' not in granted_scopes:
                print("⚠️  WARNING: activity:read_all scope not granted!")
                print("You may need to try again and accept all permissions")

    except Exception as e:
        print(f"❌ Error parsing URL: {e}")
        return

    print()
    print("🔄 STEP 2: Exchange code for refresh token")
    print("=" * 50)
    token_url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code"
    }

    try:
        print("🔄 Exchanging authorization code for tokens...")
        response = requests.post(token_url, data=payload)

        if response.status_code != 200:
            print(f"❌ Token exchange failed: {response.status_code}")
            print(f"Response: {response.text}")
            return

        tokens = response.json()

        print("🎉 SUCCESS! Got tokens with proper scopes:")
        print("=" * 50)
        print(f"🔑 Access Token: {tokens['access_token'][:20]}...")
        print(f"🔄 Refresh Token: {tokens['refresh_token']}")
        print(f"⏰ Expires At: {tokens['expires_at']}")

        # Step 3: Test the tokens immediately
        print()
        print("🧪 STEP 3: Testing the new tokens")
        print("=" * 50)

        activities_url = "https://www.strava.com/api/v3/athlete/activities"
        headers = {'Authorization': f'Bearer {tokens["access_token"]}'}
        params = {'per_page': 1, 'page': 1}

        test_response = requests.get(activities_url, headers=headers, params=params)

        if test_response.status_code == 200:
            print(f"✅ SUCCESS! Activities API works")
        else:
            print(f"❌ Activities API test failed: {test_response.status_code}")
            print(f"Response: {test_response.text}")

        # Save the refresh token
        print()
        print("💾 STEP 4: Save the refresh token")
        print("=" * 50)


        print("✅ Refresh token saved to 'new_strava_refresh_token.txt'")
        print()
        print("🔧 TO USE THIS TOKEN:")
        print("1. Copy the refresh token above")
        print("2. Update your STRAVA_REFRESH_TOKEN environment variable")
        print("3. Restart your application")
        print()
        print("💡 This refresh token should work indefinitely (doesn't expire)")
        print("   as long as you use it at least once every 6 months")

        return tokens

    except Exception as e:
        print(f"❌ Error during token exchange: {e}")
        return


if __name__ == "__main__":
    get_proper_refresh_token()
