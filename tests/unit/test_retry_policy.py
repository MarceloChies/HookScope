import uuid

from app.database.models.attempt import DeliveryAttempt
from app.services.retry_policy import get_retry_delay_seconds, should_retry

def make_attempt(
    *,
    attempt_number: bool,
    succeeded: bool,
    status_code: int | None,
) -> DeliveryAttempt:
    
    return DeliveryAttempt(
        delivery_id=uuid.uuid4(),
        attempt_number=attempt_number,
        succeeded=succeeded,
        status_code=status_code,
    )


def test_network_error_should_retry():
    attempt = make_attempt(
        attempt_number=1,
        succeeded=False,
        status_code=None,
    )
    assert should_retry(attempt) is True


def test_server_error_should_retry():
    attempt = make_attempt(
        attempt_number=1,
        succeeded=False,
        status_code=500,
    )
    assert should_retry(attempt) is True


def test_client_error_should_not_retry():
    attempt = make_attempt(
        attempt_number=1,
        succeeded=False,
        status_code=400,
    )
    assert should_retry(attempt) is False


def test_successful_attempt_should_not_retry():
    attempt = make_attempt(
        attempt_number=1,
        succeeded=True,
        status_code=200,
    )
    assert should_retry(attempt) is False


def test_final_attempt_should_not_retry():
    attempt = make_attempt(
        attempt_number=5,
        succeeded=False,
        status_code=500
    )
    assert should_retry(attempt) is False


def test_retry_delay_matches_attempt_number():
    assert get_retry_delay_seconds(1) == 5
    assert get_retry_delay_seconds(2) == 5
    assert get_retry_delay_seconds(3) == 5
    assert get_retry_delay_seconds(4) == 5
    assert get_retry_delay_seconds(5) is None