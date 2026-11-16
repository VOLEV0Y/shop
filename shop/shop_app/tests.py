from django.contrib.auth.models import User as AuthUser
from rest_framework.test import APITestCase
from .models import (Category, Size, Product, SizeProduct, PaymentMethod,
                     Cart, CartItem, Order, Address)


class ShopApiTests(APITestCase):
    def setUp(self):
        self.cat = Category.objects.create(name='Кроссовки')
        self.s42 = Size.objects.create(size='42')
        self.s43 = Size.objects.create(size='43')
        self.p1 = Product.objects.create(name='Джордан', material='Кожа', price=9000,
                                         gender='M', color='Чёрный', category=self.cat)
        self.p2 = Product.objects.create(name='Изумрудные туфли', material='Замша', price=7000,
                                         gender='F', color='Зелёный', category=self.cat)
        self.p3 = Product.objects.create(name='Скрытая модель', material='Кожа', price=5000,
                                         gender='U', color='Белый', category=self.cat, is_active=False)
        SizeProduct.objects.create(product=self.p1, size=self.s42, quantity=5)
        PaymentMethod.objects.create(name='Картой онлайн')

    def login(self, name='ivan', pwd='Pass12345'):
        self.client.post('/api/register/', {'username': name, 'password': pwd}, format='json')
        r = self.client.post('/api/token/', {'username': name, 'password': pwd}, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + r.data['access'])
        return r

    def test_01_products_list_only_active(self):
        r = self.client.get('/api/products/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 2)

    def test_02_filter_gender(self):
        r = self.client.get('/api/products/?gender=F')
        self.assertEqual([p['name'] for p in r.data], ['Изумрудные туфли'])

    def test_03_search_substring(self):
        r = self.client.get('/api/products/?search=джор')
        self.assertEqual([p['name'] for p in r.data], ['Джордан'])

    def test_04_search_typo_fuzzy(self):
        r = self.client.get('/api/products/?search=Джордон')
        self.assertIn('Джордан', [p['name'] for p in r.data])

    def test_05_register_and_duplicate(self):
        r1 = self.client.post('/api/register/', {'username': 'a', 'password': 'x'}, format='json')
        r2 = self.client.post('/api/register/', {'username': 'a', 'password': 'x'}, format='json')
        self.assertEqual(r1.status_code, 201)
        self.assertEqual(r2.status_code, 400)

    def test_06_register_empty(self):
        r = self.client.post('/api/register/', {'username': ''}, format='json')
        self.assertEqual(r.status_code, 400)

    def test_07_token_wrong_and_right(self):
        self.client.post('/api/register/', {'username': 'a', 'password': 'p'}, format='json')
        bad = self.client.post('/api/token/', {'username': 'a', 'password': 'zzz'}, format='json')
        good = self.client.post('/api/token/', {'username': 'a', 'password': 'p'}, format='json')
        self.assertEqual(bad.status_code, 401)
        self.assertEqual(good.status_code, 200)
        self.assertIn('access', good.data)
        self.assertIn('refresh', good.data)

    def test_08_refresh_token(self):
        r = self.login()
        r2 = self.client.post('/api/token/refresh/', {'refresh': r.data['refresh']}, format='json')
        self.assertEqual(r2.status_code, 200)
        self.assertIn('access', r2.data)

    def test_09_cart_requires_auth(self):
        self.assertEqual(self.client.get('/api/cart/my_cart/').status_code, 401)
        self.assertEqual(self.client.get('/api/orders/').status_code, 401)

    def test_10_profile_requires_auth_and_works(self):
        self.assertEqual(self.client.get('/api/users/profile/').status_code, 401)
        self.login()
        self.assertEqual(self.client.get('/api/users/profile/').status_code, 200)
        r = self.client.put('/api/users/profile/', {'first_name': 'Иван', 'city': 'Сургут'}, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.client.get('/api/users/profile/').data['city'], 'Сургут')

    def test_11_cart_add_increase_decrease_remove(self):
        self.login()
        self.client.post('/api/cart/add_item/', {'product_id': self.p1.id, 'size_id': self.s42.id}, format='json')
        self.client.post('/api/cart/add_item/', {'product_id': self.p1.id, 'size_id': self.s42.id}, format='json')
        cart = self.client.get('/api/cart/my_cart/').data
        self.assertEqual(len(cart['items']), 1)
        self.assertEqual(cart['items'][0]['quantity'], 2)
        self.assertEqual(float(cart['total_price']), 18000.0)
        item = cart['items'][0]['id']
        self.client.post(f'/api/cart/{item}/update_item/', {'action': 'increase'}, format='json')
        self.client.post(f'/api/cart/{item}/update_item/', {'action': 'decrease'}, format='json')
        self.client.post(f'/api/cart/{item}/update_item/', {'action': 'decrease'}, format='json')
        self.client.post(f'/api/cart/{item}/update_item/', {'action': 'decrease'}, format='json')
        q = self.client.get('/api/cart/my_cart/').data['items'][0]['quantity']
        self.assertEqual(q, 1)  # меньше единицы не опускается
        r = self.client.delete(f'/api/cart/{item}/remove_item/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(self.client.get('/api/cart/my_cart/').data['items']), 0)

    def test_12_clear_cart(self):
        self.login()
        self.client.post('/api/cart/add_item/', {'product_id': self.p1.id, 'size_id': self.s42.id}, format='json')
        self.client.post('/api/cart/clear_cart/')
        self.assertEqual(len(self.client.get('/api/cart/my_cart/').data['items']), 0)

    def test_13_order_empty_cart(self):
        self.login()
        r = self.client.post('/api/orders/', {'address_id': 1, 'payment_id': 1}, format='json')
        self.assertEqual(r.status_code, 400)

    def test_14_user_sees_only_own_cart_items_order_list(self):
        self.login('a')
        self.client.post('/api/cart/add_item/', {'product_id': self.p1.id, 'size_id': self.s42.id}, format='json')
        self.client.credentials()
        self.login('b')
        self.assertEqual(len(self.client.get('/api/cart/my_cart/').data['items']), 0)
        self.assertEqual(len(self.client.get('/api/orders/').data), 0)

    def test_15_order_total_with_delivery(self):
        u = AuthUser.objects.create_user('z', password='p')
        cart = Cart.objects.create(user=u)
        CartItem.objects.create(cart=cart, product=self.p1, size=self.s42, quantity=2)
        ad = Address.objects.create(user=u, name='Сургут')
        order = Order.objects.create(user=u, address=ad, payment_method=PaymentMethod.objects.first(), cart=cart)
        self.assertEqual(float(order.total_price), 2 * 9000 + 5000)

    def test_16_addresses_create_and_list(self):
        self.login('a')
        r = self.client.post('/api/addresses/', {'name': 'Сургут, ул. Ленина, 1'}, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(self.client.get('/api/addresses/').status_code, 200)
        self.assertEqual(len(self.client.get('/api/addresses/').data), 1)
        self.client.credentials()
        self.login('b')
        self.assertEqual(len(self.client.get('/api/addresses/').data), 0)

    def _order_setup(self, name='buyer'):
        self.login(name)
        ad = self.client.post('/api/addresses/', {'name': 'Сургут, ул. Ленина, 1'}, format='json').data['id']
        pay = PaymentMethod.objects.first().id
        self.client.post('/api/cart/add_item/', {'product_id': self.p1.id, 'size_id': self.s42.id}, format='json')
        return ad, pay

    def test_17_order_created_with_delivery(self):
        ad, pay = self._order_setup()
        r = self.client.post('/api/orders/', {'address_id': ad, 'payment_id': pay}, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(float(r.data['total_price']), 9000 + 5000)
        # покупатель получает новую пустую корзину, состав заказа сохраняется
        self.assertEqual(len(self.client.get('/api/cart/my_cart/').data['items']), 0)
        self.assertEqual(Order.objects.get(id=r.data['id']).cart.items.count(), 1)

    def test_18_order_total_stable_after_status_change(self):
        ad, pay = self._order_setup()
        r = self.client.post('/api/orders/', {'address_id': ad, 'payment_id': pay}, format='json')
        order = Order.objects.get(id=r.data['id'])
        order.status = 'shipped'
        order.save()
        order.refresh_from_db()
        self.assertEqual(float(order.total_price), 14000.0)

    def test_19_second_order_allowed(self):
        ad, pay = self._order_setup()
        self.client.post('/api/orders/', {'address_id': ad, 'payment_id': pay}, format='json')
        self.client.post('/api/cart/add_item/', {'product_id': self.p1.id, 'size_id': self.s42.id}, format='json')
        r = self.client.post('/api/orders/', {'address_id': ad, 'payment_id': pay}, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(len(self.client.get('/api/orders/').data), 2)

    def test_20_catalog_write_only_for_staff(self):
        data = {'name': 'X', 'material': 'm', 'price': '1', 'gender': 'M', 'color': 'c', 'category': self.cat.id}
        self.assertEqual(self.client.post('/api/products/', data, format='json').status_code, 401)
        self.login('simple')
        self.assertEqual(self.client.post('/api/products/', data, format='json').status_code, 403)
        self.client.credentials()
        AuthUser.objects.create_user('boss', password='Pass12345', is_staff=True)
        t = self.client.post('/api/token/', {'username': 'boss', 'password': 'Pass12345'}, format='json').data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + t)
        self.assertEqual(self.client.post('/api/products/', data, format='json').status_code, 201)

    def test_21_user_cannot_change_foreign_cart_item(self):
        self.login('owner')
        self.client.post('/api/cart/add_item/', {'product_id': self.p1.id, 'size_id': self.s42.id}, format='json')
        item = CartItem.objects.first()
        self.client.credentials()
        self.login('stranger')
        r = self.client.post(f'/api/cart/{item.id}/update_item/', {'action': 'increase'}, format='json')
        self.assertEqual(r.status_code, 404)
        r = self.client.delete(f'/api/cart/{item.id}/remove_item/')
        self.assertEqual(CartItem.objects.filter(id=item.id).count(), 1)

    def test_22_order_with_foreign_address_rejected(self):
        self.login('a')
        foreign = self.client.post('/api/addresses/', {'name': 'Чужой'}, format='json').data['id']
        self.client.credentials()
        self.login('b')
        self.client.post('/api/cart/add_item/', {'product_id': self.p1.id, 'size_id': self.s42.id}, format='json')
        r = self.client.post('/api/orders/', {'address_id': foreign, 'payment_id': PaymentMethod.objects.first().id}, format='json')
        self.assertEqual(r.status_code, 400)

    def test_23_order_status_not_editable_by_user(self):
        ad, pay = self._order_setup()
        oid = self.client.post('/api/orders/', {'address_id': ad, 'payment_id': pay}, format='json').data['id']
        r = self.client.patch(f'/api/orders/{oid}/', {'status': 'delivered'}, format='json')
        self.assertEqual(r.status_code, 405)
