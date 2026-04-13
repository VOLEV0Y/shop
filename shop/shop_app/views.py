from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User as AuthUser
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category, MusicTrack, UserProfile


def get_music_tracks():
    try:
        return MusicTrack.objects.filter(is_active=True).order_by('order')
    except Exception:
        return []


def main_page(request):
    products = Product.objects.filter(is_active=True)

    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(material__icontains=search_query) |
            Q(color__icontains=search_query)
        ).order_by('name')

    gender_filter = request.GET.get('gender', '')
    if gender_filter:
        products = products.filter(gender=gender_filter)

    categories = Category.objects.all()
    cart = request.session.get('cart', {})
    cart_items_count = sum(cart.values())

    context = {
        'products': products,
        'categories': categories,
        'cart_items_count': cart_items_count,
        'music_tracks': get_music_tracks(),
    }
    return render(request, 'home.html', context)


def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            item_total = product.price * quantity
            cart_items.append({'product': product, 'quantity': quantity, 'total_price': item_total})
            total_price += item_total
        except Product.DoesNotExist:
            continue

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'cart_items_count': sum(cart.values()),
        'music_tracks': get_music_tracks(),
    }
    return render(request, 'cart.html', context)


def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        try:
            Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return redirect('/')
        cart = request.session.get('cart', {})
        cart[product_id] = cart.get(product_id, 0) + 1
        request.session['cart'] = cart
    return redirect('/')


def increase_cart_item(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        cart[str(product_id)] += 1
        request.session['cart'] = cart
    return redirect('/cart/')


def decrease_cart_item(request, product_id):
    cart = request.session.get('cart', {})
    key = str(product_id)
    if key in cart:
        if cart[key] > 1:
            cart[key] -= 1
        else:
            del cart[key]
        request.session['cart'] = cart
    return redirect('/cart/')


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    key = str(product_id)
    if key in cart:
        del cart[key]
        request.session['cart'] = cart
    return redirect('/cart/')


def clear_cart(request):
    if 'cart' in request.session:
        del request.session['cart']
    return redirect('/cart/')


# ===== АВТОРИЗАЦИЯ =====

def login_view(request):
    if request.user.is_authenticated:
        return redirect('/profile/')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            messages.error(request, 'Введите логин и пароль')
            return render(request, 'login.html', {'music_tracks': get_music_tracks()})

        # Автосоздание суперпользователя admin/admin
        if username == 'admin' and password == 'admin':
            admin_user, created = AuthUser.objects.get_or_create(username='admin')
            if created or not admin_user.is_superuser:
                admin_user.set_password('admin')
                admin_user.is_staff = True
                admin_user.is_superuser = True
                admin_user.save()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/profile/')
        else:
            messages.error(request, 'Неверный логин или пароль')

    return render(request, 'login.html', {'music_tracks': get_music_tracks()})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('/profile/')

    if request.method == 'POST':
        username   = request.POST.get('username', '').strip()
        email      = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        phone      = request.POST.get('phone', '').strip()
        password1  = request.POST.get('password1', '')
        password2  = request.POST.get('password2', '')

        if not all([username, email, first_name, last_name, password1, password2]):
            messages.error(request, 'Заполните все обязательные поля')
        elif password1 != password2:
            messages.error(request, 'Пароли не совпадают')
        elif len(password1) < 4:
            messages.error(request, 'Пароль должен быть не менее 4 символов')
        elif AuthUser.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким логином уже существует')
        elif AuthUser.objects.filter(email=email).exists():
            messages.error(request, 'Email уже используется')
        else:
            user = AuthUser.objects.create_user(
                username=username, email=email, password=password1,
                first_name=first_name, last_name=last_name,
            )
            # Сохраняем телефон в профиль
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.phone = phone
            profile.save()

            login(request, user)
            return redirect('/profile/')

    return render(request, 'register.html', {'music_tracks': get_music_tracks()})


@login_required(login_url='/login/')
def profile_view(request):
    cart = request.session.get('cart', {})
    # Создаём профиль если его нет
    UserProfile.objects.get_or_create(user=request.user)
    context = {
        'cart_items_count': sum(cart.values()),
        'music_tracks': get_music_tracks(),
    }
    return render(request, 'profile.html', context)


@login_required(login_url='/login/')
def profile_update(request):
    if request.method != 'POST':
        return redirect('/profile/')

    user = request.user
    first_name = request.POST.get('first_name', '').strip()
    last_name  = request.POST.get('last_name', '').strip()
    email      = request.POST.get('email', '').strip()
    phone      = request.POST.get('phone', '').strip()
    password1  = request.POST.get('password1', '')
    password2  = request.POST.get('password2', '')

    # Проверка email на уникальность (кроме своего)
    if email and AuthUser.objects.filter(email=email).exclude(pk=user.pk).exists():
        messages.error(request, 'Этот email уже используется')
        return redirect('/profile/')

    # Проверка пароля
    if password1:
        if password1 != password2:
            messages.error(request, 'Пароли не совпадают')
            return redirect('/profile/')
        if len(password1) < 4:
            messages.error(request, 'Пароль должен быть не менее 4 символов')
            return redirect('/profile/')
        user.set_password(password1)
        update_session_auth_hash(request, user)  # не разлогиниваем

    if first_name: user.first_name = first_name
    if last_name:  user.last_name  = last_name
    if email:      user.email      = email
    user.save()

    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.phone = phone
    profile.save()

    messages.success(request, 'Профиль успешно обновлён!')
    return redirect('/profile/')


def logout_view(request):
    logout(request)
    return redirect('/')
