// The one status vocabulary of the app: every run, check and lecture is described with these words and tones.
import type { Approval, Gate, Run, RunStatus, RunSummary } from './types'

export type Tone = 'neutral' | 'iris' | 'mint' | 'amber' | 'rose'

export const GATES: Gate[] = ['gate0_details', 'gate1_context', 'gate2_outcomes', 'gate3_proposal']
export const GATE_NAME: Record<Gate, string> = {
  gate0_details: 'Details',
  gate1_context: 'Context',
  gate2_outcomes: 'Outcomes',
  gate3_proposal: 'Final sheet',
}
export const GATE_SLUG: Record<Gate, string> = { gate0_details: 'details', gate1_context: 'context', gate2_outcomes: 'outcomes', gate3_proposal: 'final' }
export const SLUG_GATE: Record<string, Gate> = { details: 'gate0_details', context: 'gate1_context', outcomes: 'gate2_outcomes', final: 'gate3_proposal' }
export const GATE_ABOUT: Record<Gate, string> = {
  gate0_details: 'The complete course form, with what ProfsAgent filled in for you',
  gate1_context: 'Topics, rules, and how the course fits with IIIT-D and courses elsewhere',
  gate2_outcomes: 'Course outcomes, learning outcomes and their programme mapping',
  gate3_proposal: 'Weekly plan, assessment, books and the course sheet',
}

export const STATUS: Record<RunStatus, { label: string; tone: Tone }> = {
  queued: { label: 'Waiting to start', tone: 'neutral' },
  running: { label: 'Working', tone: 'iris' },
  waiting: { label: 'Needs you', tone: 'amber' },
  paused: { label: 'Paused: AI quota', tone: 'amber' },
  error: { label: 'Needs attention', tone: 'rose' },
  done: { label: 'Approved', tone: 'mint' },
  stopped: { label: 'Stopped by you', tone: 'neutral' },
}

export function statusLabel(r: Pick<RunSummary, 'status' | 'gate'>): string {
  const s = STATUS[r.status] ?? { label: r.status }
  return r.status === 'waiting' && r.gate ? `Needs you: ${GATE_NAME[r.gate]}` : s.label
}

export type StageState = 'approved' | 'current' | 'working' | 'problem' | 'stopped' | 'upcoming'

/** Where each of the four checks stands, from a full run (approvals known). */
export function stageStates(run: Run): Record<Gate, StageState> {
  const approved = new Set(run.approvals.filter((a) => a.decision === 'approve').map((a) => a.gate))
  const out = {} as Record<Gate, StageState>
  let next = true // the first check that is not approved yet is where the run stands
  for (const g of GATES) {
    if (approved.has(g) || run.status === 'done') {
      out[g] = 'approved'
      continue
    }
    if (!next) {
      out[g] = 'upcoming'
      continue
    }
    next = false
    out[g] =
      run.status === 'waiting' && run.gate === g ? 'current'
      : run.status === 'stopped' ? 'stopped'
      : run.status === 'error' || run.status === 'paused' ? 'problem'
      : run.status === 'waiting' ? 'upcoming'
      : 'working'
  }
  return out
}

/** The same, estimated from a list row (no approvals): everything before the last known check is approved. */
export function stageStatesOf(r: RunSummary): Record<Gate, StageState> {
  const at = r.gate ? GATES.indexOf(r.gate) : -1
  const out = {} as Record<Gate, StageState>
  GATES.forEach((g, i) => {
    if (r.status === 'done') out[g] = 'approved'
    else if (r.status === 'waiting') out[g] = i < at ? 'approved' : i === at ? 'current' : 'upcoming'
    else if (r.status === 'stopped') out[g] = i < at ? 'approved' : i === at ? 'stopped' : 'upcoming'
    else {
      const cur = at + 1 // working on what follows the last check that was answered
      out[g] = i < cur ? 'approved' : i === cur ? (r.status === 'error' || r.status === 'paused' ? 'problem' : 'working') : 'upcoming'
    }
  })
  return out
}

export const approvalOf = (run: Run, g: Gate): Approval | undefined => run.approvals.find((a) => a.gate === g)
export const isBusy = (s: RunStatus) => s === 'queued' || s === 'running'
export const isApproved = (r: Pick<RunSummary, 'status'>) => r.status === 'done'
