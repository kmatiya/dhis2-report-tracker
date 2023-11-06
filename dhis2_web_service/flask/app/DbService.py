import psycopg2
import pandas as pd


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

    def get_from_db(self, table_name):
        conn = psycopg2.connect(
            database=self.__database,
            user=self.__user,
            password=self.__password,
            host=self.__host,
            port=self.__port
        )

        cur = conn.cursor()
        cur.execute(f"""SELECT * FROM {table_name}
                    """)
        column_names = [desc[0] for desc in cur.description]
        tuples_list = cur.fetchall()
        df = pd.DataFrame(tuples_list, columns=column_names)
        df = df.drop(columns=["index"])
        conn.close()
        return df
