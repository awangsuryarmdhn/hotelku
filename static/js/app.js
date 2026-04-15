/**
 * MantaHotel — Client-side JavaScript
 * =====================================
 * Handles: page loading bar, toasts, sidebar, icons, PWA, error messages.
 */

// ── Page Loading Bar ─────────────────────────────
const PageLoader = (function () {
    let timer = null;
    let progress = 0;
    let bar = null;

    function getBar() {
        if (!bar) {
            bar = document.getElementById('page-loading-bar');
        }
        return bar;
    }

    function start() {
        const el = getBar();
        if (!el) return;
        progress = 0;
        el.style.width = '0%';
        el.style.opacity = '1';
        el.classList.add('active');

        clearInterval(timer);
        timer = setInterval(function () {
            // Asymptotic progress — never quite reaches 90% naturally
            if (progress < 85) {
                progress += (85 - progress) * 0.08;
                el.style.width = progress + '%';
            }
        }, 80);
    }

    function finish() {
        const el = getBar();
        if (!el) return;
        clearInterval(timer);
        progress = 100;
        el.style.width = '100%';
        setTimeout(function () {
            el.style.opacity = '0';
            el.classList.remove('active');
            setTimeout(function () { el.style.width = '0%'; }, 300);
        }, 250);
    }

    function error() {
        const el = getBar();
        if (!el) return;
        clearInterval(timer);
        el.classList.add('error');
        el.style.width = '100%';
        setTimeout(function () {
            el.style.opacity = '0';
            setTimeout(function () {
                el.classList.remove('error');
                el.style.width = '0%';
            }, 300);
        }, 500);
    }

    return { start, finish, error };
})();

// ── Page Transition (navigation links) ─────────────────
document.addEventListener('click', function (e) {
    const link = e.target.closest('a[href]');
    if (!link) return;
    const href = link.getAttribute('href');
    // Only trigger for same-origin, non-hash, non-external, non-download links
    if (
        href &&
        !href.startsWith('#') &&
        !href.startsWith('javascript:') &&
        !link.hasAttribute('download') &&
        !link.hasAttribute('target') &&
        !e.ctrlKey && !e.metaKey && !e.shiftKey
    ) {
        try {
            const url = new URL(href, window.location.origin);
            if (url.origin === window.location.origin) {
                PageLoader.start();
            }
        } catch (_) { /* relative urls are fine */ }
    }
});

// Finish loader when page is fully loaded
window.addEventListener('load', function () {
    PageLoader.finish();
});

// Also finish on DOMContentLoaded for quick pages
document.addEventListener('DOMContentLoaded', function () {
    PageLoader.finish();
});

// ── Toast Notification System ────────────────────
const Toast = (function () {
    function getContainer() {
        let container = document.getElementById('toast-overlay');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-overlay';
            container.className = 'toast-overlay';
            document.body.appendChild(container);
        }
        return container;
    }

    function show(message, type, duration) {
        duration = duration || 6000;
        const container = getContainer();
        const icons = {
            success: '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>',
            error:   '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
            warning: '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>',
            info:    '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>',
        };

        const toast = document.createElement('div');
        toast.className = 'toast-msg toast-' + (type || 'info');
        toast.innerHTML = '<span class="toast-icon">' + (icons[type] || icons.info) + '</span>' +
                          '<span class="toast-text">' + message + '</span>' +
                          '<button class="toast-close" onclick="this.parentElement.remove()">×</button>';

        container.appendChild(toast);
        requestAnimationFrame(function () { toast.classList.add('show'); });

        setTimeout(function () {
            toast.classList.remove('show');
            setTimeout(function () { toast.remove(); }, 350);
        }, duration);
    }

    return { show };
})();

// ── Error Report Overlay ──────────────────────────
function showErrorReport(code, title, detail, hint) {
    const id = 'err-overlay-' + Date.now();
    const overlay = document.createElement('div');
    overlay.id = id;
    overlay.className = 'error-overlay';
    overlay.innerHTML =
        '<div class="error-modal">' +
        '  <div class="error-modal-header">' +
        '    <span class="error-code">Error ' + (code || '???') + '</span>' +
        '    <button onclick="document.getElementById(\'' + id + '\').remove()" class="error-close">×</button>' +
        '  </div>' +
        '  <div class="error-modal-body">' +
        '    <div class="error-title">' + (title || 'Terjadi Kesalahan') + '</div>' +
        '    <div class="error-detail">' + (detail || 'Detail kesalahan tidak tersedia.') + '</div>' +
        (hint ? '<div class="error-hint"><strong>Solusi:</strong> ' + hint + '</div>' : '') +
        '    <div class="error-report-note">⚠️ Laporkan error ini ke tim teknis: <strong>mantahotel@support</strong></div>' +
        '  </div>' +
        '  <div class="error-modal-footer">' +
        '    <button onclick="window.location.reload()" class="btn-error-retry">Coba Lagi</button>' +
        '    <button onclick="document.getElementById(\'' + id + '\').remove()" class="btn-error-dismiss">Tutup</button>' +
        '  </div>' +
        '</div>';
    document.body.appendChild(overlay);
    requestAnimationFrame(function () { overlay.classList.add('show'); });
}

// ── HTMX Error Handling ───────────────────────────
document.body.addEventListener('htmx:responseError', function (event) {
    PageLoader.error();
    const status = event.detail.xhr.status;
    const errorMap = {
        400: { title: 'Permintaan Tidak Valid (400)', detail: 'Data yang dikirimkan tidak valid atau tidak lengkap.', hint: 'Periksa kembali form dan coba lagi.' },
        401: { title: 'Sesi Berakhir (401)', detail: 'Anda perlu login ulang untuk melanjutkan.', hint: 'Klik "Coba Lagi" dan login kembali.' },
        403: { title: 'Akses Ditolak (403)', detail: 'Anda tidak memiliki hak untuk mengakses halaman ini.', hint: 'Hubungi administrator untuk mendapatkan akses.' },
        404: { title: 'Halaman Tidak Ditemukan (404)', detail: 'Halaman atau data yang diminta tidak ditemukan di server.', hint: 'Periksa URL atau kembali ke beranda.' },
        408: { title: 'Koneksi Timeout (408)', detail: 'Server terlalu lama merespons. Koneksi database mungkin lambat.', hint: 'Periksa koneksi internet Anda dan coba lagi.' },
        429: { title: 'Terlalu Banyak Permintaan (429)', detail: 'Anda mengirimkan terlalu banyak permintaan dalam waktu singkat.', hint: 'Tunggu beberapa detik dan coba lagi.' },
        500: { title: 'Error Server Internal (500)', detail: 'Terjadi kesalahan di server. Tim teknis perlu meninjau log server.', hint: 'Laporkan waktu kejadian dan tindakan yang dilakukan ke tim teknis.' },
        502: { title: 'Gateway Error (502)', detail: 'Server tidak dapat menerima respons dari upstream.', hint: 'Server mungkin sedang restart. Coba lagi dalam 1-2 menit.' },
        503: { title: 'Layanan Tidak Tersedia (503)', detail: 'Server sedang dalam pemeliharaan atau kelebihan beban.', hint: 'Coba lagi beberapa menit kemudian.' },
        504: { title: 'Gateway Timeout (504)', detail: 'Server tidak merespons tepat waktu (koneksi database lambat).', hint: 'Periksa koneksi database Supabase dan coba lagi.' },
    };
    const err = errorMap[status] || { title: 'Kesalahan Jaringan (' + status + ')', detail: 'Terjadi kesalahan yang tidak diketahui saat berkomunikasi dengan server.', hint: 'Coba muat ulang halaman.' };
    showErrorReport(status, err.title, err.detail, err.hint);
});

document.body.addEventListener('htmx:sendError', function () {
    PageLoader.error();
    Toast.show('Tidak dapat terhubung ke server. Periksa koneksi internet Anda.', 'error', 8000);
});

document.body.addEventListener('htmx:timeout', function () {
    PageLoader.error();
    showErrorReport(408, 'Koneksi Timeout', 'Server tidak merespons dalam batas waktu yang ditentukan.', 'Periksa koneksi internet dan status server database.');
});

document.body.addEventListener('htmx:beforeRequest', function () {
    PageLoader.start();
});

document.body.addEventListener('htmx:afterSettle', function () {
    PageLoader.finish();
    if (window.lucide) {
        lucide.createIcons();
    }
});

// ── Initialize Lucide Icons ──────────────────────
document.addEventListener('DOMContentLoaded', function () {
    if (window.lucide) {
        lucide.createIcons();
    }

    // Auto-dismiss Django messages toasts
    var toasts = document.querySelectorAll('.toast-item');
    toasts.forEach(function (toast) {
        setTimeout(function () {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(function () { toast.remove(); }, 400);
        }, 5000);
    });
});

// ── Sidebar Toggle (Mobile) ─────────────────────
function toggleSidebar() {
    var sidebar = document.getElementById('sidebar');
    var backdrop = document.getElementById('sidebar-backdrop');
    if (sidebar) sidebar.classList.toggle('open');
    if (backdrop) backdrop.classList.toggle('open');
}

// ── HTMX CSRF Configuration ─────────────────────
document.body.addEventListener('htmx:configRequest', function (event) {
    var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfToken) {
        event.detail.headers['X-CSRFToken'] = csrfToken.value;
    }
});

// ── PWA Service Worker ───────────────────────────
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
        navigator.serviceWorker.register('/sw.js')
            .then(function (reg) { console.log('MantaHotel SW:', reg.scope); })
            .catch(function (err) { console.warn('MantaHotel SW failed:', err); });
    });
}
