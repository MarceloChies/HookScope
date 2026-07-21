from app.database.models.attempt import DeliveryAttempt

MAX__ATEMPTS = 5

RETRY_DELAYS_SESCONDS = {
    1: 5,
    2: 5,
    3: 5,
    4: 5,
}

def should_retry(attempt: DeliveryAttempt) -> bool:
    if attempt.succeeded:
        return False
    
    if attempt.attempt_number >= MAX__ATEMPTS:
        return False
    
    if attempt.status_code is None:
        return True
    
    return(
        attempt.status_code == 408
        or attempt.status_code == 429
        or attempt.status_code >= 500
    )

def get_retry_delay_seconds(attempt_number: int) -> int | None:
    return RETRY_DELAYS_SESCONDS.get(attempt_number)