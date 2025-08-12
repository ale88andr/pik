import logging
from datetime import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.forms import model_to_dict
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
from order.forms.order import (
    BuyOrderForm,
    CreateOrderForm,
    OrderForm,
    OrderSearchForm,
    SetArrivedOrderForm,
    SetTrackNumOrderForm
)
from order.models.order import Order


logger = logging.getLogger(__name__)


def list(request):
    form = OrderSearchForm(request.GET)
    sort = request.GET.get("sort", "-created_at")
    orders = Order.objects.select_related("purchase", "customer", "marketplace").all()

    if is_search_form_filled(request, form.fields) and form.is_valid():
        search = form.cleaned_data.get("query")
        status = form.cleaned_data.get("status")

        if search:
            orders = orders.search(query=search)

        filters = {
            "customer": form.cleaned_data.get("customer"),
            "marketplace": form.cleaned_data.get("marketplace"),
            "purchase": form.cleaned_data.get("purchase"),
            "status": int(status) if status else None
        }

        filters = {key: value for key, value in filters.items() if value is not None}
        orders = orders.filter(**filters)
        
    orders = orders.order_by(sort)
    total = orders.count()
        
    # Pagination
    page_num = request.GET.get('page', 1)
    paginator = Paginator(orders, 15)

    try:
        orders = paginator.page(page_num)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)

    context = {
        "form": form,
        "records": orders,
        "total": total,
        "current_page": orders.number - 1,
        "page_section": ORDERS,
        "page_section_url": ORDERS_URL,
        "page_title": ORDER_LIST_TITLE
    }

    return render(request, "order/list.html", context)


def detail(request, pk):
    order = get_object_or_404(Order, pk=pk)

    context = {
        "order": order,
        "page_section": ORDERS,
        "page_section_url": ORDERS_URL,
        "page_title": order.title
    }

    return render(request, "order/detail.html", context)


def create(request):
    is_post = request.method == "POST"
    form = CreateOrderForm(request.POST, files=request.FILES) if is_post else CreateOrderForm()

    if is_post:
        if form.is_valid():
            order = form.save()

            logger.info(f"Создан заказ #{order.pk} — '{order.title}' пользователем {request.user}, параметры заказа: {order.to_dict}")
            messages.success(request, f"{ORDER_CREATE_MSG} {order.title}")

            target = "create-order" if "add_another" in request.POST else ORDERS_URL
            return redirect(target)
        else:
            messages.error(request, DEFAULT_FORM_ERROR)

    context = {
        "form": form,
        "is_new": True,
        "page_section": ORDERS,
        "page_section_url": ORDERS_URL,
        "page_title": ORDER_ADD_TITLE
    }

    return render(request, "order/form.html", context)


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
    order = get_object_or_404(Order, pk=pk)

    if request.method == "POST":
        form = BuyOrderForm(request.POST, instance=order)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.status = Order.Status.BUYED
            instance.buyed_at = datetime.now()
            instance.save()

            messages.success(request, ORDER_UPDATE_MSG)
            logger.info(f"Заказ #{order.pk} помечен как выкупленный")

            return redirect("order", pk=order.pk)
        else:
            messages.error(request, DEFAULT_FORM_ERROR)
            logger.warning(f"Ошибка при выкупе заказа #{order.pk}: {form.errors}")
    else:
        form = BuyOrderForm(instance=order)

    context = {
        "form": form,
        "page_section": ORDERS,
        "page_section_url": ORDERS_URL,
        "page_title": order.title
    }

    return render(request, "order/form.html", context)


def set_track_num(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == "POST":
        form = SetTrackNumOrderForm(request.POST, instance=order)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.status = Order.Status.IN_DELIVERY
            instance.save()

            messages.success(request, ORDER_TRACK_MSG)
            return redirect(request.session.get("previous_page"))
        else:
            messages.error(request, DEFAULT_FORM_ERROR)
    else:
        request.session['previous_page'] = request.META.get('HTTP_REFERER', ORDERS_URL)
        form = SetTrackNumOrderForm(model_to_dict(order))

    context =  {
        "form": form,
        "page_section": ORDERS,
        "page_section_url": ORDERS_URL,
        "page_title": order.title
    }

    return render(request, "order/form.html", context)


def set_delivered(request, pk):
    order = get_object_or_404(Order, id=pk)

    if request.method == "POST":
        order.status = Order.Status.DELIVERED
        order.save()

        messages.success(request, f"{order} {ORDER_STATUS_MSG}")
        return redirect(request.headers.get("Referer", ORDERS_URL))


def set_arrived(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == "POST":
        form = SetArrivedOrderForm(request.POST, instance=order)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.status = Order.Status.ARRIVED
            instance.save()

            track_orders = form.cleaned_data.get("track_orders")
            if track_orders:
                orders = Order.objects.filter(
                    track_num=order.track_num,
                    purchase_id=order.purchase_id,
                    id__in=track_orders
                ).exclude(id=order.id)

                updated_orders = 0
                for order in orders:
                    order.status = Order.Status.ARRIVED
                    order.weight = 0
                    order.save()
                    updated_orders += 1

                if updated_orders:
                    logger.info(f"Обновлены {updated_orders} связанных заказов с трек-номером {order.track_num}")

            messages.success(request, f"{order} {ORDER_STATUS_MSG}")

            return redirect(request.session.get('previous_page', ORDERS_URL))
    else:
        request.session['previous_page'] = request.META.get('HTTP_REFERER', ORDERS_URL)
        form = SetArrivedOrderForm(model_to_dict(order))

        form.fields["track_orders"].queryset = Order.objects.filter(
            track_num=order.track_num,
            purchase_id=order.purchase_id
        ).exclude(id=order.id)

    context = {
        "form": form,
        "page_section": ORDERS,
        "page_section_url": ORDERS_URL,
        "page_title": f"{order.title} - Подтверждение прибытия заказа"
    }

    return render(request, "order/form.html", context)


def delete(request, pk):
    obj = get_object_or_404(Order, pk=pk)
    obj.delete()
    logger.info(f"Заказ #{obj.id} — '{obj.title}' удален!")
    return redirect(request.headers.get("Referer", ORDERS_URL))
