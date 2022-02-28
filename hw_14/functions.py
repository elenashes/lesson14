import sqlite3

def db_connection(sqlite_query):
    """
    служебная функция для установки соединения с БД и его закрытия
    :param sqlite_query:
    :return: список словарей с результатами запроса
    """
    with sqlite3.connect('netflix.db') as connection:
        connection.row_factory = sqlite3.Row
        data = []
        for item in connection.execute(sqlite_query).fetchall():
            data.append(dict(item))
        return data