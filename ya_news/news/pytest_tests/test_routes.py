from http import HTTPStatus

from django.urls import reverse

import pytest
from pytest_django.asserts import assertRedirects


# Маршруты
@pytest.mark.django_db
@pytest.mark.parametrize(
    "page_url", ("news:home", "users:login", "users:logout", "users:signup")
)
def test_pages_avialable_for_anonimous_user(client, page_url):
    """Главная страница и страницы авторизации доступны анониму"""
    url = reverse(page_url)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_pages_availability_for_author(client, news):
    """Страница отдельной новости доступна анонимну"""
    url = reverse("news:detail", args=(news.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    "parametrized_client, expected_status",
    (
        (pytest.lazy_fixture("not_author_client"), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture("author_client"), HTTPStatus.OK),
    ),
)
@pytest.mark.parametrize(
    "page_url",
    ("news:edit", "news:delete"),
)
def test_pages_availability_for_different_users(
    parametrized_client, page_url, comment, expected_status
):
    """Cтраница редактирования/удаления комментария доступна только автору"""
    url = reverse(page_url, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


# Редиректы
@pytest.mark.parametrize("page_url", ("news:delete", "news:edit"))
def test_redirect_for_delete_comments(client, comment, page_url):
    """Аноним не может зайти на страницы ректирования/удаления комментов."""
    url = reverse(page_url, args=(comment.id,))
    login_url = reverse("users:login")
    expected_url = f"{login_url}?next={url}"

    response = client.get(url)
    assertRedirects(response, expected_url)
