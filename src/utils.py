def user_input_for_request() -> tuple[str, int, int] | str:
    """
    Функция для получения от пользователя данных для запроса
    """
    keyword = input('Введите фразу для поиска в названии компании ("stop" - выход из программы): ')
    if keyword == 'stop': return 'stop'

    while True:
        min_vacancies = 20
        max_vacancies = 100
        print(f'Введите минимальное (не менее 10) и максимальное (не более 100) количество вакансий у компании '
              f'(через "space"):\n("stop" - выход из программы, '
              f'"enter" - значения по умолчанию - от {min_vacancies} до {max_vacancies})')

        user_input = input()
        if user_input == 'stop': return 'stop'
        if user_input == '': break
        try:
            min_vacancies, max_vacancies = user_input.split(' ')
        except ValueError:
            continue
        if min_vacancies.isdigit() and max_vacancies.isdigit():
            if int(min_vacancies) >= int(max_vacancies) or int(min_vacancies) < 10 or int(max_vacancies) > 100:
                continue
            else:
                break

    return keyword, int(min_vacancies), int(max_vacancies)


def user_input_for_db_interact() -> tuple[int, str] | str:
    """
    Функция для получения пользовательского выбора по выводу результатов
    """
    keyword = ''
    print(
        'Выберите запрос (число - выбор, "stop" - выход из программы):\n'
        '  1. Получить список всех компаний и количество вакансий у каждой компании.\n'
        '  2. Получить список всех вакансий с указанием названия компании, названия вакансии, зарплаты и ссылки на вакансию.\n'
        '  3. Получить среднюю зарплату по вакансиям.\n'
        '  4. Получить список всех вакансий, у которых зарплата выше средней по всем вакансиям.\n'
        '  5. Получить список всех вакансий, в названии которых содержится указанная фраза.\n'
    )

    while True:
        user_input = input()
        if user_input == 'stop': return 'stop'
        if user_input in ('1', '2', '3', '4', '5'): break
    if user_input == '5':
        keyword = input('Фраза для поиска: ')

    return int(user_input), keyword


if __name__ == '__main__':
    print(user_input_for_request())
    print(user_input_for_db_interact())
