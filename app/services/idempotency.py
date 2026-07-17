import hashlib
import json
from typing import Any

def create_payload_fingerprint(payload: dict[str, Any]) -> str:
    normalized_payload = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )

    payload_bytes = normalized_payload.encode("utf-8")

    return hashlib.sha256(payload_bytes).hexdigest()