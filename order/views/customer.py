import io

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.forms import model_to_dict
from django.db.models import Count, Sum
from django.contrib import messages

from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib import colors

from order.forms.customer import CustomerForm
from order.forms.order import CreatePurchaseCustomerOrderForm
from order.forms.search import SearchForm
from order.models.customer import Customer
from order.models.marketplace import Marketplace
from order.models.purchase import Purchase
from app.settings import STATIC_ROOT


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
        "customer/list.html",
        {"form": form, "search_query": query, "customers": customers, "total": customers.count()}
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

    return render(request, "order/form.html", {"form": form})


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


def purchase(request, pk, purchase_pk):
    customer = get_object_or_404(Customer, pk=pk)
    purchase = get_object_or_404(Purchase, pk=purchase_pk)
    purchase_orders = customer.customer_orders.filter(purchase=purchase_pk)

    return render(
        request, 
        "customer/purchase.html", 
        {
            "customer": customer, 
            "orders": purchase_orders,
            "purchase": purchase,
            "total": purchase_orders.count()
        })


def purchase_pdf(request, pk, purchase_pk):
    pdfmetrics.registerFont(TTFont("DejaVuSans", "DejaVuSans.ttf", "utf-8"))
    default_style = ParagraphStyle("Body", fontName="DejaVuSans", fontSize=12)
    title_style = ParagraphStyle("Body", fontName="DejaVuSans", fontSize=20, alignment=TA_CENTER)
    
    customer = get_object_or_404(Customer, pk=pk)
    purchase = get_object_or_404(Purchase, pk=purchase_pk)
    purchase_orders = customer.customer_orders.filter(purchase=purchase_pk)
    
    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = f"filename='{customer.name}.pdf'"
    
    doc = SimpleDocTemplate(
        response, 
        pagesize=A4, 
        rightMargin=40, 
        leftMargin=40, 
        topMargin=20, 
        bottomMargin=40, 
        title="Заказы"
    )
    
    content = []
    
    logo = STATIC_ROOT + "assets/images/logo.png"
    img = Image(logo, 25*mm, 25*mm)
    content.append(img)
    content.append(Spacer(1, 10))
    content.append(Paragraph("Покупки в Китае", title_style))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"Клиент: { customer.name }", default_style))
    content.append(Spacer(1, 5))
    content.append(Paragraph(f"Закупка: { purchase.title }", default_style))
    content.append(Spacer(1, 5))
    content.append(Paragraph(f"Заказы: { purchase_orders.count() }", default_style))
    content.append(Spacer(1, 5))
    
    content.append(Paragraph("Заказы", title_style))
    content.append(Spacer(1, 20))
    
    table_data = [["Наименование", "Статус", "Цена ¥", "Цена ₽", "Вес (кг.)", "Трек номер"]]
    
    for order in purchase_orders:
        table_data.append([
            order.title, 
            order.get_status, 
            order.order_price, 
            order.calculate_order_exchange_price(),
            order.weight,
            order.track_num
        ])
    
    t = Table(
        table_data,
        # colWidths=[5 * cm, 4 * cm, 2 * cm, 2 * cm, 2 * cm, 3 * cm],
        style=[
            ("FONTNAME", (0,0), (-1,-1), "DejaVuSans"),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ])
    
    content.append(t)
    
    doc.build(content)
    
    return response
