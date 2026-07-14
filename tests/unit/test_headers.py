from app.api.routes.ingest import sanitize_headers

def test_sanitize_headers_redacts_sensitive_values():
    headers = {
        "cookie": "",
        "x-api-key" : "secret-key",
        "content-type" : "application/json",
    }

    result = sanitize_headers(headers)

    assert result["cookie"] == "[REDACTED]"
    assert result["x-api-key"] == "[REDACTED]"
    assert result["content-type"] == "application/json"


def test_sanitize_headers_does_not_change_original_dictionary():
    headers = {"authorization": "secret-token"}

    sanitize_headers(headers)

    assert headers["authorization"] == "secret-token"

    
