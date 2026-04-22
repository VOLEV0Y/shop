(function() {
    function getCSRFToken() {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, 10) === 'csrftoken=') {
                    cookieValue = decodeURIComponent(cookie.substring(10));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function showMessage(container, text, type) {
        let msgDiv = container.querySelector('.ajax-message');
        if (!msgDiv) {
            msgDiv = document.createElement('div');
            msgDiv.className = 'ajax-message';
            container.prepend(msgDiv);
        }
        msgDiv.textContent = text;
        msgDiv.style.cssText = `padding:10px; margin-bottom:15px; 
        border-radius:6px; background:${type === 'error' ? '#ffefef' : '#e8f5e9'};
        color:${type === 'error' ? '#c00' : '#2e7d32'}; 
        border:1px solid ${type === 'error' ? '#ffcdd2' : '#c8e6c9'}`;
        setTimeout(() => msgDiv.remove(), 3000);
    }

    function phoneMask(input) {
        let value = input.value.replace(/\D/g, '');
        if (value.length > 11) value = value.slice(0, 11);
        let formatted = '';
        if (value.length > 0) formatted = '+7';
        if (value.length > 1) formatted += ' (' + value.slice(1, 4);
        if (value.length > 4) formatted += ') ' + value.slice(4, 7);
        if (value.length > 7) formatted += '-' + value.slice(7, 9);
        if (value.length > 9) formatted += '-' + value.slice(9, 11);
        input.value = formatted;
    }
    function applyPhoneMasks() {
        document.querySelectorAll('input[name="phone"]').forEach(input => {
            if (!input.hasAttribute('data-mask-attached')) {
                input.setAttribute('data-mask-attached', 'true');
                input.addEventListener('input', function() { phoneMask(this); });
                if (input.value.trim()) phoneMask(input);
            }
        });
    }
    applyPhoneMasks();

    let tracks = window.BRAT_TRACKS || [];
    if (tracks.length) {
        const STORAGE_KEY = 'brat_player';
        let state = {
            index: 0, time: 0, muted: false, volume: 0.5, paused: false
        };
        try {
            const saved = JSON.parse(sessionStorage.getItem(STORAGE_KEY));
            if (saved) Object.assign(state, saved);
        } catch(e) {}
        let audio = new Audio();
        audio.volume = state.muted ? 0 : state.volume;

        function saveState() {
            try {
                sessionStorage.setItem(STORAGE_KEY, JSON.stringify({
                    index: state.index,
                    time: audio.currentTime,
                    muted: state.muted,
                    volume: state.volume,
                    paused: state.paused
                }));
            } catch(e) {}
        }
        function updateUI() {
            let nameEl = document.getElementById('track-name');
            let muteBtn = document.getElementById('mute-btn');
            let pauseBtn = document.getElementById('pause-btn');
            let volSlider = document.getElementById('vol-slider');
            if (nameEl) nameEl.textContent = tracks[state.index].name;
            if (muteBtn) muteBtn.textContent = state.muted ? '🔇' : '🔊';
            if (pauseBtn) pauseBtn.textContent = (audio.paused || state.paused) ? '▶' : '⏸';
            if (volSlider) volSlider.value = state.muted ? 0 : state.volume;
        }
        function loadTrack(index, startTime, autoplay) {
            state.index = index;
            audio.src = tracks[index].url;
            audio.currentTime = startTime || 0;
            audio.volume = state.muted ? 0 : state.volume;
            if (!state.paused && autoplay !== false) {
                audio.play().catch(() => {
                    document.addEventListener('click', function startOnClick() {
                        if (!state.paused) audio.play();
                        document.removeEventListener('click', startOnClick);
                    });
                });
            }
            updateUI();
        }
        window.bratNextTrack = function() {
            state.index = (state.index + 1) % tracks.length;
            state.paused = false;
            loadTrack(state.index, 0, true);
            saveState();
        };
        window.bratTogglePause = function() {
            if (audio.paused) {
                state.paused = false;
                audio.play();
            } else {
                state.paused = true;
                audio.pause();
            }
            updateUI();
            saveState();
        };
        window.bratToggleMute = function() {
            state.muted = !state.muted;
            audio.volume = state.muted ? 0 : state.volume;
            let volSlider = document.getElementById('vol-slider');
            if (volSlider) volSlider.value = state.muted ? 0 : state.volume;
            updateUI();
            saveState();
        };
        window.bratSetVolume = function(val) {
            state.volume = parseFloat(val);
            state.muted = state.volume === 0;
            audio.volume = state.volume;
            updateUI();
            saveState();
        };
        audio.addEventListener('ended', window.bratNextTrack);
        window.addEventListener('beforeunload', () => {
            state.paused = audio.paused;
            saveState();
        });
        setInterval(() => { if (!audio.paused) saveState(); }, 1000);
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => loadTrack(state.index, state.time, true));
        } else {
            loadTrack(state.index, state.time, true);
        }
    }

    function handleAuthForm(form, url, successRedirect) {
        if (!form) return;
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': getCSRFToken(), 'X-Requested-With': 'XMLHttpRequest' },
                    body: formData
                });
                const result = await response.json();
                if (result.success) {
                    window.location.href = successRedirect;
                } else {
                    showMessage(form, result.error || 'Ошибка', 'error');
                }
            } catch (err) {
                showMessage(form, 'Серверная ошибка', 'error');
            }
        });
    }
    handleAuthForm(document.querySelector('form[action="/login/"]'), '/login/', '/profile/');
    handleAuthForm(document.querySelector('form[action="/register/"]'), '/register/', '/profile/');

    function attachAddToCartEvents() {
        document.querySelectorAll('form[action="/add-to-cart/"]').forEach(form => {
            form.removeEventListener('submit', addToCartHandler);
            form.addEventListener('submit', addToCartHandler);
        });
    }
    async function addToCartHandler(e) {
        e.preventDefault();
        const form = e.currentTarget;
        const formData = new FormData(form);
        await fetch('/add-to-cart/', {
            method: 'POST',
            headers: { 'X-CSRFToken': getCSRFToken(), 'X-Requested-With': 'XMLHttpRequest' },
            body: formData
        });
        const resp = await fetch('/cart/?count_only=1', { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
        const data = await resp.json();
        updateCartBadge(data.cart_count);
        const btn = form.querySelector('button');
        const originalText = btn.textContent;
        btn.textContent = '✓ В корзине';
        setTimeout(() => btn.textContent = originalText, 1000);
    }

    function updateProductList(url) {
        fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const newProducts = doc.querySelector('.products');
                const oldProducts = document.querySelector('.products');
                if (newProducts && oldProducts) {
                    oldProducts.replaceWith(newProducts);
                    attachAddToCartEvents();
                    applyPhoneMasks();
                }
                window.history.pushState({}, '', url);
            })
            .catch(console.error);
    }
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const query = new URLSearchParams(new FormData(searchForm)).toString();
            updateProductList('/?' + query);
        });
    }
    document.querySelectorAll('.nav a').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const url = link.getAttribute('href');
            if (url && url !== '#') updateProductList(url);
        });
    });
    attachAddToCartEvents();

    function updateCartBadge(count) {
        const badge = document.querySelector('.cart-badge');
        if (badge) {
            if (count > 0) {
                badge.textContent = count;
                badge.style.display = 'flex';
            } else {
                badge.style.display = 'none';
            }
        }
    }
    async function refreshCartBlock() {
        const cartContainer = document.querySelector('.assortment');
        if (!cartContainer || !window.location.pathname.includes('/cart/')) return;
        const resp = await fetch('/cart/?ajax=1', { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
        const html = await resp.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const newCartHtml = doc.querySelector('.assortment').innerHTML;
        cartContainer.innerHTML = newCartHtml;
        attachCartEvents();
        applyPhoneMasks();
    }
    async function cartAction(url, method = 'POST') {
        try {
            const res = await fetch(url, {
                method: method,
                headers: { 'X-CSRFToken': getCSRFToken(), 'X-Requested-With': 'XMLHttpRequest' }
            });
            const data = await res.json();
            if (data.cart_count !== undefined) updateCartBadge(data.cart_count);
            if (window.location.pathname.includes('/cart/')) await refreshCartBlock();
        } catch(e) { console.error(e); }
    }
    function attachCartEvents() {
        document.querySelectorAll('.quantity-btn, .remove-btn').forEach(btn => {
            btn.removeEventListener('click', cartClickHandler);
            btn.addEventListener('click', cartClickHandler);
        });
        const clearBtn = document.querySelector('.clear-cart-btn');
        if (clearBtn) {
            clearBtn.removeEventListener('click', clearCartHandler);
            clearBtn.addEventListener('click', clearCartHandler);
        }
    }
    function cartClickHandler(e) {
        e.preventDefault();
        const url = this.getAttribute('href');
        if (url) cartAction(url, 'GET');
    }
    async function clearCartHandler(e) {
        e.preventDefault();
        await cartAction('/clear-cart/', 'POST');
    }
    if (window.location.pathname.includes('/cart/')) attachCartEvents();

    const profileForm = document.querySelector('#edit-mode form');
    if (profileForm) {
        profileForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(profileForm);
            try {
                const response = await fetch('/profile/update/', {
                    method: 'POST',
                    headers: { 'X-CSRFToken': getCSRFToken(), 'X-Requested-With': 'XMLHttpRequest' },
                    body: formData
                });
                const result = await response.json();
                if (result.success) {
                    window.location.reload();
                } else {
                    showMessage(profileForm, result.error || 'Ошибка обновления', 'error');
                }
            } catch(err) {
                showMessage(profileForm, 'Ошибка сервера', 'error');
            }
        });
    }

    if (window.location.pathname.includes('/cart/')) {
        setInterval(() => {
            fetch('/cart/?count_only=1', { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                .then(res => res.json())
                .then(data => updateCartBadge(data.cart_count))
                .catch(() => {});
        }, 5000);
    }

    const observer = new MutationObserver(() => {
        applyPhoneMasks();
        attachAddToCartEvents();
        if (window.location.pathname.includes('/cart/')) attachCartEvents();
    });
    observer.observe(document.body, { childList: true, subtree: true });
})();