import pytest
from django.urls import reverse, NoReverseMatch

# Список именованных маршрутов
named_urls = [
    "dashboard",
    "orders",
    "create-order",
    "order_edit",
    "order-buy",
    "order-set-track",
    "order-set-delivered",
    "order-set-arrived",
    "order_delete",
    "order",
    "customers",
    "customer_edit",
    "customer_delete",
    "customer",
    "customer-purchase-xls2",
    "create-customer-order",
    "customer-purchase",
    "customer_new",
    "purchases",
    "edit-purchase",
    "delete-purchase",
    "create-purchase-order",
    "purchase",
    "create-purchase",
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
