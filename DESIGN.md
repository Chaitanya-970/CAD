# DESIGN.md — Assam Flood Intelligence Platform (AFIP)

> **Source:** Extracted from [Template.pptx](file:///c:/Users/LOQ/OneDrive/Desktop/CAD/Template.pptx) (13-slide brand deck)
> **Applies To:** Both the hackathon presentation slides AND the web application frontend
> **Purpose:** Ensure visual consistency between the PPT and the website so judges see one cohesive brand

---

## 1. Color Palette

The template uses a warm, earthy palette with a deep burgundy/wine as the primary accent. All colors below are extracted directly from the PPTX.

### 1.1 Core Colors

| Role | Hex | RGB | Name | Usage |
|------|-----|-----|------|-------|
| **Primary** | `#8B1E2D` | 139, 30, 45 | Wine / Deep Burgundy | Headings, accent shapes, buttons, active states |
| **Primary Light** | `#D64545` | 214, 69, 69 | Coral Red | Hero text, hover states, gradient partner for Primary |
| **Background (Warm)** | `#E9DED1` | 233, 222, 209 | Warm Linen | Page backgrounds, card backgrounds, light sections |
| **Background (Light)** | `#F5EEE6` | 245, 238, 230 | Cream | Alternate section backgrounds, card surfaces, subtle contrast |
| **Text Primary** | `#111111` | 17, 17, 17 | Near-Black | Body text, labels, descriptions |
| **White** | `#FFFFFF` | 255, 255, 255 | White | Card backgrounds on dark sections, text-on-dark |

### 1.2 Semantic Colors (for the flood app — NOT from the template)

These are domain-specific colors needed for the map and alerts. They should harmonize with the template palette.

| Role | Hex | Usage |
|------|-----|-------|
| **Danger / High Risk** | `#D64545` | Map: flood zones (risk > 0.7), SOS pins, offline banner |
| **Warning / Moderate Risk** | `#E8A838` | Map: moderate risk zones (risk 0.3–0.7), low-bandwidth banner |
| **Safe / Low Risk** | `#2D8B5E` | Map: safe zones, safe-zone markers, online-restored banner |
| **Info** | `#3B7DD8` | Informational toasts, Gov-GPT chat bubbles |

> **Design rationale:** The template's `#D64545` naturally doubles as the "danger" color. The warning amber and safe green are chosen to complement the warm palette without clashing. The info blue is muted to avoid looking jarring against the linen backgrounds.

### 1.3 CSS Custom Properties

```css
:root {
  /* Template palette */
  --color-primary: #8B1E2D;
  --color-primary-light: #D64545;
  --color-bg-warm: #E9DED1;
  --color-bg-light: #F5EEE6;
  --color-text: #111111;
  --color-white: #FFFFFF;

  /* Semantic (flood-specific) */
  --color-danger: #D64545;
  --color-warning: #E8A838;
  --color-safe: #2D8B5E;
  --color-info: #3B7DD8;

  /* Derived */
  --color-primary-hover: #A62B3C;    /* lighten primary slightly for hover */
  --color-border: #D5C9BA;           /* warm border derived from bg-warm */
  --color-text-muted: #6B5E52;       /* muted text for secondary info */
  --color-shadow: rgba(139, 30, 45, 0.1); /* primary-tinted shadow */
}
```

---

## 2. Typography

The template uses 3 fonts with very clear roles. The website must mirror this hierarchy.

### 2.1 Font Stack

| Font | Weight/Style | Template Role | Website Role | Fallback |
|------|-------------|---------------|-------------|----------|
| **Oswald** | Bold (700) | Giant hero words ("PRESENTATION", "ABOUT", "THANK") | Page titles, section headings (h1) | `Impact, Arial Black, sans-serif` |
| **Twister** | Regular | Decorative script words ("Brand", "Us", "Mission") | Accent headings, feature labels, numbers (h2, h3) | `Georgia, serif` |
| **Inter** | Regular (400), Bold (700), Italic | Body text, descriptions, metadata | All body text, labels, buttons, inputs | `system-ui, -apple-system, sans-serif` |

> **⚠️ Font Note:** "Twister" is a custom/premium font. If it's not available as a web font, use **Playfair Display** (Google Fonts) as the closest free alternative — it has the same warm, editorial, slightly decorative serif feel. For the PPT, the font must be embedded or installed on the presenting laptop.

### 2.2 Type Scale

Derived from the template's font sizes, translated to a web-appropriate scale:

| Level | PPT Size | Website Size | Font | Usage |
|-------|----------|-------------|------|-------|
| Display | 190–250pt | `clamp(3rem, 8vw, 6rem)` | Oswald Bold | Hero/landing page title only |
| H1 | 100–130pt | `clamp(2rem, 5vw, 3.5rem)` | Oswald Bold | Page headings ("DASHBOARD", "CROP ASSESSMENT") |
| H2 | 80–100pt | `clamp(1.5rem, 3vw, 2.5rem)` | Twister | Section sub-headings, feature names |
| H3 | 30pt | `1.25rem` | Inter Bold | Card titles, popup headings |
| Body | 25pt | `1rem` (16px) | Inter Regular | Paragraphs, descriptions, labels |
| Small | — | `0.875rem` (14px) | Inter Regular | Metadata, timestamps, captions |
| Caption | — | `0.75rem` (12px) | Inter Regular | Map labels, fine print |

### 2.3 CSS Font Imports

```css
/* Google Fonts — add to <head> or import in CSS */
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,400;0,700;1,400&family=Oswald:wght@700&family=Playfair+Display:ital,wght@0,400;0,700;1,400&display=swap');

/* Font assignments */
:root {
  --font-display: 'Oswald', Impact, Arial Black, sans-serif;
  --font-accent: 'Twister', 'Playfair Display', Georgia, serif;
  --font-body: 'Inter', system-ui, -apple-system, sans-serif;
}

body {
  font-family: var(--font-body);
  font-size: 1rem;
  line-height: 1.6;
  color: var(--color-text);
}

h1 { font-family: var(--font-display); text-transform: uppercase; letter-spacing: 0.02em; }
h2 { font-family: var(--font-accent); }
h3 { font-family: var(--font-body); font-weight: 700; }
```

---

## 3. Layout & Spacing

### 3.1 PPT Layout Patterns

The template uses these recurring layout structures across its 13 slides:

| Pattern | Slides | Description |
|---------|--------|-------------|
| **Hero Split** | 1, 13 | Full-bleed dark background (`#8B1E2D` gradient), giant centered text, brand logo top-left |
| **Text + Image** | 2, 4, 6 | Left half = large heading + body text, Right half = full-height image/shape |
| **Numbered Grid** | 3, 5, 8, 9, 10 | Section heading top-left, numbered items (01, 02, 03) in cards with descriptions |
| **Product Cards** | 7 | Three equal-width cards with image placeholder + description |
| **Timeline** | 6, 11 | Numbered items in vertical sequence with connecting line |
| **Testimonials** | 12 | Numbered quotes with descriptions |

### 3.2 Website Layout Translation

| PPT Pattern | Website Equivalent | Where Used |
|-------------|-------------------|------------|
| Hero Split | Full-width hero banner with gradient | Landing page |
| Text + Image | Split-pane layout (map on one side, controls on other) | Dashboard |
| Numbered Grid | Feature cards with numeric badges | Feature highlights |
| Product Cards | Info cards with icons | Safe zone list, SOS list |
| Timeline | Status timeline | SOS message history |

### 3.3 Spacing Scale

```css
:root {
  --space-xs: 0.25rem;   /* 4px */
  --space-sm: 0.5rem;    /* 8px */
  --space-md: 1rem;      /* 16px */
  --space-lg: 1.5rem;    /* 24px */
  --space-xl: 2rem;      /* 32px */
  --space-2xl: 3rem;     /* 48px */
  --space-3xl: 4rem;     /* 64px */
}
```

### 3.4 Border Radius

The template uses sharp, angular shapes (no rounded corners on cards). The website should follow suit for brand consistency:

```css
:root {
  --radius-none: 0;          /* Cards, buttons — sharp and editorial */
  --radius-sm: 4px;          /* Inputs, small interactive elements */
  --radius-md: 8px;          /* Popups, tooltips, map controls */
  --radius-full: 9999px;     /* Badges, status indicators only */
}
```

---

## 4. Component Design Specs

### 4.1 Buttons

```css
.btn-primary {
  background: var(--color-primary);
  color: var(--color-white);
  font-family: var(--font-body);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: var(--space-sm) var(--space-lg);
  border: none;
  cursor: pointer;
  transition: background 0.2s ease;
}

.btn-primary:hover {
  background: var(--color-primary-hover);
}

.btn-outline {
  background: transparent;
  color: var(--color-primary);
  border: 2px solid var(--color-primary);
  /* same padding and font as btn-primary */
}
```

### 4.2 Cards

```css
.card {
  background: var(--color-white);
  border: 1px solid var(--color-border);
  padding: var(--space-lg);
  box-shadow: 0 2px 8px var(--color-shadow);
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}

.card:hover {
  box-shadow: 0 4px 16px var(--color-shadow);
  transform: translateY(-2px);
}

.card-dark {
  background: var(--color-primary);
  color: var(--color-white);
  border: none;
}
```

### 4.3 Map Popups

The Leaflet popup should match the card style:

```css
.leaflet-popup-content-wrapper {
  background: var(--color-white);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: 0 4px 16px var(--color-shadow);
  font-family: var(--font-body);
}

.popup-title {
  font-family: var(--font-accent);
  color: var(--color-primary);
  font-size: 1.25rem;
  margin-bottom: var(--space-sm);
}

.popup-risk-badge {
  display: inline-block;
  padding: 2px 8px;
  text-transform: uppercase;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.popup-risk-badge.high { background: var(--color-danger); color: white; }
.popup-risk-badge.moderate { background: var(--color-warning); color: white; }
.popup-risk-badge.safe { background: var(--color-safe); color: white; }
```

### 4.4 Chat Interface (Gov-GPT)

```css
.chat-panel {
  background: var(--color-bg-light);
  border-left: 3px solid var(--color-primary);
  font-family: var(--font-body);
}

.chat-bubble-user {
  background: var(--color-primary);
  color: var(--color-white);
  align-self: flex-end;
  padding: var(--space-sm) var(--space-md);
}

.chat-bubble-ai {
  background: var(--color-white);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  align-self: flex-start;
  padding: var(--space-sm) var(--space-md);
}
```

### 4.5 Status Banners (Survival Mode)

```css
.banner-offline {
  background: var(--color-danger);
  color: var(--color-white);
  font-weight: 700;
  text-align: center;
  padding: var(--space-sm) var(--space-md);
}

.banner-low-bandwidth {
  background: var(--color-warning);
  color: var(--color-text);
}

.banner-restored {
  background: var(--color-safe);
  color: var(--color-white);
}
```

---

## 5. Visual Patterns

### 5.1 Background Alternation

The template alternates between warm linen and cream backgrounds. The website should mirror this:

```
Section 1 (Hero):      #8B1E2D gradient → #D64545
Section 2 (Content):   #E9DED1 (warm linen)
Section 3 (Content):   #F5EEE6 (cream) 
Section 4 (Content):   #E9DED1 (warm linen)
...
Footer:                #8B1E2D (dark)
```

### 5.2 Numbered Elements

The template heavily uses large decorative numbers ("01", "02", "03") in Twister font with `#8B1E2D` color as visual anchors. Use this pattern for:
- Feature cards on the landing page
- SOS message items in the list
- Safe zone ranking display

```css
.numbered-item::before {
  content: attr(data-number);
  font-family: var(--font-accent);
  font-size: 3rem;
  color: var(--color-primary);
  opacity: 0.3;
  position: absolute;
  top: -0.5rem;
  left: var(--space-md);
}
```

### 5.3 Text Hierarchy

The template's most striking visual pattern is the **split-level heading**: a large Oswald Bold word in `#D64545` (Coral Red) paired with a smaller Twister word in `#E9DED1` (Warm Linen) slightly overlapping.

Example from Slide 2: "ABOUT" (Oswald, red) + "Us" (Twister, linen)

Translate to the website:
```html
<div class="split-heading">
  <span class="heading-primary">FLOOD</span>
  <span class="heading-accent">Intelligence</span>
</div>
```

```css
.split-heading {
  position: relative;
}
.heading-primary {
  font-family: var(--font-display);
  color: var(--color-primary-light);
  text-transform: uppercase;
}
.heading-accent {
  font-family: var(--font-accent);
  color: var(--color-primary);
}
```

---

## 6. PPT-Specific Design Guide

### 6.1 Slide Mapping for AFIP Presentation

Adapt the 13-slide template to the hackathon presentation:

| Slide # | Template Content | AFIP Adaptation |
|---------|-----------------|-----------------|
| 1 | Brand Presentation (Hero) | **AFIP — Title Slide** "ASSAM FLOOD Intelligence Platform" |
| 2 | About Us | **Problem Statement** — The 3 core problems from the PS |
| 3 | Our Mission (Numbered Grid) | **Our Solution** — 3 pillars: Predict, Alert, Protect |
| 4 | Our Vision (Text + Image) | **Architecture Diagram** — Frontend/Backend/External APIs |
| 5 | Core Values (Numbered Grid) | **Key Features** — 4 headline features with icons |
| 6 | Our Story (Timeline) | **User Journey** — Step-by-step flow from prediction to alert |
| 7 | Products (Cards) | **Live Demo Screenshots** — Map, Chat, Crop Upload |
| 8 | Target Audience (Numbered) | **Target Users** — Government officials, farmers, relief workers |
| 9 | Market Position | **Tech Stack** — Next.js, FastAPI, Llama 3.1, Twilio, Bhashini |
| 10 | Branding Elements | **Innovation** — QLoRA fine-tuning, Survival Mode, Assamese IVR |
| 11 | Marketing & Communication | **Impact & Scalability** — How this scales beyond Assam |
| 12 | Achievements & Testimonials | **Demo Results** — Success metrics from PRD §11 |
| 13 | Thank You | **Thank You + Team** |

### 6.2 PPT Color Usage Rules

- **Dark slides** (1, 13): Use `#8B1E2D` background with `#D64545` and `#E9DED1` text
- **Light slides** (2–12): Use `#E9DED1` or `#F5EEE6` background with `#111111` body text and `#8B1E2D` accents
- **All headings**: Oswald Bold in `#D64545` (Coral Red)
- **All decorative text**: Twister in `#8B1E2D` (Burgundy) or `#E9DED1` (Linen)
- **All body text**: Inter Regular in `#111111`
- **Numbered badges**: Twister 80pt in `#8B1E2D`

### 6.3 Font Installation Checklist

Ensure these fonts are installed on the presenting laptop:
- [ ] Oswald Bold (Google Fonts — free)
- [ ] Twister (custom — must be embedded in PPTX or installed)
- [ ] Inter (Google Fonts — free)

---

## 7. Responsive Considerations (Website Only)

### 7.1 Breakpoints

```css
/* Primary demo target */
@media (min-width: 1366px) { /* Default — demo laptop */ }

/* Fallback */
@media (max-width: 1365px) { /* Slightly smaller screens */ }
@media (max-width: 768px)  { /* Tablet — nice-to-have, not required */ }
```

### 7.2 Dashboard Layout

```
┌─────────────────────────────────────────────────────┐
│  Header: Logo + Nav + Survival Banner               │  64px
├───────────────────────────────────┬──────────────────┤
│                                   │                  │
│         Leaflet Map               │  Side Panel      │
│         (flex: 1)                 │  (380px fixed)   │
│                                   │  Chat / Controls │
│                                   │                  │
├───────────────────────────────────┴──────────────────┤
│  Status Bar: village count, red zones, SOS active    │  40px
└─────────────────────────────────────────────────────┘
```

---

## 8. Icon Style

Use a consistent, minimal icon set. Recommended: **Lucide Icons** (open source, React-friendly, clean line style that pairs well with the editorial template aesthetic).

```bash
npm install lucide-react
```

Key icons needed:
- `AlertTriangle` — flood warnings
- `MapPin` — village markers
- `Phone` — IVR calls
- `MessageSquare` — SMS / Chat
- `Camera` — crop upload
- `Wifi` / `WifiOff` — survival mode
- `Shield` — safe zones

---

## Self-Check

1. All 6 hex colors (`#8B1E2D`, `#D64545`, `#E9DED1`, `#F5EEE6`, `#111111`, `#FFFFFF`) verified against PPTX extraction data. ✅
2. All 3 fonts (Oswald Bold, Twister, Inter) confirmed in extraction output. ✅
3. Font size scale derived from actual PPT sizes (25pt, 30pt, 80pt, 100pt, 130pt, 160pt, 190pt, 250pt). ✅
4. Background color alternation pattern verified across all 13 slides. ✅
5. No conflicts with RULES.md (R23: no Tailwind, R45: Chrome only). ✅
