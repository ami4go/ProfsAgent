// The course at a glance: the one thing to do next, the four checks, the record of decisions, and what can be taken away.
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, CircleAlert, CircleCheck, Hourglass, ListChecks, RotateCcw, Square, UserRound } from 'lucide-react'
import { api, problemOf, runUrl } from '@/lib/api'
import { startAgain } from '@/lib/actions'
import { ago, dayTime, plural, time, until } from '@/lib/format'
import { useBusy, useTick } from '@/lib/hooks'
import { keys, useDeliveryCourses, useRefresh } from '@/lib/queries'
import { GATES, GATE_ABOUT, GATE_NAME, GATE_SLUG, stageStates, type StageState } from '@/lib/status'
import { toast } from '@/lib/toast'
import type { Run } from '@/lib/types'
import { Badge, Button, Card, CardBody, CardHeader, Cradle, Disclosure, Field, FileLink, Select, Stars, Textarea } from '@/components/ui'
import { PageBody } from '@/components/app/Shell'
import { ProgressPanel, ReviewRecord } from '@/components/app/RunPanels'
import { useCourse } from './Layout'

export function CourseFiles({ rid, title }: { rid: string; title?: string }) {
  return (
    <div className="grid gap-2 sm:grid-cols-3">
      <FileLink href={runUrl(rid, '/download/pdf')} newTab name="Course sheet" meta="PDF · official layout" />
      <FileLink href={runUrl(rid, '/download/xlsx')} name="IIIT-D course template" meta="Excel · filled in" />
      <FileLink href={runUrl(rid, '/download/md')} name={title ?? 'Full proposal'} meta="Markdown · with appendices" />
    </div>
  )
}

function Hero({ run, rid, base }: { run: Run; rid: string; base: string }) {
  const nav = useNavigate()
  const refresh = useRefresh()
  const [busy, go] = useBusy()
  useTick(15_000, run.status === 'paused')
  const retry = () => go(async () => { await api.post(runUrl(rid, '/retry')); await refresh(keys.run(rid), keys.runs) }, (e) => toast.error(problemOf(e, 'Could not restart')))
  const shell = (tone: string, icon: React.ReactNode, title: React.ReactNode, body: React.ReactNode, actions?: React.ReactNode) => (
    <Card className={`relative overflow-hidden ${tone}`}>
      <div className="flex flex-wrap items-center justify-between gap-x-6 gap-y-4 p-5 sm:p-6">
        <div className="flex min-w-0 items-start gap-4">
          <span aria-hidden className="flex size-11 shrink-0 items-center justify-center rounded-xl border border-line bg-surface-2 [&_svg]:size-5">{icon}</span>
          <div className="min-w-0">
            <p className="label-caps mb-1">What’s next</p>
            <h2 className="text-xl font-semibold text-ink-1">{title}</h2>
            <div className="mt-1 max-w-2xl text-base text-ink-2">{body}</div>
          </div>
        </div>
        {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
      </div>
    </Card>
  )
  if (run.status === 'waiting' && run.gate) {
    const pr = run.problems
    return shell('border-amber-line', <UserRound className="text-amber-300" />, `Your check: ${GATE_NAME[run.gate]}`,
      <>{GATE_ABOUT[run.gate]}. {pr?.blocked ? <span className="text-rose-300">{plural(pr.errors, 'open problem')} to look at.</span> : 'Nothing continues until you decide.'}</>,
      <Button variant="glow" size="lg" to={`${base}/design/${GATE_SLUG[run.gate]}`} iconRight={<ArrowRight aria-hidden />}>Review now</Button>)
  }
  if (run.status === 'queued' || run.status === 'running')
    return shell('border-iris-line', <Cradle size={22} />, run.status === 'queued' ? (run.queue_position > 1 ? 'Waiting for another course to finish' : 'Starting') : 'ProfsAgent is working',
      <span aria-live="polite">{run.progress.current_label ?? 'Finishing'}… You can close this page; the course keeps going on this laptop.</span>,
      <Button to={`${base}/design`} iconRight={<ArrowRight aria-hidden />}>Watch the progress</Button>)
  if (run.status === 'paused')
    return shell('border-amber-line', <Hourglass className="text-amber-300" />, 'Paused: the free AI quota is used up for now',
      <>Your progress is saved. The course continues by itself{run.resume_at ? <> at <b className="font-semibold text-ink-1">{time(run.resume_at)}</b> ({until(run.resume_at)})</> : ' later'}. Gemini’s free daily quota resets at about 1:30 pm IST.</>,
      <Button loading={busy} onClick={retry}>Try now</Button>)
  if (run.status === 'error')
    return shell('border-rose-line', <CircleAlert className="text-rose-300" />, run.error?.message ?? 'Something went wrong',
      <>Your progress is saved.{run.error?.detail && <Disclosure className="mt-1" summary="Technical detail"><p className="font-mono text-xs text-ink-3 [overflow-wrap:anywhere]">{run.error.detail}</p></Disclosure>}</>,
      <Button variant="primary" loading={busy} icon={<RotateCcw aria-hidden />} onClick={retry}>Try again</Button>)
  if (run.status === 'done')
    return shell('border-mint-line', <CircleCheck className="text-mint-400" />, 'Your course is ready',
      <>Approved by {run.by}. Next, plan how each lecture is taught: your own material, slides made for you, learning resources, guest speakers and simulations.</>,
      <Button variant="glow" size="lg" to={`${base}/lectures`} icon={<ListChecks aria-hidden />}>Plan the lectures</Button>)
  const last = run.approvals[run.approvals.length - 1]
  return shell('', <Square className="text-ink-3" />, 'You stopped this run',
    <>{run.gate ? `At the ${GATE_NAME[run.gate]} step` : 'While it was working'}{last?.decision === 'reject' && last.comment ? <>, because: “{last.comment}”</> : ''}. Nothing more happens to it.</>,
    <Button variant="primary" icon={<RotateCcw aria-hidden />} onClick={() => startAgain(rid, nav)}>Start again with changes</Button>)
}

const WORD: Record<StageState, [string, 'mint' | 'amber' | 'iris' | 'rose' | 'neutral']> = {
  approved: ['Approved', 'mint'], current: ['Needs you', 'amber'], working: ['Working', 'iris'], problem: ['Needs attention', 'rose'], stopped: ['Stopped here', 'neutral'], upcoming: ['Not started', 'neutral'],
}
function Steps({ run, base }: { run: Run; base: string }) {
  const st = stageStates(run)
  return (
    <ol className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4" aria-label="The four checks of the design">
      {GATES.map((g, i) => {
        const a = run.approvals.find((x) => x.gate === g && x.decision === 'approve')
        const [word, tone] = WORD[st[g]]
        const can = st[g] !== 'upcoming'
        return (
          <li key={g} className="relative rounded-xl border border-line bg-surface-1 p-4 shadow-1">
            <div className="flex items-center justify-between gap-2">
              <span className="label-caps">Step {i + 1}</span>
              <Badge tone={tone} dot pulse={st[g] === 'working'}>{word}</Badge>
            </div>
            <h3 className="mt-2 text-md font-semibold text-ink-1">{GATE_NAME[g]}</h3>
            <p className="mt-0.5 text-sm text-ink-3">{GATE_ABOUT[g]}</p>
            <div className="mt-3 flex items-center justify-between gap-2 text-xs text-ink-3">
              <span className="truncate">{a ? `${a.by}${a.at ? ` · ${ago(a.at)}` : ''}` : ' '}</span>
              {can && <Button size="sm" variant="ghost" to={`${base}/design/${GATE_SLUG[g]}`} className="-mr-2" iconRight={<ArrowRight aria-hidden />}>{st[g] === 'current' ? 'Review' : 'Open'}</Button>}
            </div>
          </li>
        )
      })}
    </ol>
  )
}

const FB: [string, string][] = [['outcomes', 'Course outcomes'], ['weeks', 'Weekly plan'], ['assessment', 'Assessment'], ['books', 'Books and papers'], ['overall', 'Would you use this as your starting draft?']]
function Feedback({ run, rid }: { run: Run; rid: string }) {
  const { data: prev } = useQuery({ queryKey: ['feedback', rid], queryFn: () => api.get<{ entries: unknown[] }>(runUrl(rid, '/feedback')) })
  const [ratings, setRatings] = useState<Record<string, number>>({})
  const [change, setChange] = useState('')
  const [saved, setSaved] = useState('')
  const [sent, setSent] = useState(false)
  const [err, setErr] = useState('')
  const [busy, go] = useBusy()
  const send = () => go(async () => {
    await api.post(runUrl(rid, '/feedback'), { ratings, change, time_saved: saved, by: run.by })
    setSent(true); setRatings({}); setChange(''); setSaved(''); setErr('')
    toast.success('Feedback saved. Thank you.')
  }, (e) => setErr(problemOf(e, 'Could not save')))
  if (sent) return (
    <Card><CardHeader title="Thank you" description="Your feedback is saved with this course." actions={<Button size="sm" variant="ghost" onClick={() => setSent(false)}>Add more</Button>} /></Card>
  )
  return (
    <Card>
      <CardHeader title="How good is this draft?" description={prev?.entries.length ? `${plural(prev.entries.length, 'earlier answer')} saved. Your ratings help us improve the system.` : 'Your ratings help us improve the system.'} />
      <CardBody>
        <ul className="divide-y divide-line">
          {FB.map(([k, label]) => <li key={k} className="flex flex-wrap items-center justify-between gap-2 py-1.5"><span className="text-base text-ink-2">{label}</span><Stars label={label} value={ratings[k] ?? 0} onChange={(n) => setRatings((r) => ({ ...r, [k]: n }))} /></li>)}
        </ul>
        <div className="mt-4 grid gap-4 sm:grid-cols-[1fr_16rem]">
          <Field label="What would you change?" htmlFor="fb-change" optional><Textarea id="fb-change" rows={2} value={change} onChange={(e) => setChange(e.target.value)} placeholder="CO3 is too vague; the project should be worth more; week 6 is overloaded" /></Field>
          <Field label="Time this saved you" htmlFor="fb-time" optional>
            <Select id="fb-time" value={saved} onChange={(e) => setSaved(e.target.value)}>{['', 'None', 'Under an hour', '1–3 hours', '3–8 hours', 'More than a day'].map((v) => <option key={v} value={v}>{v || 'Choose…'}</option>)}</Select>
          </Field>
        </div>
        {err && <p role="alert" className="mt-2 text-sm text-rose-300">{err}</p>}
        <Button className="mt-4" loading={busy} onClick={send}>Send feedback</Button>
      </CardBody>
    </Card>
  )
}

export function OverviewPage() {
  const { run, rid, base } = useCourse()
  const { data: dc } = useDeliveryCourses()
  const d = dc?.courses.find((c) => c.run_id === rid)
  const live = ['queued', 'running', 'paused', 'error'].includes(run.status)
  const done = run.status === 'done'
  return (
    <PageBody width="wide" className="space-y-6">
      <Hero run={run} rid={rid} base={base} />
      <Steps run={run} base={base} />
      <div className={live || done ? 'grid items-start gap-6 xl:grid-cols-[minmax(0,1fr)_24rem]' : 'grid items-start gap-6 lg:grid-cols-2'}>
        {(live || done) && <div className="min-w-0 space-y-6">
          {live && <ProgressPanel run={run} />}
          {done && (
            <Card>
              <CardHeader title="Take it with you" description="The approved design, in the formats the department asks for" />
              <CardBody><CourseFiles rid={rid} /></CardBody>
            </Card>
          )}
          {done && (
            <Card>
              <CardHeader title="Lecture planning" description={d?.lectures ? `${plural(d.lectures, 'lecture')} in the weekly plan` : 'Opens the weekly plan lecture by lecture'}
                actions={<Button size="sm" to={`${base}/lectures`} iconRight={<ArrowRight aria-hidden />}>Open the lectures</Button>} />
              {d?.lectures ? (
                <CardBody>
                  <dl className="grid grid-cols-3 gap-4">
                    {[['Lectures', d.lectures], ['Planned', d.decided], ['With results', d.with_results]].map(([k, v]) => (
                      <div key={k}><dt className="text-sm text-ink-3">{k}</dt><dd className="text-2xl font-semibold text-ink-1">{v}</dd></div>
                    ))}
                  </dl>
                </CardBody>
              ) : null}
            </Card>
          )}
          {done && <Feedback run={run} rid={rid} />}
        </div>}
        <div className={live || done ? 'min-w-0 space-y-6' : 'contents'}>
          <ReviewRecord approvals={run.approvals} />
          <Card>
            <CardHeader title="Activity" description="What happened to this course" />
            <CardBody>
              <ol className="space-y-2.5">
                {[...run.history].reverse().slice(0, 12).map((h, i) => (
                  <li key={i} className="flex gap-3 text-sm"><time className="w-28 shrink-0 text-ink-3 tnum">{dayTime(h.at)}</time><span className="min-w-0 text-ink-2 [overflow-wrap:anywhere]">{h.event.replace(/gate\d_(\w+)/g, (_, w) => `the ${w} check`)}</span></li>
                ))}
              </ol>
            </CardBody>
          </Card>
        </div>
      </div>
    </PageBody>
  )
}
