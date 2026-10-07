/* YAMORA Retails - Interactive JS functionality */

document.addEventListener('DOMContentLoaded', function () {

    // 1. Toast Notification Trigger
    function showToast(message, type = 'success') {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.style.position = 'fixed';
            container.style.bottom = '20px';
            container.style.right = '20px';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'danger' ? 'danger' : (type === 'warning' ? 'warning' : 'primary')} border-0 show shadow-lg mb-2`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body font-weight-medium">
                    <i class="bi bi-info-circle-fill me-2"></i> ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;

        container.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 4000);
    }

    // 2. Quantity Plus/Minus Controls
    document.querySelectorAll('.btn-qty-minus').forEach(button => {
        button.addEventListener('click', function () {
            const input = this.nextElementSibling;
            if (input && input.value > 1) {
                input.value = parseInt(input.value) - 1;
            }
        });
    });

    document.querySelectorAll('.btn-qty-plus').forEach(button => {
        button.addEventListener('click', function () {
            const input = this.previousElementSibling;
            if (input) {
                const max = parseInt(input.getAttribute('max')) || 99;
                if (parseInt(input.value) < max) {
                    input.value = parseInt(input.value) + 1;
                }
            }
        });
    });

    // 3. AJAX Add to Cart Handler
    document.querySelectorAll('.ajax-add-to-cart').forEach(form => {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            const actionUrl = this.action;
            const formData = new FormData(this);

            fetch(actionUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                    return;
                }
                return response.json();
            })
            .then(data => {
                if (data && data.success) {
                    showToast(data.message, 'success');
                    const badge = document.getElementById('cart-badge');
                    if (badge) {
                        badge.textContent = data.cart_count;
                        badge.classList.remove('d-none');
                    }
                }
            })
            .catch(err => {
                console.error("Cart submit error:", err);
            });
        });
    });

    // 4. AJAX Wishlist Toggle Handler
    document.querySelectorAll('.btn-wishlist-toggle').forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const url = this.getAttribute('data-url');

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(res => {
                if (res.redirected) {
                    window.location.href = res.url;
                    return;
                }
                return res.json();
            })
            .then(data => {
                if (data && data.success) {
                    showToast(data.message, data.added ? 'success' : 'info');
                    if (data.added) {
                        this.classList.add('active');
                        this.querySelector('i').className = 'bi bi-heart-fill text-danger';
                    } else {
                        this.classList.remove('active');
                        this.querySelector('i').className = 'bi bi-heart';
                    }
                }
            });
        });
    });

});
