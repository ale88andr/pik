import pytest
from order.models import Marketplace


@pytest.mark.django_db
def test_create_marketplace():
    mp = Marketplace.objects.create(title="AliExpress", url="https://aliexpress.com")
    assert mp.pk is not None
    assert mp.title == "AliExpress"
    assert mp.url == "https://aliexpress.com"


@pytest.mark.django_db
def test_str_representation():
    mp = Marketplace.objects.create(title="Ozon")
    assert str(mp) == "Ozon"


@pytest.mark.django_db
def test_unique_title():
    Marketplace.objects.create(title="Ozon")
    with pytest.raises(Exception):
        Marketplace.objects.create(title="Ozon")


@pytest.mark.django_db
def test_unique_url():
    Marketplace.objects.create(title="Yandex Market", url="https://market.yandex.ru")
    with pytest.raises(Exception):
        Marketplace.objects.create(title="Another", url="https://market.yandex.ru")


@pytest.mark.django_db
def test_null_and_blank_url():
    mp = Marketplace.objects.create(title="No URL")
    assert mp.url is None


@pytest.mark.django_db
def test_ordering_by_title():
    Marketplace.objects.create(title="Ozon")
    Marketplace.objects.create(title="Amazon")
    titles = [m.title for m in Marketplace.objects.all()]
    assert titles == sorted(titles)
