import time


__all__ = ["ChronoContext"]


class ChronoContext:
    """
    Chrono class for measuring time. Designed to be used with `with` statement.

    ```py
    with ChronoContext() as cc:
        time.sleep(1)
    print(cc.elapsed)
    ```
    """

    def __init__(self):
        self.__start = 0
        self.__end = 0
        self.__elapsed = 0
        self.__done = False

    def __enter__(self):
        self.__start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.__end = time.perf_counter()
        self.__elapsed = self.__end - self.__start
        self.__done = True

    @property
    def elapsed(self):
        if not self.__done:
            raise RuntimeError("ChronoContext hasn't finished yet")
        return self.__elapsed

    @property
    def start(self):
        return self.__start

    @property
    def end(self):
        return self.__end

    def get_formatted_elapsed(self, fmt: str = "%H:%M:%S"):
        """
        Get formatted elapsed time.

        ## Parameters
        - `fmt` - str, (optional)\\
        format for time.strftime\\
        defaults to `"%H:%M:%S"`

        ## Returns
        `str` - formatted elapsed time
        """

        # use property so it raises error if not done
        return time.strftime(fmt, time.gmtime(self.elapsed))
