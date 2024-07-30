from datetime import timedelta
import pytest

from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from news.models import News, Comment

User = get_user_model()


@pytest.mark.django_db
def test_news_count(client):
    """Количество новостей на странице не превышает пагинацию."""

    all_news = [
        News(title=f"Новость {index}", text="Текст.")
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)

    response = client.get(reverse("news:home"))
    object_list = response.context["object_list"]
    news_count = len(object_list)

    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client):
    """Сортировка новостей идёт от самой новых к старым."""

    today = timezone.now()
    all_news = [
        News(
            title=f"Новость {index}",
            text="Просто текст.",
            date=today - timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)

    response = client.get(reverse("news:home"))
    object_list = response.context["object_list"]
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)

    assert all_dates == sorted_dates


def test_comments_order(author, author_client, news):
    """Сортировка комментариев идёт от старых к новому."""

    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f"Tекст {index}",
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    response = author_client.get(reverse("news:detail", args=(news.id,)))
    assert "news" in response.context
    news = response.context["news"]
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
@pytest.mark.parametrize(
    "parametrized_client, form_status",
    (
        (pytest.lazy_fixture("author_client"), True),
        (pytest.lazy_fixture("client"), False),
    ),
)
def test_anonymous_client_has_no_form(parametrized_client, form_status, news):
    """Анонимному пользователю недоступна форма для отправки комментария"""

    url = reverse("news:detail", args=(news.id,))
    response = parametrized_client.get(url)
    form_check = "form" in response.context
    assert form_check is form_status
