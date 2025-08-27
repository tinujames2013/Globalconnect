# sitevisitor/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from adminpanel.models import Job  # import your Job model

class JobSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Job.objects.all()

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, "updated_at") else None


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        # These must be names from your urls.py
        return ["sitevisitor:home", "sitevisitor:login", "sitevisitor:register"]

    def location(self, item):
        return reverse(item)
