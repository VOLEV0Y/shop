<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-title">BRAT</div>
      <p class="auth-subtitle">Войдите в свой аккаунт</p>
      <div v-if="error" class="error-msg">{{ error }}</div>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>Логин</label>
          <input type="text" v-model="username" placeholder="Введите логин" required>
        </div>
        <div class="form-group">
          <label>Пароль</label>
          <input type="password" v-model="password" placeholder="Введите пароль" required>
        </div>
        <button type="submit" class="auth-btn">ВОЙТИ</button>
      </form>
      <div class="divider"><hr><span>или</span><hr></div>
      <div class="auth-links">Нет аккаунта? <router-link to="/register">Зарегистрироваться</router-link></div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api';
import { useMainStore } from '../store';

const username = ref('');
const password = ref('');
const error = ref('');
const router = useRouter();
const store = useMainStore();

const handleLogin = async () => {
  try {
      const response = await api.post('token/', { username: username.value, password: password.value });
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      localStorage.setItem('username', username.value);
      
      store.isAuthenticated = true;
      store.username = username.value;
      store.fetchCartCount();
      router.push('/profile');
  } catch (err) {
      error.value = 'Неверный логин или пароль';
  }
};
</script>