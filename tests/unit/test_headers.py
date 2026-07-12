from app.api.routes.ingest import sanitize_headers

def test_sanitized_headers_hides_sensitives_values():
    headers = {
        "cookie": "",
        "x-api-key" : "secret-key",
        "content-type" : "application/json",
    }

    result = sanitize_headers(headers)

    assert result["cookie"] == "[REDACTED]"
    assert result["x-api-key"] == "[REDACTED]"
    assert result["content-type"] == "application/json"

    