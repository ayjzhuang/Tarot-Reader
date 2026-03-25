CSS_BLOCK = """<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@200;300;400;500;600;700&display=swap');
:root {
  --bg:#f4f5f0; --bg-alt:#eaede4; --ink:#2c3328; --ink-dim:#4a5544;
  --ink-faint:#7a8672; --sage:#6b7f5e; --sage-light:#95a88a;
  --sage-deep:#3d4f35; --brown:#7a6548; --cream:#f9faf5;
  --border:rgba(44,51,40,0.12); --border-mid:rgba(44,51,40,0.22); --surface:#e8ebe2;
}
*,*::before,*::after{box-sizing:border-box}
html,body,[class*="css"]{font-family:'Manrope',-apple-system,sans-serif!important;background:var(--bg)!important;color:var(--ink)!important}
.stApp{background:var(--bg)!important}
#MainMenu,header,footer,[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"],[data-testid="stHeader"]{display:none!important}
[data-testid="stAppViewContainer"]>section>div{padding-top:0!important}
.block-container{padding:0 1.5rem 3rem!important;max-width:600px!important;margin-top:0!important}
</style>"""

CSS_INPUTS = """<style>
.stTextInput>div>div>input{background:transparent!important;border:none!important;border-bottom:1.5px solid var(--border-mid)!important;border-radius:0!important;color:var(--ink)!important;font-family:'Manrope',sans-serif!important;font-size:1.05rem!important;font-weight:400!important;padding:0.6rem 0!important;box-shadow:none!important}
.stTextInput>div>div>input:focus{border-bottom-color:var(--sage)!important;box-shadow:none!important}
.stTextInput>div>div>input::placeholder{color:var(--ink-faint)!important;font-weight:300!important}
.stTextInput label{display:none!important}
.stSelectbox>div>div{background:transparent!important;border:none!important;border-bottom:1.5px solid var(--border-mid)!important;border-radius:0!important;color:var(--ink)!important;font-family:'Manrope',sans-serif!important;font-size:0.95rem!important}
.stSelectbox label{display:none!important}
[data-baseweb="select"]>div{background:var(--bg)!important;border-color:var(--border-mid)!important;border-radius:0!important}
[data-baseweb="popover"]{background:var(--bg)!important}
[role="option"]{background:var(--bg)!important;color:var(--ink)!important;font-family:'Manrope',sans-serif!important}
[role="option"]:hover{background:var(--surface)!important}
label{display:none!important}
</style>"""

CSS_BUTTONS = """<style>
.stButton{text-align:center!important}
.stButton>button{background:transparent!important;border:1.5px solid var(--border-mid)!important;color:var(--ink-dim)!important;font-family:'Manrope',sans-serif!important;font-size:0.74rem!important;font-weight:500!important;letter-spacing:0.08em!important;text-transform:uppercase!important;padding:0.55rem 1.6rem!important;border-radius:3px!important;width:auto!important;transition:all 0.15s ease!important;cursor:pointer!important;line-height:1.4!important}
.stButton>button:hover{border-color:var(--sage)!important;color:var(--sage-deep)!important}
.primary-btn .stButton>button{background:var(--sage-deep)!important;border-color:var(--sage-deep)!important;color:var(--cream)!important;padding:0.65rem 2.2rem!important;font-size:0.76rem!important}
.primary-btn .stButton>button:hover{opacity:0.8!important;border-color:var(--sage-deep)!important;color:var(--cream)!important}
.small-btn .stButton>button{font-size:0.68rem!important;padding:0.22rem 0.65rem!important;border-width:1px!important;color:var(--ink-faint)!important;letter-spacing:0.05em!important}
.small-btn .stButton>button:hover{color:var(--ink-dim)!important;border-color:var(--sage)!important}
.small-btn .stButton{text-align:left!important}
.chip-btn .stButton>button{font-size:0.7rem!important;padding:0.35rem 1rem!important;border-width:1px!important;color:var(--ink-faint)!important;letter-spacing:0.02em!important;text-transform:none!important;font-weight:400!important;border-radius:20px!important}
.chip-btn .stButton>button:hover{color:var(--sage-deep)!important;border-color:var(--sage)!important;background:rgba(107,127,94,0.08)!important}
.chip-btn .stButton{text-align:center!important}
</style>"""

CSS_MISC = """<style>
.stExpander{border:none!important;border-top:1px solid var(--border)!important;border-radius:0!important;background:transparent!important}
details>summary{font-family:'Manrope',sans-serif!important;font-size:0.72rem!important;font-weight:500!important;color:var(--ink-faint)!important;letter-spacing:0.08em!important;text-transform:uppercase!important;padding:0.7rem 0!important}
details>summary:hover{color:var(--ink-dim)!important}
.foot{font-family:'Manrope',sans-serif;font-size:0.68rem;font-weight:400;color:var(--ink-faint);text-align:center;letter-spacing:0.1em;text-transform:uppercase;margin:2rem 0 1rem}
.stAlert{background:transparent!important;border:1px solid var(--border-mid)!important;color:var(--ink-dim)!important;border-radius:3px!important;font-family:'Manrope',sans-serif!important;font-size:0.85rem!important}
@keyframes gentle-glow{0%,100%{opacity:0.4;transform:scale(1)}50%{opacity:0.7;transform:scale(1.05)}}
.landing-glow{position:fixed;top:-20%;left:50%;transform:translateX(-50%);width:600px;height:600px;border-radius:50%;background:radial-gradient(circle,rgba(107,127,94,0.15) 0%,rgba(107,127,94,0.05) 40%,transparent 70%);animation:gentle-glow 6s ease-in-out infinite;pointer-events:none;z-index:0}
</style>"""

CSS_ALL = CSS_BLOCK + CSS_INPUTS + CSS_BUTTONS + CSS_MISC
