import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, date
import sys, os, math, json, calendar

sys.path.insert(0, os.path.dirname(__file__))
from tarot_reader import (
    life_path_number, get_sun_sign, draw_cards,
    CARDS, SIGN_CARD_AFFINITIES,
    ALL_TEMPLATES, ALL_TEMPLATES_REV, _sentence_fragment, _reversed_keywords,
    compute_weights_debug,
)

st.set_page_config(page_title="Tarot", page_icon="✦",
                   layout="centered", initial_sidebar_state="collapsed")

# ─────────────────────────────────────────────
#  CARD SVG
# ─────────────────────────────────────────────
ROMAN = ["0","I","II","III","IV","V","VI","VII","VIII","IX","X",
         "XI","XII","XIII","XIV","XV","XVI","XVII","XVIII","XIX","XX","XXI"]

SUIT_COLORS = {
    "Wands":     "#a0734a",   # warm brown-amber
    "Cups":      "#5a7f8a",   # muted teal
    "Swords":    "#7a8672",   # sage grey
    "Pentacles": "#6b7f5e",   # sage green
    "":          "#7a6548",   # warm brown (Major)
}

def card_svg_str(card, is_reversed=False, w=180, h=280):
    element = card.get("element", "earth")
    suit    = card.get("suit", "")
    arcana  = card.get("arcana", "")
    num     = card.get("number", 0)
    roman   = ROMAN[min(num, 21)]
    name    = card["name"]
    rot     = f'transform="rotate(180,{w//2},{h//2})"' if is_reversed else ""

    # All cards: tinted background based on suit
    SUIT_BG = {
        "Wands":     "#faf6f2",   # warm cream
        "Cups":      "#f2f6f7",   # cool sage-blue
        "Swords":    "#f4f5f2",   # neutral sage
        "Pentacles": "#f2f5f0",   # green-cream
        "":          "#f7f5f0",   # warm brown-cream (Major)
    }
    bg  = SUIT_BG.get(suit, "#f4f5f0")
    ink = "#2c3328"
    accent = SUIT_COLORS.get(suit, "#7a6548")

    def x(v): return round(v * w / 200, 1)
    def y(v): return round(v * h / 280, 1)

    # Element label top-left, suit top-right (with accent color)
    header = (
        f'<text x="{x(18)}" y="{y(22)}" font-family="Manrope,sans-serif" font-size="{x(5.5)}" '
        f'fill="{accent}" opacity="0.7" letter-spacing="1">{element.upper()}</text>'
        f'<text x="{w-x(18)}" y="{y(22)}" text-anchor="end" font-family="Manrope,sans-serif" '
        f'font-size="{x(5.5)}" fill="{accent}" opacity="0.7" letter-spacing="1">'
        f'{"MAJOR" if not suit else suit.upper()}</text>'
        f'<line x1="{x(12)}" y1="{y(30)}" x2="{w-x(12)}" y2="{y(30)}" '
        f'stroke="{accent}" stroke-width="{x(0.4)}" opacity="0.2"/>'
    )

    if arcana == "Major":
        spokes = "".join(
            f'<line x1="{x(100)}" y1="{y(148)}" '
            f'x2="{x(100+56*math.cos(math.radians(i*30)))}" '
            f'y2="{y(148+56*math.sin(math.radians(i*30)))}" '
            f'stroke="{ink}" stroke-width="{x(0.5)}" opacity="0.07"/>'
            for i in range(12))
        illus = (
            f'<g {rot}>{spokes}'
            f'<circle cx="{x(100)}" cy="{y(148)}" r="{x(54)}" fill="none" stroke="{ink}" stroke-width="{x(0.9)}"/>'
            f'<circle cx="{x(100)}" cy="{y(148)}" r="{x(38)}" fill="none" stroke="{ink}" stroke-width="{x(0.4)}" opacity="0.35"/>'
            f'<text x="{x(100)}" y="{y(156)}" text-anchor="middle" font-family="Georgia,serif" '
            f'font-size="{x(22)}" fill="{ink}" opacity="0.8">{roman}</text>'
            f'</g>'
        )
    elif suit == "Wands":
        illus = (
            f'<g {rot}>'
            f'<line x1="{x(100)}" y1="{y(82)}" x2="{x(100)}" y2="{y(208)}" stroke="{ink}" stroke-width="{x(1.5)}" stroke-linecap="round"/>'
            f'<line x1="{x(76)}" y1="{y(114)}" x2="{x(124)}" y2="{y(114)}" stroke="{ink}" stroke-width="{x(0.9)}" stroke-linecap="round" opacity="0.5"/>'
            f'<line x1="{x(82)}" y1="{y(148)}" x2="{x(118)}" y2="{y(148)}" stroke="{ink}" stroke-width="{x(0.7)}" stroke-linecap="round" opacity="0.35"/>'
            f'<circle cx="{x(100)}" cy="{y(82)}" r="{x(3.5)}" fill="{ink}" opacity="0.7"/>'
            f'</g>'
        )
    elif suit == "Cups":
        illus = (
            f'<g {rot}>'
            f'<path d="M{x(76)} {y(100)} Q{x(70)} {y(140)} {x(80)} {y(164)} '
            f'Q{x(90)} {y(182)} {x(100)} {y(185)} Q{x(110)} {y(182)} {x(120)} {y(164)} '
            f'Q{x(130)} {y(140)} {x(124)} {y(100)} Z" '
            f'fill="none" stroke="{ink}" stroke-width="{x(1.2)}"/>'
            f'<line x1="{x(76)}" y1="{y(100)}" x2="{x(124)}" y2="{y(100)}" stroke="{ink}" stroke-width="{x(1.2)}"/>'
            f'<line x1="{x(100)}" y1="{y(185)}" x2="{x(100)}" y2="{y(202)}" stroke="{ink}" stroke-width="{x(1.2)}"/>'
            f'<line x1="{x(84)}" y1="{y(202)}" x2="{x(116)}" y2="{y(202)}" stroke="{ink}" stroke-width="{x(1.2)}"/>'
            f'</g>'
        )
    elif suit == "Swords":
        illus = (
            f'<g {rot}>'
            f'<line x1="{x(100)}" y1="{y(78)}" x2="{x(100)}" y2="{y(200)}" stroke="{ink}" stroke-width="{x(1.0)}"/>'
            f'<polygon points="{x(100)},{y(78)} {x(105)},{y(112)} {x(100)},{y(120)} {x(95)},{y(112)}" '
            f'fill="{ink}" fill-opacity="0.12" stroke="{ink}" stroke-width="{x(0.8)}"/>'
            f'<line x1="{x(76)}" y1="{y(160)}" x2="{x(124)}" y2="{y(160)}" stroke="{ink}" stroke-width="{x(1.0)}"/>'
            f'<rect x="{x(95)}" y="{y(199)}" width="{x(10)}" height="{y(16)}" rx="{x(3)}" '
            f'fill="{ink}" fill-opacity="0.3" stroke="{ink}" stroke-width="{x(0.8)}"/>'
            f'</g>'
        )
    elif suit == "Pentacles":
        pts  = [(x(100+40*math.cos(math.radians(i*72-90))),
                 y(148+40*math.sin(math.radians(i*72-90)))) for i in range(5)]
        star = " ".join(f"{pts[(i*2)%5][0]},{pts[(i*2)%5][1]}" for i in range(5))
        illus = (
            f'<g {rot}>'
            f'<circle cx="{x(100)}" cy="{y(148)}" r="{x(46)}" fill="none" stroke="{ink}" stroke-width="{x(0.9)}"/>'
            f'<polygon points="{star}" fill="{ink}" fill-opacity="0.07" stroke="{ink}" '
            f'stroke-width="{x(0.9)}" stroke-linejoin="round"/>'
            f'</g>'
        )
    else:
        illus = ""

    disp_name = name if len(name) <= 22 else name[:20] + "…"

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
        f'<rect width="{w}" height="{h}" rx="{x(9)}" fill="{bg}"/>'
        f'<rect x="{x(6)}" y="{y(6)}" width="{w-x(12)}" height="{h-y(12)}" '
        f'rx="{x(6)}" fill="none" stroke="{accent}" stroke-width="{x(0.5)}" opacity="0.25"/>'
        f'{header}'
        f'{illus}'
        f'<line x1="{x(22)}" y1="{y(232)}" x2="{x(178)}" y2="{y(232)}" '
        f'stroke="{accent}" stroke-width="{x(0.5)}" opacity="0.2"/>'
        f'<text x="{x(100)}" y="{h-y(12)}" text-anchor="middle" font-family="Manrope,sans-serif" '
        f'font-size="{x(7.5)}" fill="{ink}" opacity="0.8" font-weight="500">{disp_name}</text>'
        f'</svg>'
    )


def back_svg_str(w=180, h=280):
    cx = w // 2
    def x(v): return round(v * w / 200, 1)
    def y(v): return round(v * h / 280, 1)
    rings = "".join(
        f'<circle cx="{cx}" cy="{y(140)}" r="{x(r)}" fill="none" '
        f'stroke="#95a88a" stroke-width="{x(0.5)}" opacity="{0.15 + i*0.07}"/>'
        for i, r in enumerate([70, 55, 40, 26, 13])
    )
    spokes = "".join(
        f'<line x1="{cx}" y1="{y(70)}" x2="{cx}" y2="{y(210)}" '
        f'stroke="#95a88a" stroke-width="{x(0.3)}" opacity="0.1" '
        f'transform="rotate({i*30},{cx},{y(140)})"/>'
        for i in range(6)
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
        f'<rect width="{w}" height="{h}" rx="{x(9)}" fill="#1a2118"/>'
        f'<defs><radialGradient id="rg" cx="50%" cy="50%" r="55%">'
        f'<stop offset="0%" stop-color="#95a88a" stop-opacity="0.12"/>'
        f'<stop offset="100%" stop-color="#1a2118" stop-opacity="0"/>'
        f'</radialGradient></defs>'
        f'<rect width="{w}" height="{h}" rx="{x(9)}" fill="url(#rg)"/>'
        f'<rect x="{x(7)}" y="{y(7)}" width="{w-x(14)}" height="{h-y(14)}" '
        f'rx="{x(6)}" fill="none" stroke="#95a88a" stroke-width="{x(0.7)}" opacity="0.3"/>'
        f'{rings}{spokes}'
        f'<circle cx="{cx}" cy="{y(140)}" r="{x(5)}" fill="#95a88a" opacity="0.5"/>'
        f'<circle cx="{cx}" cy="{y(140)}" r="{x(2)}" fill="#95a88a" opacity="0.9"/>'
        f'</svg>'
    )


# ─────────────────────────────────────────────
#  TRANSLATIONS
# ─────────────────────────────────────────────
T = {
    "en": {
        "step1_q":    "What is your name?",
        "step1_ph":   "Your name",
        "step1_btn":  "Continue",
        "step2_q":    "When were you born?",
        "step2_btn":  "Continue",
        "step3_q":    "What do you wish to know?",
        "step3_ph":   "Write your question freely",
        "step3_btn":  "Read the cards",
        "btn_land":   "Begin",
        "choose":     "Draw three cards from the spread",
        "cards_left": ["2 remaining", "1 remaining", "The reading begins"],
        "your_reading": "Your Reading",
        "pos":        ["Past", "Present", "Future"],
        "pos_sub":    ["Foundation", "Challenge", "Outcome"],
        "upright":    "Upright", "reversed": "Reversed",
        "why":        "Why this card",
        "new":        "Start over",
        "months":     ["Jan","Feb","Mar","Apr","May","Jun",
                       "Jul","Aug","Sep","Oct","Nov","Dec"],
        "tagline":    "A personalised reading from 78 cards",
        "back":       "Back",
        "q_suggest":  ["What does my love life hold?", "Will my career change?", "What should I focus on?", "General fortune"],
        "q_or":       "or type your own",
        "q_custom":   "✎ Write my own question…",
        "q_default":  "What does the universe want me to know?",
    },
    "zh": {
        "step1_q":    "您叫什么名字？",
        "step1_ph":   "请输入您的姓名",
        "step1_btn":  "继续",
        "step2_q":    "您的出生日期是？",
        "step2_btn":  "继续",
        "step3_q":    "您想询问什么？",
        "step3_ph":   "请自由书写您的问题",
        "step3_btn":  "开始解读",
        "btn_land":   "开始",
        "choose":     "从牌阵中抽取三张牌",
        "cards_left": ["还剩2张", "还剩1张", "解读即将开始"],
        "your_reading": "您的解读",
        "pos":        ["过去", "现在", "未来"],
        "pos_sub":    ["基础", "挑战", "结果"],
        "upright":    "正位", "reversed": "逆位",
        "why":        "为什么是这张牌",
        "new":        "重新开始",
        "months":     ["1月","2月","3月","4月","5月","6月",
                       "7月","8月","9月","10月","11月","12月"],
        "tagline":    "来自七十八张牌的个人化解读",
        "back":       "返回",
        "q_suggest":  ["我的感情运势如何？", "事业会有变化吗？", "我应该关注什么？", "整体运势"],
        "q_or":       "或输入您自己的问题",
        "q_custom":   "✎ 输入自定义问题…",
        "q_default":  "宇宙想让我知道什么？",
    },
}

SIGN_ZH = {
    "aries":"白羊座","taurus":"金牛座","gemini":"双子座","cancer":"巨蟹座",
    "leo":"狮子座","virgo":"处女座","libra":"天秤座","scorpio":"天蝎座",
    "sagittarius":"射手座","capricorn":"摩羯座","aquarius":"水瓶座","pisces":"双鱼座",
}

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
defaults = {
    'slide': 'landing',
    'form_step': 0,
    'lang': 'en',
    'drawn': None,
    'user': {},
    'tmp_name': '',
    'tmp_birthdate': '',
    'tmp_question': '',
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

lang = st.session_state.lang
tr   = T[lang]

# ─────────────────────────────────────────────
#  GLOBAL CSS (imported from _css_block.py)
# ─────────────────────────────────────────────
from _css_block import CSS_ALL
st.markdown(CSS_ALL, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def lang_toggle():
    st.markdown('<div class="small-btn">', unsafe_allow_html=True)
    if st.button("中文" if lang == "en" else "EN", key=f"lang_{st.session_state.slide}_{st.session_state.form_step}"):
        st.session_state.lang = "zh" if lang == "en" else "en"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SLIDE 1 — LANDING (pure Streamlit, no iframe)
# ─────────────────────────────────────────────
if st.session_state.slide == 'landing':

    st.markdown('<div style="height:5rem"></div>', unsafe_allow_html=True)

    # Subtle animated glow behind title
    st.markdown('<div class="landing-glow"></div>', unsafe_allow_html=True)

    # Title
    st.markdown(
        '<h1 style="font-family:\'Manrope\',sans-serif;font-weight:200;font-size:2.4rem;'
        'color:#2c3328;letter-spacing:0.22em;text-transform:uppercase;text-align:center;'
        'margin:0 0 0.8rem 0;position:relative;z-index:1;">Tarot</h1>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div style="width:50px;height:1px;background:rgba(107,127,94,0.4);margin:0 auto 0.8rem;"></div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<p style="font-family:\'Manrope\',sans-serif;font-weight:400;font-size:0.78rem;'
        f'color:#7a8672;letter-spacing:0.12em;text-transform:uppercase;text-align:center;'
        f'margin:0 0 3rem 0;">{tr["tagline"]}</p>',
        unsafe_allow_html=True
    )

    # Begin button (primary)
    st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
    if st.button(tr["btn_land"], key="begin_btn"):
        st.session_state.slide = 'form'
        st.session_state.form_step = 0
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:0.6rem"></div>', unsafe_allow_html=True)

    # Browse button (ghost — default style)
    st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
    if st.button("Browse all 78 cards" if lang == "en" else "浏览全部78张牌", key="browse_btn"):
        st.session_state.slide = 'browse'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:1.2rem"></div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;">', unsafe_allow_html=True)
    lang_toggle()
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  SLIDE — BROWSE ALL CARDS
# ─────────────────────────────────────────────
elif st.session_state.slide == 'browse':

    c1, c2, c3 = st.columns([1, 4, 1])
    with c1:
        st.markdown('<div class="small-btn">', unsafe_allow_html=True)
        if st.button(tr["back"], key="back_browse"):
            st.session_state.slide = 'landing'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        '<h2 style="font-family:\'Manrope\',sans-serif;font-weight:300;font-size:1.4rem;'
        'color:#2c3328;letter-spacing:0.12em;text-transform:uppercase;text-align:center;'
        'margin:0.5rem 0 2rem;">The 78 Cards</h2>',
        unsafe_allow_html=True
    )

    # Group by arcana/suit
    groups = [
        ("Major Arcana", [c for c in CARDS if c["arcana"] == "Major"]),
        ("Wands", [c for c in CARDS if c.get("suit") == "Wands"]),
        ("Cups", [c for c in CARDS if c.get("suit") == "Cups"]),
        ("Swords", [c for c in CARDS if c.get("suit") == "Swords"]),
        ("Pentacles", [c for c in CARDS if c.get("suit") == "Pentacles"]),
    ]

    for group_name, group_cards in groups:
        accent = SUIT_COLORS.get(group_name.split()[-1] if group_name != "Major Arcana" else "", "#7a6548")
        st.markdown(
            f'<div style="font-family:\'Manrope\',sans-serif;font-weight:600;font-size:0.75rem;'
            f'color:{accent};letter-spacing:0.1em;text-transform:uppercase;'
            f'margin:1.5rem 0 0.8rem;border-bottom:1px solid {accent}22;padding-bottom:0.4rem;">'
            f'{group_name}</div>',
            unsafe_allow_html=True
        )

        # Display cards in a grid — 4 per row
        cols_per_row = 4
        for row_start in range(0, len(group_cards), cols_per_row):
            row_cards = group_cards[row_start:row_start + cols_per_row]
            cols = st.columns(cols_per_row)
            for j, card in enumerate(row_cards):
                with cols[j]:
                    svg = card_svg_str(card, w=140, h=218)
                    st.markdown(svg, unsafe_allow_html=True)
                    st.markdown(
                        f'<div style="font-family:\'Manrope\',sans-serif;font-size:0.68rem;'
                        f'font-weight:500;color:#2c3328;text-align:center;margin:0.3rem 0 0;">'
                        f'{card["name"]}</div>'
                        f'<div style="font-family:\'Manrope\',sans-serif;font-size:0.6rem;'
                        f'font-weight:300;color:#7a8672;text-align:center;line-height:1.5;'
                        f'margin:0.2rem 0 0.8rem;">'
                        f'{card["upright_meaning"]}</div>',
                        unsafe_allow_html=True
                    )


# ─────────────────────────────────────────────
#  SLIDE 2 — FORM (step-by-step wizard)
# ─────────────────────────────────────────────
elif st.session_state.slide == 'form':

    step = st.session_state.form_step

    # Top bar: back + lang
    c1, c2, c3 = st.columns([1, 4, 1])
    with c1:
        st.markdown('<div class="small-btn">', unsafe_allow_html=True)
        if st.button(tr["back"], key="back_form"):
            if step == 0:
                st.session_state.slide = 'landing'
            else:
                st.session_state.form_step = step - 1
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        lang_toggle()

    # Step progress indicator (dots)
    dots_html = ""
    for i in range(3):
        if i < step:
            dot = f'<span style="width:8px;height:8px;border-radius:50%;background:#3d4f35;display:inline-block;"></span>'
        elif i == step:
            dot = f'<span style="width:8px;height:8px;border-radius:50%;background:#6b7f5e;display:inline-block;"></span>'
        else:
            dot = f'<span style="width:8px;height:8px;border-radius:50%;background:rgba(44,51,40,0.15);display:inline-block;"></span>'
        dots_html += dot
    st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:center;gap:8px;margin:1.2rem 0 2rem;">
  {dots_html}
  <span style="font-family:'Manrope',sans-serif;font-size:0.68rem;font-weight:400;color:#7a8672;letter-spacing:0.05em;margin-left:4px;">
    {step + 1} / 3
  </span>
</div>
""", unsafe_allow_html=True)

    # ── Step 0: Name ──
    if step == 0:
        st.markdown(
            f'<p style="font-family:\'Manrope\',sans-serif;font-size:1.3rem;'
            f'font-weight:300;color:#2c3328;margin-bottom:1.5rem;letter-spacing:0.02em;">'
            f'{tr["step1_q"]}</p>',
            unsafe_allow_html=True
        )
        name = st.text_input("name", value=st.session_state.tmp_name,
                              placeholder=tr["step1_ph"], label_visibility="collapsed")
        st.markdown('<div style="height:1.5rem"></div>', unsafe_allow_html=True)
        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        if st.button(tr["step1_btn"], key="step1_btn"):
            if not name.strip():
                st.warning("Please enter your name." if lang == "en" else "请输入您的姓名。")
            else:
                st.session_state.tmp_name = name.strip()
                st.session_state.form_step = 1
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Step 1: Date of Birth ──
    elif step == 1:
        st.markdown(
            f'<p style="font-family:\'Manrope\',sans-serif;font-size:1.3rem;'
            f'font-weight:300;color:#2c3328;margin-bottom:1.5rem;letter-spacing:0.02em;">'
            f'{tr["step2_q"]}</p>',
            unsafe_allow_html=True
        )
        dc1, dc2, dc3 = st.columns([1, 1.4, 1.6])
        with dc1: birth_day = st.selectbox("d", range(1, 32), label_visibility="collapsed")
        with dc2: birth_month_str = st.selectbox("m", tr["months"], label_visibility="collapsed")
        with dc3:
            cy = date.today().year
            years = list(range(cy, 1899, -1))
            # Default to ~1995 (index ~31) instead of current year
            default_idx = min(cy - 1995, len(years) - 1)
            birth_year = st.selectbox("y", years, index=default_idx, label_visibility="collapsed")
        month_num = tr["months"].index(birth_month_str) + 1
        birth_day = min(birth_day, calendar.monthrange(birth_year, month_num)[1])
        birthdate = f"{birth_year}-{month_num:02d}-{birth_day:02d}"
        st.markdown('<div style="height:1.5rem"></div>', unsafe_allow_html=True)
        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        if st.button(tr["step2_btn"], key="step2_btn"):
            st.session_state.tmp_birthdate = birthdate
            st.session_state.form_step = 2
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Step 2: Question ──
    elif step == 2:
        st.markdown(
            f'<p style="font-family:\'Manrope\',sans-serif;font-size:1.3rem;'
            f'font-weight:300;color:#2c3328;margin-bottom:1.5rem;letter-spacing:0.02em;">'
            f'{tr["step3_q"]}</p>',
            unsafe_allow_html=True
        )

        # Topic selector dropdown
        topic_custom = tr["q_custom"]
        topic_options = tr["q_suggest"] + [topic_custom]
        selected_topic = st.selectbox(
            "topic", topic_options, index=0,
            label_visibility="collapsed", key="topic_select"
        )

        # Show free-text input only when "Write my own" is selected
        if selected_topic == topic_custom:
            st.markdown('<div style="height:0.6rem"></div>', unsafe_allow_html=True)
            question = st.text_input("q", value=st.session_state.tmp_question,
                                      placeholder=tr["step3_ph"], label_visibility="collapsed")
        else:
            question = selected_topic

        st.markdown('<div style="height:1.5rem"></div>', unsafe_allow_html=True)
        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)

        def _do_reading(q_text):
            birthdate = st.session_state.tmp_birthdate
            lp   = life_path_number(birthdate)
            ss   = get_sun_sign(birthdate)
            drawn = draw_cards(q_text, lp, ss, n=3)
            st.session_state.user = {
                "name": st.session_state.tmp_name,
                "birthdate": birthdate,
                "question": q_text,
                "life_path": lp,
                "sun_sign": ss,
            }
            st.session_state.drawn = drawn
            st.session_state.slide = 'cards'
            st.session_state.tmp_question = ''
            st.rerun()

        if st.button(tr["step3_btn"], key="step3_btn"):
            if selected_topic == topic_custom:
                final_q = question.strip() if question.strip() else tr["q_default"]
            else:
                final_q = selected_topic
            _do_reading(final_q)
        st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  SLIDE 3 — CARDS + READING
#  Reading text lives INSIDE the HTML component,
#  revealed in sync with each card flip.
# ─────────────────────────────────────────────
elif st.session_state.slide == 'cards':
    drawn        = st.session_state.drawn
    user         = st.session_state.user
    lp           = user["life_path"]
    ss           = user["sun_sign"]
    sign_display = SIGN_ZH.get(ss, ss.capitalize()) if lang == "zh" else ss.capitalize()
    pos_labels   = tr["pos"]
    pos_subs     = tr["pos_sub"]

    # Build reading sentences
    reading_data = []
    for i, card in enumerate(drawn):
        is_rev    = card['position'] == 'reversed'
        meaning   = card['upright_meaning'] if not is_rev else card['reversed_meaning']
        # Pick reversed templates when card is reversed
        if is_rev and i < len(ALL_TEMPLATES_REV):
            templates = ALL_TEMPLATES_REV[i]
        elif i < len(ALL_TEMPLATES):
            templates = ALL_TEMPLATES[i]
        else:
            templates = ALL_TEMPLATES[-1]
        template  = templates[card.get('number', 0) % len(templates)]
        kw        = _reversed_keywords(card) if is_rev else card['keywords']
        sentence  = template.format(
            name=card['name'],
            meaning_fragment=_sentence_fragment(meaning),
            keywords=", ".join(kw[:3]),
            kw0=kw[0] if kw else "",
            kw1=kw[1] if len(kw) > 1 else kw[0],
            element=card.get('element', 'mystery').capitalize(),
        )
        if lang == "zh":
            try:
                from deep_translator import GoogleTranslator
                sentence = GoogleTranslator(source='en', target='zh-CN').translate(sentence)
            except:
                pass

        # Natural language "why this card" explanation
        reasons = []
        ast_match = card['name'] in SIGN_CARD_AFFINITIES.get(ss, [])
        num_match = lp in card.get('numerology_affinity', [])
        if ast_match:
            reasons.append(f"it carries an affinity with {sign_display}")
        if num_match:
            reasons.append(f"life path {lp} resonates with this card")
        # Always include semantic context with the draw weight
        reasons.append(f"its themes aligned with your question ({card['weight']:.1f}% draw weight)")
        why_text = ", ".join(reasons) + "."
        why_text = why_text[0].upper() + why_text[1:]

        reading_data.append({
            "pos":    pos_labels[i],
            "pos_sub": pos_subs[i],
            "name":   card['name'],
            "orient": tr["reversed"] if is_rev else tr["upright"],
            "text":   sentence,
            "why":    why_text,
            "weight": card['weight'],
            "why_label": tr["why"],
        })

    # Build card SVG data
    cards_data = []
    chr92 = chr(92)
    for i, card in enumerate(drawn):
        is_rev    = card['position'] == 'reversed'
        front     = card_svg_str(card, is_reversed=is_rev, w=160, h=248)
        back      = back_svg_str(160, 248)
        front_esc = front.replace(chr92, chr92*2).replace('`', '\\`')
        back_esc  = back.replace(chr92, chr92*2).replace('`', '\\`')
        cards_data.append({"front": front_esc, "back": back_esc})

    cards_json   = json.dumps(cards_data)
    reading_json = json.dumps(reading_data)

    # Back SVG for fan (smaller)
    fan_back = back_svg_str(80, 124).replace(chr92, chr92*2).replace('`', '\\`')

    choose_txt   = tr["choose"]
    reading_txt  = tr["your_reading"]
    cards_left   = json.dumps(tr["cards_left"])

    full_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@200;300;400;500;600;700&display=swap');
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{
    background:#f4f5f0;
    font-family:'Manrope',sans-serif;
    font-weight:400;
    color:#2c3328;
    overflow-x:hidden;
}}

/* ── STAGE ── */
#stage{{
    width:100%;
    display:flex;flex-direction:column;
    align-items:center;
    padding:2rem 1rem 0;
}}

/* ── PROMPT / COUNTER ── */
#prompt{{
    font-family:'Manrope',sans-serif;
    font-weight:400;
    font-size:0.78rem;
    color:rgba(44,51,40,0.55);
    letter-spacing:0.12em;
    text-transform:uppercase;
    margin-bottom:0.8rem;
    opacity:0;transition:opacity 0.7s ease;
    text-align:center;
}}
#counter{{
    font-family:'Manrope',sans-serif;
    font-weight:300;
    font-size:0.9rem;
    color:rgba(44,51,40,0.5);
    letter-spacing:0.04em;
    margin-bottom:1.5rem;
    opacity:0;transition:opacity 0.5s ease;
    min-height:1.3em;text-align:center;
}}

/* ── FAN ── */
#fan{{
    position:relative;
    width:520px;height:260px;
    margin:0 auto;
    flex-shrink:0;
}}
.fan-card{{
    position:absolute;
    width:80px;height:124px;
    border-radius:5px;overflow:hidden;
    cursor:pointer;
    transform-origin:center bottom;
    transition:transform 0.4s cubic-bezier(0.34,1.2,0.64,1),
               box-shadow 0.3s ease, opacity 0.4s ease;
    box-shadow:0 2px 10px rgba(0,0,0,0.1);
    left:50%;top:50%;
    margin-left:-40px;margin-top:-62px;
}}
.fan-card:hover{{
    box-shadow:0 8px 24px rgba(0,0,0,0.15)!important;
    z-index:100!important;
}}
.fan-card.selected{{
    box-shadow:0 0 0 1.5px #7a6548,0 8px 24px rgba(0,0,0,0.18)!important;
    z-index:99!important;
}}
.fan-card.fade{{opacity:0.1;cursor:default;pointer-events:none;}}
.fc-inner{{width:100%;height:100%;transform-style:preserve-3d;transition:transform 0.9s cubic-bezier(0.4,0,0.2,1);}}
.fc-inner.flipped{{transform:rotateY(180deg);}}
.fc-face{{position:absolute;width:100%;height:100%;backface-visibility:hidden;-webkit-backface-visibility:hidden;border-radius:5px;overflow:hidden;}}
.fc-front{{transform:rotateY(180deg);}}
.fc-face svg{{width:100%;height:100%;display:block;}}

/* ── REVEAL ROW ── */
#reveal{{
    display:flex;gap:20px;justify-content:center;
    align-items:flex-start;
    margin-top:1rem;
    opacity:0;transition:opacity 0.5s ease;
    min-height:180px;flex-wrap:wrap;
}}
.rv-card{{
    display:flex;flex-direction:column;align-items:center;gap:6px;
    opacity:0;transform:translateY(18px);
    transition:opacity 0.5s ease,transform 0.5s ease;
}}
.rv-scene{{width:120px;height:188px;perspective:800px;}}
.rv-inner{{
    width:100%;height:100%;
    transform-style:preserve-3d;
    transition:transform 1.1s cubic-bezier(0.4,0,0.2,1);
    border-radius:7px;
    box-shadow:0 4px 20px rgba(0,0,0,0.12);
}}
.rv-inner.flipped{{transform:rotateY(180deg);}}
.rv-face{{position:absolute;width:100%;height:100%;backface-visibility:hidden;-webkit-backface-visibility:hidden;border-radius:7px;overflow:hidden;}}
.rv-front{{transform:rotateY(180deg);}}
.rv-face svg{{width:100%;height:100%;display:block;}}

/* Card labels */
.rv-pos{{font-family:'Manrope',sans-serif;font-weight:500;font-size:8px;color:rgba(44,51,40,0.5);letter-spacing:0.12em;text-transform:uppercase;text-align:center;}}
.rv-name{{font-family:'Manrope',sans-serif;font-weight:600;font-size:12px;color:#2c3328;text-align:center;max-width:120px;}}
.rv-orient{{font-family:'Manrope',sans-serif;font-weight:400;font-size:8px;color:rgba(44,51,40,0.45);letter-spacing:0.08em;}}

/* ── READING SECTION (inside component) ── */
#reading{{
    width:100%;max-width:600px;
    margin:2.5rem auto 0;
    padding:0 1rem 3rem;
    opacity:0;
    transition:opacity 0.8s ease;
}}

/* Section header */
.reading-label{{
    font-family:'Manrope',sans-serif;
    font-weight:400;
    font-size:0.72rem;
    color:rgba(44,51,40,0.45);
    letter-spacing:0.15em;
    text-transform:uppercase;
    text-align:center;
    margin-bottom:2rem;
}}

.r-block{{
    padding:1.6rem 0;
    border-bottom:1px solid rgba(26,20,16,0.1);
    opacity:0;transform:translateY(10px);
    transition:opacity 0.6s ease,transform 0.6s ease;
}}
.r-block:last-of-type {{ border-bottom:none; }}

.r-top{{
    display:flex;align-items:baseline;gap:0.6rem;
    margin-bottom:0.8rem;
    flex-wrap:wrap;
}}
.r-pos-label{{
    font-family:'Manrope',sans-serif;font-weight:500;
    font-size:0.68rem;color:rgba(44,51,40,0.45);
    letter-spacing:0.1em;text-transform:uppercase;
}}
.r-name{{
    font-family:'Manrope',sans-serif;font-weight:600;
    font-size:1.15rem;color:#2c3328;
}}
.r-orient{{
    font-family:'Manrope',sans-serif;font-weight:400;
    font-size:0.68rem;color:rgba(44,51,40,0.45);
    letter-spacing:0.08em;text-transform:uppercase;
}}
.r-text{{
    font-family:'Manrope',sans-serif;font-weight:300;
    font-style:italic;font-size:0.95rem;
    color:rgba(44,51,40,0.7);line-height:1.85;
    margin-bottom:0.9rem;
}}

/* Why toggle */
.why-toggle{{
    font-family:'Manrope',sans-serif;font-weight:500;
    font-size:0.68rem;color:rgba(44,51,40,0.4);
    letter-spacing:0.08em;text-transform:uppercase;
    cursor:pointer;
    border:none;background:none;
    padding:0;
    transition:color 0.2s ease;
    display:flex;align-items:center;gap:0.4rem;
}}
.why-toggle:hover{{color:rgba(44,51,40,0.7);}}
.why-toggle .arrow{{
    font-size:0.5rem;
    transition:transform 0.25s ease;
    display:inline-block;
}}
.why-toggle.open .arrow{{transform:rotate(90deg);}}

.why-body{{
    display:none;
    margin-top:0.7rem;
    padding:0.9rem 1rem;
    background:rgba(44,51,40,0.03);
    border-left:1.5px solid rgba(44,51,40,0.12);
}}
.why-body.open{{display:block;}}

.why-sent{{
    font-family:'Manrope',sans-serif;font-weight:300;
    font-style:italic;font-size:0.85rem;
    color:rgba(44,51,40,0.55);line-height:1.8;
    margin-bottom:0.5rem;
}}
.why-pills{{display:flex;gap:6px;flex-wrap:wrap;margin-top:0.5rem;}}
.why-pill{{
    font-family:'Manrope',sans-serif;font-weight:500;font-size:0.65rem;
    color:rgba(44,51,40,0.55);letter-spacing:0.04em;
    border:1px solid rgba(44,51,40,0.18);
    padding:0.2rem 0.55rem;border-radius:3px;
}}
.why-pill.match{{color:#7a6548;border-color:rgba(138,104,48,0.35);}}
</style>
</head><body>

<div id="stage">
  <div id="prompt">{choose_txt}</div>
  <div id="counter"></div>
  <div id="fan"></div>
  <div id="reveal"></div>

  <div id="reading">
    <div class="reading-label">{reading_txt}</div>
    <div id="r-blocks"></div>
  </div>
</div>

<script>
const CARDS_SVG  = {cards_json};
const READING    = {reading_json};
const CARDS_LEFT = {cards_left};
const BACK_SMALL = `{fan_back}`;
const N_FAN = 13;

const promptEl  = document.getElementById('prompt');
const counterEl = document.getElementById('counter');
const fanEl     = document.getElementById('fan');
const revealEl  = document.getElementById('reveal');
const readingEl = document.getElementById('reading');
const rBlocksEl = document.getElementById('r-blocks');

let selected = [], done = false;

// ── Build fan ──
const angles = Array.from({{length:N_FAN}}, (_,i) => -52 + i*(104/(N_FAN-1)));
const fanCards = [];

for(let i=0;i<N_FAN;i++){{
    const card = document.createElement('div');
    card.className = 'fan-card';
    card.style.zIndex = i < N_FAN/2 ? i : N_FAN-i;
    card.innerHTML = `<div class="fc-inner">
        <div class="fc-face fc-back">${{BACK_SMALL}}</div>
        <div class="fc-face fc-front"></div>
    </div>`;
    fanEl.appendChild(card);
    fanCards.push(card);
    card.addEventListener('click', () => onPick(card, i));
}}

function spreadFan() {{
    return new Promise(r => {{
        fanCards.forEach((c, i) => {{
            setTimeout(() => {{
                c.style.transform = `rotate(${{angles[i]}}deg) translateY(-70px)`;
                c.style.zIndex = i < N_FAN/2 ? i+1 : N_FAN-i+1;
            }}, i*45);
        }});
        setTimeout(r, N_FAN*45+500);
    }});
}}

function onPick(card, idx) {{
    if(done) return;
    if(card.classList.contains('selected')) {{
        card.classList.remove('selected');
        selected = selected.filter(x => x !== idx);
        updateCounter(); return;
    }}
    if(selected.length >= 3) return;
    card.classList.add('selected');
    selected.push(idx);
    updateCounter();
    if(selected.length === 3) setTimeout(revealCards, 450);
}}

function updateCounter() {{
    const left = 3 - selected.length;
    if(left === 0) {{
        counterEl.textContent = CARDS_LEFT[2];
    }} else {{
        counterEl.textContent = CARDS_LEFT[3 - left - 1] || `Select ${{left}} more`;
    }}
}}

function revealCards() {{
    done = true;
    fanCards.forEach((c,i) => {{ if(!selected.includes(i)) c.classList.add('fade'); }});
    fanCards.forEach((c,i) => {{
        if(selected.includes(i)) {{
            c.style.transition = 'transform 0.45s ease, opacity 0.4s ease 0.8s';
            c.style.transform += ' translateY(-14px)';
        }}
    }});
    setTimeout(() => {{
        fanEl.style.transition = 'opacity 0.4s ease';
        fanEl.style.opacity = '0';
        setTimeout(() => {{
            fanEl.style.display = 'none';
            showReveal();
        }}, 400);
    }}, 800);
}}

function showReveal() {{
    revealEl.innerHTML = '';
    revealEl.style.opacity = '1';
    promptEl.style.opacity = '0';
    counterEl.style.opacity = '0';

    READING.forEach((rd, i) => {{
        const w = document.createElement('div');
        w.className = 'rv-card';
        const backBig = `{back_svg_str(120,188).replace(chr92, chr92*2).replace('`','\\`')}`;
        w.innerHTML = `
            <div class="rv-pos">${{rd.pos}}</div>
            <div class="rv-scene">
                <div class="rv-inner" id="rv-${{i}}">
                    <div class="rv-face rv-back">${{backBig}}</div>
                    <div class="rv-face rv-front">${{CARDS_SVG[i].front}}</div>
                </div>
            </div>
            <div class="rv-name">${{rd.name}}</div>
            <div class="rv-orient">${{rd.orient}}</div>`;
        revealEl.appendChild(w);

        // Stagger card drop-in + flip
        setTimeout(() => {{
            w.style.opacity = '1';
            w.style.transform = 'translateY(0)';
            setTimeout(() => {{
                document.getElementById('rv-'+i).classList.add('flipped');
                // Reveal this card's reading text after flip completes
                setTimeout(() => showReadingBlock(i), 900);
            }}, 600);
        }}, i*550 + 150);
    }});

    // Show reading container after all cards start animating
    setTimeout(() => {{
        readingEl.style.opacity = '1';
    }}, READING.length * 550 + 800);
}}

function showReadingBlock(i) {{
    const rd = READING[i];
    const block = document.createElement('div');
    block.className = 'r-block';
    block.id = 'rb-' + i;

    // Build why pills
    const pillsHtml = `
        <span class="why-pill">${{rd.weight}}% draw weight</span>
    `;

    block.innerHTML = `
        <div class="r-top">
            <span class="r-pos-label">${{rd.pos}} &middot; ${{rd.pos_sub}}</span>
            <span class="r-name">${{rd.name}}</span>
            <span class="r-orient">&mdash; ${{rd.orient}}</span>
        </div>
        <div class="r-text">${{rd.text}}</div>
        <button class="why-toggle" onclick="toggleWhy(${{i}}, this)">
            <span class="arrow">&#9658;</span>
            ${{rd.why_label}}
        </button>
        <div class="why-body" id="why-${{i}}">
            <div class="why-sent">${{rd.why}}</div>
            <div class="why-pills">${{pillsHtml}}</div>
        </div>
    `;
    rBlocksEl.appendChild(block);

    // Animate in
    requestAnimationFrame(() => {{
        requestAnimationFrame(() => {{
            block.style.opacity = '1';
            block.style.transform = 'translateY(0)';
        }});
    }});
}}

function toggleWhy(i, btn) {{
    const body = document.getElementById('why-'+i);
    const isOpen = body.classList.contains('open');
    body.classList.toggle('open', !isOpen);
    btn.classList.toggle('open', !isOpen);
}}

// ── Init ──
async function run() {{
    promptEl.style.opacity = '1';
    counterEl.style.opacity = '1';
    counterEl.textContent = 'Select three cards from the spread';
    await spreadFan();
}}
run();
</script>
</body></html>"""

    # Restart button ABOVE the component so it's always visible
    st.markdown('<div style="display:flex;justify-content:center;margin:1rem 0;">', unsafe_allow_html=True)
    st.markdown('<div class="restart-btn">', unsafe_allow_html=True)
    if st.button(tr["new"], key="restart"):
        for k in ['drawn','user','tmp_name','tmp_birthdate','tmp_question']:
            st.session_state[k] = {} if k == 'user' else (None if k == 'drawn' else '')
        st.session_state.form_step = 0
        st.session_state.slide = 'landing'
        st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)

    components.html(full_html, height=1400, scrolling=True)

    # ── Weight diagnostics panel ──
    with st.expander("⚙ Weight diagnostics"):
        debug = compute_weights_debug(user["question"], lp, ss)
        entropy_pct = round(debug["entropy"] / debug["max_entropy"] * 100, 1)

        st.markdown(
            f'<div style="font-family:Manrope,sans-serif;font-size:0.75rem;color:#4a5544;">'
            f'Entropy: {debug["entropy"]:.2f} / {debug["max_entropy"]:.2f} ({entropy_pct}% of uniform) · '
            f'Range: {debug["prob_range"][0]:.3f}% – {debug["prob_range"][1]:.3f}%'
            f'</div>', unsafe_allow_html=True
        )
        st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)

        st.markdown(
            '<div style="font-family:Manrope,sans-serif;font-size:0.68rem;color:#7a8672;'
            'letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.5rem;font-weight:500;">Top 10 most likely cards</div>',
            unsafe_allow_html=True
        )
        for card in debug["top_10"]:
            flags = []
            if card["numerology"] > 1: flags.append("NUM ×1.3")
            if card["astrology"] > 1: flags.append("AST ×1.2")
            flag_str = f"  [{', '.join(flags)}]" if flags else ""
            st.markdown(
                f'<div style="font-family:Manrope,sans-serif;font-size:0.82rem;color:#4a5544;'
                f'padding:0.15rem 0;">'
                f'<span style="display:inline-block;width:55px;text-align:right;margin-right:8px;'
                f'font-size:0.72rem;color:#7a8672;">'
                f'{card["probability"]:.2f}%</span>'
                f'{card["name"]}'
                f'<span style="font-size:0.62rem;color:#7a6548;'
                f'margin-left:6px;">{flag_str}</span>'
                f'<span style="font-size:0.6rem;color:#7a8672;'
                f'margin-left:8px;">sem={card["semantic_raw"]:.3f}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

        st.markdown('<div style="height:0.8rem"></div>', unsafe_allow_html=True)
        st.markdown(
            '<div style="font-family:Manrope,sans-serif;font-size:0.68rem;color:#7a8672;'
            'letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.5rem;font-weight:500;">Your drawn cards\' ranks</div>',
            unsafe_allow_html=True
        )
        for card in drawn:
            rank = next(
                (j+1 for j, b in enumerate(debug["breakdown"]) if b["name"] == card["name"]),
                "?"
            )
            st.markdown(
                f'<div style="font-family:Manrope,sans-serif;font-size:0.82rem;color:#4a5544;'
                f'padding:0.15rem 0;">'
                f'<span style="font-size:0.72rem;color:#7a6548;'
                f'margin-right:6px;">#{rank}/78</span>'
                f'{card["name"]} — {card["weight"]:.2f}%'
                f'</div>',
                unsafe_allow_html=True
            )

    st.markdown(
        f'<div class="foot">Life path {lp} · {sign_display} · 78 cards</div>',
        unsafe_allow_html=True
    )