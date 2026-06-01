from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Sum
from django.utils import timezone
from .models import Product, Order, OrderItem
from .forms import ProductForm, RegisterForm
from django.http import HttpResponse, JsonResponse  # 🟢 Imported JsonResponse for AJAX functionality
import folium  # 🗺️ Integrated satellite map rendering library

# =============================================================================
# 🔐 ACCESS CONTROL AND PRIVILEGES (STRICT)
# =============================================================================

def is_admin(user):
    """Surgical block: only Jeremias or a superuser can access the Admin Dashboard."""
    return user.is_superuser or user.username == "Jeremias"

def is_staff_member(user):
    """Verifies if the user belongs to the operational staff team."""
    return user.is_staff or user.is_superuser

# =============================================================================
# 👤 REGISTRATION AND AUTHENTICATION SYSTEM (DIRECT TO ACCOUNT.HTML)
# =============================================================================

def register(request):
    """
    Creates a new user.
    Ensures a standard profile role and routes the user straight to userLogin.html.
    """
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_superuser = False
            user.is_staff = False
            user.save()
            
            try:
                from django.apps import apps
                CustomerProfileModel = apps.get_model('store', 'CustomerProfile')
                profile, created = CustomerProfileModel.objects.get_or_create(user=user)
                profile.city = form.cleaned_data.get('city', '')
                profile.address = form.cleaned_data.get('address', '')
                profile.phone = form.cleaned_data.get('phone', '')
                profile.save()
            except Exception:
                pass

            messages.success(request, "Account created successfully! Please log in below.")
            return redirect('login')
        else:
            messages.error(request, "Registration error. Please check the provided data.")
    else:
        form = RegisterForm()
    
    return render(request, 'store/register.html', {'form': form})


def login_view(request):
    """
    Centralized Login Manager.
    If Jeremias -> Redirects to admin_dashboard.html
    If STANDARD USER -> OPENS THE TEMPLATE account.html IMMEDIATELY WITHOUT CHANGING THE ROUTE URL.
    """
    if request.method == "POST":
        user_in = request.POST.get("username")
        pass_in = request.POST.get("password")
        
        user = authenticate(request, username=user_in, password=pass_in)

        if user is not None:
            auth_login(request, user)
            
            # 1. IF USER IS JEREMIAS (MASTER ADMIN)
            if is_admin(user):
                messages.success(request, f"Master Access Confirmed. Welcome, {user.username}.")
                return redirect('admin_dashboard')
            
            # 2. IF STANDARD USER (RENDERS ACCOUNT.HTML DIRECTLY)
            else:
                messages.success(request, "Login successful!")
                orders = Order.objects.filter(user=user).order_by('-created_at')
                context = {
                    "orders": orders,
                    "user": user,
                    "total_orders": orders.count(),
                    "active_wishlist": len(request.session.get('wishlist', []))
                }
                # Renders the desired template directly in the POST response
                return render(request, 'store/account.html', context)
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, "userLogin.html", {
                "error": "Access denied. Invalid credentials.",
                "old_val": user_in
            })
            
    return render(request, "userLogin.html")


def logout_view(request):
    """🟢 FIXED: Safely terminates the standard user session (Termination Section)."""
    logout(request)
    messages.info(request, "Session ended successfully.")
    return redirect('user_login')  # Redirects the common user to their login screen


def admin_logout(request):
    """Ends Jeremias's session safely and renders the Home page."""
    logout(request)
    messages.info(request, "Admin session closed successfully.")
    return redirect('home')

# =============================================================================
# 📊 ENVIRONMENT ACCESSED VIA DIRECT URL (FALLBACK ACC_DASHBOARD)
# =============================================================================

@login_required(login_url='login')
def account_dashboard(request):
    """
    Fallback view when the user types the account URL directly into the browser while logged in.
    Guarantees strict delivery of the account.html file.
    """
    if is_admin(request.user):
        return redirect('admin_dashboard')

    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {
        "orders": orders,
        "user": request.user,
        "total_orders": orders.count(),
        "active_wishlist": len(request.session.get('wishlist', []))
    }
    return render(request, 'account.html', context)

# =============================================================================
# 🏠 VITRINE NAVIGATION WITH INTEGRATED SATELLITE RADAR (PUBLIC)
# =============================================================================

def home(request):
    """Store Front / Home Page with Integrated Folium Map System."""
    query = request.GET.get('q')
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            is_published=True
        ).distinct()
    else:
        products = Product.objects.filter(is_published=True).order_by('-created_at')[:8]
    
    # 🗺️ 1. Generation of the interactive map at La Bombonera
    mapa = folium.Map(
        location=[-34.635650, -58.364650], 
        zoom_start=16,
        tiles="OpenStreetMap"
    )
    
    # 🔥 LINK CONFIGURED: Clicking the popup opens the official website in a new tab
    popup_conteudo = """
    <div style="font-family: Arial, sans-serif; font-size: 13px; color: #333;">
        <b>Boca Mania Megastore</b><br>
        Pick up your order here!<br><br>
        <a href="https://www.bocajuniors.com.ar/la-bombonera" 
           target="_blank" 
           style="background-color: #003aa5; color: #f2b705; padding: 5px 10px; text-decoration: none; font-weight: bold; border-radius: 4px; display: inline-block; margin-top: 5px;">
           💙 Visit La Bombonera 💛
        </a>
    </div>
    """
    
    # 🗺️ 2. Adding the marker with the new linked popup
    folium.Marker(
        [-34.635650, -58.364650],
        popup=folium.Popup(popup_conteudo, max_width=250),
        tooltip="Click to visit La Bombonera",
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(mapa)
    
    # 🗺️ 3. Transmutation of the Python map to clean HTML string
    mapa_html = mapa.get_root().render()

    return render(request, "store/home.html", {
        "products": products,
        "search_query": query,
        "now": timezone.now(),
        "mapa_bombonera": mapa_html
    })

def product_list(request):
    """General Product Catalog."""
    category = request.GET.get('category')
    sort = request.GET.get('sort')
    
    products = Product.objects.filter(is_published=True)
    
    if category:
        products = products.filter(category=category)
        
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_at')
        
    return render(request, 'products/list.html', {
        'products': products,
        'current_category': category,
        'current_sort': sort
    })

def product_detail(request, id):
    """Product Detail View."""
    product = get_object_or_404(Product, id=id)
    related_products = Product.objects.filter(
        is_published=True
    ).exclude(id=id).order_by('?')[:4]
    
    return render(request, 'products/detail.html', {
        'product': product,
        'related_products': related_products
    })

# =============================================================================
# 📦 ADMINISTRATIVE CONTROL PANEL (JEREMIAS ONLY)
# =============================================================================

@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Hidden Management Dashboard - Jeremias Only."""
    products = Product.objects.all().order_by('-created_at')
    orders = Order.objects.all().order_by('-created_at')
    
    revenue = orders.aggregate(Sum('total'))['total__sum'] or 0
    sales_count = orders.count()
    low_stock = products.filter(stock__lte=5).count()
    
    return render(request, "store/admin_dashboard.html", {
        "products": products,
        "orders": orders,
        "revenue": revenue,
        "sales_count": sales_count,
        "low_stock": low_stock,
        "published": products.filter(is_published=True).count()
    })

# =============================================================================
# 📦 PRODUCT MANAGEMENT (ADMIN)
# =============================================================================

@login_required(login_url='login')
@user_passes_test(is_admin)
def product_create(request):
    """Adds a new item to the catalog."""
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            action = request.POST.get('action')

            if action == 'publish':
                product.is_published = True
                messages.success(request, f"🔥 {product.name} published successfully!")
            elif action == 'draft':
                product.is_published = False
                messages.warning(request, f"📋 {product.name} saved as draft.")
            else:
                product.is_published = True 
                messages.success(request, f"Success: {product.name} added.")

            product.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    
    return render(request, 'products/form.html', {
        'form': form, 
        'mode': 'create',
        'title': 'Add New Product'
    })

@login_required(login_url='login')
@user_passes_test(is_admin)
def product_update(request, id):
    """Technical maintenance/edit of existing catalog products."""
    product = get_object_or_404(Product, id=id)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            action = request.POST.get('action')

            if action == 'publish':
                product.is_published = True
                messages.success(request, "Changes published successfully!")
            elif action == 'draft':
                product.is_published = False
                messages.warning(request, "Saved as hidden draft.")
            
            product.save()
            return redirect('admin_dashboard')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'edit_product.html', {'form': form, 'product': product})

@login_required(login_url='login')
@user_passes_test(is_admin)
def product_delete(request, id):
    """Permanently deletes a product from the system."""
    product = get_object_or_404(Product, id=id)
    product.delete()
    messages.warning(request, "Product removed permanently.")
    return redirect('admin_dashboard')

@login_required(login_url='login')
@user_passes_test(is_admin)
def publish_product(request, pk):
    """Instantly toggles product visibility to public."""
    product = get_object_or_404(Product, pk=pk)
    product.is_published = True
    product.save()
    return redirect('admin_dashboard')

@login_required(login_url='login')
@user_passes_test(is_admin)
def unpublish_product(request, pk):
    """Instantly hides the product from the public catalog."""
    product = get_object_or_404(Product, pk=pk)
    product.is_published = False
    product.save()
    return redirect('admin_dashboard')

# =============================================================================
# 🛒 INTEGRATED PROTOCOLS (REAL-TIME AJAX SESSION CART SYSTEM)
# =============================================================================

def get_cart_data_matrix(request):
    """Internal utility function to calculate session subtotals and totals."""
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0.0

    for product_id_str, qty in cart.items():
        try:
            product = Product.objects.get(id=int(product_id_str))
            subtotal = float(product.price) * int(qty)
            total += subtotal
            cart_items.append({
                'product': product,
                'qty': int(qty),
                'subtotal': round(subtotal, 2)
            })
        except Product.DoesNotExist:
            continue

    return cart_items, round(total, 2)


def cart_detail(request):
    """Opens the cart manifest template rendering session data."""
    cart_items, total = get_cart_data_matrix(request)
    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total': total
    })


def add_to_cart(request, id):
    """Adds a product, manages live stock validation, and returns JSON or redirects."""
    quantity_to_add = int(request.POST.get('quantity', 1)) if request.method == "POST" else 1
    product = get_object_or_404(Product, id=id)
    
    # Critical stock validation before debiting from the database
    if product.stock < quantity_to_add:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False, 
                'message': f"Only {product.stock} units available in stock."
            }, status=400)
        messages.error(request, f"Only {product.stock} units available.")
        return redirect('product_detail', id=id)
        
    # 📉 Debits from the physical Database stock in real-time
    product.stock -= quantity_to_add
    product.save()

    # 🛒 Session array management
    cart = request.session.get('cart', {})
    product_id_str = str(id)

    if product_id_str in cart:
        cart[product_id_str] += quantity_to_add
    else:
        cart[product_id_str] = quantity_to_add
    
    request.session['cart'] = cart
    request.session.modified = True

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.method == 'POST':
        cart_items, cart_total = get_cart_data_matrix(request)
        item_qty = cart[product_id_str]
        item_subtotal = round(float(product.price) * item_qty, 2)
        return JsonResponse({
            'success': True,
            'cart_total': cart_total,
            'item_qty': item_qty,
            'item_subtotal': item_subtotal,
            'new_stock': f"{product.stock} Units Available",
            'total_cart_items': len(cart),
            'removed': False,
            'message': "Item added to cart!"
        })

    return redirect('cart_detail')


def remove_from_cart(request, id):
    """Decrement action (asynchronous)."""
    product = get_object_or_404(Product, id=id)
    cart = request.session.get('cart', {})
    product_id_str = str(id)
    
    item_qty = 0
    item_subtotal = 0.0
    removed = False

    if product_id_str in cart:
        if cart[product_id_str] > 1:
            cart[product_id_str] -= 1
            item_qty = cart[product_id_str]
            item_subtotal = round(float(product.price) * item_qty, 2)
        else:
            del cart[product_id_str]
            removed = True
        
        request.session['cart'] = cart
        request.session.modified = True

    cart_items, cart_total = get_cart_data_matrix(request)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.method == 'POST':
        return JsonResponse({
            'success': True,
            'cart_total': cart_total,
            'item_qty': item_qty,
            'item_subtotal': item_subtotal,
            'removed': removed
        })

    return redirect('cart_detail')


def delete_cart_item(request, id):
    """Completely purges a cart item line."""
    cart = request.session.get('cart', {})
    product_id_str = str(id)

    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
        request.session.modified = True

    cart_items, cart_total = get_cart_data_matrix(request)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.method == 'POST':
        return JsonResponse({
            'success': True,
            'cart_total': cart_total,
            'item_qty': 0,
            'item_subtotal': 0,
            'removed': True
        })

    return redirect('cart_detail')


def clear_cart(request):
    """Clears all shopping arsenal stored in the session."""
    if 'cart' in request.session:
        del request.session['cart']
        request.session.modified = True
    messages.warning(request, "All shopping arsenal has been purged.")
    return redirect('cart_detail')


# =============================================================================
# 💳 SECURE CHECKOUT PROTOCOL (FIXED & BALANCED FOR GUEST AND USERS)
# =============================================================================

def checkout(request):
    """
    Proper Checkout Process:
    GET: Renders the payment panel (checkout.html) using manifest data.
    POST: Processes simulated card payment and closes the order as approved.
    """
    cart_items, total = get_cart_data_matrix(request)
    if not cart_items:
        messages.error(request, "Cannot process an empty manifest.")
        return redirect('cart_detail')
        
    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None, 
            total=total, 
            status='Paid & Approved'
        )
        
        for item in cart_items:
            OrderItem.objects.create(
                order=order, 
                product=item['product'], 
                quantity=item['qty'], 
                price=item['product'].price
            )
        
        request.session['cart'] = {}
        request.session.modified = True
        
        messages.success(request, "Transaction authorized by the main network!")
        return render(request, "store/checkout_success.html", {"order": order})

    return render(request, 'store/checkout.html', {
        'cart_items': cart_items, 
        'total': total,
        'user': request.user
    })


def add_to_wishlist(request, id):
    """Appends an item reference to a temporary session wishlist."""
    wishlist = request.session.get('wishlist', [])
    if id not in wishlist:
        wishlist.append(id)
        messages.success(request, "Added to Wishlist.")
    request.session['wishlist'] = wishlist
    request.session.modified = True
    return redirect('product_list')

# =============================================================================
# 👑 COMPLEMENTARY SCREEN RENDER FALLBACKS
# =============================================================================

def user_login(request):
    return render(request, "userLogin.html")

def admin_login(request):
    return render(request, "store/admin_dashboard.html")

# =============================================================================
# 🚀 CORE SYSTEM ERROR HANDLING HANDLERS
# =============================================================================

def handler404(request, exception):
    return render(request, 'errors/404.html', status=404)

def handler500(request):
    return render(request, 'errors/500.html', status=500)


def forgot_password_view(request):
    return render(request, 'forgotPassword.html')