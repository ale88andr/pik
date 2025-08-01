from datetime import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.forms import model_to_dict
from django.contrib import messages

from app.utils import is_search_form_filled
from order.constants import (
    DEFAULT_FORM_ERROR,
    ORDER_ADD_TITLE,
    ORDER_CREATE_MSG,
    ORDER_EDIT_TITLE,
    ORDER_LIST_TITLE,
    ORDER_STATUS_MSG,
    ORDER_TRACK_MSG,
    ORDER_UPDATE_MSG,
    ORDERS,
    ORDERS_URL
)
from order.forms.order import BuyOrderForm, CreateOrderForm, OrderForm, OrderSearchForm, SetArrivedOrderForm, SetTrackNumOrderForm
from order.models.order import Order


def list(request):
    form = OrderSearchForm(request.GET)
    sort = request.GET.get("sort", "created_at")
    orders = Order.objects

    if is_search_form_filled(request, form.fields) and form.is_valid():
        search = form.cleaned_data["query"]

        if search:
            orders = orders.search(query=search)

        filters = {
            "customer": form.cleaned_data["customer"],
            "marketplace": form.cleaned_data["marketplace"],
            "purchase": form.cleaned_data["purchase"],
            "status": int(form.cleaned_data["status"]) if form.cleaned_data["status"] else None
        }

        filters = {key: value for key, value in filters.items() if value is not None}
        orders = orders.filter(**filters)
    else:
        orders.all()

    return render(
        request,
        "order/list.html",
        {
            "form": form,
            "records": orders.order_by(sort),
            "total": orders.count(),
            "page_section": ORDERS,
            "page_section_url": ORDERS_URL,
            "page_title": ORDER_LIST_TITLE
        }
    )


def detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(
        request,
        "order/detail.html",
        {
            "order": order,
            "page_section": ORDERS,
            "page_section_url": ORDERS_URL,
            "page_title": order
        }
    )


def create(request):
    form = CreateOrderForm(request.POST, files=request.FILES) if request.method == "POST" else CreateOrderForm()
    if request.method == "POST":
        form = CreateOrderForm(request.POST, files=request.FILES)
        if form.is_valid():
            order = form.save()
            messages.success(request, f"{ORDER_CREATE_MSG} {order.title}")

            if "add_another" in request.POST:
                return redirect("create-order")

            return redirect(ORDERS_URL)
        else:
            messages.error(request, DEFAULT_FORM_ERROR)
    else:
        form = CreateOrderForm()

    return render(
        request,
        "order/form.html",
        {
            "form": form,
            "is_new": True,
            "page_section": ORDERS,
            "page_section_url": ORDERS_URL,
            "page_title": ORDER_ADD_TITLE
        }
    )


def edit(request, pk):
    obj = get_object_or_404(Order, id=pk)

    if request.method == "POST":
        form = OrderForm(request.POST, files=request.FILES, instance=obj)
        if form.is_valid():
            form.save()

            messages.success(request, ORDER_UPDATE_MSG)
            return redirect("order", pk=obj.pk)
        else:
            messages.error(request, DEFAULT_FORM_ERROR)
    else:
        form = OrderForm(model_to_dict(obj))

    return render(
        request,
        "order/form.html",
        {
            "form": form,
            "page_section": ORDERS,
            "page_section_url": ORDERS_URL,
            "page_title": f"{ORDER_EDIT_TITLE} {obj}"
        }
    )


def buy(request, pk):
    order = get_object_or_404(Order, id=pk)
    if request.method == "POST":
        form = BuyOrderForm(request.POST, instance=order)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.status = Order.Status.BUYED
            instance.buyed_at = datetime.now()
            instance.save()

            messages.success(request, ORDER_UPDATE_MSG)
            return redirect("order", pk=order.pk)
        else:
            messages.error(request, DEFAULT_FORM_ERROR)
    else:
        form = BuyOrderForm(model_to_dict(order))

    return render(request, "order/form.html", {
        "form": form,
        "page_section": ORDERS,
        "page_section_url": ORDERS_URL,
        "page_title": order.title
    })


def set_track_num(request, pk):
    order = get_object_or_404(Order, id=pk)
    if request.method == "POST":
        form = SetTrackNumOrderForm(request.POST, instance=order)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.status = Order.Status.IN_DELIVERY
            instance.save()

            messages.success(request, ORDER_TRACK_MSG)
            return redirect(request.session['previous_page'])
        else:
            messages.error(request, DEFAULT_FORM_ERROR)
    else:
        request.session['previous_page'] = request.META.get('HTTP_REFERER', ORDERS_URL)
        form = SetTrackNumOrderForm(model_to_dict(order))

    return render(request, "order/form.html", {
        "form": form,
        "page_section": ORDERS,
        "page_section_url": ORDERS_URL,
        "page_title": order.title
    })


def set_delivered(request, pk):
    order = get_object_or_404(Order, id=pk)
    if request.method == "POST":
        order.status = Order.Status.DELIVERED
        order.save()

        messages.success(request, f"{order} {ORDER_STATUS_MSG}")
        return redirect(request.headers.get("Referer", ORDERS_URL))


def set_arrived(request, pk):
    order = get_object_or_404(Order, id=pk)
    if request.method == "POST":
        form = SetArrivedOrderForm(request.POST, instance=order)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.status = Order.Status.ARRIVED
            instance.save()
            messages.success(request, f"{order} {ORDER_STATUS_MSG}")
            return redirect(request.session.get('previous_page', ORDERS_URL))
    else:
        request.session['previous_page'] = request.META.get('HTTP_REFERER', ORDERS_URL)
        form = SetArrivedOrderForm(model_to_dict(order))

    return render(request, "order/form.html", {
        "form": form,
        "page_section": ORDERS,
        "page_section_url": ORDERS_URL,
        "page_title": f"{order.title} - Подтверждение прибытия заказа"
    })


def delete(request, pk):
    obj = get_object_or_404(Order, pk=pk)
    obj.delete()
    return redirect(request.headers.get("Referer", ORDERS_URL))
