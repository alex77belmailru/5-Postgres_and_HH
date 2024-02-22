from src.utils import *
from src.classes import *

DB_NAME = 'hh'

def main():
    # запрос у пользователя параметров поиска:
    # ('ключевое слово', 'минимальное количество вакансий у компании', 'максимальное количество вакансий у компании')
    user_input = user_input_for_request()
    if user_input == 'stop': return

    employers = HH.get_employers(user_input)  # получение списка компаний
    if not employers: return
    vacancies = HH.get_vacancies()  # получение списка вакансий

    hh_db = PostgresDB(DB_NAME)  # создание бд
    hh_db.insert_data('employers', employers, columns=4)  # заполнение таблицы employers
    hh_db.insert_data('vacancies', vacancies, columns=6)  # заполнение таблицы vacancies
    hh_db.close_connection()

    manage_db = DBManager(DB_NAME)  # экземпляр для получения данных из бд

    # возможные варианты запросов к бд
    actions = ['manage_db.get_companies_and_vacancies_count()',
               'manage_db.get_all_vacancies()',
               'manage_db.get_avg_salary()',
               'manage_db.get_vacancies_with_higher_salary()',
               'manage_db.get_vacancies_with_keyword(user_choice[1])']

    # цикл работы с бд
    while True:
        user_choice = user_input_for_db_interact()
        if user_choice == 'stop':
            manage_db.close_connection()
            break
        eval(actions[user_choice[0] - 1])


if __name__ == '__main__':
    main()
