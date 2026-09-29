// Trustabl brand tokens — TWO SKINS, selected at render time.
//
//   NAVY  (default) 2026-07-14: the whole video library unified on this dark theme,
//         matching the bookends' existing #0D1B2A. Every composition authored after
//         that date (LgFull, NvFull, SlipDual, SlipLiongard, Spof, network,
//         archetypes, the deepdive/* scenes) is designed against navy.
//   LIGHT 2026-06-26..07-14: the original skin the Artifacts Explainer shipped in
//         (Trustabl-Artifacts-Explained.mp4, rendered 2026-06-29). Restored
//         2026-07-30 to allow re-rendering that video in its delivered look.
//
// Both skins carry identical token names, so any component reading BRAND.* re-skins
// with no per-file edits — see components.tsx Header/MonoCard for the two spots that
// needed real logic changes (logo contrast, mono bg).
//
// SELECT A SKIN with the REMOTION_SKIN env var (navy is the default, so every
// existing render script keeps its current output with no change):
//   REMOTION_SKIN=light npx remotion render src/index.ts Explainer out/x.mp4
const NAVY = {
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

type Skin = typeof NAVY;

// LIGHT skin — the Artifacts Explainer's delivered look, reconstructed 2026-07-30.
// trustabl-remotion/ is not a git repo, so this was recovered from three sources:
//   [frame]  pixel-sampled from the UNGRADED Remotion proofs out/g_*.png + k_*.png
//            (2026-06-29, ~1h before the delivered master) — exact, these are the
//            renderer's own output. NB the 4K master itself is useless for this: it
//            has been through finish.sh, which shifts paper #f3f2ef -> #f3f1ee.
//   [ds]     the diagram-design system this skin was adopted from
//            (demo-video/diagram-design/skills/diagram-design/references/style-guide.md
//            token table, light column), with accent swapped tangerine -> Trustabl teal.
//   [solved] recovered by rendering candidates and minimising pixel delta against the
//            proof in the band that token alone drives. accentHi mattered most: it is
//            NOT a brighter accent as in navy — it is DARKER (#0f6f62 vs accent #16887a),
//            and it drives both focal node titles and mono `hi:` lines, so the first
//            guess (#51c1b5, mis-sampled off the Trustabl logo) was visibly wrong.
//   [est]    NOT recovered. `shadow` is unverifiable from a downscaled proof, and
//            `danger` was only narrowed (#c0392b / #c8392b / #b3392b all score within
//            0.002 mean delta) because it renders as one line of small mono text in the
//            contract + opa sections. Both need a human eye before delivery.
//
// Verified 2026-07-30 against all 7 sections that have a June proof: 97.0-97.7% of pixels
// exactly identical, 99.7-100% within 8/255. Every remaining difference is the later
// em-dash -> comma text edit, not a skin regression.
const LIGHT: Skin = {
  paper: '#f3f2ef',                    // [frame] 69% of every proof — warm white-smoke
  paper2: '#ececec',                   // [ds]
  panel: '#ffffff',                    // [frame] nodes are white, not paper-filled
  ink: '#2d3142',                      // [frame] jet-black, darkest glyph pixel
  sub: '#4f5d75',                       // [ds] blue-slate
  soft: '#7a8399',                      // [ds]
  line: 'rgba(45,49,66,0.12)',          // [ds] ink at 12%
  lineSolid: '#bfc0c0',                 // [ds] silver
  accent: '#16887a',                    // [frame] Trustabl deep teal (replaces tangerine)
  accentHi: '#0f6f62',                  // [solved] DARKER than accent; see note above
  accentTint: 'rgba(22,136,122,0.08)',  // [ds] accent at 8%
  panelTint: '#dfe8e4',                 // [frame] 1.1-1.3% of every proof — focal box fill
  link: '#2e5aa8',                      // [ds]
  danger: '#c0392b',                    // [est] narrowed only; navy #FF6B5C
  good: '#16887a',                      // = accent, as in navy
  gold: '#8f7025',                      // [solved] navy #E0C066
  nvGreen: '#76B900',                   // NVIDIA's own green
  dot: 'rgba(45,49,66,0.09)',           // [ds] inversion rule: same opacity, RGB flipped
  shadow: '0 6px 22px rgba(45,49,66,0.10), 0 2px 6px rgba(45,49,66,0.06)', // [est] soft
  mono: '#fbfbf9',                      // [frame] 13.5-14.4% of every proof — card fill
  logoChip: 'transparent',              // navy-only fix; dark vendor marks read on white
};

const SKIN = (process.env.REMOTION_SKIN ?? 'navy').toLowerCase();
if (SKIN !== 'navy' && SKIN !== 'light') {
  throw new Error(`REMOTION_SKIN must be "navy" or "light", got "${SKIN}"`);
}
export const BRAND: Skin = SKIN === 'light' ? LIGHT : NAVY;

// Two spots need real logic, not just a token: vendor logos and the mono card. Navy backs
// near-black vendor PNGs (OWASP/CNCF/in-toto/OPA) with a light chip or they vanish, which
// also shrinks the mark to fit inside the chip's padding. The light skin renders those marks
// bare at the chip's outer size — that is what the 2026-06-29 Explainer shipped, and the
// difference is visible (its header OWASP mark is 1.41x today's). See components.tsx.
export const LIGHT_SKIN = SKIN === 'light';

export const FPS = 60;
// Scale a frame literal that was tuned at 30fps to the current FPS, so animation keyframes
// keep the same wall-clock timing at any fps (identity at 30, ×2 at 60).
export const K = (f: number) => Math.round((f * FPS) / 30);
export const W = 2400;          // design width (16:10 coordinate space — all specs coords live here)
export const H = 1500;          // design height
export const CW = 2560;         // canvas width  (true 16:9 output, renders ×1.5 -> 3840)
export const CH = 1440;         // canvas height (true 16:9 output, renders ×1.5 -> 2160 = 4K)
export const CY = 720;
