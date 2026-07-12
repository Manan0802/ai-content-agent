from config import SETTINGS

_TOKEN_URI = "https://oauth2.googleapis.com/token"
_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


class YouTubeClient:
    def __init__(self, client_id: str | None = None, client_secret: str | None = None,
                 refresh_token: str | None = None):
        self._client_id = client_id or SETTINGS.youtube_client_id
        self._client_secret = client_secret or SETTINGS.youtube_client_secret
        self._refresh_token = refresh_token or SETTINGS.youtube_refresh_token

    def is_configured(self) -> bool:
        return bool(self._client_id and self._client_secret and self._refresh_token)

    def _insert(self, body: dict, file_path: str) -> dict:
        # Imported lazily so unit tests never need the Google libs installed.
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload

        creds = Credentials(
            token=None,
            refresh_token=self._refresh_token,
            token_uri=_TOKEN_URI,
            client_id=self._client_id,
            client_secret=self._client_secret,
            scopes=_SCOPES,
        )
        youtube = build("youtube", "v3", credentials=creds)
        media = MediaFileUpload(file_path, mimetype="video/mp4",
                                chunksize=1024 * 1024, resumable=True)
        request = youtube.videos().insert(
            part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            _, response = request.next_chunk()
        return response

    def upload_video(self, file_path: str, title: str, description: str,
                     tags: list[str], privacy: str = "unlisted") -> str:
        body = {
            "snippet": {"title": title, "description": description, "tags": tags},
            "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False},
        }
        response = self._insert(body, file_path)
        return response["id"]
