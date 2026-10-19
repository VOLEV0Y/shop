import { createRouter, createWebHistory } from 'vue-router';
import Home from './views/Home.vue';
import Cart from './views/Cart.vue';
import Login from './views/Login.vue';
import Register from './views/Register.vue';
import Profile from './views/Profile.vue';
import ProductDetail from './views/ProductDetail.vue';
import Checkout from './views/Checkout.vue';

const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: '/', component: Home },
        { path: '/cart', component: Cart },
        { path: '/login', component: Login },
        { path: '/register', component: Register },
        { path: '/profile', component: Profile },
        { path: '/product/:id', component: ProductDetail },
        { path: '/checkout', component: Checkout },
    ]
});
export default router;