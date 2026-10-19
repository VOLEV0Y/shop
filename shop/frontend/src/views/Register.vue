<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-title">BRAT</div>
      <p class="auth-subtitle">Создайте аккаунт</p>
      <div v-if="error" class="error-msg">{{ error }}</div>

      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label>Логин</label><input type="text" v-model="username" required />
        </div>
        <div class="form-group">
          <label>Пароль</label><input type="password" v-model="password" required />
        </div>
        <button type="submit" class="auth-btn">ЗАРЕГИСТРИРОВАТЬСЯ</button>
      </form>
      <div class="divider">
        <hr />
        <span>или</span>
        <hr />
      </div>
      <div class="auth-links">
        Уже есть аккаунт? <router-link to="/login">Войти</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import api from "../api";

const username = ref("");
const password = ref("");
const error = ref("");
const router = useRouter();

const handleRegister = async () => {
  try {
    await api.post("register/", { username: username.value, password: password.value });
    alert("Регистрация успешна! Войдите.");
    router.push("/login");
  } catch (err) {
    error.value = err.response?.data?.error || "Ошибка при регистрации";
  }
};
</script>
