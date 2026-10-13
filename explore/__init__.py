"""Пакет'explore' — Flask-приложение 'Explore'.

Содержит:

- фабрику приложения 'create_app' (модуль 'explore');
- модели 'Tour' и 'Book' (модуль 'explore.models');
- конфигурацию для БД 'Config' (модуль 'explore.config')
- CLI-команды 'init-db', 'drop-db'.

Запуск:
    flask --app explore run --debug

Инициализация БД:
    flask --app explore init-db"""

from flask import Flask, Response, render_template, request, redirect, url_for
from explore.config import ProductionConfig, DevelopmentConfig
from explore.models import db, Tour, Book
import click
import re
from os import getenv
from typing import Union


PATTERN_PHONE = re.compile(r'^\+7\d{10}$')  # Паттерн для проверки номера телефона

config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    }


def create_app(config_class=None) -> Flask:
    if config_class is None:
        env = getenv("FLASK_ENV", "development")
        config_class = config[env]

    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

# ---------- CLI-команды ----------

    @app.cli.command("init_db")
    def init_db() -> None:
        """ Функция создает таблицы базы данных и заполняет ее тестовыми данными.
        
        flask --app explore init_db
        Команда выполняет первичную инициализацию схемы через SQLAlchemy
        и загружает фиксированный набор маршрутов
        
        Логика выполнения:
        1. Создает отсутствующие таблицы базы данных.
        2. Итерируется по списку словарей `tours_data`.
        3. Проверяет наличие тура в БД по уникальному `slug`.
        - Если тур найден возвращается экземпляр Tour, иначе возвращается None
        4. Добавляет отсутствующие записи и фиксирует транзакцию (commit)."""

        db.create_all()

        tours_data: list[dict[str, str]] = [
            {"slug": "lake", "title": "День 1 — Озеро",
            "image": "route-lake.jpg", "description": "Прогулка по берегу..."},
            {"slug": "mountains", "title": "День 2 — Горы",
            "image": "route-mountains.jpg", "description": "Лёгкий подъём..."},
            {"slug": "waterfall", "title": "День 3 — Водопад",
            "image": "route-waterfall.jpg", "description": "Тропа к водопаду..."},
        ]

        for data in tours_data:
            if not Tour.query.filter_by(slug=data['slug']).first():
                db.session.add(Tour(**data))

        db.session.commit()

    
    @app.cli.command('drop_db')
    def drop_db():
        """Удаление таблицы
        flask --app explore drop_db"""
        db.drop_all()
        

 # ---------- Роуты ----------

    @app.route('/')
    def index() -> str:
        """Главная страница сайта.
        Returns:
            str: HTML-шаблон главной страницы"""
        return render_template('index.html')

    @app.route("/tour/<slug>", methods=["GET", "POST"])
    def tour_detail(slug: str) -> Union[str, Response]:
        """Отображает страницу с формой и обрабатывает ее.

        При GET-запросе возвращает страницу с формой заказа.
        При POST-запросе валидирует введенные пользователем контактные данные:
        - проверяет заполненность обязательных полей (ФИО, телефон);
        - проверяет формат телефонного номера по регулярному выражению.
        В случае успешной валидации создает запись бронирования в базе данных
        и выполняет перенаправление на страницу этого же тура.

        Args:
            slug (str): Уникальный текстовый идентификатор тура в URL.

        Returns:
            tuple: ('Тур не найден', 404), если тур с указанным slug отсутствует.
            Response: Редирект на страницу тура (успешная отправка).
            str: HTML-шаблон (str) с формой и возможными ошибками валидации.
        """
        tour = Tour.query.filter_by(slug=slug).first()
        if tour is None:
            return 'Тур ненайден', 404

        errors: list[str] = []
        form: dict[str, str]= {}

        if request.method == 'POST':
            form['name'] = request.form.get('name', '').strip()
            form['surname'] = request.form.get('surname', '').strip()
            form["middle_name"] = request.form.get("middle_name", "").strip()
            form["phone"] = request.form.get("phone", "").strip()
            form["email"] = request.form.get("email", "").strip()

            if not form['name']:
                errors.append('Укажите имя')
            if not form['surname']:
                errors.append('Укажите фамилию')
            if not form['middle_name']:
                errors.append('Укажите отчество')
            if not form['phone']:
                errors.append('Укажите телефон')
            if not PATTERN_PHONE.match(form['phone']):
                errors.append('Неверно ввели номер телефона')

            if not errors:
                booking = Book(
                    tour_id=tour.id,
                    name=form['name'],
                    surname=form['surname'],
                    middle_name=form['middle_name'],
                    phone=form['phone'],
                    email=form['email'] or None,
                )

                db.session.add(booking)
                db.session.commit()

                return redirect(url_for('book_success', slug=slug))

        return render_template("tour_booking.html", tour=tour, slug=slug, errors=errors, form=form)

    @app.route('/tour/<slug>/success')
    def book_success(slug: str) -> Union[str, Response]:
        """Показать страницу подтверждения бронирования.
        Находит тур по slug и отображает страницу с сообщением
        об успешной заявке. Использует изображение тура как фон.
        Args:
            slug: Уникальный идентификатор тура в URL.
        Returns:
            HTML-страница с подтверждением бронирования."""
        tour = Tour.query.filter_by(slug=slug).first() # Находим тур
        if tour is None:
            return 'Тур не найден', 404
        return render_template("success.html", tour=tour, slug=slug)
        
        

    return app