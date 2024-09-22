import queue
import threading


class SQLiteWorker(threading.Thread):
    def __init__(self, input_queue: queue.Queue, connection_pool, **kwargs):
        super().__init__(**kwargs)
        self._input_queue = input_queue
        self._connection_pool = connection_pool
        create_table_query = """
            CREATE TABLE IF NOT EXISTS metrics (
                function_name TEXT PRIMARY KEY,
                calls INTEGER,
                execution_time REAL,
                errors INTEGER
            )
        """
        self._execute_query(create_table_query)
        self._func_name_cache = set()
        self.daemon = True
        self.start()

    def run(self):
        while True:
            val = self._input_queue.get()
            if val is None:
                break
            function_name = val.get("function_name")
            calls = val.get("calls")
            execution_time = val.get("execution_time")
            errors = val.get("errors")
            if function_name in self._func_name_cache:
                sql_query = f"""
                    UPDATE metrics SET calls = {calls}, execution_time = {execution_time}, errors = {errors} WHERE function_name = '{function_name}'
                """
                self._execute_query(sql_query)
            else:
                sql_query = f"""
                    INSERT OR REPLACE INTO metrics (function_name, calls, execution_time, errors)
                    VALUES ('{function_name}', {calls}, {execution_time}, {errors})
                """
                if self._execute_query(sql_query):
                    self._func_name_cache.add(function_name)

    def _execute_query(self, query):
        conn = self._connection_pool.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            conn.commit()
        except Exception as e:
            print(e)
            return False
        finally:
            cursor.close()
            self._connection_pool.return_connection(conn)
        return True
