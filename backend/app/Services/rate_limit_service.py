import time
from fastapi import HTTPException

MAX_REQUESTS_PER_HOUR = 20
request_count = 0
window_start = time.time()


def check_and_increment_request_limit():
    global request_count, window_start

    current_time = time.time()

    if current_time - window_start > 3600:
        request_count = 0
        window_start = current_time

    if request_count >= MAX_REQUESTS_PER_HOUR:
        raise HTTPException(
            status_code=429,
            detail="Demo limit reached. Please try again later."
        )

    request_count += 1