from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from rembg import remove
from PIL import Image
import io
import magic
from .models import RateLimitRecord, ProcessedImage

def get_client_ip(request):
    """İstemci IP adresini al"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def check_rate_limit(ip):
    """Rate limit kontrolü"""
    time_threshold = timezone.now() - timedelta(seconds=settings.RATE_LIMIT_PERIOD)
    recent_requests = RateLimitRecord.objects.filter(
        ip_address=ip,
        timestamp__gte=time_threshold
    ).count()
    
    return recent_requests < settings.RATE_LIMIT_REQUESTS

def home(request):
    """Ana sayfa"""
    return render(request, 'home.html')

@csrf_exempt
def remove_background(request):
    """Arka plan kaldırma endpoint'i"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Sadece POST istekleri kabul edilir'}, status=405)
    
    # Rate limit kontrolü
    ip = get_client_ip(request)
    if not check_rate_limit(ip):
        return JsonResponse({
            'error': 'Çok fazla istek gönderdiniz. Lütfen biraz bekleyin.'
        }, status=429)
    
    # Dosya kontrolü
    if 'image' not in request.FILES:
        return JsonResponse({'error': 'Resim dosyası bulunamadı'}, status=400)
    
    image_file = request.FILES['image']
    
    # Dosya boyutu kontrolü
    if image_file.size > settings.MAX_UPLOAD_SIZE:
        return JsonResponse({
            'error': f'Dosya boyutu {settings.MAX_UPLOAD_SIZE / (1024*1024)}MB\'dan küçük olmalı'
        }, status=400)
    
    # Dosya tipi kontrolü
    try:
        mime = magic.from_buffer(image_file.read(2048), mime=True)
        image_file.seek(0)
        
        if mime not in settings.ALLOWED_IMAGE_TYPES:
            return JsonResponse({'error': 'Sadece resim dosyaları kabul edilir'}, status=400)
    except:
        return JsonResponse({'error': 'Dosya tipi kontrol edilemedi'}, status=400)
    
    try:
        # Resmi aç
        input_image = Image.open(image_file)
        
        # Arka planı kaldır
        output_image = remove(input_image)
        
        # PNG olarak kaydet
        output_buffer = io.BytesIO()
        output_image.save(output_buffer, format='PNG')
        output_buffer.seek(0)
        
        # Rate limit kaydı ekle
        RateLimitRecord.objects.create(ip_address=ip)
        
        # İstatistik kaydı
        ProcessedImage.objects.create(
            original_name=image_file.name,
            ip_address=ip,
            file_size=image_file.size
        )
        
        # PNG olarak döndür
        response = HttpResponse(output_buffer.getvalue(), content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="removed_bg_{image_file.name.split(".")[0]}.png"'
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': f'Resim işlenirken hata oluştu: {str(e)}'}, status=500)

def privacy_policy(request):
    """Gizlilik politikası"""
    return render(request, 'privacy.html')

def terms(request):
    """Kullanım şartları"""
    return render(request, 'terms.html')