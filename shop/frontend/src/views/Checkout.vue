<template>
  <div class="assortment" style="max-width: 600px">
    <h2>ОФОРМЛЕНИЕ ЗАКАЗА</h2>
    <div style="margin-top: 20px">
      <div v-if="addresses.length">
        <label>Выберите сохранённый адрес:</label>
        <select v-model="addressId" class="edit-input" style="margin: 10px 0">
          <option disabled value="">Выберите адрес</option>
          <option v-for="addr in addresses" :key="addr.id" :value="addr.id">
            {{ addr.name }}
          </option>
        </select>
      </div>

      <label>{{ addresses.length ? "Или введите новый адрес:" : "Адрес доставки:" }}</label>
      <input
        v-model="newAddress"
        class="edit-input"
        style="margin: 10px 0"
        placeholder="Город, улица, дом, квартира"
      />

      <label>Способ оплаты:</label>
      <select v-model="paymentId" class="edit-input" style="margin: 10px 0">
        <option disabled value="">Выберите способ</option>
        <option v-for="pay in payments" :key="pay.id" :value="pay.id">
          {{ pay.name }}
        </option>
      </select>

      <button @click="submitOrder" class="add-to-cart" style="margin-top: 20px">
        ПОДТВЕРДИТЬ ЗАКАЗ
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import api from "../api";
import { useMainStore } from "../store";
import { toast } from "vue3-toastify";

const addresses = ref([]);
const payments = ref([]);
const addressId = ref("");
const paymentId = ref("");
const newAddress = ref("");
const router = useRouter();
const store = useMainStore();

const submitOrder = async () => {
  if ((!addressId.value && !newAddress.value.trim()) || !paymentId.value) {
    return toast.warning("Заполните все поля");
  }
  try {
    let addrId = addressId.value;
    if (newAddress.value.trim()) {
      const created = await api.post("addresses/", { name: newAddress.value.trim() });
      addrId = created.data.id;
    }
    await api.post("orders/", {
      address_id: addrId,
      payment_id: paymentId.value,
    });
    store.fetchCartCount();
    toast.success("Заказ успешно оформлен!");
    router.push("/profile");
  } catch (e) {
    toast.error(e.response?.data?.error || "Ошибка оформления");
  }
};

onMounted(async () => {
  try {
    const [addrRes, payRes] = await Promise.all([
      api.get("addresses/"),
      api.get("payments/"),
    ]);
    addresses.value = addrRes.data;
    payments.value = payRes.data;
    if (!addresses.value.length) {
      const profile = (await api.get("users/profile/")).data;
      newAddress.value = [profile.city, profile.street, profile.apartment]
        .filter(Boolean)
        .join(", ");
    }
  } catch (e) {
    console.error("Ошибка загрузки данных для оформления", e);
  }
});
</script>
