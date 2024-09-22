import random
import time
from metrics import metrics_collector, metrics_queue, SQLiteWorker
from db import SQLiteConnectionPool


@metrics_collector
def test_function(seconds: int):
    """
    Simulates an I/O intensive function. If the function were CPU intensive,
    consider using multiprocessing for metrics_collector or waiting for the GIL (Global Interpreter Lock)
    to be disabled.
    """
    rand_val = random.random()
    if rand_val < 0.5:
        raise Exception("An error occurred in test_function")
    time.sleep(seconds)


def main():
    connection_pool = SQLiteConnectionPool("metrics.db")
    sqlite_worker = SQLiteWorker(metrics_queue, connection_pool)
    # --------------------------------
    for i in range(1, 4):
        try:
            test_function(i)
        except Exception as e:
            print(e)
    print(metrics_collector.get_metrics("test_function"))
    # --------------------------------
    connection_pool.close_all_connections()
    metrics_queue.put(None)
    sqlite_worker.join()


if __name__ == "__main__":
    main()
