<template>
  <div id="app-container">
    <header>
      <div class="header">
        <div class="logo-section">
          <div class="logo">
            <img src="/images/logo.jpeg" alt="Логотип BRAT" />
          </div>
          <h1>
            <router-link to="/" style="text-decoration: none; color: inherit"
              >BRAT</router-link
            >
          </h1>
        </div>

        <div class="nav">
          <router-link to="/?gender=F">ЖЕНЩИНАМ</router-link>
          <router-link to="/?gender=M">МУЖЧИНАМ</router-link>
          <router-link to="/?gender=U">УНИСЕКС</router-link>
        </div>

        <div class="header-actions">
          <form class="search-form" @submit.prevent="doSearch">
            <input type="text" v-model="searchQuery" placeholder="Поиск обуви..." />
            <button type="submit" class="search-btn">Найти</button>
          </form>

          <router-link
            v-if="store.isAuthenticated"
            to="/profile"
            class="header-btn header-btn--profile"
          >
            {{ store.username ? store.username.toUpperCase() : "ПРОФИЛЬ" }}
          </router-link>
          <router-link v-else to="/login" class="header-btn header-btn--profile"
            >ВОЙТИ</router-link
          >

          <router-link to="/cart" class="header-btn header-btn--cart">
            КОРЗИНА
            <span class="cart-badge" v-if="store.cartCount > 0">{{
              store.cartCount
            }}</span>
          </router-link>
        </div>
      </div>
    </header>

    <main>
      <router-view></router-view>
    </main>

    <footer>
      <div class="footer">
        <div class="footer-content">
          <div class="footer-left">
            <div class="footer-brand">BRAT</div>
            <p>© 2026 Все права защищены</p>
            <p>ООО «БРАТ продажа обуви»</p>
          </div>
          <div class="footer-center">
            <p><strong>Контакты</strong></p>
            <p>brat@gmail.com</p>
            <p>+7 (499) 521-71-14</p>
          </div>
          <div class="footer-right">
            <p><strong>Мы в соцсетях:</strong></p>
            <div class="social-icons">
              <div class="social-icon">
                <img src="/images/watchap.png" alt="WhatsApp" />
              </div>
              <div class="social-icon">
                <img src="/images/instagram.png" alt="Instagram" />
              </div>
              <div class="social-icon">
                <img src="/images/telega.png" alt="Telegram" />
              </div>
            </div>
            <p style="margin-top: 20px"><strong>Способы оплаты:</strong></p>
            <div class="payment-icons">
              <div class="payment-icon"><img src="/images/viza.jpg" alt="Visa" /></div>
              <div class="payment-icon">
                <img src="/images/master.png" alt="MasterCard" />
              </div>
              <div class="payment-icon"><img src="/images/mir.jpg" alt="Мир" /></div>
            </div>
          </div>
        </div>
      </div>
    </footer>

    <MusicPlayer />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useMainStore } from "./store";
import MusicPlayer from "./components/MusicPlayer.vue";

const store = useMainStore();
const router = useRouter();
const route = useRoute();

const searchQuery = ref(route.query.search || "");
let debounceTimer = null;

watch(searchQuery, (newValue) => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    if (newValue.trim()) {
      router.push({ path: "/", query: { search: newValue } });
    } else {
      router.push({ path: "/" });
    }
  }, 500);
});

const doSearch = () => {
  router.push({ path: "/", query: { search: searchQuery.value } });
};

onMounted(() => {
  store.fetchCartCount();
});
</script>

<style></style>
