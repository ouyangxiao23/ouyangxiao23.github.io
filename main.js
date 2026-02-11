// Sticky nav shadow on scroll
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 10);
}, { passive: true });

// Mobile menu toggle
const navToggle = document.getElementById('nav-toggle');
const navLinks = document.getElementById('nav-links');

navToggle.addEventListener('click', () => {
    navToggle.classList.toggle('open');
    navLinks.classList.toggle('open');
});

// Close mobile menu on link click
navLinks.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
        navToggle.classList.remove('open');
        navLinks.classList.remove('open');
    });
});

// Active nav link highlighting via IntersectionObserver
const sections = document.querySelectorAll('section[id], .hero[id]');
const navItems = document.querySelectorAll('.nav-links a');

const observerOptions = {
    rootMargin: '-80px 0px -60% 0px',
    threshold: 0
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const id = entry.target.getAttribute('id');
            navItems.forEach(item => {
                item.classList.toggle('active', item.getAttribute('href') === `#${id}`);
            });
        }
    });
}, observerOptions);

sections.forEach(section => observer.observe(section));

// Language toggle
const langToggle = document.getElementById('lang-toggle');
const langOpts = langToggle.querySelectorAll('.lang-opt');

function setLang(lang) {
    document.body.classList.toggle('zh', lang === 'zh');
    document.documentElement.lang = lang;
    langOpts.forEach(opt => {
        opt.classList.toggle('active', opt.dataset.lang === lang);
    });
    localStorage.setItem('lang', lang);
}

// Restore saved language preference
const savedLang = localStorage.getItem('lang');
if (savedLang) {
    setLang(savedLang);
} else {
    // Default to English, mark EN as active
    langOpts.forEach(opt => {
        opt.classList.toggle('active', opt.dataset.lang === 'en');
    });
}

langToggle.addEventListener('click', () => {
    const isZh = document.body.classList.contains('zh');
    setLang(isZh ? 'en' : 'zh');
});

// Dark mode toggle
const themeToggle = document.getElementById('theme-toggle');

function setTheme(dark) {
    document.body.classList.toggle('dark', dark);
    localStorage.setItem('theme', dark ? 'dark' : 'light');
}

// Restore saved theme, or use system preference
const savedTheme = localStorage.getItem('theme');
if (savedTheme) {
    setTheme(savedTheme === 'dark');
} else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    setTheme(true);
}

themeToggle.addEventListener('click', () => {
    setTheme(!document.body.classList.contains('dark'));
});

// Password protection for sensitive links
(() => {
    const overlay = document.getElementById('pw-overlay');
    const input = document.getElementById('pw-input');
    const error = document.getElementById('pw-error');
    const submitBtn = document.getElementById('pw-submit');
    const cancelBtn = document.getElementById('pw-cancel');
    const expectedHash = window.__pwHash;
    let pendingUrl = null;

    if (!overlay || !expectedHash) return;

    async function sha256(text) {
        const data = new TextEncoder().encode(text);
        const buf = await crypto.subtle.digest('SHA-256', data);
        return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('');
    }

    function openModal(url) {
        pendingUrl = url;
        input.value = '';
        error.classList.remove('visible');
        overlay.classList.add('open');
        setTimeout(() => input.focus(), 50);
    }

    function closeModal() {
        overlay.classList.remove('open');
        pendingUrl = null;
    }

    async function submit() {
        const hash = await sha256(input.value);
        if (hash === expectedHash) {
            sessionStorage.setItem('pw_ok', '1');
            closeModal();
            if (pendingUrl) window.open(pendingUrl, '_blank');
        } else {
            error.classList.add('visible');
            input.select();
        }
    }

    document.querySelectorAll('a[data-protected]').forEach(link => {
        link.addEventListener('click', e => {
            if (sessionStorage.getItem('pw_ok')) return;
            e.preventDefault();
            openModal(link.href);
        });
    });

    submitBtn.addEventListener('click', submit);
    cancelBtn.addEventListener('click', closeModal);
    input.addEventListener('keydown', e => { if (e.key === 'Enter') submit(); });
    overlay.addEventListener('click', e => { if (e.target === overlay) closeModal(); });
})();
