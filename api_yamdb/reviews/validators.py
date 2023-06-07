import re

from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year(value):
    year_now = timezone.now().year
    if value <= 0 or value > year_now:
        raise ValidationError(
            'Год создания должен быть нашей эры и не больше текущего.'
        )


def validate_username(username):
    pattern = r"^[\w.@+-]+"
    match = set(re.sub(pattern, "", username))

    if match:
        raise ValidationError(
            f'В username недопустимы символы {" ".join(match)}'
        )

    if username == 'me':
        raise ValidationError(
            ('Имя пользователя не может быть me'),
            params={'value': username},
        )
