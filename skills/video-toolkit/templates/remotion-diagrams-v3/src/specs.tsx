import { BRAND } from './brand';
import { NARRATION, cue } from './narration.gen';

export type NodeSpec = { x: number; y: number; w: number; h: number; title: string; sub?: string; focal?: boolean; logo?: string; cornerLogo?: string; small?: boolean; tcolor?: string };
export type ArrowSpec = { x1: number; y1: number; x2: number; y2: number; label?: string; head?: boolean; dashed?: boolean };
export type MonoSpec = { x: number; y: number; w: number; h: number; title?: string; lines: { t: string; hi?: boolean; bad?: boolean }[] };
export type Group = { nodes?: NodeSpec[]; arrows?: ArrowSpec[]; pills?: { x: number; y: number; text: string; color?: string; logo?: string; bare?: boolean }[]; mono?: MonoSpec; atSec?: number };
export type Spec = { id: string; eyebrow?: string; title: string; logo?: string; ms?: boolean; badge?: string; badgeColor?: string; audio: string; audioDur: number; focalAt?: number; dx?: number; dy?: number; groups: Group[] };

const A = BRAND.accentHi, G = BRAND.good, D = BRAND.danger, L = BRAND.line;
const MONO = (lines: MonoSpec['lines'], title: string): MonoSpec => ({ x: 1200, y: 1245, w: 2080, h: 300, title, lines });
// the canonical contract.json card — IDENTICAL on every slide it appears (the user's
// reference box: accent-tint focal, Trustabl shield, "one canonical contract / agent").
const CONTRACT_BOX = (x: number, y: number): NodeSpec => ({ x, y, w: 360, h: 210, title: 'contract.json', sub: 'one contract per agent', focal: true, logo: 'trustabl' });

export const SPECS: Spec[] = [
  {
    id: 'overview', title: 'What Trustabl Produces', logo: 'trustabl', audio: 'sy_overview.mp3', audioDur: NARRATION.overview.dur, dx: 0, dy: 0,
    groups: [
      { nodes: [{ x: 700, y: 720, w: 400, h: 210, title: 'Trustabl', focal: true, logo: 'trustabl' }] },
      { atSec: cue('overview', 2), arrows: [{ x1: 920, y1: 720, x2: 1320, y2: 465 }], nodes: [{ x: 1640, y: 465, w: 600, h: 140, title: 'Detect', sub: 'findings · readiness score', small: true, tcolor: A }] },
      { atSec: cue('overview', 3, 0.05), arrows: [{ x1: 920, y1: 720, x2: 1320, y2: 635 }], nodes: [{ x: 1640, y: 635, w: 600, h: 140, title: 'Describe', sub: 'contract.json · conformance', small: true, tcolor: A }] },
      { atSec: cue('overview', 3, 0.45), arrows: [{ x1: 920, y1: 720, x2: 1320, y2: 805 }], nodes: [{ x: 1640, y: 805, w: 600, h: 140, title: 'Enforce', sub: 'OPA/Rego · ACS · OpenShell', small: true, tcolor: A }] },
      { atSec: cue('overview', 3, 0.75), arrows: [{ x1: 920, y1: 720, x2: 1320, y2: 975 }], nodes: [{ x: 1640, y: 975, w: 600, h: 140, title: 'Prove', sub: 'compliance map · signed snapshot', small: true, tcolor: A }] },
      { atSec: cue('overview', 0, 0.6), pills: [{ x: 1200, y: 1240, text: 'One scan, compiled into every format your stack and your auditors trust' }] },
    ],
  },
  {
    id: 'scan', eyebrow: '01 · Detect', title: 'The Scan', logo: 'trustabl', audio: 'sy_scan.mp3', audioDur: NARRATION.scan.dur, focalAt: cue('scan', 0), dx: 135, dy: -82,
    groups: [
      { nodes: [{ x: 450, y: 720, w: 490, h: 250, title: 'AI Agents', sub: 'tools · subagents · skills · MCP servers · handoffs · guardrails · model' }] },
      { arrows: [{ x1: 715, y1: 720, x2: 850, y2: 720, label: 'audited by' }], nodes: [{ x: 1045, y: 720, w: 350, h: 210, title: 'trustabl scan', sub: 'static analysis', focal: true, logo: 'trustabl' }] },
      { atSec: cue('scan', 5), arrows: [{ x1: 1240, y1: 720, x2: 1510, y2: 540 }, { x1: 1240, y1: 720, x2: 1510, y2: 720 }, { x1: 1240, y1: 720, x2: 1510, y2: 900 }],
        nodes: [{ x: 1730, y: 540, w: 400, h: 120, title: 'Findings', sub: '29 · severity-ranked', small: true }, { x: 1730, y: 720, w: 400, h: 120, title: 'Readiness Score', sub: '96%', small: true, tcolor: A }, { x: 1730, y: 900, w: 400, h: 120, title: 'Inventory', sub: '30 agents · 2 SDKs', small: true }] },
      { atSec: cue('scan', 7), pills: [{ x: 1045, y: 888, text: 'ScanID · deterministic, folds the rules-pack SHA' }] },
      { mono: MONO([{ t: 'Scan summary' }, { t: '  SDKs:            claude_agent_sdk, openai_agents' }, { t: '  Agents found:    30        Subagents: 1' }, { t: '  Findings:        29  (low 27 · high 2)', hi: true }, { t: '  Overall score:   96%', hi: true }], 'trustabl scan · output') },
    ],
  },
  {
    id: 'contract', eyebrow: '02 · Compile', title: 'The Contract', logo: 'trustabl', audio: 'sy_contract.mp3', audioDur: NARRATION.contract.dur, focalAt: cue('contract', 0, 0.75), dx: 160, dy: -55,
    groups: [
      { nodes: [{ x: 360, y: 720, w: 320, h: 190, title: 'Scan Result', sub: 'inventory + findings', focal: true, logo: 'trustabl' }] },
      { nodes: [CONTRACT_BOX(920, 720)], arrows: [{ x1: 540, y1: 720, x2: 720, y2: 720, label: 'compiles' }] },
      { atSec: cue('contract', 6), arrows: [{ x1: 1120, y1: 720, x2: 1265, y2: 480 }, { x1: 1120, y1: 720, x2: 1265, y2: 640 }, { x1: 1120, y1: 720, x2: 1265, y2: 800 }, { x1: 1120, y1: 720, x2: 1265, y2: 960 }],
        nodes: [{ x: 1565, y: 480, w: 560, h: 110, title: 'ACS Manifest', small: true }, { x: 1565, y: 640, w: 560, h: 110, title: 'OPA / Rego Bundle', small: true }, { x: 1565, y: 800, w: 560, h: 110, title: 'Conformance Spec', small: true }, { x: 1565, y: 960, w: 560, h: 110, title: 'OpenShell Policy', small: true }] },
      { mono: MONO([{ t: '"name": "SupportAgent",' }, { t: '"tools": [ "lookup_order",' }, { t: '           "run_diagnostics  [shells_out]",   <- dangerous', bad: true }, { t: '           "submit_refund" ],' }, { t: '"handoffs": ["BillingSpecialist"],', hi: true }, { t: '"input_guards":["block_prompt_injection"], "output_guards":["redact_pii"]', hi: true }], 'contract.json · SupportAgent') },
    ],
  },
  {
    id: 'conformance', eyebrow: '03 · Describe', title: 'The Conformance Spec', logo: 'trustabl', audio: 'sy_conformance.mp3', audioDur: NARRATION.conformance.dur, focalAt: cue('conformance', 1), dx: 195, dy: -127,
    groups: [
      { nodes: [CONTRACT_BOX(360, 720)] },
      { nodes: [{ x: 930, y: 720, w: 380, h: 200, title: 'Conformance Spec', sub: 'expected behavior', focal: true, logo: 'trustabl' }], arrows: [{ x1: 560, y1: 720, x2: 720, y2: 720, label: 'renders' }] },
      { atSec: cue('conformance', 6), nodes: [{ x: 1640, y: 630, w: 380, h: 120, title: 'Runtime Monitor', sub: 'each call vs. expectations', small: true }, { x: 1640, y: 810, w: 380, h: 120, title: 'Verdict', sub: 'allow · deny', small: true, tcolor: G }], arrows: [
        { x1: 1140, y1: 720, x2: 1340, y2: 720, label: 'checked live', head: false },
        { x1: 1340, y1: 630, x2: 1340, y2: 810, head: false },
        { x1: 1340, y1: 630, x2: 1430, y2: 630 },
        { x1: 1340, y1: 810, x2: 1430, y2: 810 },
      ] },
      { mono: MONO([{ t: '"enforce": true,', hi: true }, { t: '"expectations": {' }, { t: '   "allowed_tools": ["lookup_order","run_diagnostics","submit_refund"],', hi: true }, { t: '   "allowed_handoffs": ["BillingSpecialist"],' }, { t: '   "required_input_guards": ["block_prompt_injection"],' }, { t: '   "approval_required_tools": ["run_diagnostics"] }' }], 'conformance · agt_db28092f') },
    ],
  },
  {
    id: 'opa', eyebrow: '04 · Enforce', title: 'Policy as Code', logo: 'opa', audio: 'sy_opa.mp3', audioDur: NARRATION.opa.dur, focalAt: cue('opa', 1), dy: -155,
    groups: [
      { nodes: [CONTRACT_BOX(340, 720)] },
      { nodes: [{ x: 900, y: 720, w: 390, h: 220, title: 'Rego Bundle', sub: 'deny-by-default · compiled', logo: 'opa' }],
        arrows: [{ x1: 540, y1: 720, x2: 685, y2: 720, label: 'compiles' }],
        pills: [{ x: 900, y: 875, text: 'CNCF-graduated · the engine behind Kubernetes admission', color: L }] },
      { atSec: cue('opa', 5), arrows: [{ x1: 1115, y1: 720, x2: 1335, y2: 720, label: 'evaluated by' }], nodes: [{ x: 1520, y: 720, w: 330, h: 150, title: 'OPA', sub: 'decides: allow / deny', small: true }] },
      { atSec: cue('opa', 6), arrows: [{ x1: 1705, y1: 720, x2: 1910, y2: 720, label: 'enforces' }], nodes: [{ x: 2080, y: 720, w: 300, h: 150, title: 'Agent Host', sub: '(enforcement point)', small: true }] },
      { mono: MONO([{ t: 'package trustabl.tool_allowlist', hi: true }, { t: 'default verdict := {"decision": "allow"}' }, { t: '# empty allowlist  -> warn (never deny-all)' }, { t: 'verdict := {"decision":"warn", reason:"unbounded_allowlist"} ...' }, { t: '# tool not on the contract -> deny' }, { t: 'verdict := {"decision":"deny",  reason:"off_contract_tool"} ...', bad: true }], 'tool_allowlist.rego') },
    ],
  },
  {
    id: 'acs', eyebrow: '05 · Enforce', title: 'Microsoft Agent Control Specification', ms: true, audio: 'sy_acs.mp3', audioDur: NARRATION.acs.dur, focalAt: cue('acs', 0, 0.45), dx: 200, dy: -150,
    groups: [
      { nodes: [CONTRACT_BOX(340, 720)] },
      { nodes: [{ x: 900, y: 720, w: 400, h: 220, title: 'ACS Manifest', sub: 'intervention_points + policies', logo: 'ms' }], arrows: [{ x1: 540, y1: 720, x2: 680, y2: 720, label: 'exports' }] },
      { atSec: cue('acs', 4), arrows: [{ x1: 1120, y1: 720, x2: 1300, y2: 720, label: 'evaluated at' }], nodes: [{ x: 1580, y: 720, w: 520, h: 210, title: '8 Lifecycle Checkpoints', sub: 'agent_startup · input · pre_model_call · post_model_call · pre_tool_call · post_tool_call · output · agent_shutdown', small: true }] },
      { atSec: cue('acs', 7), pills: [{ x: 1580, y: 875, text: 'verdict: allow · warn · deny · escalate · transform', color: L }] },
      { mono: MONO([{ t: '"agent_control_specification_version": "0.3.1-beta",' }, { t: '"intervention_points": [', hi: true }, { t: '   { policy.id: "require_input_guard" },' }, { t: '   { policy.id: "tool_allowlist" } ],' }, { t: '"tools": ["lookup_order","run_diagnostics","submit_refund"]' }, { t: '# policies evaluate in Rego / Cedar at fixed checkpoints' }], 'acs · manifest') },
    ],
  },
  {
    id: 'openshell', eyebrow: '06 · Enforce', title: 'NVIDIA OpenShell', logo: 'nvidia', audio: 'sy_openshell.mp3', audioDur: NARRATION.openshell.dur, focalAt: cue('openshell', 2), dx: 68, dy: -130,
    groups: [
      { nodes: [CONTRACT_BOX(360, 745)] },
      { nodes: [
          { x: 1080, y: 745, w: 600, h: 360, title: '' },
          { x: 1080, y: 712, w: 320, h: 100, title: 'The Agent', sub: 'confined to the contract', small: true },
          { x: 945, y: 855, w: 268, h: 96, title: 'Filesystem', sub: 'Landlock isolation', small: true },
          { x: 1215, y: 855, w: 268, h: 96, title: 'Network', sub: 'deny-by-default', small: true, tcolor: D },
        ],
        arrows: [{ x1: 560, y1: 745, x2: 760, y2: 745, label: 'generates policy' }],
        pills: [{ x: 1080, y: 620, text: 'OpenShell Sandbox', color: L, logo: 'nvidia', bare: true }] },
      { atSec: cue('openshell', 5), arrows: [{ x1: 1400, y1: 745, x2: 1705, y2: 745, label: 'enforced at runtime' }], nodes: [{ x: 1905, y: 745, w: 360, h: 150, title: 'Kernel-Level', sub: 'Seccomp · Landlock', small: true }], pills: [{ x: 1080, y: 985, text: "generated from your code · enforced outside the agent, which can't rewrite its own guardrails", color: L }] },
      { mono: MONO([{ t: '# OpenShell policy schema (NVIDIA), what it controls:' }, { t: 'version, filesystem_policy, landlock, process, network_policies', hi: true }, { t: 'network_policies:  pair allowed binaries -> allowed endpoints' }, { t: '' }, { t: 'Trustabl emits a least-privilege policy toward this model from' }, { t: 'the contract, the allowed tools become an enforced sandbox.' }], 'openshell · policy') },
    ],
  },
  {
    id: 'compliance', eyebrow: '07 · Prove', title: 'The Compliance Map', logo: 'owasp', audio: 'sy_compliance.mp3', audioDur: NARRATION.compliance.dur, focalAt: cue('compliance', 2), dx: 190, dy: -92,
    groups: [
      { nodes: [{ x: 320, y: 650, w: 320, h: 200, title: 'Scan Findings', sub: 'severity-ranked', focal: true, logo: 'trustabl' }] },
      { nodes: [{ x: 880, y: 650, w: 410, h: 220, title: 'OWASP LLM Top 10', sub: 'risk taxonomy', logo: 'owasp' }], arrows: [{ x1: 500, y1: 650, x2: 655, y2: 650, label: 'classified as' }] },
      { atSec: cue('compliance', 4), nodes: [{ x: 1640, y: 478, w: 380, h: 74, title: 'NIST 800-53', small: true }, { x: 1640, y: 564, w: 380, h: 74, title: 'ISO 27002', small: true }, { x: 1640, y: 650, w: 380, h: 74, title: 'SOC 2', small: true }, { x: 1640, y: 736, w: 380, h: 74, title: 'EU AI Act', small: true }, { x: 1640, y: 822, w: 380, h: 74, title: 'PCI DSS', small: true }], arrows: [
        { x1: 1105, y1: 650, x2: 1320, y2: 650, label: 'maps to', head: false },
        { x1: 1320, y1: 478, x2: 1320, y2: 822, head: false },
        { x1: 1320, y1: 478, x2: 1430, y2: 478 },
        { x1: 1320, y1: 564, x2: 1430, y2: 564 },
        { x1: 1320, y1: 650, x2: 1430, y2: 650 },
        { x1: 1320, y1: 736, x2: 1430, y2: 736 },
        { x1: 1320, y1: 822, x2: 1430, y2: 822 },
      ] },
      { atSec: cue('compliance', 8), pills: [{ x: 880, y: 880, text: 'maps findings to controls, it does NOT certify compliance', color: BRAND.gold }] },
      { mono: MONO([{ t: '"frameworks": 11,', hi: true }, { t: '"posture": { "needs_attention": 10, "not_evidenced": 6, "evidenced_clean": 1 },', hi: true }, { t: '"flagged_control": { "ISO-27002:8.25", "Secure development life cycle" },' }, { t: '"disclaimer": "...generates evidence toward controls;' }, { t: '               it does not certify compliance."' }], 'compliance.json') },
    ],
  },
  {
    id: 'snapshot', eyebrow: '08 · Prove', title: 'The Signed Snapshot', logo: 'intoto', audio: 'sy_snapshot.mp3', audioDur: NARRATION.snapshot.dur, focalAt: cue('snapshot', 3), dx: 240, dy: -130,
    groups: [
      { nodes: [{ x: 360, y: 720, w: 460, h: 230, title: 'Governance Snapshot', sub: 'scan · rules · digests · policy', focal: true, logo: 'trustabl' }] },
      { arrows: [{ x1: 610, y1: 720, x2: 750, y2: 720, label: 'wrapped in' }], nodes: [{ x: 960, y: 720, w: 380, h: 230, title: 'DSSE Envelope', sub: 'payload + signature', logo: 'intoto' }] },
      { atSec: cue('snapshot', 4), nodes: [{ x: 1600, y: 630, w: 380, h: 110, title: 'Authentic', sub: 'this scan, this commit', small: true, tcolor: G }, { x: 1600, y: 810, w: 380, h: 110, title: 'Tampered', sub: 'one byte off → fails', small: true, tcolor: D }], arrows: [
        { x1: 1170, y1: 720, x2: 1300, y2: 720, label: 'verify', head: false },
        { x1: 1300, y1: 630, x2: 1300, y2: 810, head: false, dashed: true },
        { x1: 1300, y1: 630, x2: 1390, y2: 630, dashed: true },
        { x1: 1300, y1: 810, x2: 1390, y2: 810, dashed: true },
      ] },
      { atSec: cue('snapshot', 3, 0.6), pills: [{ x: 960, y: 875, text: 'rides the same rails as SBOMs & SLSA · CNCF supply-chain', color: L }] },
      { mono: MONO([{ t: '"rules_version": "aa5c508e...",  "contract_id": "ctr_37d245cb",' }, { t: '"readiness_score": 0.955,  "findings_digest": "sha256:f39c9d61...",' }, { t: '"data_ownership": "Trustabl holds the signed index; the customer', hi: true }, { t: '   keeps the raw traces, prompts and responses."' }, { t: '--- snapshot.dsse.json ---' }, { t: '"payloadType": "application/vnd.in-toto+json",  "signatures":[ ... ]' }], 'snapshot.json + dsse') },
    ],
  },
];
