# Design — Paldeck · Palworld Pal Editor

A locked visual system for the editor. It changes presentation and interaction only; save parsing, editing behavior, data structures, and routes remain untouched.

## Genre

Modern-minimal game utility: dense enough for expert editing, but calm, legible, and dependable at common Windows display scales.

## Product identity

- Product name in the interface: Paldeck · Pal Editor.
- Product repository: `https://github.com/Guineabear/Palworld-Pal-Editor`.
- The interface contains no legacy promotional links, donation interruptions, social-channel advertising, or previous-maintainer branding.
- Legally required attribution remains in the license and repository history, outside the product interface.

## Macrostructure family

- App views: Paldeck Workbench — persistent command bar, one entity sidebar, selected-entity header, continuous editing canvas, and sticky live summary.
- Entry/auth views: Focused open-save surface — one primary action, recent path, and concise safety guidance.
- Modals: Centered utility surface with clear dismissal and contained scrolling.

## Theme

- Deep blue-charcoal paper surfaces.
- Cyan is the primary selection and action accent.
- Green, amber, and red are reserved for success, experimental warnings, and destructive actions.
- Accent usage stays restrained so Pal icons and technology artwork remain visually dominant.

## Typography

- Display and body: Segoe UI, with Segoe UI Emoji and broadly available fallbacks.
- Mono: Cascadia Mono or Consolas for paths and internal values.
- Headings remain upright and compact.

## Spacing

A named 4-point scale lives in `frontend/palworld-pal-editor-webui/src/assets/tokens.css`. New UI styles use the tokens rather than one-off values.

## Motion

- Short opacity, colour, and transform feedback only.
- No layout animation.
- Reduced-motion mode removes transforms and shortens transitions.

## Microinteractions stance

- Visible keyboard focus on every control.
- Silent success; existing save behavior is preserved.
- Disabled states remain readable and unmistakable.
- Tooltips appear on hover and keyboard focus.

## What every view shares

- The same paper, rule, text, focus, and accent tokens.
- The same control height, corner language, focus ring, and compact typography.
- Responsive containment: no editor panel may force the root viewport wider than the available workspace.

## Technology view

- One row per player level.
- The level marker remains fixed at the left of its row.
- Cards scroll horizontally inside the available row width with a visible scrollbar.
- Cards never expand the editor canvas or get clipped by the viewport.
- Technology is searchable by localized name, category, or internal name.

## Editing views

- Pal box, Player, and Technology are direct sidebar destinations rather than nested tabs or menus.
- Pal editor: Identity, Growth, Work, and Skills appear as named sections in one continuous page.
- Advanced and destructive operations remain visually secondary but are never hidden inside a generic Tools menu.
- The Pal page uses a sticky live summary so users can verify level, stats, and passive count without leaving the form.

## Exports

The canonical CSS export is `frontend/palworld-pal-editor-webui/src/assets/tokens.css`.
