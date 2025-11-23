from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib.sitemaps.views import sitemap
from remover import views
from remover.sitemaps import StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
}

# Root URL için tarayıcı diline göre yönlendirme
urlpatterns = [
    path('', views.root_redirect, name='root_redirect'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
]

# Diğer URL'ler i18n_patterns içinde
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('remove-background/', views.remove_background, name='remove_background'),
    path('privacy/', views.privacy_policy, name='privacy'),
    path('terms/', views.terms, name='terms'),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin panel özelleştirmeleri
admin.site.site_header = "Background Remover Admin"
admin.site.site_title = "Background Remover"
admin.site.index_title = "Yönetim Paneli"