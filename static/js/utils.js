// Helper bersama untuk halaman yang memuat data lewat AJAX (Projects, Experience).

// Data dari JSON tidak ikut di-escape otomatis oleh Django, jadi wajib di-escape sebelum masuk innerHTML.
function escapeHtml(value) {
    return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
}

// Mengambil nilai cookie, dipakai untuk mengirim header X-CSRFToken pada request POST.
function getCookie(name) {
    if (!document.cookie) return null;

    for (const cookie of document.cookie.split(';')) {
        const [key, ...rest] = cookie.trim().split('=');
        if (key === name) return decodeURIComponent(rest.join('='));
    }
    return null;
}
