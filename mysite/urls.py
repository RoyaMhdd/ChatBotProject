from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),       # مسیرهای کاربران
    path('chat/', include('chat.urls')),   # مسیرهای HTML چت
    path('api/', include('chat.urls')),    # مسیرهای API چت

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
