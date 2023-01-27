from functools import lru_cache

from psycopg_pool import ConnectionPool

from configuration import dbConfig

db_pool = ConnectionPool(open=False, kwargs=dbConfig)


@lru_cache
def get_table_names():
    with db_pool.connection() as connection:
        tables = connection.execute(
            """ select table_name from information_schema.columns where column_name = 'geom' """
        ).fetchall()
        return tables
