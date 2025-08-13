import pytest
from datetime import date
from django.contrib.auth import get_user_model
from order.models import Purchase

User = get_user_model()


@pytest.mark.django_db
def test_create_purchase():
    purchase = Purchase.objects.create(title="Закупка №1", exchange=85.5)
    assert purchase.pk is not None
    assert purchase.title == "Закупка №1"
    assert purchase.exchange == 85.5
    assert purchase.other_expenses == 0
    assert purchase.created_at is not None


@pytest.mark.django_db
def test_str_representation():
    purchase = Purchase.objects.create(title="Весенняя закупка", exchange=80)
    assert str(purchase) == "Весенняя закупка"


@pytest.mark.django_db
def test_open_and_close_methods():
    purchase = Purchase.objects.create(title="Открытие", exchange=80)
    assert purchase.opened_date is None
    assert purchase.closed_date is None

    today = date.today()
    purchase.open(today)
    assert purchase.opened_date == today

    purchase.close(today)
    assert purchase.closed_date == today


@pytest.mark.django_db
def test_is_opened_property():
    purchase = Purchase.objects.create(title="Статус", exchange=80)
    assert purchase.is_opened is True

    purchase.close(date.today())
    assert purchase.is_opened is False


@pytest.mark.django_db
def test_ordering_by_opened_date():
    Purchase.objects.create(title="Позже", exchange=80, opened_date=date(2024, 5, 1))
    Purchase.objects.create(title="Раньше", exchange=80, opened_date=date(2024, 1, 1))
    titles = [p.title for p in Purchase.objects.all()]
    assert titles == ["Раньше", "Позже"]


@pytest.mark.django_db
def test_author_assignment():
    user = User.objects.create(username="zakupshik")
    purchase = Purchase.objects.create(title="С автором", exchange=80, author=user)
    assert purchase.author.username == "zakupshik"


@pytest.mark.django_db
def test_decimal_fields_accept_valid_values():
    purchase = Purchase.objects.create(
        title="Цены",
        exchange=85.5,
        weight=12.34,
        dilivery_cost1=500.00,
        dilivery_cost2=300.00,
        other_expenses=150.00,
    )
    assert purchase.weight == 12.34
    assert purchase.dilivery_cost1 == 500.00
    assert purchase.dilivery_cost2 == 300.00
    assert purchase.other_expenses == 150.00
