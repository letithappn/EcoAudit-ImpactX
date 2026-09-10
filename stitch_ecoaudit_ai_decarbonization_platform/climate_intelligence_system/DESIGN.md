---
name: Climate Intelligence System
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#44474c'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#75777d'
  outline-variant: '#c5c6cd'
  surface-tint: '#525f75'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#0e1c2f'
  on-primary-container: '#77849c'
  inverse-primary: '#bac7e1'
  secondary: '#1d4ed8'
  on-secondary: '#ffffff'
  secondary-container: '#4069f2'
  on-secondary-container: '#fffbff'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#002114'
  on-tertiary-container: '#069669'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d6e3fe'
  primary-fixed-dim: '#bac7e1'
  on-primary-fixed: '#0e1c2f'
  on-primary-fixed-variant: '#3a475c'
  secondary-fixed: '#dce1ff'
  secondary-fixed-dim: '#b7c4ff'
  on-secondary-fixed: '#001551'
  on-secondary-fixed-variant: '#0039b5'
  tertiary-fixed: '#85f8c4'
  tertiary-fixed-dim: '#68dba9'
  on-tertiary-fixed: '#002114'
  on-tertiary-fixed-variant: '#005137'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.025em
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.01em
  metric-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.02em
  metric-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 22px
  body-md:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  label-md:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.03em
  mono-data:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: '0'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  space-2xs: 0.125rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-base: 1rem
  space-lg: 1.25rem
  space-xl: 1.5rem
  space-2xl: 2rem
  space-3xl: 2.5rem
  space-4xl: 3rem
  gutter-compact: 0.75rem
  gutter-default: 1.25rem
  margin-screen: 1.5rem
---

## Brand & Style

This design system delivers an institutional-grade, audit-ready operational environment for enterprise carbon accounting, supply-chain footprinting, and regulatory decarbonization governance (CSRD, CBAM, SEC, ISSB). The visual philosophy merges high-density analytical utility with structured executive clarity.

The target audience spans Chief Sustainability Officers, financial controllers, carbon auditors, and supply chain analysts who require zero visual ambiguity, mathematically precise data displays, and rapid audit verification workflows. 

The aesthetic is Modern Corporate with Technical Precision: deep obsidian and midnight navy structural framing, cool slate canvases, electric cobalt interaction cues, and verified emerald-teal status indicators. The environment instills authoritative confidence, institutional accountability, and computational rigor.

## Colors

The system uses a four-tier semantic hierarchy anchored by deep midnight navy, purposeful cobalt accents, metric-specific emeralds, and warning ambers:

- **Structural Anchor (Primary - `#0B192C`):** Applied to persistent navigation, brand anchors, table headers, high-level structural sidebars, and critical primary typography. Secondary slate navy (`#0F172A`) serves as nested header backgrounds and deep data segments.
- **Action & Focus (Secondary - `#1D4ED8` & `#2563EB`):** Reserved for primary interactive controls, selected card states, focus rings, interactive chart states, and navigational highlights.
- **Verified Environmental Metrics (Tertiary - `#059669` & `#10B981`):** Applied strictly to validated emissions reductions, verified carbon removal credits, net-zero trajectory positives, and audit sign-offs.
- **System Neutral & Scaffolding (`#64748B`):** Governs structural borders (`#E2E8F0`), muted backgrounds (`#F8FAFC`), subdued card fills (`#F1F5F9`), and supporting metric labels.
- **Caution & Unaudited Warning (`#D97706` / `#F59E0B`):** Dedicated exclusively to unverified Scope 3 estimates, anomalous emission spikes, missing emission factor data, and impending CBAM declaration deadlines.

## Typography

The type scale balances executive scannability with dense computational verification:

- **Headlines & Executive KPI Callouts:** Set in **Plus Jakarta Sans** with tight tracking (`-0.025em` to `-0.01em`). This geometry introduces human-friendly structural authority across dashboard headers, module titles, and carbon ledger cards without compromising corporate discipline.
- **Operational Data & Ledger Content:** Set in **Inter**, configured with tabular numbers (`tnum`) enabled by default across all financial, metric, and percentage tables. This ensures decimal alignment across Scope 1, 2, and 3 emission line items.
- **Labels & Audit Confidence Tags:** Use uppercase or semi-bold micro-variants (`11px` to `13px`) with expanded tracking to maintain maximum contrast and legibility within badges, data cells, and status indicators.

## Layout & Spacing

The architecture operates on an asymmetric dual-pane structure: a fixed structural navigation rail (`80px` collapsed, `256px` expanded) docked to a flexible high-density workspace.

- **Grid System:** Standardized 12-column desktop grid utilizing a `1.25rem` (`20px`) gutter. Data ledger tables scale responsively using full-width containers with horizontal scroll locks for dense tabular columns.
- **Rhythm & Padding:** Interior padding is calculated on an `8px` scale. Card padding standardizes at `1.25rem` (`20px`) for standard cards and `0.75rem` (`12px`) for nested sub-cards or ledger line items to maintain dense metric visibility.
- **Breakpoints & Adaptation:**
  - **Desktop (≥ 1280px):** Full multi-column dashboard with side-by-side Sankey flow maps, ledger breakdowns, and persistent KPI strips.
  - **Tablet (768px – 1279px):** Collapsed primary navy rail, 2-column KPI grid, stacked chart-and-table views with overflow horizontally enabled for audit grids.
  - **Mobile (< 768px):** Structural sidebar converts to an off-canvas drawer; metric cards convert to full-width swipeable carousels; ledger tables adapt into key-value stacked rows.

## Elevation & Depth

The design system minimizes decorative elevation, favoring sharp surface contrast, purposeful borders, and clinical depth layering:

- **Layer 0 (Canvas Base):** Clean, cool white surface (`#FFFFFF` to `#F8FAFC`) framed by the continuous primary midnight navy navigation spine (`#0B192C`).
- **Layer 1 (Card & Module Surfaces):** Pure white `#FFFFFF` bounded by crisp hairline borders (`1px solid #E2E8F0` or `#E5E7EB`). Subtle tonal definition is provided by an ambient low-opacity shadow: `0px 1px 2px 0px rgba(11, 25, 44, 0.04)`.
- **Layer 2 (Selected & Interactive States):** Applied to active report templates, hovered data cards, and focused filter drawers. Border shifts to `1px solid #2563EB` with an ambient ring: `0px 0px 0px 1px #2563EB, 0px 4px 6px -1px rgba(29, 78, 216, 0.08)`.
- **Layer 3 (Modals, Overlays, and Tooltips):** Audit drill-down panels and contextual emission-factor tooltips use clean white elevation anchored by: `0px 10px 15px -3px rgba(11, 25, 44, 0.08), 0px 4px 6px -4px rgba(11, 25, 44, 0.03)` with a precise `1px solid #CBD5E1` outline.

## Shapes

The design system employs refined geometric rounding to balance analytical precision with modern enterprise software standards:

- **Cards & Data Modules:** `0.75rem` (`12px`) to `1rem` (`16px`) radius, creating crisp containment without appearing blunt or sharp.
- **Form Inputs, Filter Controls & Small Buttons:** `0.5rem` (`8px`) corner radius, maintaining structural alignment against tabular grid lines.
- **Badges, Confidence Tags & Status Pills:** Fully rounded (`9999px`), ensuring clear geometric separation between functional containers and informational metadata pills.
- **Chart Bars & Progress Tracks:** Subtle `4px` top/end radiuses on vertical and horizontal data bars to soften digital representations while keeping data baselines flat.

## Components

### Buttons & Interactive Triggers
- **Primary Action:** Solid electric cobalt (`#1D4ED8`) background, white label, `0.5rem` radius, hover state `#1E40AF`, active press `#172554`.
- **Secondary / Audit Confirm:** Deep navy (`#0B192C`) solid background with white text, utilized for formal report generation, sign-offs, and data exports.
- **Ghost / Table Inline:** Transparent background with `#0F172A` text, hovering to `#F1F5F9`. Borderless or hairline `#E2E8F0`.

### Cards & Reporting Selection Modules
- **Standard Card:** Framed with `1px solid #E2E8F0` on white, featuring an inner header banner or graphic showcase zone with light grey/blue backing (`#F8FAFC`).
- **Interactive Report Tile:** Dual-zone layout. Top zone holds the compliance authority logo (e.g., CDP, CSRD, ISSB) on neutral slate; bottom zone contains the title in bold navy and sub-text description. When active, card transitions to a `2px solid #2563EB` border.

### Badges & Audit Confidence Indicators
- **Verified / Compliant:** Background `#ECFDF5`, text `#065F46`, border `#A7F3D0`. Prepended with an emerald verification check.
- **Scope 3 Estimate / In Review:** Background `#FFFBEB`, text `#92400E`, border `#FDE68A`.
- **Anomalous / Non-Compliant:** Background `#FEF2F2`, text `#991B1B`, border `#FECACA`.
- **Confidence Rating:** Pill displaying confidence tiers (e.g., `Grade A — 98% Measured`, `Grade C — 60% Modeled`) set with monospaced data precision.

### High-Density Data Tables & Ledgers
- **Header Rows:** `#F8FAFC` background with `1px solid #E2E8F0` top and bottom dividing borders. Text styled in `label-sm` uppercase navy slate (`#475569`).
- **Data Rows:** `#FFFFFF` background with subtle hover state `#F8FAFC`. Explicit baseline alignment with tabular numeric values (`tnum`), trailing unit markers (`tCO₂e`), and collapsible chevron affordances for hierarchical parent-child category breakdowns.

### Form Inputs & Search Fields
- Crisp input containers with `#FFFFFF` fill, `1px solid #CBD5E1` border, `0.5rem` radius, and `13px` Inter font. Focus states employ a clean `2px` cobalt focus ring (`#2563EB`) with zero displacement.