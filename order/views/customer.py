from django.shortcuts import render, get_object_or_404, redirect
from django.forms import model_to_dict
from django.db.models import Count, Sum

from order.forms.customer import CustomerForm
from order.forms.search import SearchForm
from order.models.customer import Customer


def list(request):
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
        "customer/list.html",
        {"form": form, "search_query": query, "customers": customers, "total": customers.count()}
    )


def detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    purchases = customer.customer_orders.values(
        "purchase__title",
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

    return render(request, "customer/detail.html", {"customer": customer, "orders": purchases})


def create(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.save()
            return redirect("customer", pk=customer.pk)
    else:
        form = CustomerForm()

    return render(request, "customer/form.html", {"form": form})


def edit(request, pk):
    if request.method == "POST":
        obj = get_object_or_404(Customer, id=pk)
        form = CustomerForm(request.POST, files=request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            return redirect("customer", pk=obj.pk)
    else:
        customer = get_object_or_404(Customer, pk=pk)
        form = CustomerForm(model_to_dict(customer))

    return render(request, "customer/form.html", {"form": form})


def delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    return redirect("customers")
