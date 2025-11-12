from django.db import models
from django.core.validators import MinValueValidator

class User(models.Model):
    nickname = models.CharField(max_length=50, unique=True, verbose_name="Никнейм")
    email = models.EmailField(unique=True, verbose_name="Почта")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    first_name = models.CharField(max_length=30, verbose_name="Имя")
    last_name = models.CharField(max_length=30, verbose_name="Фамилия")

    def __str__(self):
        return f"{self.nickname} ({self.email})"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Size(models.Model):
    size = models.CharField(max_length=10, verbose_name="Размер")

    def __str__(self):
        return self.size

    class Meta:
        verbose_name = "Размер"
        verbose_name_plural = "Размеры"


class Product(models.Model):
    GENDER_CHOICES = [
        ('M', 'Мужской'),
        ('F', 'Женский'),
        ('U', 'Унисекс'),
    ]

    name = models.CharField(max_length=200, verbose_name="Название")
    material = models.CharField(max_length=100, verbose_name="Материал")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Пол")
    color = models.CharField(max_length=50, verbose_name="Цвет")
    description = models.TextField(blank=True, verbose_name="Описание")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    sizes = models.ManyToManyField(Size, through='SizeProduct', verbose_name="Размеры")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Изображение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    is_active = models.BooleanField(default=True, verbose_name="Активный")

    def __str__(self):
        return f"{self.name} - {self.color}"

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"


class SizeProduct(models.Model):
    size = models.ForeignKey(Size, on_delete=models.CASCADE, verbose_name="Размер")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(default=0, verbose_name="Количество в наличии")

    def __str__(self):
        return f"{self.product.name} - {self.size.size} (осталось: {self.quantity})"

    class Meta:
        verbose_name = "Размер-Товар"
        verbose_name_plural = "Размер-Товары"
        unique_together = ['size', 'product']


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    name = models.TextField(verbose_name="Адрес")
    is_primary = models.BooleanField(default=False, verbose_name="Основной адрес")

    def __str__(self):
        return f"{self.user.nickname} - {self.name}"

    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"


class PaymentMethod(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Способ оплаты"
        verbose_name_plural = "Способы оплаты"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает обработки'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    address = models.ForeignKey(Address, on_delete=models.CASCADE, verbose_name="Адрес доставки")
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, verbose_name="Способ оплаты")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Общая стоимость")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return f"Заказ #{self.id} - {self.user.nickname}"

    def calculate_total_price(self):
        return sum(item.total_price() for item in self.order_items.all())

    def save(self, *args, **kwargs):
        self.total_price = self.calculate_total_price() 
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items', verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    size = models.ForeignKey(Size, on_delete=models.CASCADE, verbose_name="Размер")
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name="Количество")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за единицу")

    def __str__(self):
        return f"{self.product.name} ({self.size.size}) x {self.quantity}"

    def total_price(self):
        return self.price * self.quantity

    class Meta:
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказе"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    size = models.ForeignKey(Size, on_delete=models.CASCADE, verbose_name="Размер")
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name="Количество")
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    def __str__(self):
        return f"{self.user.nickname} - {self.product.name} ({self.size.size})"

    def total_price(self):
        return self.product.price * self.quantity

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"
        unique_together = ['user', 'product', 'size']