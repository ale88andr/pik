import pytest
from django.core.exceptions import ValidationError
from order.models import Customer


@pytest.mark.django_db
def test_create_customer():
    customer = Customer.objects.create(
        name="Иван Иванов", phone="+7(777)777-77-77", telegram_id="ivan777", tax=10
    )
    assert customer.pk is not None
    assert customer.name == "Иван Иванов"
    assert customer.tax == 10


@pytest.mark.django_db
def test_str_representation():
    customer = Customer.objects.create(name="Алиса")
    assert str(customer) == "Алиса"


@pytest.mark.django_db
def test_invalid_phone():
    customer = Customer(name="Ошибка", phone="12345")
    with pytest.raises(ValidationError):
        customer.full_clean()


@pytest.mark.django_db
def test_invalid_telegram_id():
    customer = Customer(name="Ошибка", telegram_id="invalid id!")
    with pytest.raises(ValidationError):
        customer.full_clean()


@pytest.mark.django_db
def test_tax_out_of_bounds():
    customer = Customer(name="Налог", tax=150)
    with pytest.raises(ValidationError):
        customer.full_clean()


@pytest.mark.django_db
def test_ordering_by_name():
    Customer.objects.create(name="Борис")
    Customer.objects.create(name="Алексей")
    names = [c.name for c in Customer.objects.all()]
    assert names == sorted(names)


@pytest.mark.django_db
def test_search_by_name():
    Customer.objects.create(name="Мария", phone="+7(777)777-77-77", telegram_id="masha")
    Customer.objects.create(name="Олег", phone="+7(777)777-77-78", telegram_id="oleg")

    results = Customer.objects.search("Мар")
    assert len(results) == 1
    assert results[0].name == "Мария"


@pytest.mark.django_db
def test_search_by_phone():
    Customer.objects.create(name="Анна", phone="+7(777)123-45-67")
    results = Customer.objects.search("123")
    assert len(results) == 1
    assert results[0].name == "Анна"


@pytest.mark.django_db
def test_search_by_telegram():
    Customer.objects.create(name="Дима", telegram_id="dima777")
    results = Customer.objects.search("777")
    assert len(results) == 1
    assert results[0].name == "Дима"
