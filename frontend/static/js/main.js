const apiBaseUrl = window.location.origin;
let cartCount = 0;

const showAlert = (elementId, message, type = 'success') => {
    const alert = document.getElementById(elementId);
    if (alert) {
        alert.textContent = message;
        alert.className = `alert alert-${type}`;
        alert.classList.remove('d-none');
        setTimeout(() => alert.classList.add('d-none'), 4000);
    } else {
        window.alert(message);
    }
};

const togglePasswordVisibility = () => {
    document.querySelectorAll('.password-toggle').forEach(button => {
        button.addEventListener('click', () => {
            const target = document.getElementById(button.dataset.target);
            if (!target) return;
            const type = target.getAttribute('type') === 'password' ? 'text' : 'password';
            target.setAttribute('type', type);
            button.textContent = type === 'password' ? 'إظهار' : 'إخفاء';
        });
    });
};

const normalizeImageUrl = (rawUrl) => {
    if (!rawUrl) return null;
    let url = rawUrl.replace(/\\/g, '/');
    if (url.startsWith('Clothings_Photo/')) {
        return `/${url}`;
    }
    if (url.startsWith('/Clothings_Photo/')) {
        return url;
    }
    if (url.startsWith('http://') || url.startsWith('https://')) {
        return url;
    }
    return url;
};

const renderProducts = (products) => {
    const container = document.getElementById('products-container');
    if (!container) return;

    container.innerHTML = products.map(product => {
        const image = normalizeImageUrl(product.image_url) || 'https://via.placeholder.com/400x300?text=Product';
        return `
            <div class="col">
                <div class="card h-100 product-card shadow-sm">
                    <img src="${image}" class="card-img-top" alt="${product.name}">
                    <div class="card-body d-flex flex-column">
                        <h5 class="card-title">${product.name}</h5>
                        <p class="card-text text-muted">${product.description || 'وصف المنتج غير متوفر حالياً.'}</p>
                        <div class="mt-auto d-flex justify-content-between align-items-center">
                            <span class="price-tag">${product.price} جنيه</span>
                            <button class="btn btn-primary btn-sm add-to-cart" data-product-id="${product.id}">إضافة للسلة</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');

    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', () => {
            cartCount += 1;
            document.getElementById('cart-count').textContent = `السلة: ${cartCount}`;
            showAlert('signup-alert', 'تمت إضافة المنتج إلى السلة', 'success');
        });
    });
};

const loadProducts = async () => {
    const container = document.getElementById('products-container');
    if (!container) return;

    try {
        const response = await fetch(`${apiBaseUrl}/api/products`);
        if (!response.ok) throw new Error('حدث خطأ أثناء تحميل المنتجات.');
        const products = await response.json();
        if (!products.length) {
            container.innerHTML = '<div class="col"><div class="alert alert-info">لا توجد منتجات حالياً.</div></div>';
            return;
        }
        renderProducts(products);
    } catch (error) {
        container.innerHTML = `<div class="col"><div class="alert alert-danger">${error.message}</div></div>`;
    }
};

const handleLogin = async () => {
    const form = document.getElementById('login-form');
    if (!form) return;

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value.trim();

        try {
            const response = await fetch(`${apiBaseUrl}/api/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password }),
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.detail || result.message || 'فشل تسجيل الدخول');
            showAlert('login-alert', result.message, 'success');
            setTimeout(() => window.location.href = '/', 1200);
        } catch (error) {
            showAlert('login-alert', error.message, 'danger');
        }
    });
};

const handleSignup = async () => {
    const form = document.getElementById('signup-form');
    if (!form) return;

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const username = document.getElementById('name').value.trim();
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value.trim();
        const confirm_password = document.getElementById('confirm_password').value.trim();

        try {
            const response = await fetch(`${apiBaseUrl}/api/signup`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password, confirm_password, Info: {} }),
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.detail || result.message || 'فشل إنشاء الحساب');
            showAlert('signup-alert', result.message || 'تم إنشاء الحساب بنجاح', 'success');
            setTimeout(() => window.location.href = '/login', 1400);
        } catch (error) {
            showAlert('signup-alert', error.message, 'danger');
        }
    });
};

window.addEventListener('DOMContentLoaded', () => {
    loadProducts();
    handleLogin();
    handleSignup();
    togglePasswordVisibility();
});
