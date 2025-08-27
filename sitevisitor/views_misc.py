# sitevisitor/views_misc.py
from django.http import HttpResponse

def robots_txt(request):
    content = (
        "User-Agent: *\n"
        "Disallow:\n"
        "Sitemap: https://www.joweb.in/sitemap.xml\n"
    )
    return HttpResponse(content, content_type="text/plain")
