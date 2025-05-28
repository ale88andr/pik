from django.shortcuts import render


def index(request):
    return render(
        request,
        "dashboard/index.html",
        {
            "page_title": "Панель",
            "page_section": "Обзор",
        }
    )