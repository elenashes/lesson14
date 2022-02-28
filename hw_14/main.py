import json
from flask import Flask
from functions import db_connection

app = Flask(__name__)


@app.route('/movie/<title>')
def get_by_title(title):
    """
    функция для поиска фильма по названию. При наличии нескольких результатов возвращает последний добавленный.
    :param title:
    :return: словарь с данными о найденном фильме
    """
    sqlite_query = f"""
    SELECT * FROM netflix
    WHERE title LIKE '%{title}%'
    AND date_added = (SELECT MAX(date_added)
    FROM netflix
    WHERE title LIKE '%{title}%')
    LIMIT 1"""
    sql_result = db_connection(sqlite_query)

    for item in sql_result:
        result = {"title": item["title"],
                  "country": item["country"],
                  "release_year": item["release_year"],
                  "genre": item["listed_in"],
                  "description": item["description"]}

    return app.response_class(response=json.dumps(result), status=200, mimetype="application/json")


@app.route('/movie/<int:year_1>/to/<int:year_2>')
def search_by_year(year_1, year_2):
    """
    Ищет фильмы по годам выхгода в указанном диапазоне
    :param year_1:
    :param year_2:
    :return: список (из 100 элементов) словарей с заголовком и описанием фильмов, вышедших в указанном диапазоне
    """
    sqlite_query = f"""
    SELECT title, release_year FROM netflix
    WHERE release_year BETWEEN {year_1} AND {year_2}
    LIMIT 100
    """
    sql_result = db_connection(sqlite_query)
    result = []

    for item in sql_result:
        result_dict = {
                       "title": item["title"],
                       "release_year": item["release_year"]
                      }
        result.append(result_dict)
    return app.response_class(response=json.dumps(result), status=200, mimetype="application/json")


@app.route('/rating/<rating>')
def get_by_rating(rating):
    """
    Выводит список фильмов с указанным рейтингом.
    SQL запрос дополняется в зависимости от выбранного возрастного ограничения.
    :param rating:
    :return: список словарей с заданными ключами, отвечающими условиям поиска по рейтингу
    """
    sqlite_query = f"""SELECT * FROM netflix """
    if rating == "children":
        sqlite_query += f"""WHERE rating = 'G' """
    elif rating == "family":
        sqlite_query += f"""WHERE rating LIKE '%G%' """
    elif rating == "adult":
        sqlite_query += f"""WHERE rating = 'R' OR rating = 'NC-17' """

    sql_result = db_connection(sqlite_query)
    result = []

    for item in sql_result:
        result_dict = {
            "title": item["title"],
            "rating": item["rating"],
            "description": item["description"]
        }
        result.append(result_dict)
    return app.response_class(response=json.dumps(result), status=200, mimetype="application/json")


@app.route('/genre/<genre>')
def get_by_genre(genre):
    """
    Выводит список фильмов указанного жанра.
    :param genre:
    :return: список (максимум 10) словарей с заданными ключами, отвечающими условиям поиска по жанру
    """
    sqlite_query = f"""
    SELECT * FROM netflix
    WHERE listed_in LIKE '%{genre}%'
    ORDER BY release_year DESC
    LIMIT 10 """
    sql_result = db_connection(sqlite_query)
    result = []

    for item in sql_result:
        result_dict = {
            "title": item["title"],
            "release_year": item["release_year"],
            "description": item["description"]
        }
        result.append(result_dict)

    return app.response_class(response=json.dumps(result), status=200, mimetype="application/json")


def get_actors(actor_1, actor_2):
    """
    SQL запрос возвращает список cast актерских составов, в которых есть указанные актеры
    Далее из этого составляется список всех актеров, которые играли с ними, за исключением их самих
    Далее проверяется число вхождений каждого актера из вышеуказанного списка, и, если оно больше 2,
    выводится множество.
    :param actor_1:
    :param actor_2:
    :return: множество, состоящее из актеров, игравших с заданными более 2 раз.
    """
    sqlite_query = f"""
    SELECT `cast` FROM netflix 
    WHERE `cast` LIKE '%{actor_1}%' AND `cast` LIKE '%{actor_2}%'
    AND (SELECT COUNT('cast') FROM netflix
    WHERE `cast` LIKE '%{actor_1}%' AND `cast` LIKE '%{actor_2}%')>2
    """

    sql_result = db_connection(sqlite_query)
    result = []
    for item in sql_result:
        actors = item["cast"].split(", ")
        for actor in actors:
            if actor != actor_1 and actor != actor_2:
                result.append(actor)

    matching_actors = []
    for item in result:
        if result.count(item) > 2:
            matching_actors.append(item)

    return set(matching_actors)


def get_movie(type, release_year, listed_in):
    """
    Функция реализует запрос по указанным параметрам и выводит список фильмов, которые им соответствуют.
    :param type:
    :param release_year:
    :param listed_in:
    :return: список фильмов с заданными параметрами
    """
    sqlite_query = f"""
    SELECT title, description FROM netflix
    WHERE type LIKE '%{type}%'
    AND release_year={release_year}
    AND listed_in LIKE '%{listed_in}%'"""

    sql_result = db_connection(sqlite_query)
    result = []

    for item in sql_result:
        result_dict = {
            "title": item["title"],
            "description": item["description"]
        }
        result.append(result_dict)

    return result


if __name__ == '__main__':
    app.run()



