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
