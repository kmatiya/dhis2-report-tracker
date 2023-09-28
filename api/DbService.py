import psycopg2
import pandas as pd
from sqlalchemy import create_engine


class DbService:
    def __init__(self, database: str,
                 user: str,
                 password: str,
                 host: str,
                 port: int):
        self.__database = database
        self.__user = user
        self.__password = password
        self.__host = host
        self.__port = port

    def write_to_db(self, table_name: str, data_frame):
        # establish connections
        engine = create_engine(f'postgresql://{self.__user}:{self.__password}@{self.__host}:{self.__port}/'
                               f'{self.__database}')
        conn = engine.connect()
        conn1 = psycopg2.connect(
            database=self.__database,
            user=self.__user,
            password=self.__password,
            host=self.__host,
            port=self.__port
        )

        conn1.autocommit = True
        cursor = conn1.cursor()

        # drop table if it already exists
        cursor.execute(f'drop table if exists {table_name}')
        columns = ""

        for each_column_name in data_frame.columns.tolist():
            columns = f'{columns}{each_column_name} TEXT,'

        columns = columns[:-1]
        sql = f'''CREATE TABLE {table_name}({columns});'''

        cursor.execute(sql)

        # converting data to sql
        data_frame.to_sql(table_name, conn, if_exists='replace')

        # fetching all rows
        sql1 = f'''select * from {table_name};'''
        cursor.execute(sql1)
        for i in cursor.fetchall():
            print(i)

        conn1.commit()
        conn1.close()
