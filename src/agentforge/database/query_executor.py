
import pandas as pd
import requests
from requests.auth import HTTPDigestAuth

from agentforge.config import settings


def execute_query(query: str) -> pd.DataFrame:
    if not settings.TIDB_QUERY_ENDPOINT:
        raise RuntimeError("TIDB_QUERY_ENDPOINT is not configured.")

    if not settings.TIDB_PUBLIC_KEY or not settings.TIDB_PRIVATE_KEY:
        raise RuntimeError("TiDB API credentials are not configured.")

    try:
        response = requests.post(
            settings.TIDB_QUERY_ENDPOINT,
            json={"sql": query},
            auth=HTTPDigestAuth(
                settings.TIDB_PUBLIC_KEY,
                settings.TIDB_PRIVATE_KEY
            ),
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        response.raise_for_status()
        payload = response.json()

        if payload.get("type") == "error":
            raise RuntimeError(str(payload))

        data = payload.get("data", {})
        rows = data.get("rows", [])

        return pd.DataFrame(rows)

    except requests.RequestException as exc:
        raise RuntimeError(f"TiDB API request failed: {exc}") from exc
    except (ValueError, TypeError) as exc:
        raise RuntimeError(f"Unexpected TiDB response: {exc}") from exc
