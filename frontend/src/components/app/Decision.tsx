// The professor's decision at a check. Approving is always explicit: a dialog says what is being approved, what happens
// next, and asks for a reason when problems are still open.
import { useState } from 'react'
import { ArrowRight, Check, CircleStop, ShieldAlert } from 'lucide-react'
import { Badge, Button, Field, Modal, Textarea } from '@/components/ui'
import { GATE_NAME } from '@/lib/status'
import { plural } from '@/lib/format'
import type { Gate, Problems } from '@/lib/types'

const NEXT: Record<Gate, string[]> = {
  gate0_details: ['Your completed form becomes the brief for the design.', 'ProfsAgent reads it, finds related IIIT-D courses and similar courses elsewhere, and turns your wishes into rules.', 'You check the course context next.'],
  gate1_context: ['The topics, rules and prerequisites on this page are fixed for the design.', 'ProfsAgent writes the course outcomes and learning outcomes.', 'You check the outcomes next.'],
  gate2_outcomes: ['These outcomes and their programme mapping are fixed.', 'ProfsAgent plans modules and weeks, labs and assessment, finds and checks books, and fills in the course sheet.', 'You check the final course sheet next.'],
  gate3_proposal: ['The course is saved as approved by you.', 'The course sheet (PDF, Excel template) is final and can be downloaded.', 'Lecture planning opens for this course.'],
}
const APPROVE_LABEL: Record<Gate, string> = { gate0_details: 'Confirm and start the design', gate1_context: 'Approve the context', gate2_outcomes: 'Approve the outcomes', gate3_proposal: 'Approve the course' }

/** What came of a decision: `error` keeps the dialog open and shows the sentence; otherwise the dialog closes. */
export type Decided = { error?: string }
interface BarProps { gate: Gate; problems?: Problems; onDecide: (decision: 'approve' | 'reject', comment: string) => Promise<Decided> }

export function DecisionBar({ gate, problems, onDecide }: BarProps) {
  const [mode, setMode] = useState<null | 'approve' | 'reject'>(null)
  const [text, setText] = useState('')
  const [local, setLocal] = useState('')
  const [busy, setBusy] = useState(false)
  const error = ''
  const blocked = !!problems?.blocked
  const open = (m: 'approve' | 'reject') => { setText(''); setLocal(''); setMode(m) }
  const submit = () => {
    if (mode === 'reject' && !text.trim()) return setLocal('Say briefly why you are stopping.')
    if (mode === 'approve' && blocked && !text.trim()) return setLocal('Give a reason for continuing despite the open problems.')
    setBusy(true)
    onDecide(mode!, text.trim()).then((r) => {
      setBusy(false)
      if (r.error) setLocal(r.error)
      else setMode(null)
    })
  }
  return (
    <>
      <div className="fixed inset-x-0 bottom-0 z-20 lg:left-[16rem]">
        <div className="glass-strong border-t border-line-strong">
          <div className="mx-auto flex max-w-[84rem] flex-wrap items-center justify-between gap-3 px-4 py-3 sm:px-6">
            <div className="min-w-0">
              <p className="flex flex-wrap items-center gap-2 text-base font-medium text-ink-1">
                Your decision: {GATE_NAME[gate]}
                {blocked ? <Badge tone="rose" icon={<ShieldAlert aria-hidden />}>{plural(problems!.errors, 'open problem')}</Badge> : <Badge tone="mint" icon={<Check aria-hidden />}>Ready to approve</Badge>}
              </p>
              <p className="hidden text-xs text-ink-3 sm:block">Nothing continues until you decide. Your decision is recorded with your name.</p>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <Button variant="ghost" icon={<CircleStop aria-hidden />} onClick={() => open('reject')}>Stop this run</Button>
              <Button variant="glow" size="lg" iconRight={<ArrowRight aria-hidden />} onClick={() => open('approve')}>{blocked ? 'Continue anyway…' : `${APPROVE_LABEL[gate]}…`}</Button>
            </div>
          </div>
        </div>
      </div>

      <Modal open={mode === 'approve'} onOpenChange={(o) => !o && setMode(null)} sticky size="md"
        banner={<div aria-hidden className="h-1.5 bg-gradient-to-r from-iris-500 via-iris-400 to-mint-400" />}
        title={APPROVE_LABEL[gate]} description={`Step ${['gate0_details', 'gate1_context', 'gate2_outcomes', 'gate3_proposal'].indexOf(gate) + 1} of 4 · ${GATE_NAME[gate]}`}
        footer={<>
          <Button variant="ghost" onClick={() => setMode(null)}>Not yet</Button>
          <Button variant="primary" loading={busy} icon={<Check aria-hidden />} onClick={submit}>{blocked ? 'Approve with this reason' : APPROVE_LABEL[gate]}</Button>
        </>}>
        <p className="label-caps mb-2">What happens when you approve</p>
        <ul className="space-y-2">
          {NEXT[gate].map((s) => (
            <li key={s} className="flex gap-2.5 text-base text-ink-2"><span aria-hidden className="mt-1 flex size-4 shrink-0 items-center justify-center rounded-full bg-iris-soft text-iris-300"><Check className="size-2.5" strokeWidth={3.5} /></span>{s}</li>
          ))}
        </ul>
        {blocked && (
          <div className="mt-4 rounded-lg border border-rose-line bg-rose-soft px-3.5 py-3 text-sm text-rose-300">
            <b className="font-semibold">{plural(problems!.errors, 'problem')} still open.</b> You can continue, but your reason is recorded as an override on the course sheet.
          </div>
        )}
        <Field className="mt-4" htmlFor="decision-note" label={blocked ? 'Reason for continuing' : 'Note for the record'} optional={!blocked} error={local || error}>
          <Textarea id="decision-note" rows={3} autoFocus={blocked} value={text} invalid={!!(local || error)} onChange={(e) => { setText(e.target.value); setLocal('') }}
            placeholder={blocked ? 'The research project covers PO3; its assessment will be added later' : 'Anything you want recorded with this step'} />
        </Field>
      </Modal>

      <Modal open={mode === 'reject'} onOpenChange={(o) => !o && setMode(null)} sticky size="sm" title="Stop this run?"
        description="The run ends at this step. You can start again with the same form and change it."
        footer={<>
          <Button variant="ghost" onClick={() => setMode(null)}>Keep reviewing</Button>
          <Button variant="danger" loading={busy} icon={<CircleStop aria-hidden />} onClick={submit}>Stop the run</Button>
        </>}>
        <Field htmlFor="stop-why" label="Why are you stopping?" error={local || error} hint="It helps us improve the system.">
          <Textarea id="stop-why" rows={3} autoFocus value={text} invalid={!!(local || error)} onChange={(e) => { setText(e.target.value); setLocal('') }}
            placeholder="The outcomes don’t match what I teach; I’ll change the topics and start again" />
        </Field>
      </Modal>
    </>
  )
}
