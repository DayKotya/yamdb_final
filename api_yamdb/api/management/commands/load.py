import logging
import os
import sys
from csv import DictReader

from django.conf import settings
from django.core.management import BaseCommand
from reviews.models import (Category, Comment, Genre, GenreTitle, Review,
                            Title, User)

DATA_DIR = settings.BASE_DIR / 'static/data'


class Command(BaseCommand):
    help = "Загрузка данных из csv"

    def fill_category(self):
        if not os.path.exists(DATA_DIR / 'category.csv'):
            raise FileNotFoundError(
                f'Файл для загрузки категорий не найден в {DATA_DIR}\n'
                'Проверьте, что файл category.csv существует.'
            )
        rows = DictReader(open(DATA_DIR / 'category.csv', encoding='utf-8'))
        for row in rows:
            if not Category.objects.filter(slug=row['slug']).exists():
                category = Category(
                    id=row['id'], name=row['name'], slug=row['slug']
                )
                Category.save(category)
            else:
                logging.error(f'Категория {row["slug"]} уже существует!')

        logging.debug('Загрузка данных о категории прошла успешно!')

    def fill_genre_title(self):
        if not os.path.exists(DATA_DIR / 'titles.csv'):
            raise FileNotFoundError(
                f'Файл для загрузки жанров для тайтлов не найден в {DATA_DIR}.'
                'Проверьте, что файл genre_title.csv существует.'
            )
        rows = DictReader(open(DATA_DIR / 'genre_title.csv', encoding='utf-8'))
        for row in rows:
            if Genre.objects.filter(id=row['genre_id']).exists():
                genre = Genre.objects.get(id=row['genre_id'])
                if Title.objects.filter(id=row['title_id']).exists():
                    title = Title.objects.get(id=row['title_id'])
                    genretitle = GenreTitle(
                        id=row['id'],
                        title_id=title,
                        genre_id=genre,
                    )
                    GenreTitle.save(genretitle)
                else:
                    logging.error('Не найдено произведение!')
            else:
                logging.error('Не найден жанр!')

        logging.debug('Загрузка данных о жанрах для тайтлов прошла успешно!')

    def fill_genre(self):
        if not os.path.exists(DATA_DIR / 'genre.csv'):
            raise FileNotFoundError(
                f'Файл для загрузки жанров не найден в {DATA_DIR}\n'
                'Проверьте, что файл genre.csv существует.'
            )
        rows = DictReader(open(DATA_DIR / 'genre.csv', encoding='utf-8'))
        for row in rows:
            if not Genre.objects.filter(slug=row['slug']).exists():
                genre = Genre(id=row['id'], name=row['name'], slug=row['slug'])
                Genre.save(genre)
            else:
                logging.error(f'Жанр {row["slug"]} уже существует!')

        logging.debug('Загрузка данных о жанрах прошла успешно!')

    def fill_titles(self):
        if not os.path.exists(DATA_DIR / 'titles.csv'):
            raise FileNotFoundError(
                f'Файл для загрузки тайтлов не найден в {DATA_DIR}\n'
                'Проверьте, что файл titles.csv существует.'
            )
        rows = DictReader(open(DATA_DIR / 'titles.csv', encoding='utf-8'))
        for row in rows:
            if not Title.objects.filter(
                name=row['name'], year=row['year']
            ).exists():
                title = Title(
                    id=row['id'],
                    name=row['name'],
                    year=row['year'],
                    category_id=row['category'],
                )
                Title.save(title)
            else:
                logging.error(
                    f'Фильм - {row["name"]} {row["year"]} '
                    f'года выпуска уже существует!'
                )

        logging.debug('Загрузка данных о тайтлах прошла успешно!')

    def fill_users(self):
        if not os.path.exists(DATA_DIR / 'users.csv'):
            raise FileNotFoundError(
                f'Файл для загрузки пользователей не найден в {DATA_DIR}\n'
                'Проверьте, что файл users.csv существует.'
            )
        rows = DictReader(open(DATA_DIR / 'users.csv', encoding='utf-8'))
        for row in rows:
            if not User.objects.filter(
                username=row['username'], email=row['email']
            ).exists():
                user = User(
                    id=row['id'],
                    username=row['username'],
                    email=row['email'],
                    role=row['role'],
                    bio=row['bio'],
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                )
                User.save(user)
            else:
                logging.error(
                    f'Пользователь {row["username"]} '
                    f'c почтой {row["email"]} уже существует'
                )

        logging.debug('Загрузка данных о пользователях прошла успешно!')

    def fill_review(self):
        if not os.path.exists(DATA_DIR / 'review.csv'):
            raise FileNotFoundError(
                f'Файл для загрузки отзывов не найден в {DATA_DIR}\n'
                'Проверьте, что файл review.csv существует.'
            )
        rows = DictReader(open(DATA_DIR / 'review.csv', encoding='utf-8'))
        for row in rows:
            author = User.objects.get(id=row['author'])
            title = Title.objects.get(id=row['title_id'])
            if not Review.objects.filter(title=title, author=author).exists():
                review = Review(
                    id=row['id'],
                    title=title,
                    text=row['text'],
                    author=author,
                    score=row['score'],
                    pub_date=row['pub_date'],
                )
                Review.save(review)
            else:
                logging.error(
                    f'Отзыв на произведение {title.name} '
                    f'от автора {author.username} уже существует!'
                )

        logging.debug('Загрузка данных об отзывах прошла успешно!')

    def fill_comments(self):
        if not os.path.exists(DATA_DIR / 'review.csv'):
            raise FileNotFoundError(
                f'Файл для загрузки комментариев не найден в {DATA_DIR}\n'
                'Проверьте, что файл comments.csv существует.'
            )
        rows = DictReader(open(DATA_DIR / 'comments.csv', encoding='utf-8'))
        for row in rows:
            author = User.objects.get(id=row['author'])
            review = Review.objects.get(id=row['review_id'])
            if not Comment.objects.filter(
                author=author, review=review
            ).exists():
                comment = Comment(
                    id=row['id'],
                    review=review,
                    text=row['text'],
                    author=author,
                    pub_date=row['pub_date'],
                )
                Comment.save(comment)
            else:
                logging.error(
                    f'Комментарий пользователя {author.username} '
                    f'к обзору на произведение {review.title.name} '
                    f'уже добавлен!'
                )

        logging.debug('Загрузка данных об отзывах прошла успешно!')

    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(stream=sys.stdout)
        logger.addHandler(hdlr=handler)
        self.fill_category()
        self.fill_users()
        self.fill_genre()
        self.fill_titles()
        self.fill_genre_title()
        self.fill_review()
        self.fill_comments()
