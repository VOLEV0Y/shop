import { defineStore } from 'pinia';
import api from './api';

export const useMainStore = defineStore('main', {
    state: () => ({
        isAuthenticated: !!localStorage.getItem('access_token'),
        cartCount: 0,
        username: localStorage.getItem('username') || '',
    }),
    actions: {
        async fetchCartCount() {
            if (!this.isAuthenticated) return;
            try {
                const res = await api.get('cart/my_cart/');
                this.cartCount = res.data.items.reduce((sum, item) => sum + item.quantity, 0);
            } catch (e) {
                console.log('Ошибка загрузки корзины');
            }
        },
        logout() {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('username');
            this.isAuthenticated = false;
            this.cartCount = 0;
            this.username = '';
            window.location.href = '/';
        }
    }
});