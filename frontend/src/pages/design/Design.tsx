// The design workspace: the four checks on the left, the chosen one on the right. The check that is waiting can be
// edited and decided; earlier ones can be read again exactly as they were approved.
import { useEffect, useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useNavigate, useParams } from 'react-router-dom'
import { RotateCcw } from 'lucide-react'
import { ApiError, api, problemOf, runUrl } from '@/lib/api'
import { startAgain } from '@/lib/actions'
import { dayTime, plural, time, until } from '@/lib/format'
import { useBusy, useTick } from '@/lib/hooks'
import { keys, useOptions, useRefresh, useStage } from '@/lib/queries'
import { GATES, GATE_ABOUT, GATE_NAME, SLUG_GATE, stageStates } from '@/lib/status'
import { toast } from '@/lib/toast'
import type { CourseForm as Form, DetailsView, EditResult, FormErrors, Gate, Gate1View, Gate2View, Gate3View, GateView, Run } from '@/lib/types'
import { ApprovedBadge, Badge, Button, Callout, EmptyState, Ext, GeneratedBadge, Loading } from '@/components/ui'
import { CourseForm, blankForm } from '@/components/app/CourseForm'
import { DecisionBar, type Decided } from '@/components/app/Decision'
import { Findings } from '@/components/app/Findings'
import { ProgressPanel } from '@/components/app/RunPanels'
import { PageBody } from '@/components/app/Shell'
import { StageNav } from '@/components/app/StageRail'
import { useCourse } from '../course/Layout'
import { ContextView } from './Context'
import type { SaveFn } from './editing'
import { FinalSheetView } from './FinalSheet'
import { OutcomesView } from './Outcomes'

const TITLE: Record<Gate, [string, string]> = {
  gate0_details: ['Check the course details', 'Course details'],
  gate1_context: ['Check the course context', 'Course context'],
  gate2_outcomes: ['Check the course outcomes', 'Course outcomes'],
  gate3_proposal: ['Check the final course sheet', 'Final course sheet'],
}

function DetailsIntro({ v, errors }: { v: DetailsView; errors: FormErrors }) {
  const n = Object.keys(v.filled).length
  return (
    <div className="space-y-3">
      {n ? (
        <Callout tone="iris" title={`ProfsAgent filled in ${plural(n, 'detail')}`}>
          Each one is marked, says why, and names what it was based on. Change anything you like; nothing is designed until you confirm.
          {v.similar.length > 0 && <p className="mt-1 text-sm">Similar IIIT-D courses it looked at: {v.similar.map((c, i) => <span key={c.code}>{i > 0 && ' · '}<Ext href={c.url}>{c.code} {c.name ?? ''}</Ext></span>)}</p>}
        </Callout>
      ) : <Callout tone="mint" title="You filled in everything yourself">Check the details, then start the design.</Callout>}
      {v.unfilled.length > 0 && <Callout tone="amber">ProfsAgent couldn’t suggest a value for some fields; please fill them in where marked.</Callout>}
      {Object.keys(errors).length > 0 && <Callout tone="rose" title="Some details are still missing">Fill in the fields marked in red.</Callout>}
    </div>
  )
}

function StageBody({ gate, view, rid, save, final }: { gate: Gate; view: GateView; rid: string; save?: SaveFn; final?: boolean }) {
  if (gate === 'gate1_context') return <ContextView v={view as Gate1View} save={save} />
  if (gate === 'gate2_outcomes') return <OutcomesView v={view as Gate2View} save={save} />
  return <FinalSheetView v={view as Gate3View} rid={rid} save={save} final={final} />
}

function ReadOnlyStage({ run, rid, gate }: { run: Run; rid: string; gate: Gate }) {
  const { data, isLoading, error } = useStage(rid, gate, true)
  const { data: options } = useOptions()
  if (isLoading) return <Loading label="Loading this step" />
  if (!data) return <EmptyState title="Nothing to show for this step">{problemOf(error, 'This step has nothing to show yet.')}</EmptyState>
  if (gate === 'gate0_details') {
    const v = data.view as DetailsView
    if (!options) return <Loading />
    return <CourseForm value={{ ...blankForm(), ...v.form }} onChange={() => {}} errors={{}} options={options} mode="read" />
  }
  return <StageBody gate={gate} view={data.view} rid={rid} final={run.status === 'done'} />
}

function StatusNote({ run, rid }: { run: Run; rid: string }) {
  const nav = useNavigate()
  const refresh = useRefresh()
  const [busy, go] = useBusy()
  useTick(15_000, run.status === 'paused')
  const retry = () => go(async () => { await api.post(runUrl(rid, '/retry')); await refresh(keys.run(rid), keys.runs) }, (e) => toast.error(problemOf(e, 'Could not restart')))
  if (run.status === 'paused') return (
    <Callout tone="amber" title="The free AI quota is used up for now" actions={<Button size="sm" loading={busy} onClick={retry}>Try now</Button>}>
      Your progress is saved. The course continues by itself{run.resume_at ? <> at <b className="font-semibold text-ink-1">{time(run.resume_at)}</b> ({until(run.resume_at)})</> : ' later'}. Gemini’s free daily quota resets at about 1:30 pm IST.
    </Callout>
  )
  if (run.status === 'error') return (
    <Callout tone="rose" title={run.error?.message ?? 'Something went wrong'} actions={<Button size="sm" variant="primary" loading={busy} icon={<RotateCcw aria-hidden />} onClick={retry}>Try again</Button>}>
      Your progress is saved.{run.error?.detail && <span className="mt-1 block font-mono text-xs text-ink-3 [overflow-wrap:anywhere]">{run.error.detail}</span>}
    </Callout>
  )
  if (run.status === 'stopped') {
    const last = run.approvals[run.approvals.length - 1]
    return (
      <Callout tone="neutral" title="You stopped this run here" actions={<Button size="sm" variant="primary" icon={<RotateCcw aria-hidden />} onClick={() => startAgain(rid, nav)}>Start again with changes</Button>}>
        {last?.decision === 'reject' && last.comment ? <>Your reason: “{last.comment}”. </> : null}What ProfsAgent had written is shown below; it was not approved.
      </Callout>
    )
  }
  return null
}

export function DesignPage() {
  const { run, rid, base } = useCourse()
  const { stage } = useParams()
  const nav = useNavigate()
  const qc = useQueryClient()
  const refresh = useRefresh()
  const { data: options } = useOptions()
  const states = stageStates(run)
  const stepDone = (id: string) => !!run.progress.steps.find((s) => s.id === id)?.done
  const available: Record<Gate, boolean> = {
    gate0_details: stepDone('fill_details'),
    gate1_context: stepDone('s3_constraints'),
    gate2_outcomes: stepDone('s4_outcomes'),
    gate3_proposal: stepDone('render'),
  }
  const here = run.status === 'done' ? 'gate3_proposal' : run.status === 'waiting' && run.gate ? run.gate : (GATES.find((g) => states[g] !== 'approved') ?? 'gate3_proposal')
  const active: Gate = (stage && SLUG_GATE[stage]) || here
  const waitingHere = run.status === 'waiting' && run.gate === active && !!run.view
  const idx = GATES.indexOf(active)

  // the details form, while it is the waiting check
  const formView = waitingHere && active === 'gate0_details' ? (run.view as DetailsView) : null
  const [form, setForm] = useState<Form>(() => ({ ...blankForm(), ...(formView?.form ?? {}) }))
  const [errors, setErrors] = useState<FormErrors>({})
  useEffect(() => { if (formView) { setForm({ ...blankForm(), ...formView.form }); setErrors({}) } }, [run.run_id, run.gate, run.status])  // eslint-disable-line react-hooks/exhaustive-deps

  const save: SaveFn = async (section, value) => {
    try {
      const r = await api.post<EditResult>(runUrl(rid, '/edit'), { gate: run.gate, section, value })
      qc.setQueryData(keys.run(rid), r.run)
      const n = r.changes.length
      toast.success(n ? `${plural(n, 'change')} saved and checked again. Open problems: ${r.open_before} → ${r.open_after}.${r.note ? ' ' + r.note : ''}` : 'Nothing changed.')
      return null
    } catch (e) {
      if (e instanceof ApiError && e.status === 422) return Object.keys(e.errors).length ? e.errors : { _: 'Could not save' }
      await refresh(keys.run(rid))
      return { _: problemOf(e, 'Could not save') }
    }
  }

  const decide = async (decision: 'approve' | 'reject', comment: string): Promise<Decided> => {
    const gate = run.gate!
    try {
      await api.post(runUrl(rid, '/decision'), { gate, decision, comment, ...(gate === 'gate0_details' && decision === 'approve' ? { values: form } : {}) })
    } catch (e) {
      if (e instanceof ApiError && e.status === 422) {
        setErrors(e.errors)
        toast.error('Some details are still missing')
        requestAnimationFrame(() => document.querySelector('[aria-invalid="true"]')?.scrollIntoView({ block: 'center', behavior: 'smooth' }))
        return {}
      }
      return { error: problemOf(e, 'Could not send') }
    }
    toast.success(decision === 'reject' ? 'Stopped.' : gate === 'gate0_details' ? 'Details confirmed. ProfsAgent starts designing the course.' : gate === 'gate3_proposal' ? 'Approved. Your course is ready.' : 'Approved. ProfsAgent continues with the next part.')
    await refresh(keys.run(rid), keys.runs, keys.deliveryCourses)
    nav(gate === 'gate3_proposal' && decision === 'approve' ? base : `${base}/design`)
    window.scrollTo(0, 0)
    return {}
  }

  const approval = run.approvals.find((a) => a.gate === active && a.decision === 'approve')
  const live = ['queued', 'running', 'paused', 'error'].includes(run.status)
  const showReadOnly = !waitingHere && available[active] && (states[active] === 'approved' || states[active] === 'stopped' || idx < GATES.indexOf(here))
  const atWork = !waitingHere && !showReadOnly

  return (
    <PageBody width="wide">
      <div className="grid grid-cols-[minmax(0,1fr)] items-start gap-6 lg:grid-cols-[15.5rem_minmax(0,1fr)]">
        <aside className="min-w-0 lg:sticky lg:top-20">
          <StageNav rid={rid} states={states} active={active} available={available} by={Object.fromEntries(run.approvals.filter((a) => a.decision === 'approve').map((a) => [a.gate, a.by]))} />
        </aside>

        <div className="min-w-0 space-y-5">
          <header className="flex flex-wrap items-end justify-between gap-x-6 gap-y-3">
            <div className="min-w-0">
              <p className="label-caps mb-1.5">Step {idx + 1} of 4</p>
              <h2 className="h-display text-2xl text-ink-1 sm:text-3xl">{TITLE[active][waitingHere ? 0 : 1]}</h2>
              <p className="mt-1 text-base text-ink-3">{GATE_ABOUT[active]}</p>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              {waitingHere && active !== 'gate0_details' && <GeneratedBadge>Written by ProfsAgent · not approved yet</GeneratedBadge>}
              {waitingHere && <Badge tone="amber">Waiting for your decision</Badge>}
              {!waitingHere && approval && <ApprovedBadge>Approved by {approval.by}{approval.at ? ` · ${dayTime(approval.at)}` : ''}</ApprovedBadge>}
              {!waitingHere && !approval && states[active] === 'stopped' && <Badge>Not approved</Badge>}
            </div>
          </header>

          {(states[active] === 'problem' || states[active] === 'stopped') && <StatusNote run={run} rid={rid} />}

          {waitingHere && formView && (
            <>
              <DetailsIntro v={formView} errors={errors} />
              {options ? <CourseForm value={form} onChange={(p) => { setForm((f) => ({ ...f, ...p })); setErrors((e) => { const n = { ...e }; for (const k of Object.keys(p)) { delete n[k as keyof FormErrors]; if ('ltp'.includes(k)) delete n.ltp } return n }) }} errors={errors} options={options} mode="review" filled={formView.filled} /> : <Loading />}
            </>
          )}

          {waitingHere && !formView && (
            <>
              <Findings problems={run.problems} canEdit />
              <StageBody gate={active} view={run.view!} rid={rid} save={save} />
            </>
          )}

          {showReadOnly && (
            <>
              {approval?.override && <Callout tone="amber">{plural(approval.override.errors, 'thing was', 'things were')} left open when this step was approved{approval.comment ? <>: “{approval.comment}”</> : '.'}</Callout>}
              <ReadOnlyStage run={run} rid={rid} gate={active} />
            </>
          )}

          {atWork && (live ? <ProgressPanel run={run} /> : states[active] === 'upcoming' ? (
            <EmptyState title={`${GATE_NAME[active]} comes later`}>This step opens once the ones before it are approved.</EmptyState>
          ) : !available[active] && run.status !== 'stopped' ? <EmptyState title="Nothing to show for this step">This course was made outside the app, so this step was not recorded.</EmptyState> : null)}
        </div>
      </div>

      {waitingHere && <DecisionBar key={run.gate} gate={active} problems={run.problems} onDecide={decide} />}
    </PageBody>
  )
}
