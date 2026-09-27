# Design System: Multi-Language Translation Workspace

## 1. Visual Theme & Atmosphere
An editor-grade linguistic workspace calibrated for distraction-free focus, high legibility, and rapid bilingual translation. The atmosphere feels like an editorial publishing suite—purposeful, quiet, and refined. Visual Density is calibrated at 4/10, Design Variance at 6/10, and Motion Intensity at 5/10.

## 2. Color Palette & Roles
- **Canvas Base** (`#09090B`) — Neutral charcoal canvas background (Zinc-950)
- **Editor Surface** (`#121215`) — Text panel background container (Zinc-900)
- **Subtle Frontier** (`#27272A`) — 1px structural border dividing source & target panes (Zinc-800)
- **Focus Border** (`#3F3F46`) — Active editor outline state (Zinc-700)
- **Signal Azure** (`#3B82F6`) — Primary action accent, swap trigger, and primary CTA
- **Success Mint** (`#10B981`) — Audio synthesis active state, copy confirmation indicator
- **Primary Glyph** (`#F4F4F5`) — Primary headline and editable translation content (Zinc-100)
- **Subdued Text** (`#A1A1AA`) — Character counter, language tags, and auxiliary metadata (Zinc-400)

## 3. Typography Rules
- **Display & Section Headers:** `Satoshi` or `Geist Sans`, track-tighter (`-0.03em`), font-weight 600.
- **Editor & Translation Body:** `Geist Sans`, relaxed line-height (`1.65`), optimal reading measure of max 65ch.
- **Telemetry & Metadata:** `JetBrains Mono`, tabular characters for live word count, character count, and language ISO codes.
- **Banned:** `Inter`, comic fonts, and generic serif typefaces (`Times New Roman`, `Georgia`).

## 4. Component Stylings
- **Dual-Pane Translation Workbench:** Split-screen layout with 1px border separation. Left pane hosts the source input with auto-detection badge; right pane hosts the synthesized translation output.
- **Central Language Swap Anchor:** Circular tactile button centered between source and target language selectors with rotational hover feedback (`rotate(180deg)`).
- **Utility Action Bar:** Subdued bottom rail within each card housing Copy, Text-to-Speech (Audio), Clear, and Word Count pill.
- **Tactile Buttons:** Minimum 44px touch targets with `-translate-y-[1px]` hover and `scale-[0.98]` active feedback.
- **Feedback & Toasts:** Discrete non-modal confirmation banners when text is copied to clipboard.

## 5. Layout Principles
- Split-screen workspace on viewports `>= 768px` maintaining visual parity between source and translated output.
- Strict mobile collapse below `768px`: Single vertical stack placing the source input above the target translation output.
- Container constrained to `max-w-[1400px]` with balanced padding to prevent edge fatigue.

## 6. Motion & Interaction
- Spring physics for language swap button transitions (`stiffness: 120, damping: 18`).
- Smooth fade-in translation text stream.
- Audio wave indicator during speech playback.
- Hardware-accelerated CSS properties only (`transform`, `opacity`).

## 7. Anti-Patterns (Strictly Enforced)
- Zero emojis in UI controls, status messages, and markup. Clean SVG icons only.
- No saturated purple/magenta AI neon glow effects.
- No pure black (`#000000`) backgrounds.
- No centered hero layout or marketing fluff text.
- No fake translation statistics or placeholder testimonials.
