import pytest
from decimal import Decimal
from order.models import Order, Customer, Purchase, Marketplace


@pytest.fixture
def setup_order(db):
    customer = Customer.objects.create(name="Клиент", tax=10)
    purchase = Purchase.objects.create(title="Закупка", exchange=80)
    Marketplace.objects.create(title="AliExpress", url="https://aliexpress.com")
    order = Order.objects.create(
        title="Товар",
        url="https://aliexpress.com/item/123",
        order_price=Decimal("100"),
        buy_price=Decimal("80"),
        exchange=Decimal("85"),
        customer=customer,
        purchase=purchase,
    )
    return order


@pytest.mark.django_db
def test_order_str(setup_order):
    assert str(setup_order) == "Товар"


@pytest.mark.django_db
def test_marketplace_auto_assignment(setup_order):
    assert setup_order.marketplace.title == "AliExpress"


@pytest.mark.django_db
def test_calculate_order_exchange_price(setup_order):
    assert setup_order.calculate_order_exchange_price() == round(
        Decimal("100") * Decimal("85"), 2
    )


@pytest.mark.django_db
def test_calculate_buy_exchange_price(setup_order):
    assert setup_order.calculate_buy_exchange_price() == round(
        Decimal("80") * Decimal("85"), 2
    )


@pytest.mark.django_db
def test_tax_property(setup_order):
    assert setup_order.tax == Decimal("10.00")


@pytest.mark.django_db
def test_get_difference(setup_order):
    expected = round(Decimal("100") * Decimal("80") - Decimal("80") * Decimal("85"), 2)
    assert setup_order.get_difference == expected


@pytest.mark.django_db
def test_get_total_profit(setup_order):
    profit = setup_order.calculate_difference_tax() + setup_order.get_difference
    assert setup_order.get_total_profit == profit


@pytest.mark.django_db
def test_search_manager(setup_order):
    results = Order.objects.search("Тов")
    assert setup_order in results
