/**
 * MantaHotel — Client-side JavaScript
 * =====================================
 * Minimal JS — HTMX handles most interactivity.
 * This file handles: toasts, sidebar toggle, icons, PWA registration.
 */

// ── Initialize Lucide Icons ──────────────────────
document.addEventListener('DOMContentLoaded', function () {
    if (window.lucide) {
        lucide.createIcons();
    }

    // Re-initialize icons after HTMX swaps
    document.body.addEventListener('htmx:afterSwap', function () {
        if (window.lucide) {
            lucide.createIcons();
        }
    });
});

// ── Sidebar Toggle (Mobile) ─────────────────────
function toggleSidebar() {
    var sidebar = document.getElementById('sidebar');
    if (sidebar) {
        sidebar.classList.toggle('open');
    }
}

// ── Toast Auto-dismiss ──────────────────────────
document.addEventListener('DOMContentLoaded', function () {
    var toasts = document.querySelectorAll('.toast-item');
    toasts.forEach(function (toast) {
        setTimeout(function () {
            toast.style.opacity = '0';
            setTimeout(function () { toast.remove(); }, 300);
        }, 5000);
    });
});

// ── HTMX Configuration ─────────────────────────
document.body.addEventListener('htmx:configRequest', function (event) {
    // Include CSRF token in all HTMX requests
    var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfToken) {
        event.detail.headers['X-CSRFToken'] = csrfToken.value;
    }
});

// ── PWA Service Worker Registration ─────────────
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(function (registration) {
                console.log('MantaHotel SW registered:', registration.scope);
            })
            .catch(function (error) {
                console.log('MantaHotel SW registration failed:', error);
            });
    });
}
