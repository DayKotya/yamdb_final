from django.conf import settings
from django.utils import timezone
from rest_framework import serializers
from reviews.models import Category, Comment, Genre, Review, Title, User
from reviews.validators import validate_username


class SignupSerializer(serializers.Serializer):
    """Сериализатор регистрации пользователя."""

    username = serializers.CharField(
        required=True,
        max_length=settings.NAME_LENGTH,
        validators=[validate_username],
    )
    email = serializers.EmailField(
        required=True,
        max_length=settings.EMAIL_LENGTH,
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
        )


class TokenSerializer(serializers.Serializer):
    """Сериализатор получения токена авторизации."""

    username = serializers.CharField(
        required=True,
        max_length=settings.NAME_LENGTH,
        validators=[validate_username],
    )
    confirmation_code = serializers.CharField(
        required=True,
    )


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели пользователя"""

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=('username', 'email'),
                message=("Some custom message."),
            )
        ]


class CategorySerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(
        max_length=settings.SLUG_LENGTH,
        min_length=None,
        allow_blank=False,
    )

    def validate_slug(self, value):
        if Category.objects.filter(slug=value).exists():
            raise serializers.ValidationError('Такой slug уже используется!')
        return value

    class Meta:
        model = Category
        fields = (
            'name',
            'slug',
        )
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(
        max_length=settings.SLUG_LENGTH,
        min_length=None,
        allow_blank=False,
    )

    def validate_slug(self, value):
        if Genre.objects.filter(slug=value).exists():
            raise serializers.ValidationError('Такой slug уже используется!')
        return value

    class Meta:
        model = Genre
        fields = (
            'name',
            'slug',
        )
        lookup_field = 'slug'


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True)
    rating = serializers.IntegerField()

    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category',
        )
        model = Title


class TitleCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
    )
    year = serializers.IntegerField()

    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category',
        )
        model = Title

    def validate_year(self, value):
        year_now = timezone.now().year
        if value <= 0 or value > year_now:
            raise serializers.ValidationError(
                'Год создания должен быть нашей эры и не больше текущего.'
            )
        return value

    def to_representation(self, title):
        title.rating = 0
        return TitleSerializer(title).data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        fields = '__all__'
        model = Comment
        read_only_fields = ('review',)


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = (
            'id',
            'text',
            'author',
            'score',
            'pub_date',
        )
        model = Review

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        title_id = self.context['request'].parser_context['kwargs']['title_id']
        author = self.context['request'].user.id
        if Review.objects.filter(
            author=author,
            title_id=title_id,
        ).exists():
            raise serializers.ValidationError(
                'Вы уже писали отзыв на это произведения!'
            )
        return data
