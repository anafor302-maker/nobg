from django.http import HttpResponseForbidden
from django.conf import settings
from .models import BannedIP, SuspiciousActivity

class BotProtectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # IP adresini al
        ip = self.get_client_ip(request)
        
        # Banlı IP kontrolü
        if BannedIP.objects.filter(ip_address=ip, is_active=True).exists():
            return HttpResponseForbidden("Erişim engellendi.")
        
        # Şüpheli URL kontrolü
        path = request.path.lower()
        for pattern in settings.SUSPICIOUS_PATTERNS:
            if pattern in path:
                # Şüpheli aktiviteyi kaydet
                SuspiciousActivity.objects.create(
                    ip_address=ip,
                    requested_url=request.path,
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
                )
                
                # 3 şüpheli deneme sonrası otomatik ban
                suspicious_count = SuspiciousActivity.objects.filter(ip_address=ip).count()
                if suspicious_count >= 3:
                    BannedIP.objects.get_or_create(
                        ip_address=ip,
                        defaults={'reason': 'Otomatik - Şüpheli aktivite'}
                    )
                    return HttpResponseForbidden("Erişim engellendi.")
                
                return HttpResponseForbidden("Geçersiz istek.")
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """İstemci IP adresini al"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip