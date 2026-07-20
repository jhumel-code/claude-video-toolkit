// Trustabl brand tokens — NAVY skin (2026-07-14: whole video library unified on
// this dark theme, matching the bookends' existing #0D1B2A). Same token names as
// the former light skin so every component/scene that reads BRAND.* re-skins
// automatically with no per-file edits — see components.tsx Header/MonoCard for
// the two spots that needed real logic changes (logo contrast, mono bg).
export const BRAND = {
  // paper: the bookends' navy, so bookend and content scenes are one surface
  paper: '#0D1B2A',
  paper2: '#13233A',
  panel: '#16283F',          // backend/default node fill
  // ink / text (near-white) + light blue-slate muted
  ink: '#E8EBF0',
  sub: 'rgba(232,235,240,0.72)',
  soft: 'rgba(232,235,240,0.50)',
  // hairlines
  line: 'rgba(232,235,240,0.16)',
  lineSolid: '#33445C',
  // accent = the bookends' teal (reads as focal on navy)
  accent: '#51C1B5',
  accentHi: '#7FE0D4',
  accentTint: 'rgba(81,193,181,0.16)',
  // opaque equivalent of accentTint composited over paper — used as focal box fill so the
  // dot grid does not show through the translucent tint.
  panelTint: '#15332F',
  // arrows / links
  link: '#6FA8E8',
  danger: '#FF6B5C',
  good: '#51C1B5',
  gold: '#E0C066',
  nvGreen: '#8FD13F',
  dot: 'rgba(255,255,255,0.09)',
  shadow: '0 6px 22px rgba(0,0,0,0.35), 0 2px 6px rgba(0,0,0,0.25)',
  // code/terminal card background — was a hardcoded light hex in components.tsx
  mono: '#0A1626',
  // solid backing chip for dark-mark vendor logos (OWASP/CNCF/in-toto/OPA are
  // near-black PNGs; without this they vanish on navy — see components.tsx Header)
  logoChip: '#EEF1F4',
};
export const FPS = 60;
// Scale a frame literal that was tuned at 30fps to the current FPS, so animation keyframes
// keep the same wall-clock timing at any fps (identity at 30, ×2 at 60).
export const K = (f: number) => Math.round((f * FPS) / 30);
export const W = 2400;          // design width (16:10 coordinate space — all specs coords live here)
export const H = 1500;          // design height
export const CW = 2560;         // canvas width  (true 16:9 output, renders ×1.5 -> 3840)
export const CH = 1440;         // canvas height (true 16:9 output, renders ×1.5 -> 2160 = 4K)
export const CY = 720;
