from time import sleep


def request_retry(func):
    def wrapper(*args, max_retries: int = 5, **kwargs):
        attemps, wait_time = 0, 2
        while True:
            try:
                response = func(*args, **kwargs)
                return response
            except Exception as error:
                if attemps >= max_retries:
                    raise error
                # transient errors: 408, 429, 502, 503, 504
                # 408: Request Timeout | 429: Too Many Requests | 502: Bad Gateway | 503: Service Unavailable | 504: Gateway Timeout
                if error.response is not None and error.response.status_code is not None \
                and error.response.status_code not in [408, 429, 502, 503, 504]:
                    raise error
                attemps += 1
                print(f"Request error. Retrying in {wait_time} seconds")
                sleep(wait_time)
                wait_time = wait_time * 2

    return wrapper
