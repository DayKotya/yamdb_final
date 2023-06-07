from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)

from reviews.validators import validate_username, validate_year


class User(AbstractUser):
    """Модель пользователя."""

    USER = 'user'
    ADMIN = 'admin'
    MODERATOR = 'moderator'

    USER_ROLES = (
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор'),
    )

    username = models.CharField(
        validators=(validate_username,),
        max_length=settings.NAME_LENGTH,
        unique=True,
        null=True,
        verbose_name='Имя пользователя',
    )
    email = models.EmailField(
        max_length=settings.EMAIL_LENGTH,
        unique=True,
        verbose_name='Электронная почта',
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=settings.NAME_LENGTH,
        blank=True,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=settings.NAME_LENGTH,
        blank=True,
    )
    bio = models.TextField(
        verbose_name='Биография',
        blank=True,
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=max(len(x[0]) for x in USER_ROLES),
        choices=USER_ROLES,
        default=USER,
        blank=True,
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                name='%(app_label)s_%(class)s_name_unique',
                fields=['username', 'email'],
            ),
        ]

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser or self.is_staff

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR


class AbstractModel(models.Model):
    """Абстрактная модель"""

    name = models.CharField(
        max_length=settings.USER_LENGTH,
        verbose_name='Название',
    )
    slug = models.SlugField(
        unique=True,
        max_length=settings.SLUG_LENGTH,
        verbose_name='Слаг',
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9]+$', message='Некорректный slug.'
            )
        ],
    )

    class Meta:
        abstract = True
        verbose_name = 'Модель'
        verbose_name_plural = 'Модели'
        ordering = ('-name',)

    def __str__(self) -> str:
        return self.name


class Category(AbstractModel):
    """Категории произведений."""

    class Meta(AbstractModel.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(AbstractModel):
    """Жанры произведений."""

    class Meta(AbstractModel.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """Произведения."""

    name = models.CharField(
        max_length=settings.USER_LENGTH,
        verbose_name='Название произведения',
        db_index=True,
    )
    year = models.PositiveSmallIntegerField(
        verbose_name='Год выпуска',
        validators=(validate_year,),
        db_index=True,
    )
    description = models.TextField(
        verbose_name='Описание произведения',
        blank=True,
        null=True,
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр',
        through='GenreTitle',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Категория',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('-year',)

    def display_genre(self):
        return ', '.join([genre.name for genre in self.genre.all()[:3]])

    display_genre.short_description = 'Жанр'

    def __str__(self) -> str:
        return self.name


class GenreTitle(models.Model):
    genre_id = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
    )
    title_id = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Жанр-Произведения'
        verbose_name_plural = 'Жанры-Произведений'

    def __str__(self) -> str:
        return f'{self.title_id} - {self.genre_id}'


class AbstractForReviewComments(models.Model):
    text = models.TextField(
        verbose_name='Текст отзыва',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор отзыва',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text


class Review(AbstractForReviewComments):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
    )
    score = models.SmallIntegerField(
        verbose_name='Оценка',
        default=0,
        validators=(
            MinValueValidator(1, 'Не может быть меньше 1'),
            MaxValueValidator(10, 'Не может быть больше 10'),
        ),
    )

    class Meta(AbstractForReviewComments.Meta):
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        default_related_name = 'reviews'
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'title',
                    'author',
                ],
                name='Автор может поставить только одну оценку',
            )
        ]


class Comment(AbstractForReviewComments):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв',
    )

    class Meta(AbstractForReviewComments.Meta):
        default_related_name = 'comments'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
