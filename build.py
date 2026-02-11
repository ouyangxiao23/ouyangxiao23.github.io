#!/usr/bin/env python3
"""
build.py — Generates index.html from content.yaml

Usage:
    python build.py          Build index.html from content.yaml
    python build.py --init   Generate a blank content.yaml template
"""
import sys, html as html_mod, hashlib, time

try:
    import yaml
except ImportError:
    print("PyYAML is required. Install it with:  pip install pyyaml")
    sys.exit(1)

# ── SVG icon definitions (keyed by icon name in content.yaml) ─────────────
ICONS = {
    "email": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>',
    "github": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/></svg>',
    "cv": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>',
    "transcript": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/><path d="M8 7h6"/><path d="M8 11h8"/></svg>',
    "wechat": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 0 1 .213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.326.326 0 0 0 .167-.054l1.903-1.114a.864.864 0 0 1 .717-.098 10.16 10.16 0 0 0 2.837.403c.276 0 .543-.027.811-.05-.857-2.578.157-4.972 1.932-6.446 1.703-1.415 3.882-1.98 5.853-1.838-.576-3.583-4.196-6.348-8.596-6.348zM5.785 5.991c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178A1.17 1.17 0 0 1 4.623 7.17c0-.651.52-1.18 1.162-1.18zm5.813 0c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178 1.17 1.17 0 0 1-1.162-1.178c0-.651.52-1.18 1.162-1.18zm3.636 4.343c-2.554 0-4.884.955-6.308 2.544-1.313 1.467-1.737 3.4-.93 5.108.753 1.596 2.547 2.79 4.527 3.258a9.48 9.48 0 0 0 2.71.391c.768 0 1.544-.104 2.298-.313a.703.703 0 0 1 .583.08l1.544.904a.265.265 0 0 0 .136.044c.13 0 .236-.108.236-.24 0-.059-.023-.116-.039-.174l-.317-1.2a.481.481 0 0 1 .173-.54C21.847 19.36 24 17.59 24 15.41c0-2.93-3.139-5.078-8.766-5.078zm-2.833 2.27c.522 0 .944.43.944.96a.952.952 0 0 1-.944.958.952.952 0 0 1-.944-.957c0-.53.422-.96.944-.96zm4.727 0c.522 0 .944.43.944.96a.952.952 0 0 1-.944.958.952.952 0 0 1-.944-.957c0-.53.422-.96.944-.96z"/></svg>',
}


# ── Helpers ────────────────────────────────────────────────────────────────

def bi(val):
    """Wrap a bilingual value {en, zh} into paired spans. Pass-through for strings."""
    if isinstance(val, dict):
        return f'<span class="lang-en">{val["en"]}</span><span class="lang-zh">{val["zh"]}</span>'
    return str(val)


def bi_block(tag, cls, val):
    """Two block-level elements for en/zh."""
    return (
        f'<{tag} class="{cls} lang-en">{val["en"]}</{tag}>\n'
        f'                    <{tag} class="{cls} lang-zh">{val["zh"]}</{tag}>'
    )


# ── Section builders ──────────────────────────────────────────────────────

def build_stats(stats):
    parts = []
    for i, s in enumerate(stats):
        if i > 0:
            parts.append('                        <div class="stat-divider"></div>')
        unit = f'<span class="stat-unit">{s["unit"]}</span>' if s.get("unit") else ""
        parts.append(
            f'                        <div class="stat">\n'
            f'                            <span class="stat-value">{s["value"]}{unit}</span>\n'
            f'                            <span class="stat-label">{bi(s["label"])}</span>\n'
            f'                        </div>'
        )
    return "\n".join(parts)


def build_links(links):
    parts = []
    for lnk in links:
        icon_svg = ICONS.get(lnk["icon"], "")
        target = ' target="_blank" rel="noopener"' if not lnk["url"].startswith("mailto:") else ""
        label = bi(lnk["label"])
        protected = ' data-protected' if lnk.get("protected") else ""
        parts.append(
            f'                        <a href="{lnk["url"]}"{target}{protected} title="{lnk.get("title", "")}">\n'
            f'                            {icon_svg}\n'
            f'                            <span>{label}</span>\n'
            f'                        </a>'
        )
    return "\n".join(parts)


def build_research(research):
    en_paras = "\n                ".join(f"<p>{p}</p>" for p in research["en"])
    zh_paras = "\n                ".join(f"<p>{p}</p>" for p in research["zh"])
    return (
        f'            <div class="research-content lang-en">\n'
        f'                {en_paras}\n'
        f'            </div>\n'
        f'            <div class="research-content lang-zh">\n'
        f'                {zh_paras}\n'
        f'            </div>'
    )


def build_publications(pubs):
    items = []
    for pub in pubs:
        thumb_links = "\n                            ".join(
            f'<a href="{l["url"]}" class="pub-link" target="_blank" rel="noopener">{l["label"]}</a>'
            for l in pub.get("links", [])
        )
        eq = f'\n                        <p class="pub-equal">{pub["equal_contribution"]}</p>' if pub.get("equal_contribution") else ""
        items.append(
            f'                <div class="pub-item">\n'
            f'                    <div class="pub-thumb">\n'
            f'                        <img src="{pub["thumbnail"]}" alt="{html_mod.escape(pub["title"][:20])}" onerror="this.style.display=\'none\'; this.parentElement.classList.add(\'thumb-placeholder-active\');">\n'
            f'                        <div class="thumb-placeholder">\n'
            f'                            <svg viewBox="0 0 160 100" xmlns="http://www.w3.org/2000/svg">\n'
            f'                                <rect width="160" height="100" fill="#e9ecef" rx="4"/>\n'
            f'                                <text x="80" y="50" text-anchor="middle" dominant-baseline="middle" fill="#adb5bd" font-size="12" font-family="Inter, sans-serif">Paper</text>\n'
            f'                            </svg>\n'
            f'                        </div>\n'
            f'                    </div>\n'
            f'                    <div class="pub-details">\n'
            f'                        <h3 class="pub-title">\n'
            f'                            <a href="{pub["links"][0]["url"]}" target="_blank" rel="noopener">{pub["title"]}</a>\n'
            f'                        </h3>\n'
            f'                        <p class="pub-authors">{pub["authors"]}</p>{eq}\n'
            f'                        <p class="pub-venue">{pub["venue"]}</p>\n'
            f'                        <div class="pub-links">\n'
            f'                            {thumb_links}\n'
            f'                        </div>\n'
            f'                    </div>\n'
            f'                </div>'
        )
    return "\n".join(items)


def build_research_experience(exps):
    items = []
    for exp in exps:
        en_details = "\n                        ".join(f"<li>{d}</li>" for d in exp["details"]["en"])
        zh_details = "\n                        ".join(f"<li>{d}</li>" for d in exp["details"]["zh"])
        items.append(
            f'                <div class="resexp-item">\n'
            f'                    <div class="resexp-header">\n'
            f'                        <div>\n'
            f'                            <h3 class="resexp-role">{bi(exp["role"])}</h3>\n'
            f'                            <p class="resexp-org"><a href="{exp["org"]["url"]}" target="_blank" rel="noopener">{exp["org"]["name"]}</a>, {bi(exp["org"]["affiliation"])}</p>\n'
            f'                            <p class="resexp-advisor">{bi(exp["advisor"])}</p>\n'
            f'                        </div>\n'
            f'                        <span class="resexp-date">{exp["date"]}</span>\n'
            f'                    </div>\n'
            f'                    <ul class="resexp-details lang-en">\n'
            f'                        {en_details}\n'
            f'                    </ul>\n'
            f'                    <ul class="resexp-details lang-zh">\n'
            f'                        {zh_details}\n'
            f'                    </ul>\n'
            f'                </div>'
        )
    return "\n".join(items)


def build_honors(honors):
    items = []
    for h in honors:
        items.append(
            f'                <li>\n'
            f'                    <span class="honor-name">{bi(h["name"])}</span>\n'
            f'                    <span class="honor-note">{bi(h["note"])}</span>\n'
            f'                    <span class="honor-year">{h["year"]}</span>\n'
            f'                </li>'
        )
    return "\n".join(items)


def build_leadership(leaders, social_practice):
    items = []
    for l in leaders:
        items.append(
            f'                <div class="exp-item">\n'
            f'                    <div class="exp-header">\n'
            f'                        <span class="exp-role">{bi(l["role"])}</span>\n'
            f'                        <span class="exp-date">{l["date"]}</span>\n'
            f'                    </div>\n'
            f'                    {bi_block("p", "exp-desc", l["desc"])}\n'
            f'                </div>'
        )
    leader_html = "\n".join(items)

    sp_html = bi_block("p", "exp-desc", social_practice)

    return (
        f'            <div class="exp-category">\n'
        f'{leader_html}\n'
        f'            </div>\n\n'
        f'            <div class="exp-category">\n'
        f'                <h3 class="exp-heading"><span class="lang-en">Social Practice</span><span class="lang-zh">社会实践</span></h3>\n'
        f'                <div class="exp-item">\n'
        f'                    {sp_html}\n'
        f'                </div>\n'
        f'            </div>'
    )


# ── Main HTML assembly ────────────────────────────────────────────────────

def build_html(c):
    affil_en = "<br>".join(c["affiliation"]["en"])
    affil_zh = "<br>".join(c["affiliation"]["zh"])

    # Compute SHA-256 hash of the password for client-side verification
    password = c.get("password", "")
    pw_hash = hashlib.sha256(password.encode()).hexdigest() if password else ""

    # Cache-busting version string
    ver = str(int(time.time()))

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{c["name"]["en"]} | {c["affiliation"]["en"][-1]}</title>
    <meta name="description" content="{c["name"]["en"]} ({c["name"]["zh"]}) — {c["affiliation"]["en"][0]}, {c["affiliation"]["en"][-1]}">
    <meta name="keywords" content="{c["name"]["en"]}, {c["name"]["zh"]}, {c["affiliation"]["en"][-1]}, computer science, embodied intelligence, robotics">
    <meta property="og:title" content="{c["name"]["en"]} | {c["affiliation"]["en"][-1]}">
    <meta property="og:description" content="{c["affiliation"]["en"][0]} at {c["affiliation"]["en"][-1]}">
    <meta property="og:type" content="website">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="style.css?v={ver}">
</head>
<body>
    <script>
    (function(){{var t=localStorage.getItem('theme');if(t==='dark'||(!t&&window.matchMedia('(prefers-color-scheme:dark)').matches))document.body.classList.add('dark');}})();
    </script>

    <!-- Navigation -->
    <nav class="navbar" id="navbar">
        <div class="nav-content">
            <a href="#about" class="nav-name">
                <span class="lang-en">{c["name"]["en"]}</span>
                <span class="lang-zh">{c["name"]["zh"]}</span>
            </a>
            <div class="nav-right">
                <button class="lang-toggle" id="lang-toggle" aria-label="Switch language">
                    <span class="lang-opt" data-lang="en">EN</span>
                    <span class="lang-sep">/</span>
                    <span class="lang-opt" data-lang="zh">中</span>
                </button>
                <button class="theme-toggle" id="theme-toggle" aria-label="Toggle dark mode">
                    <svg class="icon-sun" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
                    <svg class="icon-moon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
                </button>
                <button class="nav-toggle" id="nav-toggle" aria-label="Toggle navigation">
                    <span></span>
                    <span></span>
                    <span></span>
                </button>
            </div>
            <ul class="nav-links" id="nav-links">
                <li><a href="#about"><span class="lang-en">About</span><span class="lang-zh">关于</span></a></li>
                <li><a href="#research"><span class="lang-en">Research</span><span class="lang-zh">研究</span></a></li>
                <li><a href="#publications"><span class="lang-en">Publications</span><span class="lang-zh">论文发表</span></a></li>
                <li><a href="#resexp"><span class="lang-en">Experience</span><span class="lang-zh">研究经历</span></a></li>
                <li><a href="#honors"><span class="lang-en">Honors</span><span class="lang-zh">荣誉</span></a></li>
                <li><a href="#experience"><span class="lang-en">Leadership</span><span class="lang-zh">学生工作</span></a></li>
            </ul>
        </div>
    </nav>

    <!-- Hero / About -->
    <section class="hero" id="about">
        <div class="container">
            <div class="hero-content">
                <div class="hero-photo">
                    <img src="assets/profile.jpg" alt="{c["name"]["en"]}" onerror="this.style.display='none'; this.parentElement.classList.add('placeholder-active');">
                    <div class="photo-placeholder">
                        <svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
                            <rect width="120" height="120" fill="#e9ecef"/>
                            <circle cx="60" cy="45" r="20" fill="#adb5bd"/>
                            <ellipse cx="60" cy="100" rx="35" ry="25" fill="#adb5bd"/>
                        </svg>
                    </div>
                </div>
                <div class="hero-text">
                    <h1>
                        <span class="lang-en">{c["name"]["en"]} <span class="name-cn">({c["name"]["zh"]})</span></span>
                        <span class="lang-zh">{c["name"]["zh"]} <span class="name-cn">({c["name"]["en"]})</span></span>
                    </h1>
                    <p class="hero-affiliation lang-en">{affil_en}</p>
                    <p class="hero-affiliation lang-zh">{affil_zh}</p>
                    <p class="hero-tagline lang-en">{c["tagline"]["en"]}</p>
                    <p class="hero-tagline lang-zh">{c["tagline"]["zh"]}</p>
                    <div class="hero-stats">
{build_stats(c["stats"])}
                    </div>
                    <div class="icon-row">
{build_links(c["links"])}
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Research -->
    <section class="section section-alt" id="research">
        <div class="container">
            <h2 class="section-title">
                <span class="lang-en">Research</span>
                <span class="lang-zh">研究方向</span>
            </h2>
{build_research(c["research"])}
        </div>
    </section>

    <!-- Publications -->
    <section class="section" id="publications">
        <div class="container">
            <h2 class="section-title">
                <span class="lang-en">Publications</span>
                <span class="lang-zh">论文发表</span>
            </h2>
            <div class="pub-list">
{build_publications(c["publications"])}
            </div>
        </div>
    </section>

    <!-- Research Experience -->
    <section class="section section-alt" id="resexp">
        <div class="container">
            <h2 class="section-title">
                <span class="lang-en">Research Experience</span>
                <span class="lang-zh">研究经历</span>
            </h2>
            <div class="resexp-list">
{build_research_experience(c["research_experience"])}
            </div>
        </div>
    </section>

    <!-- Honors & Awards -->
    <section class="section" id="honors">
        <div class="container">
            <h2 class="section-title">
                <span class="lang-en">Honors &amp; Awards</span>
                <span class="lang-zh">荣誉与奖项</span>
            </h2>
            <ul class="honors-list">
{build_honors(c["honors"])}
            </ul>
        </div>
    </section>

    <!-- Leadership & Service -->
    <section class="section section-alt" id="experience">
        <div class="container">
            <h2 class="section-title">
                <span class="lang-en">Leadership &amp; Service</span>
                <span class="lang-zh">学生工作与社会实践</span>
            </h2>

{build_leadership(c["leadership"], c["social_practice"])}
        </div>
    </section>

    <!-- Footer -->
    <footer class="footer" id="contact">
        <div class="container">
            <p>
                <span class="lang-en">{c["name"]["en"]}</span>
                <span class="lang-zh">{c["name"]["zh"]}</span>
                &middot; {c["email"]}
            </p>
            <p class="footer-update">{bi(c["last_updated"])}</p>
        </div>
    </footer>

    <!-- Password Modal -->
    <div class="pw-overlay" id="pw-overlay">
        <div class="pw-modal">
            <p class="pw-title">
                <span class="lang-en">This file is password-protected</span>
                <span class="lang-zh">此文件需要密码访问</span>
            </p>
            <input type="password" class="pw-input" id="pw-input"
                   placeholder="Enter password" autocomplete="off">
            <p class="pw-error" id="pw-error">
                <span class="lang-en">Incorrect password</span>
                <span class="lang-zh">密码错误</span>
            </p>
            <div class="pw-actions">
                <button class="pw-btn pw-cancel" id="pw-cancel">
                    <span class="lang-en">Cancel</span>
                    <span class="lang-zh">取消</span>
                </button>
                <button class="pw-btn pw-submit" id="pw-submit">
                    <span class="lang-en">Submit</span>
                    <span class="lang-zh">确认</span>
                </button>
            </div>
        </div>
    </div>

    <script>window.__pwHash="{pw_hash}";</script>
    <script src="main.js?v={ver}"></script>
</body>
</html>
'''


# ── --init: generate blank content.yaml ───────────────────────────────────

TEMPLATE_YAML = '''\
# ============================================================
# Site Content — Edit this file, then run: python build.py
# ============================================================

# -- Personal Info --
name:
  en: "Your Name"
  zh: "你的中文名"

affiliation:
  en:
    - "Year & Degree"           # e.g. "3rd Year Undergraduate"
    - "Department"              # e.g. "Department of Computer Science"
    - "University"              # e.g. "Tsinghua University"
  zh:
    - "年级与学位"
    - "院系"
    - "大学"

tagline:
  en: "One-sentence research description. HTML links allowed."
  zh: "一句话研究简介，支持HTML链接。"

# -- Academic Stats (add/remove items as needed) --
stats:
  - value: "0.00"
    unit: "/4.0"
    label: { en: "GPA", zh: "GPA" }
  - value: "Top X%"
    unit: " (rank/total)"
    label: { en: "Rank", zh: "排名" }

# -- Contact & Links --
email: "your@email.edu"

# Password to protect sensitive links (leave empty to disable)
password: ""

links:
  # icon options: email, github, cv, transcript, wechat
  # add "protected: true" to require password
  - icon: "email"
    url: "mailto:your@email.edu"
    label: "Email"
  - icon: "github"
    url: "https://github.com/yourusername"
    label: "GitHub"
  - icon: "cv"
    url: "assets/CV.pdf"
    label: "CV"
    protected: true
  - icon: "transcript"
    url: "assets/Transcript.pdf"
    label: { en: "Transcript", zh: "成绩单" }
    protected: true
  - icon: "wechat"
    url: "assets/wechat-qr.jpg"
    label: { en: "WeChat", zh: "微信" }
    protected: true

# -- Research Interests (list of paragraphs, HTML allowed) --
research:
  en:
    - "Paragraph 1: your research vision."
    - "Paragraph 2: current work."
    - "Paragraph 3: future direction."
  zh:
    - "段落1：研究愿景。"
    - "段落2：当前工作。"
    - "段落3：未来方向。"

# -- Publications (content stays in English) --
publications:
  - title: "Paper Title"
    authors: "Author1*, Author2*, <strong>Your Name</strong>, Advisor"
    equal_contribution: "* Equal Contribution"   # remove this line if not applicable
    venue: "Conference/Journal, Year"
    thumbnail: "assets/paper-thumb.jpg"
    links:
      - label: "arXiv"
        url: "https://arxiv.org/abs/XXXX.XXXXX"
      - label: "Project Page"
        url: "https://project-url.github.io/"
      - label: "Code"
        url: "https://github.com/org/repo"

# -- Research Experience --
research_experience:
  - role: { en: "Student Researcher", zh: "本科生研究员" }
    org:
      name: "Lab Name"
      url: "https://lab-url.edu/"
      affiliation: { en: "Department, University", zh: "院系，大学" }
    advisor:
      en: "Advised by <a href=\\"\\" >Prof. Name</a>"
      zh: "导师：<a href=\\"\\" >某教授</a>"
    date: "20XX – Present"
    details:
      en:
        - "What you explored or built."
        - "Another contribution."
      zh:
        - "你探索或构建了什么。"
        - "另一项贡献。"

# -- Honors & Awards --
honors:
  - name: { en: "Award Name", zh: "奖项名称" }
    note: { en: "Context for international readers", zh: "中文备注" }
    year: "20XX"

# -- Leadership & Service --
leadership:
  - role: { en: "Role, Organization", zh: "职务，组织" }
    date: "20XX – 20XX"
    desc: { en: "What you did.", zh: "你做了什么。" }

social_practice:
  en: "Summary of social practice activities."
  zh: "社会实践活动总结。"

# -- Footer --
last_updated: { en: "Last updated: Month Year", zh: "最后更新：XXXX年X月" }
'''


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    if "--init" in sys.argv:
        with open("content.yaml", "w", encoding="utf-8") as f:
            f.write(TEMPLATE_YAML)
        print("Created blank content.yaml — fill it in, then run: python build.py")
        return

    try:
        with open("content.yaml", "r", encoding="utf-8") as f:
            content = yaml.safe_load(f)
    except FileNotFoundError:
        print("content.yaml not found. Run 'python build.py --init' to generate a template.")
        sys.exit(1)

    html = build_html(content)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("Built index.html from content.yaml")


if __name__ == "__main__":
    main()
