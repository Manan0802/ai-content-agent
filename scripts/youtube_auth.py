"""One-time YouTube OAuth consent → refresh token.

Run once after setting YOUTUBE_CLIENT_ID / YOUTUBE_CLIENT_SECRET in .env:

    python -m scripts.youtube_auth

Opens a browser for you to approve upload access to your channel, then prints
the refresh token and appends YOUTUBE_REFRESH_TOKEN=... to .env. After that the
pipeline uploads on its own — no further consent needed. Scope is limited to
youtube.upload (least privilege — no read/delete).
"""
import os
from config import SETTINGS

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def main() -> None:
    if not (SETTINGS.youtube_client_id and SETTINGS.youtube_client_secret):
        raise SystemExit(
            "Set YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET in .env first "
            "(create an OAuth 2.0 Desktop client in Google Cloud Console)."
        )

    from google_auth_oauthlib.flow import InstalledAppFlow

    client_config = {
        "installed": {
            "client_id": SETTINGS.youtube_client_id,
            "client_secret": SETTINGS.youtube_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }
    flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)
    creds = flow.run_local_server(port=0)

    token = creds.refresh_token
    if not token:
        raise SystemExit(
            "No refresh token returned. Revoke the app's access at "
            "https://myaccount.google.com/permissions and run this again "
            "(a refresh token is only issued on first consent)."
        )

    print("\nYOUR REFRESH TOKEN:\n" + token + "\n")

    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    try:
        with open(env_path, "a", encoding="utf-8") as f:
            f.write(f"\nYOUTUBE_REFRESH_TOKEN={token}\n")
        print(f"Appended YOUTUBE_REFRESH_TOKEN to {env_path}")
    except OSError as e:
        print(f"Could not write .env ({e}). Paste the token above into .env manually "
              f"as YOUTUBE_REFRESH_TOKEN=...")


if __name__ == "__main__":
    main()
