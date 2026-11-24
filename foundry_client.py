"""Optional server-side Foundry read adapter; no production side effects."""
import os
from urllib.parse import quote, urlsplit
import requests

class FoundryClient:
    def __init__(self, host, ontology, token):
        parsed = urlsplit(host)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.path not in ("", "/") or parsed.query or parsed.fragment:
            raise ValueError("FOUNDRY_URL must be an HTTPS origin")
        if not ontology or not token:
            raise ValueError("Ontology and access token are required")
        self.base = host.rstrip("/") + "/api/v2/ontologies/" + quote(ontology, safe="")
        self.headers = {"Authorization": "Bearer " + token, "Accept": "application/json"}

    @classmethod
    def from_env(cls):
        return cls(os.environ["FOUNDRY_URL"], os.environ["FOUNDRY_ONTOLOGY"], os.environ["FOUNDRY_TOKEN"])

    def _get(self, path, params=None):
        response = requests.get(self.base + path, headers=self.headers, params=params, timeout=20, allow_redirects=False)
        if response.status_code != 200:
            raise RuntimeError(f"Foundry request failed (HTTP {response.status_code})")
        return response.json()

    def list_objects(self, object_type, max_pages=100):
        path = "/objects/" + quote(object_type, safe="")
        token = None
        seen = set()
        for _ in range(max_pages):
            page = self._get(path, {"pageToken": token} if token else None)
            yield from page["data"]
            token = page.get("nextPageToken")
            if not token:
                return
            if token in seen:
                raise RuntimeError("Repeated Foundry pagination token")
            seen.add(token)
        raise RuntimeError("Foundry pagination limit reached")

    def get_object(self, object_type, primary_key):
        return self._get("/objects/" + quote(object_type, safe="") + "/" + quote(str(primary_key), safe=""))
