def is_search_form_filled(request, fields):
    if fields:
        return any(map(lambda f: request.GET.get(f), fields))
    return False