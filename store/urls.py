from django.urls import path
from django.contrib.auth import views as auth_views  # Native Django views for secure session control
from . import views

urlpatterns = [
    # 🏠 Main / Core
    path('', views.home, name='home'),
    
    # 🛍️ Products & Store
    path('products/', views.product_list, name='product_list'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    
    # 👤 Authentication (Aligned with your Xeneize Layout)
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    
    # 🔴 USER LOGOUT (Connected to your "Termination Section" button)
    path('logout/', views.logout_view, name='logout'),
    
    # 👤 Dashboards (Post-Login Redirects)
    path('dashboard/', views.account_dashboard, name='dashboard'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    
    # 🔐 Admin Logout Link (Redirects directly to home.html via custom view)
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    
    # ➕ Product CRUD (Administrative Panel)
    path('product/create/', views.product_create, name='product_create'),
    path('product/update/<int:id>/', views.product_update, name='product_update'),
    path('product/delete/<int:id>/', views.product_delete, name='product_delete'),
    path('product/publish/<int:pk>/', views.publish_product, name='publish_product'),
    path('product/unpublish/<int:pk>/', views.unpublish_product, name='unpublish_product'),
    
    # 🛒 Cart System & Checkout (🤖 SUCCESSFULLY ADJUSTED)
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/delete/<int:id>/', views.delete_cart_item, name='delete_cart_item'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout, name='checkout'),
    
    # ❤️ Wishlist
    path('wishlist/add/<int:id>/', views.add_to_wishlist, name='add_to_wishlist'),
    
    # 👤 Specific Login Pages (Visual UI)
    path('user-login/', views.user_login, name='user_login'),
    path('admin-login/', views.admin_login, name='admin_login'),
]