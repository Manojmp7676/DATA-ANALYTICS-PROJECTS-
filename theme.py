"""
Shared visual theme for the Retail Analytics Dashboard.

Design concept: the retailer's own catalog is full of gift tags, ribbons,
and paper-craft items ("Cards & Paper Crafts", "Heart-themed Gifts",
"Seasonal / Christmas"). The signature visual element borrows from that —
every metric card carries a small folded "gift-tag" corner ribbon — so the
chrome of the dashboard nods to the actual product world instead of a
generic admin-panel look.

Palette:
  Base background   #12122B  (deep indigo-navy)
  Panel / card       rgba(255,255,255,0.05) glass over #1B1840
  Accent gold        #F2B84B  (price-tag gold)
  Accent violet      #8B7FE8  (ribbon violet)
  Accent teal        #5FCFC0  (secondary accent)
  Accent coral       #F0806B  (alert / at-risk accent)
  Text primary       #F5F3FF
  Text muted         #A8A3C7
"""

COLORS = {
    "bg": "#12122B",
    "panel": "#1B1840",
    "gold": "#F2B84B",
    "violet": "#8B7FE8",
    "teal": "#5FCFC0",
    "coral": "#F0806B",
    "text": "#F5F3FF",
    "muted": "#A8A3C7",
    "border": "rgba(255,255,255,0.09)",
}

PLOTLY_SEQUENCE = ["#F2B84B", "#8B7FE8", "#5FCFC0", "#F0806B", "#7C9CFF", "#C689F0", "#6EE7B7", "#9CA3AF"]


def base_css():
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

.stApp {{
    background: radial-gradient(circle at 15% 0%, #1E1A45 0%, {COLORS['bg']} 45%, #0D0C20 100%);
    color: {COLORS['text']};
}}

section[data-testid="stSidebar"] {{
    background: #14122E;
    border-right: 1px solid {COLORS['border']};
}}

h1, h2, h3, h4 {{
    font-family: 'Space Grotesk', sans-serif !important;
    color: {COLORS['text']} !important;
    letter-spacing: -0.01em;
}}

p, span, label, div {{
    color: {COLORS['text']};
}}

.dash-eyebrow {{
    font-family: 'Space Grotesk', sans-serif;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    font-size: 0.72rem;
    color: {COLORS['gold']};
    font-weight: 600;
    margin-bottom: 0.2rem;
}}

.dash-title {{
    font-size: 2.1rem;
    font-weight: 700;
    margin-top: 0;
    margin-bottom: 0.15rem;
}}

.dash-subtitle {{
    color: {COLORS['muted']};
    font-size: 0.95rem;
    margin-bottom: 1.6rem;
}}

.section-label {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.05rem;
    font-weight: 600;
    color: {COLORS['text']};
    margin: 1.6rem 0 0.6rem 0;
    padding-left: 0.6rem;
    border-left: 3px solid {COLORS['gold']};
}}

/* --- Gift-tag metric card --- */
.tag-card {{
    position: relative;
    background: linear-gradient(160deg, rgba(255,255,255,0.07), rgba(255,255,255,0.02));
    border: 1px solid {COLORS['border']};
    border-radius: 14px;
    padding: 1.1rem 1.2rem 1rem 1.2rem;
    backdrop-filter: blur(10px);
    overflow: hidden;
    min-height: 108px;
}}

.tag-card::before {{
    content: "";
    position: absolute;
    top: 0;
    right: 0;
    width: 0;
    height: 0;
    border-style: solid;
    border-width: 0 34px 34px 0;
    border-color: transparent var(--ribbon-color, {COLORS['gold']}) transparent transparent;
    opacity: 0.9;
}}

.tag-card::after {{
    content: "";
    position: absolute;
    top: 7px;
    right: 7px;
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: {COLORS['bg']};
}}

.tag-label {{
    font-size: 0.78rem;
    color: {COLORS['muted']};
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.35rem;
}}

.tag-value {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.65rem;
    font-weight: 700;
    color: {COLORS['text']};
    line-height: 1.1;
}}

.tag-delta {{
    font-size: 0.78rem;
    color: {COLORS['teal']};
    margin-top: 0.3rem;
}}

/* --- Segment badge --- */
.segment-banner {{
    display: flex;
    align-items: center;
    gap: 1rem;
    background: linear-gradient(120deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02));
    border: 1px solid {COLORS['border']};
    border-left: 5px solid var(--seg-color, {COLORS['gold']});
    border-radius: 12px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 1rem;
}}

.segment-emoji {{
    font-size: 2.1rem;
}}

.segment-name {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--seg-color, {COLORS['gold']});
}}

.segment-tagline {{
    color: {COLORS['muted']};
    font-size: 0.9rem;
}}

.rec-list {{
    background: rgba(255,255,255,0.04);
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
    padding: 1rem 1.3rem;
    margin-top: 0.6rem;
}}

.rec-list li {{
    margin-bottom: 0.45rem;
    color: {COLORS['text']};
    font-size: 0.92rem;
}}

.profile-card {{
    background: rgba(255,255,255,0.045);
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
}}

.profile-label {{
    font-size: 0.72rem;
    color: {COLORS['muted']};
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 0.2rem;
}}

.profile-value {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.15rem;
    font-weight: 600;
}}

hr {{
    border-color: {COLORS['border']} !important;
}}

div[data-testid="stSelectbox"] label, div[data-testid="stTextInput"] label {{
    color: {COLORS['muted']} !important;
    font-weight: 500;
}}

::-webkit-scrollbar {{ width: 10px; height: 10px; }}
::-webkit-scrollbar-track {{ background: {COLORS['bg']}; }}
::-webkit-scrollbar-thumb {{ background: #3A3670; border-radius: 6px; }}
</style>
"""


def metric_card(label, value, ribbon_color=None, delta=None):
    ribbon = ribbon_color or COLORS["gold"]
    delta_html = f'<div class="tag-delta">{delta}</div>' if delta else ""
    return f"""
<div class="tag-card" style="--ribbon-color:{ribbon};">
    <div class="tag-label">{label}</div>
    <div class="tag-value">{value}</div>
    {delta_html}
</div>
"""


def segment_banner(emoji, name, color, tagline):
    return f"""
<div class="segment-banner" style="--seg-color:{color};">
    <div class="segment-emoji">{emoji}</div>
    <div>
        <div class="segment-name">{name}</div>
        <div class="segment-tagline">{tagline}</div>
    </div>
</div>
"""


def recommendations_list(items):
    lis = "".join(f"<li>{item}</li>" for item in items)
    return f'<ul class="rec-list">{lis}</ul>'


def profile_card(label, value):
    return f"""
<div class="profile-card">
    <div class="profile-label">{label}</div>
    <div class="profile-value">{value}</div>
</div>
"""


def plotly_layout_defaults(fig, height=380):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=COLORS["text"], size=12),
        margin=dict(l=10, r=10, t=40, b=10),
        height=height,
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        colorway=PLOTLY_SEQUENCE,
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.08)")
    return fig
