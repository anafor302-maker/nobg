from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.conf import settings
from django.utils.translation import activate

class StaticViewSitemap(Sitemap):
    """Statik sayfalar için sitemap"""
    protocol = 'https'
    
    def items(self):
        """Her dil için tüm sayfaları döndür"""
        pages = []
        views = ['home', 'privacy', 'terms']
        
        for lang_code, lang_name in settings.LANGUAGES:
            for view_name in views:
                pages.append({
                    'lang': lang_code,
                    'view': view_name,
                })
        return pages
    
    def location(self, item):
        """URL oluştur"""
        lang_code = item['lang']
        view_name = item['view']
        
        # Geçici olarak dili aktifleştir
        activate(lang_code)
        url = reverse(view_name)
        
        # Dil prefix'i ekle
        return f'/{lang_code}{url}'
    
    def priority(self, item):
        """Sayfa önceliği"""
        if item['view'] == 'home':
            return 1.0
        return 0.8
    
    def changefreq(self, item):
        """Değişim sıklığı"""
        if item['view'] == 'home':
            return 'daily'
        return 'weekly'