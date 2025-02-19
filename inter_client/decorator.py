from time import sleep


def request_retry(func):
    def wrapper(*args, max_retries: int = 5, **kwargs):
        attemps, wait_time = 0, 2
        while True:
            # print(f"Requesting {func.__name__} with args: {args} and kwargs: {kwargs}")
            try:
                response = func(*args, **kwargs)
                return response
            except Exception as error:
                if attemps >= max_retries:
                    raise error
                attemps += 1
                print(f"Request error. Retrying in {wait_time} seconds")
                sleep(wait_time)
                wait_time = wait_time * 2

    return wrapper
