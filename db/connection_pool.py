import queue
import sqlite3
import threading


class SQLiteConnectionPool:
    def __init__(self, db_path, max_conn=3):
        self.db_path = db_path
        self.pool = queue.Queue(max_conn)
        self.semaphore = threading.Semaphore(max_conn)

        for _ in range(max_conn):
            self.pool.put(self._create_new_connection())

    def _create_new_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def get_connection(self):
        self.semaphore.acquire()
        return self.pool.get()

    def return_connection(self, conn):
        self.pool.put(conn)
        self.semaphore.release()

    def close_all_connections(self):
        while not self.pool.empty():
            conn = self.pool.get()
            conn.close()
