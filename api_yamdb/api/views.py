from api.filters import TitleFilter
from api.mixins import DestroyListCreatMixinSet
from api.permissions import (IsAdmin, IsAdminOrReadOnly,
                             IsAuthorModeratorAdminOrReadOnly)
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, ReviewSerializer,
                             SignupSerializer, TitleCreateSerializer,
                             TitleSerializer, TokenSerializer, UserSerializer)
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Genre, Review, Title, User


@api_view(('POST',))
def signup(request):
    """Регистрация и отправка кода на почту."""
    serializer = SignupSerializer(
        data=request.data,
    )
    serializer.is_valid(
        raise_exception=True,
    )
    try:
        user, _ = User.objects.get_or_create(
            **serializer.validated_data,
        )
    except IntegrityError:
        email = serializer.validated_data['email']
        text_error = (
            settings.EMAIL_ERROR
            if User.objects.filter(email=email).exists()
            else settings.USERNAME_ERROR
        )
        raise ValidationError(
            text_error,
            status.HTTP_400_BAD_REQUEST,
        )
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject='Регистрация в проекте YaMDb.',
        message=f'Ваш код подтверждения: {confirmation_code}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )
    return Response(
        serializer.data,
        status=status.HTTP_200_OK,
    )


@api_view(('POST',))
def get_token(request):
    """Получение токена авторизации."""
    serializer = TokenSerializer(
        data=request.data,
    )
    serializer.is_valid(
        raise_exception=True,
    )
    user = get_object_or_404(
        User, username=serializer.validated_data['username']
    )
    confirmation_code = serializer.data['confirmation_code']
    if not default_token_generator.check_token(
        user,
        confirmation_code,
    ):
        return Response(
            'Неверный код подтверждения',
            status=status.HTTP_400_BAD_REQUEST,
        )
    token = AccessToken.for_user(user)
    return Response(
        {'token': str(token)},
        status=status.HTTP_200_OK,
    )


class UserViewSet(viewsets.ModelViewSet):
    """Информация о пользователях."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = [
        'get',
        'post',
        'patch',
        'delete',
    ]

    @action(
        detail=False,
        methods=[
            'get',
            'patch',
        ],
        url_path='me',
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request, pk=None):
        instance = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(instance)
            return Response(
                serializer.data,
            )
        serializer = self.get_serializer(
            instance,
            request.data,
            partial=True,
        )
        serializer.is_valid(
            raise_exception=True,
        )
        serializer.save(
            role=instance.role,
            partial=True,
        )
        return Response(
            serializer.data,
        )


class CategoryViewSet(DestroyListCreatMixinSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(DestroyListCreatMixinSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score'),
    )
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
    )
    filterset_class = TitleFilter
    ordering_fields = (
        'category__slug',
        'genre__slug',
        'name',
        'year',
    )

    def get_serializer_class(self):
        if self.action in [
            'list',
            'retrieve',
        ]:
            return TitleSerializer
        return TitleCreateSerializer


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorModeratorAdminOrReadOnly,)
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination

    def get_review(self, model, value):
        return get_object_or_404(model, id=self.kwargs.get(value))

    def get_queryset(self):
        return self.get_review(Review, 'review_id').comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.get_review(Review, 'review_id'),
        )


class ReviewViewSet(viewsets.ModelViewSet):
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthorModeratorAdminOrReadOnly,)
    serializer_class = ReviewSerializer

    def get_title(self, model, value):
        return get_object_or_404(model, pk=self.kwargs.get(value))

    def get_queryset(self):
        return self.get_title(Title, 'title_id').reviews.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.get_title(Title, 'title_id'),
        )
