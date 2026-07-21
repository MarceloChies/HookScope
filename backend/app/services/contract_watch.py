from typing import Any
def get_json_type(value: Any) -> str:
    if value is None:
        return "null"
    
    if isinstance(value,bool):
        return "boolean"
    
    if isinstance(value, (int,float)):
        return "number"
    
    if isinstance (value, str):
        return "string"
    
    if isinstance (value, list):
        return "array"
    
    if isinstance (value, dict):
        return "object"
    
    return "unknown"


def compare_payload_contract(
    baseline: dict[str, Any],
    payload: dict[str,Any],
    path: str = "payload",
) -> list [dict[str,str]]:
    changes: list[dict[str,str]] = []

    for field, expected_value in baseline.items():
        field_path = f"{path}.{field}"

        if field not in payload:
            changes.append(
                {
                    "kind": "missing_field",
                    "path": field_path,
                    "expected": get_json_type(expected_value),
                    "actual": "missing",
                }
            )
            continue

        actual_value = payload[field]

        if isinstance(expected_value, dict) and isinstance(actual_value, dict):
            changes.extend(
                compare_payload_contract(
                    expected_value,
                    actual_value,
                    field_path
                )
            )
            continue

        expected_type = get_json_type(expected_value)
        actual_type = get_json_type(actual_value)

        if expected_type != actual_type:
            changes.append(
                {
                    "kind": "type_changed",
                    "path": field_path,
                    "expected": expected_type,
                    "actual": actual_type,
                }
            )

    for field, actual_value in payload.items():
        if field not in baseline:
            changes.append(
                {
                    "kind": "added_field",
                    "path": f"{path}.{field}",
                    "expected": "missing",
                    "actual": get_json_type(actual_value),
                }
            )

    return changes