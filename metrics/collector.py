from collections import defaultdict
import json
import queue
from time import perf_counter


class MetricsCollector:
    def __init__(self, output_queue):
        # FIXME: should take care for re-running the app
        self._metrics = defaultdict(
            lambda: {"calls": 0, "execution_time": 0, "errors": 0}
        )
        self.output_queue = output_queue

    def __call__(self, fn):
        def wrapper(*args, **kwargs):
            start = perf_counter()
            self._metrics[fn.__name__]["calls"] += 1
            try:
                result = fn(*args, **kwargs)
                return result
            except Exception as e:
                self._metrics[fn.__name__]["errors"] += 1
                raise e
            finally:
                self._metrics[fn.__name__]["execution_time"] += perf_counter() - start
                if self.output_queue:
                    self.output_queue.put(
                        {
                            **self._metrics[fn.__name__],
                            "function_name": fn.__name__,
                        }
                    )

        return wrapper

    def get_metrics(self, fn_name):
        calls = self._metrics[fn_name]["calls"]
        errors = self._metrics[fn_name]["errors"]
        avg_execution_time = (
            self._metrics[fn_name]["execution_time"] / calls if calls else 0
        )
        return json.dumps(
            {
                "Function": fn_name,
                "Number of calls": calls,
                "Average execution time": f"{avg_execution_time} seconds",
                "Number of errors": errors,
            },
            indent=4,
        )

metrics_queue = queue.Queue()
metrics_collector = MetricsCollector(metrics_queue)