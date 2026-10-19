<template>
  <div class="assortment" v-if="product">
    <div style="display: flex; gap: 40px; flex-wrap: wrap">
      <div style="flex: 1; min-width: 300px">
        <img
          :src="getProductImage(product)"
          style="width: 100%; border-radius: 10px; border: 2px solid #eee"
        />
      </div>
      <div style="flex: 1; min-width: 300px">
        <h2>{{ product.name }}</h2>
        <h3 style="font-size: 28px; margin: 20px 0">{{ product.price }} ₽</h3>
        <p><strong>Материал:</strong> {{ product.material }}</p>
        <p><strong>Цвет:</strong> {{ product.color }}</p>
        <p style="margin-top: 20px">{{ product.description }}</p>

        <select
          v-model="selectedSize"
          class="edit-input"
          style="margin: 20px 0; width: 100%"
        >
          <option disabled value="">Выберите размер</option>
          <option v-for="size in sizes" :key="size.id" :value="size.id">
            {{ size.size }}
          </option>
        </select>
        <button @click="addToCart" class="add-to-cart">В КОРЗИНУ</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../api";
import { useMainStore } from "../store";
import { toast } from "vue3-toastify";

const route = useRoute();
const router = useRouter();
const store = useMainStore();

const product = ref(null);
const sizes = ref([]);
const selectedSize = ref("");

const getProductImage = (p) => {
  if (p.image)
    return p.image.startsWith("http") ? p.image : `http://127.0.0.1:8000${p.image}`;
  return "/images/spartan.jpg";
};

const addToCart = async () => {
  if (!store.isAuthenticated) {
    toast.warning("Войдите в аккаунт!");
    router.push("/login");
    return;
  }
  if (!selectedSize.value) {
    toast.warning("Выберите размер!");
    return;
  }
  try {
    await api.post("cart/add_item/", {
      product_id: product.value.id,
      size_id: selectedSize.value,
    });
    store.fetchCartCount();
    toast.success("Добавлено в корзину!");
  } catch (e) {
    toast.error("Ошибка добавления");
  }
};

onMounted(async () => {
  try {
    const res = await api.get(`products/${route.params.id}/`);
    product.value = res.data;
    const sizeRes = await api.get("sizes/");
    sizes.value = sizeRes.data;
  } catch (e) {
    toast.error("Товар не найден");
    router.push("/");
  }
});
</script>
