from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Import the views from within the 'store' app
from store import views

urlpatterns = [
    # Administrative Panel Route
    path('admin/', admin.site.urls),

    # Routes for your main application (Store)
    path('', include('store.urls')),

    # CORRECTION HERE: Changed from 'template/forgotPassword.html' to 'forgot-password/'
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
]

# 🖼️ MEDIA FILES
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )