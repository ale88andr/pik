from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.forms import model_to_dict
from django.db.models import Count, Sum
from django.contrib import messages

from app.services import export_data_to_excel
from order.forms.customer import CustomerForm
from order.forms.order import CreatePurchaseCustomerOrderForm
from order.forms.search import SearchForm
from order.models.customer import Customer
from order.models.order import Order
from order.models.purchase import Purchase
from app.settings import STATIC_ROOT


PAGE_SECTION = "Клиенты"
PAGE_SECTION_URL = "customers"


def index(request):
    form = SearchForm()
    query = request.GET.get("query")
    sort = request.GET.get("sort", "created_at")

    if query:
        form = SearchForm(request.GET)
        if form.is_valid():
            search_query = form.cleaned_data["query"]
            customers = Customer.objects.search(query=search_query).order_by(sort)
    else:
        customers = Customer.objects.all().order_by(sort)

    return render(
        request,
        "customer/v2/list.html",
        {
            "form": form, 
            "search_query": query, 
            "customers": customers, 
            "total": customers.count(),
            "page_section": PAGE_SECTION,
            "page_section_url": PAGE_SECTION_URL,
            "page_title": "Список клиентов"
        }
    )


def detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    purchases = customer.customer_orders.values(
        "purchase__title",
        "purchase__id",
        "purchase",
        "purchase__exchange"
        ).annotate(
            total=Count("id"),
            sum=Sum("order_price"),
            tax=Sum("order_price") * customer.tax / 100
        )

    for purchase in purchases:
        purchase["sum"] = round(purchase.get("sum"), 2)
        purchase["sum_in_rub"] = round(purchase.get("sum") * purchase.get("purchase__exchange"), 2)
        purchase["tax"] = round(purchase.get("tax"), 2)
        purchase["tax_in_rub"] = round(purchase.get("tax") * purchase.get("purchase__exchange"), 2)

    return render(
        request, 
        "customer/v2/detail.html", 
        {
            "customer": customer, 
            "orders": purchases,
            "page_section": PAGE_SECTION,
            "page_section_url": PAGE_SECTION_URL,
            "page_title": customer
        }
    )


def create(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.save()
            return redirect("customer", pk=customer.pk)
    else:
        form = CustomerForm()

    return render(
        request, 
        "customer/v2/form.html", 
        {
            "form": form,
            "page_section": PAGE_SECTION,
            "page_section_url": PAGE_SECTION_URL,
            "page_title": "Добавление нового клиента"
        }
    )


def create_order(request, pk, purchase_pk):
    if request.method == "POST":
        purchase = get_object_or_404(Purchase, id=purchase_pk)
        form = CreatePurchaseCustomerOrderForm(request.POST, files=request.FILES)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer_id = pk
            purchase.purchase_orders.add(order, bulk=False)

            messages.success(request, f"Заказ '{order.title}' оформлен")

            if "add_another" in request.POST:
                return redirect("create-customer-order", pk=pk, purchase_pk=purchase.pk)

            return redirect("customer-purchase", pk=pk, purchase_pk=purchase_pk)
        else:
            messages.error(request, "Возникли ошибки при заполнении формы, исправте их!")
    else:
        form = CreatePurchaseCustomerOrderForm()

    return render(
        request, 
        "order/v2/form.html", 
        {
            "form": form, 
            "is_new": True,
            "page_section": PAGE_SECTION,
            "page_section_url": PAGE_SECTION_URL,
            "page_title": "Добавление нового клиента"
        }
    )


def edit(request, pk):
    obj = get_object_or_404(Customer, id=pk)
    
    if request.method == "POST":
        form = CustomerForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            
            messages.success(request, "Данные клиента обновлены!")
            return redirect("customer", pk=obj.pk)
    else:
        form = CustomerForm(model_to_dict(obj))

    return render(
        request, 
        "customer/v2/form.html", 
        {
            "form": form,
            "page_section": PAGE_SECTION,
            "page_section_url": PAGE_SECTION_URL,
            "page_title": "Изменение данных клиента"
        }
    )


def delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    return redirect("customers")


def purchase(request, pk, purchase_pk):
    sort = request.GET.get("sort", "created_at")
    customer = get_object_or_404(Customer, pk=pk)
    purchase = get_object_or_404(Purchase, pk=purchase_pk)
    purchase_orders = customer.customer_orders.filter(purchase=purchase_pk)
    summary = purchase_orders.values("status").annotate(total=Count("id"))

    return render(
        request,
        "customer/v2/purchase.html",
        {
            "customer": customer,
            "orders": purchase_orders.order_by(sort),
            "purchase": purchase,
            "total": purchase_orders.count(),
            "summary": summary,
            "statuses": Order.Status.labels,
            "page_section": PAGE_SECTION,
            "page_section_url": PAGE_SECTION_URL,
            "page_title": f"{customer}: {purchase}"
        })


def export_purchase_to_excel(request, pk, purchase_pk):

    # Query the Person model to get all records
    customer = get_object_or_404(Customer, pk=pk)
    customer_purchase_orders = customer.customer_orders.filter(purchase=purchase_pk)

    response = export_data_to_excel(customer.name, customer_purchase_orders)

    return response
