from django.db import models
from django.utils import timezone

class BannedIP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    reason = models.CharField(max_length=255)
    banned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Yasaklı IP"
        verbose_name_plural = "Yasaklı IP'ler"
        ordering = ['-banned_at']
    
    def __str__(self):
        return f"{self.ip_address} - {self.reason}"

class SuspiciousActivity(models.Model):
    ip_address = models.GenericIPAddressField()
    requested_url = models.CharField(max_length=500)
    user_agent = models.CharField(max_length=500, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Şüpheli Aktivite"
        verbose_name_plural = "Şüpheli Aktiviteler"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.ip_address} - {self.requested_url}"

class RateLimitRecord(models.Model):
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Rate Limit Kaydı"
        verbose_name_plural = "Rate Limit Kayıtları"
        indexes = [
            models.Index(fields=['ip_address', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.ip_address} - {self.timestamp}"

class ProcessedImage(models.Model):
    original_name = models.CharField(max_length=255)
    processed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    file_size = models.IntegerField()  # bytes
    
    class Meta:
        verbose_name = "İşlenmiş Resim"
        verbose_name_plural = "İşlenmiş Resimler"
        ordering = ['-processed_at']
    
    def __str__(self):
        return f"{self.original_name} - {self.processed_at}"