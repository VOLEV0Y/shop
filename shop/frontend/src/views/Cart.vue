<template>
  <div class="assortment">
    <h2>КОРЗИНА</h2>

    <div v-if="!cart.items || cart.items.length === 0" class="empty-cart">
      <p>Ваша корзина пуста</p>
      <router-link to="/" class="continue-shopping-btn">Продолжить покупки</router-link>
    </div>

    <div v-else>
      <div v-for="item in cart.items" :key="item.id" class="cart-item">
        <div class="cart-item-image">
          <img
            :src="getImageUrl(item.product_details)"
            :alt="item.product_details.name"
          />
        </div>

        <div class="cart-item-details">
          <h4>{{ item.product_details.name }}</h4>
          <p>Цена: {{ item.product_details.price }} ₽</p>

          <div class="quantity-controls">
            <span>Количество: </span>
            <button @click="updateItem(item.id, 'decrease')" class="quantity-btn">
              -
            </button>
            <span class="quantity">{{ item.quantity }}</span>
            <button @click="updateItem(item.id, 'increase')" class="quantity-btn">
              +
            </button>
          </div>

          <p>
            <b>Сумма: {{ item.total_price }} ₽</b>
          </p>
        </div>

        <div class="cart-item-actions">
          <button @click="removeItem(item.id)" class="remove-btn">Удалить</button>
        </div>
      </div>

      <div class="cart-total">Общая сумма: {{ cart.total_price }} ₽</div>

      <div class="cart-actions">
        <button @click="clearCart" class="clear-cart-btn">Очистить корзину</button>
        <button class="checkout-btn">ОФОРМИТЬ ЗАКАЗ</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../api";
import { useMainStore } from "../store";
import { toast } from "vue3-toastify";

const cart = ref({ items: [], total_price: 0 });
const store = useMainStore();

const getImageUrl = (product) => {
  if (product.image) {
    if (product.image.startsWith("http")) return product.image;
    return `http://127.0.0.1:8000${product.image}`;
  }
  const name = product.name.toLowerCase();
  if (name.includes("мафиози")) return "/images/spartan.jpg";
  if (name.includes("великий")) return "/images/tovar2.jpeg";
  if (name.includes("джордан")) return "/images/tovar3.jpg";
  return "/images/spartan.jpg";
};

const fetchCart = async () => {
  try {
    const res = await api.get("cart/my_cart/");
    cart.value = res.data;
    store.fetchCartCount();
  } catch (e) {
    console.error("Ошибка загрузки корзины", e);
  }
};

const updateItem = async (itemId, action) => {
  try {
    await api.post(`cart/${itemId}/update_item/`, { action });
    fetchCart();
  } catch (e) {
    toast.error("Ошибка изменения количества");
  }
};

const removeItem = async (itemId) => {
  try {
    await api.delete(`cart/${itemId}/remove_item/`);
    fetchCart();
  } catch (e) {
    toast.error("Ошибка удаления");
  }
};

const clearCart = async () => {
  try {
    await api.post("cart/clear_cart/");
    fetchCart();
  } catch (e) {
    toast.error("Ошибка очистки");
  }
};

onMounted(fetchCart);
</script>

<style scoped>
.empty-cart {
  text-align: center;
  padding: 40px;
}
.empty-cart p {
  font-size: 18px;
  color: #666;
  margin-bottom: 20px;
}
</style>
