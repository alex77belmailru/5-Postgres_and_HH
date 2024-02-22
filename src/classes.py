from requests import get
import psycopg2


class DBConnector:
    """
    Устанавливает соединение с бд
    """

    @staticmethod
    def _create_connection(db_name='postgres'):  # создание соединения с бд
        params = dict(
            host="localhost",
            database=db_name,
            user="postgres",
            password="0112"
        )
        connection = None
        try:
            connection = psycopg2.connect(**params)
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
        connection.autocommit = True
        return connection

    def close_connection(self):  # закрытие соединения
        self._connection.close()


class DBManager(DBConnector):
    """
    Взаимодействует с бд
    """

    def __init__(self, db_name: str):
        self._db_name = db_name

        self._connection = self._create_connection(self._db_name)  # подключение к бд "db_name"
        self._cursor = self._connection.cursor()

    def get_companies_and_vacancies_count(self):
        """
        Получает список всех компаний и количество вакансий у каждой компании.
        """

        self._cursor.execute(
            "SELECT employer_name, count(*) "
            "FROM employers "
            "JOIN vacancies "
            "USING(employer_id) "
            "GROUP BY employer_name "
            "ORDER BY employer_name")
        result = self._cursor.fetchall()
        [print(
            f'Компания: {i[0]}\t|\t'
            f'Количество вакансий: {i[1]}\t|\n'
            f'{"-" * 300}')
            for i in result]

    def get_all_vacancies(self):
        """
        Получает список всех вакансий с указанием названия компании, названия вакансии, зарплаты и ссылки на вакансию.
        """

        self._cursor.execute(
            "SELECT vacancy_name, employer_name, salary, vacancy_url "
            "FROM employers "
            "JOIN vacancies "
            "USING(employer_id) ")
        result = self._cursor.fetchall()
        [print(
            f'Вакансия: {i[0]}\t|\t'
            f'Компания: {i[1]}\t|\t'
            f'Зарплата: {"не указана" if not i[2] else i[2]}\t|\t'
            f'Ссылка на вакансию: {i[3]}\t|\n'
            f'{"-" * 300}')
            for i in result]

    def get_avg_salary(self):
        """
        Получает среднюю зарплату по вакансиям.
        """

        self._cursor.execute(
            "SELECT AVG(salary)::int  "
            "FROM vacancies "
            "WHERE salary > 0 ")
        result = self._cursor.fetchall()
        print(f'Средняя зарплата по всем вакансиям: {result[0][0]} руб/мес\n')

    def get_vacancies_with_higher_salary(self):
        """
        Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям
        """

        self._cursor.execute(
            "SELECT * "
            "FROM vacancies "
            "WHERE salary > (SELECT AVG(salary) FROM vacancies WHERE salary > 0 )")
        result = self._cursor.fetchall()
        [print(
            f'ID вакансии: {i[0]}\t|\t'
            f'Вакансия: {i[1]}\t|\t'
            f'Ссылка на вакансию: {i[2]}\t|\t'
            f'Зарплата: {"не указана" if not i[3] else i[3]}\t|\t'
            f'Город: {"не указан" if not i[4] else i[4]}\t|\t'
            f'ID Компании: {i[5]}\t|\n'
            f'{"-" * 300}')
            for i in result]

    def get_vacancies_with_keyword(self, keyword: str):
        """
        Получает список всех вакансий, в названии которых содержится указанная фраза.
        """

        keyword = (f"%{keyword}%",)
        self._cursor.execute(
            "SELECT * "
            "FROM vacancies "
            "WHERE vacancy_name ILIKE (%s)", keyword)
        result = self._cursor.fetchall()
        if not result: print('\nВакансии по запросу не найдены\n')
        [print(
            f'ID вакансии: {i[0]}\t|\t'
            f'Вакансия: {i[1]}\t|\t'
            f'Ссылка на вакансию: {i[2]}\t|\t'
            f'Зарплата: {"не указана" if not i[3] else i[3]}\t|\t'
            f'Город: {"не указан" if not i[4] else i[4]}\t|\t'
            f'ID Компании: {i[5]}\t|\n'
            f'{"-" * 300}')
            for i in result]


class PostgresDB(DBConnector):
    """
    Создает базу данных Postgres и таблицы для работы с НН
    """

    _create_tables_script = 'create_db_tables.sql'

    def __init__(self, db_name: str):
        self._db_name = db_name

        self._connection = self._create_connection()  # подключение к бд "postgres"
        self._cursor = self._connection.cursor()

        self._delete_db()  # удаление старых данных
        self._create_db()  # создание бд

        self._connection.close()  # отключение от бд "postgres"
        self._connection = self._create_connection(self._db_name)  # подключение к бд "db_name"
        self._cursor = self._connection.cursor()

        self._execute_script(self._create_tables_script)  # создание таблиц в бд

    def insert_data(self, table_name: str, data: list[tuple], columns: int) -> None:  # заполнение таблицы
        template = '(' + ','.join(['%s'] * columns) + ')'
        self._cursor.executemany(f"INSERT INTO {table_name} VALUES {template}", data)

    def _execute_script(self, script_file: str) -> None:  # выполнение sql-скрипт из файла
        try:
            with open(script_file, encoding='utf-8') as file:
                data = file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f'Отсутствует файл {script_file}')
        try:
            self._cursor.execute(data)
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)

    def _delete_db(self):  # удаление бд
        try:
            self._cursor.execute(f'DROP DATABASE IF EXISTS {self._db_name} WITH (FORCE)')
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)

    def _create_db(self) -> None:  # создание бд
        try:
            self._cursor.execute(f'CREATE DATABASE {self._db_name}')
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)


class API:
    """
    Класс для работы с API.
    """

    @staticmethod  # получение одной страницы запроса
    def _get_one_page(params: dict, url: str, page: int) -> dict:
        params.update({'page': page})
        try:
            response = get(url, params).json()
            return response
        except KeyError as err:
            raise KeyError(err)
        except Exception as err:
            raise Exception(err)


class HH(API):
    """
    Класс для работы с HeadHunter.
    """

    _max_vacancies = 2000  # максимальное число вакансий для поиска на HH
    _employers = []  # массив работодателей
    _vacancies = []  # массив вакансий
    _url_employers = 'https://api.hh.ru/employers'
    _url_vacancies = 'https://api.hh.ru/vacancies'

    @classmethod  # метод поиска компаний
    def get_employers(cls, user_input: tuple) -> list[tuple] | None:
        min_vacancies = user_input[1]
        max_vacancies = user_input[2]
        params = {
            'text': user_input[0],
            'area': 113,
            'per_page': 100,
            'only_with_vacancies': 'true'
        }

        print('Поиск компаний...')
        vacancies_find = 0
        for page in range(50):  # чтение 50 страниц по 100 вакансий
            one_page_data = cls._get_one_page(params, cls._url_employers, page)  # получение 1 страницы
            # выбор работодателей с числом вакансий в диапазоне  min_vacancies .. max_vacancies
            for employer in one_page_data['items']:
                if min_vacancies <= employer['open_vacancies'] <= max_vacancies:
                    cls._employers.append(tuple([
                        int(employer['id']),
                        employer['name'],
                        employer['alternate_url'],
                        employer['open_vacancies']]))
                    vacancies_find += employer['open_vacancies']
                if vacancies_find >= cls._max_vacancies: break
            if one_page_data['pages'] <= page: break  # проверка достижения последней страницы поиска

        print(f'Найдено компаний: {len(cls._employers)}')
        return list(set(cls._employers))

    @classmethod  # метод поиска вакансий
    def get_vacancies(cls) -> list[tuple] | None:
        if not cls._employers: return

        employers_id = []
        [employers_id.append(employer[0]) for employer in cls._employers]

        params = {
            'area': 113,
            'per_page': 100,
            'employer_id': tuple(employers_id)
        }

        print('Получение вакансий...')
        for page in range(20):  # чтение 20 страниц по 100 вакансий
            one_page_data = cls._get_one_page(params, cls._url_vacancies, page)  # получение 1 страницы
            for vacancy in one_page_data['items']:
                cls._vacancies.append(tuple([
                    int(vacancy['id']),
                    vacancy['name'],
                    vacancy['alternate_url'],
                    0 if vacancy['salary'] is None else
                    vacancy['salary']['to'] if vacancy['salary']['to'] is not None else vacancy['salary']['from'],
                    '' if vacancy['address'] is None else vacancy['address']['city'],
                    int(vacancy['employer']['id'])
                ]))

            # cls.__vacancies += one_page_data['items']

            if one_page_data['pages'] <= page: break  # проверка достижения последней страницы поиска

        print('Получено вакансий:', len(cls._vacancies))
        return cls._vacancies
