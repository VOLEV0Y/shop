<template>
  <div class="hero">
    <h2>НОВЫЕ КОЛЛЕКЦИИ</h2>
    <div class="hero-banners">
      <div class="hero-banner"><img src="/images/www.png" alt="Коллекция 1"></div>
      <div class="hero-banner"><img src="/images/w.webp" alt="Коллекция 2"></div>
      <div class="hero-banner"><img src="/images/ww.jpg" alt="Коллекция 3"></div>
    </div>
    <p>Будь всегда готов к важной встрече. Открой для себя новые коллекции обуви BRAT</p>
  </div>

  <div class="assortment">
    <h2>АССОРТИМЕНТ</h2>
    
    <div class="products">
      
      <template v-if="loading">
        <div v-for="i in 6" :key="'skeleton-'+i" class="product" style="height: 400px; background: #e0e0e0; border-radius: 10px; animation: pulse 1.5s infinite;"></div>
      </template>

      <template v-else>
        <div v-for="product in filteredProducts" :key="product.id" class="product">
          
          <router-link :to="'/product/' + product.id" class="product-image">
            <img :src="getProductImage(product)" :alt="product.name">
          </router-link>
          
          <div class="prices">
            <span class="new-price">{{ product.price }} ₽</span>
          </div>
          
          <router-link :to="'/product/' + product.id" style="text-decoration: none; color: inherit;">
              <h4>{{ product.name }}</h4>
          </router-link>

          <p class="product-material">Материал: {{ product.material }}</p>
          <p class="product-color">Цвет: {{ product.color }}</p>
          
          <select v-model="selectedSizes[product.id]" class="edit-input" style="margin-bottom:10px;">
            <option disabled value="">Выберите размер</option>
            <option v-for="size in sizes" :key="size.id" :value="size.id">{{ size.size }}</option>
          </select>

          <button @click="addToCart(product.id)" class="add-to-cart">В КОРЗИНУ</button>
        </div>

        <div v-if="filteredProducts.length === 0" style="grid-column: 1 / -1; text-align: center; padding: 40px;">
            <p style="font-size: 18px; color: #666;">Товары не найдены</p>
        </div>
      </template>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import api from '../api';
import { useMainStore } from '../store';
import { toast } from 'vue3-toastify';

const products = ref([]);
const sizes = ref([]);
const selectedSizes = ref({});
const loading = ref(true);
const store = useMainStore();
const route = useRoute();

const getProductImage = (product) => {
    if (product.image) {
        if (product.image.startsWith('http')) return product.image;
        return `http://127.0.0.1:8000${product.image}`;
    }
    const name = product.name.toLowerCase();
    if (name.includes('мафиози')) return '/images/spartan.jpg';
    if (name.includes('великий')) return '/images/tovar2.jpeg';
    if (name.includes('джордан')) return '/images/tovar3.jpg';
    if (name.includes('изумрудные')) return '/images/tovar4.jpg';
    return '/images/spartan.jpg';
};

const filteredProducts = computed(() => {
    const gender = route.query.gender;
    if (gender) return products.value.filter(p => p.gender === gender);
    return products.value;
});

const fetchData = async () => {
  loading.value = true;
  try {
      const searchQuery = route.query.search ? `?search=${route.query.search}` : '';
      const [prodRes, sizeRes] = await Promise.all([
          api.get('products/' + searchQuery), 
          api.get('sizes/')
      ]);
      products.value = prodRes.data;
      sizes.value = sizeRes.data;
  } catch (e) {
      console.error("Ошибка загрузки товаров:", e);
  } finally {
      loading.value = false;
  }
};

watch(() => route.query, () => {
    fetchData();
}, { deep: true });

const addToCart = async (productId) => {
  if (!store.isAuthenticated) {
    toast.warning('Войдите в аккаунт, чтобы добавить в корзину!');
    return;
  }
  const sizeId = selectedSizes.value[productId];
  if (!sizeId) {
    toast.warning('Пожалуйста, выберите размер!');
    return;
  }
  
  try {
      await api.post('cart/add_item/', { product_id: productId, size_id: sizeId });
      store.fetchCartCount();
      toast.success('Добавлено в корзину!');
  } catch(e) {
      toast.error('Ошибка добавления. Возможно, товар уже есть.');
  }
};

onMounted(fetchData);
</script>

<style scoped>
@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}
</style>