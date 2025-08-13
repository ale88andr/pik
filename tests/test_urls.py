import pytest
from django.urls import reverse, NoReverseMatch

# Список именованных маршрутов
named_urls = [
    "dashboard",
    "orders",
    "order-new",
    "order-edit",
    "order-buy",
    "order-set-track",
    "order-set-delivered",
    "order-set-arrived",
    "order-delete",
    "order",
    "customers",
    "customer-edit",
    "customer-delete",
    "customer",
    "customer-purchase-xls",
    "customer-new-order",
    "customer-purchase",
    "customer-new",
    "purchases",
    "purchase-edit",
    "purchase-delete",
    "purchase-new-order",
    "purchase",
    "purchase-new",
    "purchase-xls",
    "purchase-cargo-xls",
]


@pytest.mark.django_db
@pytest.mark.parametrize("name", named_urls)
def test_named_url_access(client, name):
    # Пробуем разные варианты kwargs
    for kwargs in [{"pk": 1, "purchase_pk": 1}, {"pk": 1}, {}]:
        try:
            url = reverse(name, kwargs=kwargs)
            response = client.get(url)
            assert response.status_code in [
                200,
                302,
                403,
                404,
            ], f"Неверный статус для {url}: {response.status_code}"
            return
        except NoReverseMatch:
            continue

    pytest.fail(f"Не удалось разрешить маршрут: {name}")
