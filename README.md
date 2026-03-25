# Tarot Reader

Personalised tarot readings from a 78-card Rider-Waite deck. Cards are not drawn randomly - they are weighted by an ML pipeline that scores every card against the user's question, birthdate, and sun sign, then samples from the resulting probability distribution.

Built with Python, Streamlit, and scikit-learn. Bilingual (English / 中文). No external image assets - all card art is procedural SVG.

**Live:** [tarot-reader-ayjzhuang.streamlit.app](https://tarot-reader-ayjzhuang.streamlit.app/)

---

## How it works

The user provides three inputs: name, birthdate, and a question (selected from preset topics or written freely). The engine computes a weight for each of the 78 cards, converts those weights into a probability distribution via softmax, and samples 3 cards without replacement.

### Weight computation

Each card's weight is the product of three independent scores:

**1. Semantic score** - How well the card's themes match the question.
- The question is expanded through a synonym dictionary (e.g. "love" → romance, partner, heart, connection…), then vectorised with TF-IDF alongside every card's theme corpus.
- Cosine similarity gives one signal; direct keyword overlap gives another. These are blended 60/40 (keyword/TF-IDF) and normalised to [0, 1].

**2. Numerology score** - Whether the card has affinity with the user's life path number.
- Birthdate digits are summed and reduced to a single digit (1–9) or master number (11, 22).
- Cards with a matching `numerology_affinity` receive a ×1.3 multiplier. Others get ×1.0.

**3. Astrology score** - Whether the card is affiliated with the user's sun sign.
- Sun sign is derived from the birthdate using standard date ranges.
- Affiliated cards (e.g. The Emperor for Aries, The Moon for Pisces) receive ×1.2. Others get ×1.0.

### Sampling

The three scores are multiplied per card, then passed through a softmax function (temperature = 0.3) to produce a valid probability distribution. `numpy.random.choice` draws 3 cards without replacement. Each card is independently assigned upright or reversed orientation.

```
question + birthdate
        ↓
┌──────────────────────────────────┐
│  semantic(q)  ×  numerology(bd)  │
│               ×  astrology(bd)   │
│  ─────────────────────────────── │
│  → softmax(temp=0.3) → p[78]    │
└──────────────────────────────────┘
        ↓
  np.random.choice(78, n=3, p=p)
```

---

## UI flow

1. **Landing** - Title, "Begin" button, language toggle, card browser link.
2. **Form** - Three-step wizard with dot progress indicator:
   - Step 1: Name (text input)
   - Step 2: Birthdate (day / month / year dropdowns)
   - Step 3: Question (dropdown of preset topics, or free-text via "Write my own")
3. **Card selection** - 13-card fan spread rendered as inline SVG. User clicks 3 cards.
4. **Reveal** - Selected cards flip with staggered animation. Reading text appears per card (past / present / future), each with a collapsible "Why this card" explanation showing which signals fired and the draw weight.
5. **Diagnostics** - Expandable panel showing the full weight breakdown: top 10 cards, entropy, probability range, and the drawn cards' ranks out of 78.

All card illustrations are generated procedurally as SVG - no image files. Each suit has a distinct geometric motif (circle/spokes for Major, staff for Wands, chalice for Cups, blade for Swords, pentagram for Pentacles).

---

## Project structure

```
├── app.py              # Streamlit UI, SVG generation, HTML/JS card component
├── tarot_reader.py     # Weight engine, TF-IDF scoring, numerology, astrology
├── _css_block.py       # Global CSS (layout, inputs, buttons, misc)
├── data/
│   └── cards.json      # 78 cards: keywords, themes, meanings, affinities
└── requirements.txt    # rich, scikit-learn, numpy, streamlit, deep-translator
```

---

## Run locally

```bash
git clone https://github.com/ayjzhuang/Tarot-Reader.git
cd Tarot-Reader
pip install -r requirements.txt
streamlit run app.py
```

Opens at `http://localhost:8501`.

---

## 中文说明

基于 78 张韦特塔罗牌的个人化解读应用。选牌不是随机的--系统会根据你的问题（TF-IDF 语义匹配）、生日（生命灵数 ×1.3）和太阳星座（星座亲和 ×1.2）为每张牌计算权重，经 softmax 转换为概率分布后加权抽取三张。

操作流程：输入姓名 → 选择生日 → 从预设主题中选择问题或自由输入 → 从 13 张扇形牌阵中点选三张 → 翻牌揭示「过去–现在–未来」解读，附「为什么是这张牌」说明。

支持中英双语，所有牌面插图为程序化 SVG 生成，无外部图片依赖。
