from django.contrib import admin
from django.utils.html import format_html
from .models import BannedIP, SuspiciousActivity, RateLimitRecord, ProcessedImage

@admin.register(BannedIP)
class BannedIPAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'reason', 'banned_at', 'is_active_badge']
    list_filter = ['is_active', 'banned_at']
    search_fields = ['ip_address', 'reason']
    date_hierarchy = 'banned_at'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: red;">🔴 Aktif</span>')
        return format_html('<span style="color: green;">🟢 Pasif</span>')
    is_active_badge.short_description = 'Durum'

@admin.register(SuspiciousActivity)
class SuspiciousActivityAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'requested_url', 'timestamp', 'ban_action']
    list_filter = ['timestamp']
    search_fields = ['ip_address', 'requested_url', 'user_agent']
    date_hierarchy = 'timestamp'
    readonly_fields = ['ip_address', 'requested_url', 'user_agent', 'timestamp']
    
    def ban_action(self, obj):
        banned = BannedIP.objects.filter(ip_address=obj.ip_address, is_active=True).exists()
        if banned:
            return format_html('<span style="color: red;">✓ Banlandı</span>')
        return format_html(
            '<a href="/admin/remover/bannedip/add/?ip_address={}" class="button">Banla</a>',
            obj.ip_address
        )
    ban_action.short_description = 'İşlem'
    
    def has_add_permission(self, request):
        return False

@admin.register(RateLimitRecord)
class RateLimitRecordAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'timestamp', 'request_count']
    list_filter = ['timestamp']
    search_fields = ['ip_address']
    date_hierarchy = 'timestamp'
    
    def request_count(self, obj):
        from django.utils import timezone
        from datetime import timedelta
        from django.conf import settings
        
        time_threshold = timezone.now() - timedelta(seconds=settings.RATE_LIMIT_PERIOD)
        count = RateLimitRecord.objects.filter(
            ip_address=obj.ip_address,
            timestamp__gte=time_threshold
        ).count()
        
        if count >= settings.RATE_LIMIT_REQUESTS:
            return format_html('<span style="color: red;">{} (LİMİT AŞILDI)</span>', count)
        return count
    request_count.short_description = 'Son İstek Sayısı'
    
    def has_add_permission(self, request):
        return False

@admin.register(ProcessedImage)
class ProcessedImageAdmin(admin.ModelAdmin):
    list_display = ['original_name', 'ip_address', 'file_size_mb', 'processed_at']
    list_filter = ['processed_at']
    search_fields = ['original_name', 'ip_address']
    date_hierarchy = 'processed_at'
    readonly_fields = ['original_name', 'ip_address', 'file_size', 'processed_at']
    
    def file_size_mb(self, obj):
        return f"{obj.file_size / (1024*1024):.2f} MB"
    file_size_mb.short_description = 'Dosya Boyutu'
    
    def has_add_permission(self, request):
        return False