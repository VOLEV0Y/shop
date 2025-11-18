from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import Product, Category

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
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total_price': item_total
            })
            total_price += item_total
        except Product.DoesNotExist:
            continue
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'cart_items_count': sum(cart.values())
    }
    return render(request, 'cart.html', context)

def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return redirect('/')
        
        cart = request.session.get('cart', {})
        
        if product_id in cart:
            cart[product_id] += 1
        else:
            cart[product_id] = 1
        
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
    
    if str(product_id) in cart:
        if cart[str(product_id)] > 1:
            cart[str(product_id)] -= 1
        else:
            del cart[str(product_id)]
        request.session['cart'] = cart
    
    return redirect('/cart/')

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
    
    return redirect('/cart/')

def clear_cart(request):
    if 'cart' in request.session:
        del request.session['cart']
    
    return redirect('/cart/')