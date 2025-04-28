from django.shortcuts import render, get_object_or_404, redirect
from django.forms import model_to_dict

from order.forms.customer import CustomerForm
from order.forms.search import SearchForm
from order.models.customer import Customer


def customers(request):
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


def customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    orders = customer.order_set.all()
    return render(request, "customer/detail.html", {"customer": customer, "orders": orders})


def customer_new(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.save()
            return redirect("customer", pk=customer.pk)
    else:
        form = CustomerForm()

    return render(request, "customer/form.html", {"form": form})


def customer_edit(request, pk):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.save()
            return redirect("customer", pk=customer.pk)
    else:
        customer = get_object_or_404(Customer, pk=pk)
        form = CustomerForm(model_to_dict(customer))

    return render(request, "customer/form.html", {"form": form})


def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    return redirect("customers")
