// Panels that describe a design run: what the system is doing, what the professor decided, how the design scores.
import { Check, CircleCheck, CircleX, TriangleAlert } from 'lucide-react'
import { cn } from '@/lib/cn'
import { dayTime, plural } from '@/lib/format'
import { GATE_NAME } from '@/lib/status'
import type { Approval, Evaluation, Progress, Run } from '@/lib/types'
import { Badge, Card, CardBody, CardHeader, Cradle, Disclosure, Meter } from '@/components/ui'

/** One progress pattern for every long job: what is happening, how far along, and that it is safe to leave. */
export function ProgressPanel({ run }: { run: Run }) {
  const p: Progress = run.progress
  const pct = Math.round((100 * p.done) / Math.max(1, p.total))
  const working = run.status === 'running'
  const title = { queued: run.queue_position > 1 ? 'Waiting for another course to finish' : 'Starting', running: 'ProfsAgent is working on your course', paused: 'Paused', error: 'Stopped on a problem' }[run.status as string] ?? 'Progress'
  return (
    <Card>
      <div className="flex items-center gap-4 px-5 pt-5">
        {working ? <Cradle size={30} /> : <span aria-hidden className="flex size-[30px] items-center justify-center rounded-full bg-white/[0.06] text-ink-3 text-xs font-semibold tnum">{pct}%</span>}
        <div className="min-w-0 flex-1" aria-live="polite">
          <h2 className="text-lg font-semibold text-ink-1">{title}</h2>
          <p className="text-base text-ink-2">{p.current_label ?? 'Finishing'}{working ? '…' : ''}</p>
        </div>
        <span className="hidden text-sm text-ink-3 tnum sm:block">{p.done} of {p.total} steps</span>
      </div>
      <CardBody className="pt-4">
        <Meter value={p.done} max={p.total} tone={run.status === 'error' ? 'rose' : run.status === 'paused' ? 'amber' : 'iris'} label="Steps finished" />
        <ol className="mt-4 grid gap-x-6 gap-y-1 sm:grid-cols-2">
          {p.steps.map((s) => {
            const cur = s.id === p.current
            return (
              <li key={s.id} aria-current={cur ? 'step' : undefined} className={cn('flex items-center gap-2.5 py-1 text-sm', s.done ? 'text-ink-2' : cur ? 'font-medium text-ink-1' : 'text-ink-4')}>
                <span aria-hidden className={cn('flex size-4 shrink-0 items-center justify-center rounded-full border', s.done ? 'border-mint-line bg-mint-soft text-mint-300' : cur ? 'border-iris-line bg-iris-soft' : 'border-line-strong')}>
                  {s.done ? <Check className="size-2.5" strokeWidth={3.5} /> : cur ? <span className={cn('size-1.5 rounded-full bg-iris-400', working && 'animate-pulse')} /> : null}
                </span>
                <span className="min-w-0 truncate">{s.label}</span>
                {s.gate && <span className="rounded bg-white/[0.06] px-1.5 text-2xs text-ink-3">your check</span>}
                <span className="sr-only">{s.done ? '(done)' : cur ? '(now)' : '(not started)'}</span>
              </li>
            )
          })}
        </ol>
        <p className="mt-4 text-sm text-ink-3">{plural(p.ai_calls, 'AI call')} so far; a course usually needs 25–35. You can close this page: the course keeps going on this laptop.</p>
        {p.log.length > 0 && (
          <Disclosure className="mt-3" summary="What the system is doing (technical log)">
            <pre className="max-h-64 overflow-auto rounded-lg border border-line bg-sunken p-3 font-mono text-xs leading-relaxed text-ink-2 whitespace-pre-wrap">{p.log.join('\n')}</pre>
          </Disclosure>
        )}
      </CardBody>
    </Card>
  )
}

function ApprovalRow({ a }: { a: Approval }) {
  const ok = a.decision === 'approve'
  return (
    <li className="relative flex gap-3 pb-5 last:pb-0">
      <span aria-hidden className="absolute left-[9px] top-6 bottom-0 w-px bg-line last:hidden" />
      <span aria-hidden className={cn('relative mt-0.5 flex size-[19px] shrink-0 items-center justify-center rounded-full border', ok ? 'border-mint-line bg-mint-soft text-mint-300' : 'border-line-strong bg-surface-3 text-ink-2')}>
        {ok ? <Check className="size-3" strokeWidth={3} /> : <CircleX className="size-3" />}
      </span>
      <div className="min-w-0 flex-1">
        <p className="text-base text-ink-1">
          <span className="font-medium">{GATE_NAME[a.gate] ?? a.gate}</span>{' '}
          <span className="text-ink-2">{ok ? (a.gate === 'gate0_details' ? 'confirmed' : 'approved') : 'stopped'} by {a.by}</span>
        </p>
        {a.at ? <p className="text-xs text-ink-3">{dayTime(a.at)}</p> : null}
        {a.gate === 'gate0_details' && ok && a.suggested != null && <p className="mt-1 text-sm text-ink-3">{plural(a.suggested, 'detail')} suggested by ProfsAgent; {a.changed ?? 0} changed by you</p>}
        {a.comment ? <p className="mt-1 text-sm text-ink-2">“{a.comment}”</p> : null}
        {a.override && <p className="mt-1.5 flex items-start gap-1.5 text-sm text-amber-300"><TriangleAlert aria-hidden className="mt-0.5 size-3.5 shrink-0" />{plural(a.override.errors, 'thing was', 'things were')} left open at this step.</p>}
        {!!a.edits?.length && (
          <Disclosure className="mt-1.5" summary={`${plural(a.edits.length, 'change')} made by you`}>
            <ul className="space-y-1 border-l border-line pl-3 text-sm text-ink-2">{a.edits.map((x, i) => <li key={i}>{x}</li>)}</ul>
          </Disclosure>
        )}
      </div>
    </li>
  )
}

/** Every decision the professor took on this course, in order. */
export function ReviewRecord({ approvals }: { approvals: Approval[] }) {
  if (!approvals.length) return null
  return (
    <Card>
      <CardHeader title="Review record" description="Who decided what, and when" />
      <CardBody><ol>{approvals.map((a, i) => <ApprovalRow key={i} a={a} />)}</ol></CardBody>
    </Card>
  )
}

const VERDICT: Record<string, { tone: 'mint' | 'amber' | 'rose'; label: string }> = {
  PASS: { tone: 'mint', label: 'All checks pass' },
  REVIEW: { tone: 'amber', label: 'Mostly fine; some items need a person to confirm' },
  FAIL: { tone: 'rose', label: 'Open problems remain' },
}
/** The rule-based evaluation of the finished design (no AI): completeness, alignment, constraints, regulations. */
export function EvaluationSummary({ ev, final }: { ev: Evaluation; final?: boolean }) {
  const v = ev.verdict === 'FAIL' && final ? { tone: 'amber' as const, label: 'Approved with items left open' } : VERDICT[ev.verdict] ?? { tone: 'amber' as const, label: ev.verdict }
  const Icon = v.tone === 'mint' ? CircleCheck : TriangleAlert
  const pct = (n?: number) => (n == null ? null : Math.round(n))
  const rows: { label: string; value: number | null; hint: string }[] = [
    { label: 'Outcomes taught and assessed', value: pct(ev.alignment_min_pct), hint: 'The weakest link between an outcome, where it is taught and where it is assessed' },
    { label: 'Your must-have rules met', value: pct(ev.hard_constraints_satisfied_pct), hint: 'Rules marked as a must in the context step' },
  ]
  return (
    <Card>
      <CardHeader title="Design evaluation" description="Rule checks on the whole design; no AI is involved"
        actions={<Badge tone={v.tone} icon={<Icon aria-hidden />}>{ev.verdict === 'PASS' ? 'Pass' : ev.verdict === 'REVIEW' ? 'Review' : final ? 'Left open' : 'Fail'}</Badge>} />
      <CardBody>
        <p className="text-base text-ink-1">{v.label}.{!!ev.errors && <span className="text-ink-2"> {plural(ev.errors, 'open error')}.</span>}</p>
        <dl className="mt-4 grid gap-4 sm:grid-cols-3">
          {rows.map((r) => r.value != null && (
            <div key={r.label} title={r.hint}>
              <dt className="text-sm text-ink-3">{r.label}</dt>
              <dd className="mt-1 flex items-center gap-3"><span className="w-12 text-lg font-semibold text-ink-1 tnum">{r.value}%</span><Meter value={r.value} tone={r.value >= 100 ? 'mint' : r.value >= 80 ? 'amber' : 'rose'} label={r.label} /></dd>
            </div>
          ))}
          {ev.regulation_ok != null && (
            <div>
              <dt className="text-sm text-ink-3">University regulations</dt>
              <dd className="mt-1 flex items-center gap-2 text-base font-medium text-ink-1">
                {ev.regulation_ok ? <><CircleCheck aria-hidden className="size-4 text-mint-400" />Followed</> : <><CircleX aria-hidden className="size-4 text-rose-400" />A check fails</>}
              </dd>
            </div>
          )}
        </dl>
        {!!ev.review_reasons?.length && (
          <ul className="mt-4 space-y-1.5 border-t border-line pt-3">
            {ev.review_reasons.map((r, i) => <li key={i} className="flex gap-2 text-sm text-ink-2"><TriangleAlert aria-hidden className="mt-0.5 size-3.5 shrink-0 text-amber-400" />{r.replace(/\s*\((?:V[A-Z0-9-]+,?\s*)+\)/g, '')}</li>)}
          </ul>
        )}
      </CardBody>
    </Card>
  )
}
