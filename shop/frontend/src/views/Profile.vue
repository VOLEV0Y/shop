<template>
  <div class="assortment" style="max-width: 860px">
    <h2>МОЙ ПРОФИЛЬ</h2>

    <div style="display: flex; gap: 40px; flex-wrap: wrap; margin-top: 30px">
      <div style="flex: 0 0 auto; text-align: center">
        <div
          style="
            width: 110px;
            height: 110px;
            border-radius: 50%;
            background: black;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 14px;
          "
        >
          <span
            style="color: white; font-size: 42px; font-weight: bold; letter-spacing: -2px"
          >
            {{ profile.first_name ? profile.first_name[0] : ""
            }}{{
              profile.last_name
                ? profile.last_name[0]
                : profile.username
                ? profile.username[0]
                : ""
            }}
          </span>
        </div>
        <p style="font-weight: bold; font-size: 17px">
          {{ profile.first_name }} {{ profile.last_name }}
        </p>
        <p style="color: #888; font-size: 13px">@{{ profile.username }}</p>
      </div>

      <div style="flex: 1; min-width: 280px">
        <div v-if="!isEditing">
          <div
            style="
              border: 2px solid #eee;
              border-radius: 10px;
              padding: 25px;
              margin-bottom: 20px;
            "
          >
            <h3
              style="
                font-size: 14px;
                letter-spacing: 1px;
                text-transform: uppercase;
                margin-bottom: 20px;
                border-bottom: 2px solid black;
                padding-bottom: 10px;
              "
            >
              Данные аккаунта
            </h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px">
              <div>
                <p class="label-text">Логин</p>
                <p class="value-text">{{ profile.username }}</p>
              </div>
              <div>
                <p class="label-text">Email</p>
                <p class="value-text">{{ profile.email || "—" }}</p>
              </div>
              <div>
                <p class="label-text">Имя</p>
                <p class="value-text">{{ profile.first_name || "—" }}</p>
              </div>
              <div>
                <p class="label-text">Фамилия</p>
                <p class="value-text">{{ profile.last_name || "—" }}</p>
              </div>
              <div>
                <p class="label-text">Телефон</p>
                <p class="value-text">{{ profile.phone || "—" }}</p>
              </div>
            </div>
          </div>

          <div
            style="
              border: 2px solid #eee;
              border-radius: 10px;
              padding: 25px;
              margin-bottom: 20px;
            "
          >
            <h3
              style="
                font-size: 14px;
                letter-spacing: 1px;
                text-transform: uppercase;
                margin-bottom: 20px;
                border-bottom: 2px solid black;
                padding-bottom: 10px;
              "
            >
              Адрес доставки
            </h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px">
              <div>
                <p class="label-text">Страна</p>
                <p class="value-text">{{ profile.country || "—" }}</p>
              </div>
              <div>
                <p class="label-text">Город</p>
                <p class="value-text">{{ profile.city || "—" }}</p>
              </div>
              <div>
                <p class="label-text">Улица</p>
                <p class="value-text">{{ profile.street || "—" }}</p>
              </div>
              <div>
                <p class="label-text">Квартира</p>
                <p class="value-text">{{ profile.apartment || "—" }}</p>
              </div>
            </div>
          </div>

          <div class="profile-btns">
            <router-link to="/cart" class="profile-action-btn profile-action-btn--black"
              >МОЯ КОРЗИНА</router-link
            >
            <button
              @click="isEditing = true"
              class="profile-action-btn profile-action-btn--outline"
            >
              ИЗМЕНИТЬ ДАННЫЕ
            </button>
            <button
              @click="store.logout()"
              class="profile-action-btn profile-action-btn--outline"
            >
              ВЫЙТИ
            </button>
          </div>
        </div>

        <div v-else>
          <form @submit.prevent="saveProfile">
            <div
              style="
                border: 2px solid black;
                border-radius: 10px;
                padding: 25px;
                margin-bottom: 20px;
              "
            >
              <h3
                style="
                  font-size: 14px;
                  letter-spacing: 1px;
                  text-transform: uppercase;
                  margin-bottom: 20px;
                  border-bottom: 2px solid black;
                  padding-bottom: 10px;
                "
              >
                Редактирование
              </h3>

              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px">
                <div>
                  <label class="edit-label">Имя</label
                  ><input class="edit-input" type="text" v-model="profile.first_name" />
                </div>
                <div>
                  <label class="edit-label">Фамилия</label
                  ><input class="edit-input" type="text" v-model="profile.last_name" />
                </div>
                <div>
                  <label class="edit-label">Телефон</label
                  ><input class="edit-input" type="text" v-model="profile.phone" />
                </div>
                <div>
                  <label class="edit-label">Email</label
                  ><input class="edit-input" type="email" v-model="profile.email" />
                </div>
                <div>
                  <label class="edit-label">Страна</label
                  ><input class="edit-input" type="text" v-model="profile.country" />
                </div>
                <div>
                  <label class="edit-label">Город</label
                  ><input class="edit-input" type="text" v-model="profile.city" />
                </div>
                <div>
                  <label class="edit-label">Улица</label
                  ><input class="edit-input" type="text" v-model="profile.street" />
                </div>
                <div>
                  <label class="edit-label">Квартира</label
                  ><input class="edit-input" type="text" v-model="profile.apartment" />
                </div>
                <div style="grid-column: 1 / -1">
                  <label class="edit-label"
                    >Новый пароль (оставьте пустым, если не меняете)</label
                  >
                  <input class="edit-input" type="password" v-model="newPassword" />
                </div>
              </div>
            </div>

            <div class="profile-btns">
              <button type="submit" class="profile-action-btn profile-action-btn--black">
                СОХРАНИТЬ
              </button>
              <button
                type="button"
                @click="isEditing = false"
                class="profile-action-btn profile-action-btn--outline"
              >
                ОТМЕНА
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../api";
import { useMainStore } from "../store";
import { useRouter } from "vue-router";
import { toast } from "vue3-toastify";

const store = useMainStore();
const router = useRouter();

const profile = ref({
  username: "",
  first_name: "",
  last_name: "",
  email: "",
  phone: "",
  country: "",
  city: "",
  street: "",
  apartment: "",
});
const isEditing = ref(false);
const newPassword = ref("");

const fetchProfile = async () => {
  try {
    const res = await api.get("users/profile/");
    profile.value = res.data;
  } catch (e) {
    toast.error("Ошибка загрузки профиля");
  }
};

const saveProfile = async () => {
  try {
    const payload = { ...profile.value };
    if (newPassword.value) {
      payload.password = newPassword.value;
    }

    await api.put("users/profile/", payload);
    toast.success("Данные обновлены!");
    isEditing.value = false;

    if (newPassword.value) {
      toast.info("Пароль изменен. Войдите заново.");
      store.logout();
      router.push("/login");
    }
  } catch (e) {
    toast.error("Ошибка сохранения");
  }
};

onMounted(fetchProfile);
</script>

<style scoped>
.label-text {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #999;
  margin-bottom: 4px;
}
.value-text {
  font-weight: bold;
}
</style>
