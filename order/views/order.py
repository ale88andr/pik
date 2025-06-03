from datetime import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.forms import model_to_dict
from django.contrib import messages

from app.utils import is_search_form_filled
from order.forms.order import BuyOrderForm, CreateOrderForm, OrderForm, OrderSearchForm, SetTrackNumOrderForm
from order.models.order import Order


PAGE_SECTION = "Заказы"
PAGE_SECTION_URL = "orders"


def list(request):
    form = OrderSearchForm(request.GET)
    search_form = is_search_form_filled(request, form.fields)
    sort = request.GET.get("sort", "created_at")

    if search_form and form.is_valid():
        orders = Order.objects

        search = form.cleaned_data["query"]
        customer_id = form.cleaned_data["customer"]
        marketplace_id = form.cleaned_data["marketplace"]
        purchase_id = form.cleaned_data["purchase"]
        status = int(form.cleaned_data["status"]) if form.cleaned_data["status"] else None

        if search:
            orders = orders.search(query=search)

        if customer_id:
            orders = orders.filter(customer=customer_id)

        if marketplace_id:
            orders = orders.filter(marketplace=marketplace_id)

        if status is not None:
            orders = orders.filter(status=status)

        if purchase_id:
            orders = orders.filter(purchase=purchase_id)
    else:
        orders = Order.objects.all()

    return render(
        request,
        "order/v2/list.html",
        {
            "form": form,
            "records": orders.order_by(sort),
            "total": orders.count(),
            "page_section": PAGE_SECTION,
            "page_section_url": PAGE_SECTION_URL,
            "page_title": "Список заказов"
        }
    )


def detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(
        request,
        "order/v2/detail.html",
        {
            "order": order,
            "page_section": PAGE_SECTION,
            "page_section_url": PAGE_SECTION_URL,
            "page_title": order
        }
    )


def create(request):
    if request.method == "POST":
        form = CreateOrderForm(request.POST, files=request.FILES)
        if form.is_valid():
            order = form.save()
            messages.success(request, f"Заказ '{order.title}' оформлен")

            if "add_another" in request.POST:
                return redirect("create-order")

            return redirect("orders")
        else:
            messages.error(request, "Возникли ошибки при заполнении формы, исправте их!")
    else:
        form = CreateOrderForm()

    return render(
        request,
        "order/v2/form.html",
        {
            "form": form,
            "is_new": True,
            "page_section": PAGE_SECTION,
            "page_section_url": PAGE_SECTION_URL,
            "page_title": "Добавление нового заказа"
        }
    )


def edit(request, pk):
    obj = get_object_or_404(Order, id=pk)

    if request.method == "POST":
        form = OrderForm(request.POST, files=request.FILES, instance=obj)
        if form.is_valid():
            form.save()

            messages.success(request, "Данные заказа обновлены!")
            return redirect("order", pk=obj.pk)
    else:
        form = OrderForm(model_to_dict(obj))

    return render(
        request,
        "order/v2/form.html",
        {
            "form": form,
            "page_section": PAGE_SECTION,
            "page_section_url": PAGE_SECTION_URL,
            "page_title": f"Редактирование данных заказа: {obj}"
        }
    )


def buy(request, pk):
    order = get_object_or_404(Order, id=pk)
    if request.method == "POST":
        form = BuyOrderForm(request.POST, instance=order)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.status = Order.Status.BUYED
            instance.buyed_at = datetime.date.now()
            instance.save()

            messages.success(request, "Данные заказа обновлены!")
            return redirect("order", pk=order.pk)
    else:
        form = BuyOrderForm(model_to_dict(order))

    return render(request, "order/v2/form.html", {"form": form})


def set_track_num(request, pk):
    order = get_object_or_404(Order, id=pk)
    if request.method == "POST":
        form = SetTrackNumOrderForm(request.POST, instance=order)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.status = Order.Status.IN_DELIVERY
            instance.save()

            messages.success(request, "Трек номер отслеживания доставки добавлен!")
            return redirect(request.headers.get("Referer"), "/")
    else:
        form = SetTrackNumOrderForm(model_to_dict(order))

    return render(request, "order/v2/form.html", {"form": form})


def set_delivered(request, pk):
    order = get_object_or_404(Order, id=pk)
    if request.method == "POST":
        order.status = Order.Status.DELIVERED
        order.save()

        messages.success(request, f"Статус заказа {order} обновлен!")
        return redirect(request.headers.get("Referer"), "/")


def set_arrived(request, pk):
    order = get_object_or_404(Order, id=pk)
    if request.method == "POST":
        order.status = Order.Status.ARRIVED
        order.save()

        messages.success(request, f"Статус заказа {order} обновлен!")
        return redirect(request.headers.get("Referer"), "/")


def delete(request, pk):
    obj = get_object_or_404(Order, pk=pk)
    obj.delete()
    return redirect("orders")
