from django.contrib.sitemaps import Sitemap
from .models import (
	BlogPost,
	TutorialSeries,
)

class BlogPostSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return BlogPost.objects.all()

    def lastmod(self, obj):
        return obj.date_published

class TutorialSeriesSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return TutorialSeries.objects.all()

    def lastmod(self, obj):
        return obj.date_published





