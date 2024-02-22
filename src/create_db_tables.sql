CREATE TABLE employers
(
    employer_id    int,
    employer_name  varchar(200) NOT NULL,
    employer_url   varchar(50)  NOT NULL,
    open_vacancies int          NOT NULL,

    CONSTRAINT PK_employers_employer_id PRIMARY KEY (employer_id)
);

CREATE TABLE vacancies
(
    vacancy_id   int,
    vacancy_name varchar(200) NOT NULL,
    vacancy_url  varchar(50)  NOT NULL,
    salary       int,
    city         varchar(100),
    employer_id  int,

    CONSTRAINT PK_vacancies_vacancy_id PRIMARY KEY (vacancy_id),
    CONSTRAINT FK_vacancies_employer_id FOREIGN KEY (employer_id) REFERENCES employers (employer_id)
)