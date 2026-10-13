"""Модуль хранить данные о турах и заказах
Для просмотра данных выполнить в консоли:
from explore.models import Tour, Book
Tour.query.all()
Book.query.all()"""


from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Tour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    image = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Tour id = {self.id} slug = {self.slug}>'


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tour_id = db.Column(db.Integer, db.ForeignKey("tour.id"), nullable=False)
   
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Book {self.surname} {self.name}, tour_id={self.tour_id}>"