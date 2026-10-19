from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .models import *
from .serializers import *
from rapidfuzz import process, fuzz

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        
        search_query = self.request.query_params.get('search')
        gender = self.request.query_params.get('gender')
        
        if gender:
            queryset = queryset.filter(gender=gender)

        if search_query:
            exact_match = queryset.filter(name__icontains=search_query)
            
            if exact_match.exists():
                return exact_match
            
            all_products = list(queryset)
            if not all_products:
                return queryset
                
            product_names = [p.name for p in all_products]
            
            matches = process.extract(
                search_query, 
                product_names, 
                scorer=fuzz.WRatio, 
                limit=10, 
                score_cutoff=60
            )
            
            matched_names = [match[0] for match in matches]
            
            return queryset.filter(name__in=matched_names)

        return queryset

class SizeViewSet(viewsets.ModelViewSet):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer

class MusicTrackViewSet(viewsets.ModelViewSet):
    queryset = MusicTrack.objects.filter(is_active=True)
    serializer_class = MusicTrackSerializer

class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')
        
        if not username or not password:
            return Response({'error': 'Введите логин и пароль'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Логин занят'}, status=status.HTTP_400_BAD_REQUEST)
            
        user = User.objects.create_user(username=username, password=password, email=email)
        Cart.objects.create(user=user)
        return Response({'success': True}, status=status.HTTP_201_CREATED)

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user, is_active=True)

    @action(detail=False, methods=['get'])
    def my_cart(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user, is_active=True)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user, is_active=True)
        product_id = request.data.get('product_id')
        size_id = request.data.get('size_id')
        
        item = CartItem.objects.filter(cart=cart, product_id=product_id, size_id=size_id).first()
        if item:
            item.quantity += 1
            item.save()
        else:
            CartItem.objects.create(cart=cart, product_id=product_id, size_id=size_id, quantity=1)
            
        return Response({'status': 'ok'})

    @action(detail=False, methods=['post'])
    def clear_cart(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user, is_active=True)
        cart.items.all().delete()
        return Response({'status': 'cleared'})

    @action(detail=True, methods=['post'])
    def update_item(self, request, pk=None):
        item = CartItem.objects.get(id=pk)
        action_type = request.data.get('action')
        if action_type == 'increase':
            item.quantity += 1
        elif action_type == 'decrease' and item.quantity > 1:
            item.quantity -= 1
        item.save()
        return Response({'status': 'ok'})

    @action(detail=True, methods=['delete'])
    def remove_item(self, request, pk=None):
        CartItem.objects.filter(id=pk).delete()
        return Response({'status': 'deleted'})
    
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    def create(self, request):
        cart = Cart.objects.filter(user=request.user, is_active=True).first()
        if not cart or not cart.items.exists():
            return Response({'error': 'Корзина пуста'}, status=400)
        
        address_id = request.data.get('address_id')
        payment_id = request.data.get('payment_id')
        
        order = Order.objects.create(
            user=request.user,
            address_id=address_id,
            payment_method_id=payment_id,
            cart=cart
        )

        cart.items.all().delete() 
        return Response(OrderSerializer(order).data, status=201)
    
class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)
        return Response({
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone': profile.phone,
            'country': profile.country,
            'city': profile.city,
            'street': profile.street,
            'apartment': profile.apartment,
        })

    def put(self, request):
        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)
        data = request.data
        
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.email = data.get('email', user.email)
        
        new_password = data.get('password')
        if new_password:
            user.set_password(new_password)
        
        user.save()
        
        profile.phone = data.get('phone', profile.phone)
        profile.country = data.get('country', profile.country)
        profile.city = data.get('city', profile.city)
        profile.street = data.get('street', profile.street)
        profile.apartment = data.get('apartment', profile.apartment)
        profile.save()
        
        return Response({'success': True})