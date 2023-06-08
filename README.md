# yamdb_final
yamdb_final

![Django-app workflow](https://github.com/DayKotya/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

<h2 align="center">Проект YaMDb</h2>
<h3 align="center">http://127.0.0.1:8000/redoc/ Документация для YaMDb</h3>
<h4>Проект YaMDb собирает отзывы пользователей на произведения. Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.</h4>

<h2>Установка:</h2>

<ul>
<li><p>Скопируйте репозиторий в свою папку: https://github.com/utopya88/api_yamdb.git</p></li>

<li><p>Установите виртуальное окружение: python -m venv venv</p></li>

<li><p>Активируйте виртуальное окружение: source venv/Scripts/activate</p></li>

<li><p>Установите зависимости из requirements.txt: pip install -r requirements.txt</p></li>

<li><p>Выполните миграции: python manage.py migrate</p></li>
</li>
<li><p>Запустите сервер: python manage.py runserver</p></li>
</ul>


<h2>Шаблон наполнения env-файла:</h2>

<li><p>DB_ENGINE=django.db.backends.postgresql</p>
<p>DB_NAME=postgres</p>
<p>POSTGRES_USER=username</p>
<p>POSTGRES_PASSWORD=password</p>
<p>DB_HOST=db</p>
<p>DB_PORT=1234</p></li>

<h2>Запуск контейнера:</h2>
<li><p>После копирования репозитория примените команду: docker-compose up в директории с файлом docker-compose.yaml</p></li>
<li><p>Выполните по очереди следующие команды: </p></li>

```
docker-compose exec web python manage.py migrate
```

```
docker-compose exec web python manage.py createsuperuser
```

```
docker-compose exec web python manage.py collectstatic --no-input 
```

<h2>Использованные технологии:</h2>

<ul>
<li><p>Python 3.7.9</p></li>
<li><p>Django 2.2.16</p></li>
<li><p>Djangorestframework 3.12.4</p></li>
</ul>

<h2>Примеры запросов к API:</h2>

<ul>
<li><p>Регистрация нового пользователя (POST): http://127.0.0.1:8000/api/v1/auth/signup/</p></li>
<li><p>Получение JWT-токена (POST): http://127.0.0.1:8000/api/v1/auth/token/</p></li>
<li><p>Получение списка всех категорий (GET): http://127.0.0.1:8000/api/v1/categories/</p></li>
<li><p>Получение списка всех жанров (GET): http://127.0.0.1:8000/api/v1/genres/</p></li>
<li><p>Получение списка всех произведений (GET): http://127.0.0.1:8000/api/v1/titles/</p></li>
<li><p>Получение списка всех отзывов (GET): http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/</p></li>
<li><p>Получение списка всех комментариев к отзыву (GET): http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/{review_id}/comments/</p></li>
<li><p>Получение списка всех пользователей (GET): http://127.0.0.1:8000/api/v1/users/</p></li>
<li><p>Получение пользователя по username (GET): http://127.0.0.1:8000/api/v1/users/{username}/</p></li>
<li><p>Получение данных своей учетной записи (GET): http://127.0.0.1:8000/api/v1/users/me/</p></li>
</ul>

<h1>Авторы проекта:</h1>
<h2>Главный разработчик и код ревьювер: Дмитрий Савченко. https://github.com/utopya88/</h2>
<h3>Владимир</h3>
<h3>Антон</h3>
