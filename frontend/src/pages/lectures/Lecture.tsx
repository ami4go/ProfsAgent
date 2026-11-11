// One lecture: decide how it is taught, watch the work that follows, and review what comes back.
import { useEffect, useRef, useState } from 'react'
import { ArrowLeft, ArrowRight, Check, Paperclip, Star, X } from 'lucide-react'
import { useParams } from 'react-router-dom'
import { ApiError, api, deliveryUrl, enc, problemOf } from '@/lib/api'
import { CHOICES, TASKS, WANTS, WAY_NAME, WAY_ORDER, blankChoices, classTime, lectureStatus, needsProgress, novelIsUseful, reviewCounts, yes, type TimePart } from '@/lib/delivery'
import { plural, stamp } from '@/lib/format'
import { useDelivery } from '@/lib/queries'
import { toast } from '@/lib/toast'
import type { Choices, ChoiceKey, DeliveryView, Lecture } from '@/lib/types'
import { ApprovedBadge, Badge, Button, Callout, Card, CardBody, CardHeader, Checkbox, Cradle, Disclosure, EmptyState, Field, FieldError, Input, Loading, Segmented, Spinner, Tabs, Textarea, type TabItem } from '@/components/ui'
import { ClassTimeBar, WayLegend } from '@/components/app/Charts'
import { PageBody } from '@/components/app/Shell'
import { useCourse } from '../course/Layout'
import { NotApproved } from './Lectures'
import { MixTab, PlanTab } from './Plan'
import { ClipsTab, GuestTab, OwnLinks, ResourcesTab } from './Results'
import { SimCard } from './SimCard'
import { SlidesTab } from './Slides'
import { lectureUrl, useDeliveryAction } from './shared'

type Act = ReturnType<typeof useDeliveryAction>

function TimeCard({ parts }: { parts: TimePart[] }) {
  const total = parts.reduce((s, p) => s + p.minutes, 0)
  const by = new Map<string, number>()
  parts.forEach((p) => by.set(p.way, (by.get(p.way) ?? 0) + p.minutes))
  return (
    <Card>
      <CardHeader title="How the class time is spent" actions={<span className="text-sm text-ink-3">{plural(parts.length, 'part')} · {total} min</span>} />
      <CardBody>
        <ClassTimeBar parts={parts} tall />
        <div className="mt-3 flex flex-wrap items-center justify-between gap-x-6 gap-y-2">
          <WayLegend ways={parts.map((p) => p.way)} pre={parts.some((p) => p.pre)} />
          <p className="text-xs text-ink-3">{WAY_ORDER.filter((w) => by.get(w)).map((w) => `${WAY_NAME[w]} ${by.get(w)} min`).join(' · ')}</p>
        </div>
      </CardBody>
    </Card>
  )
}

function About({ l, novel }: { l: Lecture; novel: boolean }) {
  const list = <T,>(rows: T[] | undefined, f: (x: T) => React.ReactNode) => rows?.length ? <ul className="mt-1.5 space-y-1.5">{rows.map((x, i) => <li key={i} className="text-sm text-ink-2">{f(x)}</li>)}</ul> : <p className="mt-1 text-sm text-ink-4">None</p>
  const Block = ({ title, children }: { title: string; children: React.ReactNode }) => <div className="border-t border-line py-3 first:border-t-0 first:pt-0"><h3 className="label-caps">{title}</h3>{children}</div>
  return (
    <Card>
      <CardHeader title="About this lecture" description="From the approved course design" />
      <CardBody>
        <Block title="Students should be able to">{list(l.los, (x) => <>{x.text} <Badge tone="iris" className="ml-1 align-middle">{x.bloom}</Badge></>)}</Block>
        <Block title="Course outcome it serves">{list(l.cos, (x) => <><b className="font-mono text-xs font-semibold text-ink-1">{x.id}</b> {x.text}</>)}</Block>
        <Block title="Assessed in">{list(l.assessed, (x) => <>{x.id} <span className="text-ink-3">({x.type}, week {x.due_week})</span></>)}</Block>
        <Disclosure className="border-t border-line pt-3" summary="Builds on, leads to, prerequisites, labs">
          <Block title="Builds on">{list(l.builds_on, (x) => <>{x.topic}{x.week ? <span className="text-ink-3"> (week {x.week})</span> : null}</>)}</Block>
          <Block title="Leads to">{list(l.leads_to, (x) => <>{x.topic}{x.week ? <span className="text-ink-3"> (week {x.week})</span> : null}</>)}</Block>
          <Block title="Prerequisite courses">{list(l.prereq, (x) => <><b className="font-semibold text-ink-1">{x.course}</b>{x.kind ? <span className="text-ink-3"> ({x.kind})</span> : null}{x.relied_topics?.length ? `: ${x.relied_topics.join(', ')}` : ''}</>)}</Block>
          <Block title="Labs and practice">
            {list(l.labs, (x) => <>{x.title} <span className="text-ink-3">(week {x.week}{x.tools?.length ? `; ${x.tools.join(', ')}` : ''})</span></>)}
            <p className="mt-1.5 text-xs text-ink-3">{l.hands_on ? 'Hands-on lecture' : 'Not a hands-on lecture'}{l.outside != null ? ` · about ${l.outside} h of work outside class` : ''}</p>
          </Block>
          <Block title="Closest topic already taught at IIIT-D">
            {l.match ? <p className="mt-1 text-sm text-ink-2">{l.match.topic} <span className="text-ink-3">({Math.round(l.match.similarity * 100)}% similar{l.novel && novel ? ', so this is a new topic' : ''})</span></p> : <p className="mt-1 text-sm text-ink-4">None</p>}
          </Block>
        </Disclosure>
      </CardBody>
    </Card>
  )
}

// ------------------------------------------------------------------ how will you teach it
function ChoicesCard({ v, rid, l, saved, onDone, act }: { v: DeliveryView; rid: string; l: Lecture; saved: boolean; onDone: () => void; act: Act }) {
  const [d, setD] = useState<Choices>(() => structuredClone(v.survey[l.id] ?? blankChoices()))
  const [errs, setErrs] = useState<Record<string, string>>({})
  const [busy, setBusy] = useState(false)
  const [link, setLink] = useState('')
  const file = useRef<HTMLInputElement>(null)
  const set = (p: Partial<Choices>) => { setD((x) => ({ ...x, ...p })); setErrs({}) }
  const prev = v.lectures[v.lectures.indexOf(l) - 1]
  const hasRun = !!(v.jobs?.lectures?.[l.id] || v.results[l.id])
  const surl = (rest: string) => deliveryUrl(rid, rest)

  const save = async () => {
    setBusy(true)
    try {
      const r = await api.put<{ start_c?: boolean; refresh?: boolean }>(surl(`/survey/${enc(l.id)}`), d)
      await act(async () => r, r.start_c ? (r.refresh ? 'Saved. Searching again with the new choices.' : 'Saved. The search has started.') : 'Choices saved.')
      onDone()
    } catch (e) {
      if (e instanceof ApiError && e.status === 422) setErrs(e.errors); else toast.error(problemOf(e, 'Could not save'))
    } finally { setBusy(false) }
  }
  const upload = async (files: FileList | null) => {
    if (!files?.length) return
    const fd = new FormData()
    ;[...files].forEach((f) => fd.append('files', f))
    toast('Uploading…')
    try {
      const r = await api.upload<{ saved: string[] }>(surl(`/attachments/${enc(l.id)}`), fd)
      set({ attachments: [...d.attachments, ...r.saved] })
      toast('Attached. Press Save to keep it.')
    } catch (e) { toast.error(problemOf(e, 'Upload failed')) }
  }
  const samePrev = async () => {
    try {
      const r = await api.get<{ answers: Choices }>(surl(`/previous/${enc(l.id)}`))
      setD({ ...blankChoices(), ...r.answers }); setErrs({})
      toast('Filled in from the previous lecture. Press Save to keep it.')
    } catch (e) { toast.error(problemOf(e, 'Not available')) }
  }
  const bulk = (scope: 'week' | 'module') => act(() => api.post<{ applied: string[] }>(surl('/bulk'), { lid: l.id, scope }),
    (r) => r.applied.length ? `Applied to ${plural(r.applied.length, 'lecture')} without choices: ${r.applied.join(', ')}` : 'Every lecture there already has choices; nothing changed.', 'Could not apply')

  const sub = (k: ChoiceKey) => {
    if (d[k] !== 'yes') return null
    if (k === 'attach_material') return (
      <div className="mt-3 space-y-3 border-t border-dashed border-line pt-3">
        <div className="flex flex-wrap items-center gap-2">
          <input ref={file} type="file" multiple className="sr-only" aria-label="Files to attach" onChange={(e) => upload(e.target.files)} />
          <Button size="sm" icon={<Paperclip aria-hidden />} onClick={() => file.current?.click()}>Choose files</Button>
          <Input className="!w-auto min-w-48 flex-1" type="url" aria-label="A link to your material" placeholder="https://… (paste a link)" value={link} onChange={(e) => setLink(e.target.value)} />
          <Button size="sm" onClick={() => { if (!/^https?:\/\/\S+$/.test(link.trim())) return toast.error('Paste a link that starts with http'); set({ attachments: [...d.attachments, link.trim()] }); setLink('') }}>Add link</Button>
        </div>
        {d.attachments.length > 0 && (
          <ul className="flex flex-wrap gap-1.5">{d.attachments.map((x, i) => (
            <li key={i} className="flex h-7 items-center gap-1 rounded-full border border-line-strong pl-2.5 pr-1 text-xs text-ink-2">{x.split('/').pop()}
              <button type="button" aria-label={`Remove ${x.split('/').pop()}`} className="flex size-5 cursor-pointer items-center justify-center rounded-full hover:bg-white/10" onClick={() => set({ attachments: d.attachments.filter((_, k) => k !== i) })}><X className="size-3" /></button></li>
          ))}</ul>
        )}
        <FieldError>{errs.attach}</FieldError>
        <fieldset>
          <legend className="mb-1.5 text-sm text-ink-3">What should be done with it?</legend>
          <div className="flex flex-wrap gap-x-5 gap-y-2">{TASKS.map(([t, n]) => <Checkbox key={t} checked={d.attach_tasks.includes(t)} onChange={(c) => set({ attach_tasks: c ? [...d.attach_tasks, t] : d.attach_tasks.filter((y) => y !== t) })}>{n}</Checkbox>)}</div>
        </fieldset>
        <FieldError>{errs.tasks}</FieldError>
      </div>
    )
    if (k === 'generate_material') return (
      <div className="mt-3 space-y-1.5 border-t border-dashed border-line pt-3">
        <Checkbox checked={!!d._ai_review} onChange={(c) => set({ _ai_review: c })}>Also have a second AI check the slides and their quiz <span className="text-ink-3">(1–2 more AI calls)</span></Checkbox>
        <p className="text-xs text-ink-3">Slides cite only resources you have approved when they are made; approve resources first if you want them cited, or generate again later.</p>
      </div>
    )
    if (k === 'assistance') return (
      <fieldset className="mt-3 border-t border-dashed border-line pt-3">
        <legend className="float-left mb-2 w-full text-sm text-ink-3">What kind of resources?</legend>
        <div className="grid gap-2 sm:grid-cols-2">{WANTS.map((w) => <Checkbox key={w.key} checked={d[w.key] === 'yes'} onChange={(c) => set({ [w.key]: c ? 'yes' : 'no' })}>{w.label}</Checkbox>)}</div>
        <FieldError>{errs.wants}</FieldError>
      </fieldset>
    )
    return null
  }

  return (
    <Card>
      <CardHeader title="How will you teach this lecture?" description="Pick one or more. Nothing is searched or generated until you save."
        actions={saved ? <ApprovedBadge>Choices saved</ApprovedBadge> : <Badge tone="amber">Not planned yet</Badge>} />
      <CardBody>
        <div className="space-y-2">
          {CHOICES.map((c) => {
            const on = d[c.key] === 'yes'
            return (
              <div key={c.key} className={`rounded-lg border px-3.5 py-3 transition-colors duration-150 ${on ? 'border-iris-line bg-iris-soft/50' : 'border-line hover:border-line-strong'}`}>
                <Checkbox checked={on} onChange={(x) => set({ [c.key]: x ? 'yes' : 'no' })} description={c.help ? `${c.help}${c.key === 'attach_material' && !v.material_connected?.attach ? ' Not connected yet.' : ''}` : undefined}><span className="font-medium">{c.label}</span></Checkbox>
                {sub(c.key)}
              </div>
            )
          })}
        </div>
        <FieldError>{errs.none}</FieldError>
        <div className="mt-5 grid gap-5 md:grid-cols-2">
          <div>
            <p className="mb-1.5 text-sm font-medium text-ink-1">How confident are you teaching this topic?</p>
            <Segmented label="Confidence from 1 to 5" value={String(d.confidence ?? '')} onChange={(n) => set({ confidence: +n })} options={[1, 2, 3, 4, 5].map((n) => ({ id: String(n), label: String(n) }))} />
            <p className="mt-1.5 text-xs text-ink-3">1 = not at all, 5 = fully</p>
          </div>
          <Field label="Anything we should know?" htmlFor="d-note" optional><Textarea id="d-note" rows={2} value={d.note ?? ''} placeholder="Students struggle with configuring tool permissions" onChange={(e) => set({ note: e.target.value })} /></Field>
        </div>
        <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-line pt-4">
          <div className="flex flex-wrap gap-2">
            {prev && <Button size="sm" variant="ghost" disabled={!v.survey[prev.id]} title={v.survey[prev.id] ? undefined : 'The previous lecture has no saved choices yet'} onClick={samePrev}>Same as previous lecture</Button>}
          </div>
          <div className="flex gap-2">
            {saved && <Button variant="ghost" onClick={onDone}>Cancel</Button>}
            <Button variant="primary" loading={busy} iconRight={<ArrowRight aria-hidden />} onClick={save}>{saved && hasRun ? 'Save changes' : 'Save and start'}</Button>
          </div>
        </div>
        {saved && <p className="mt-3 text-xs text-ink-3">To copy these choices to lectures that have none yet: <button type="button" className="cursor-pointer underline" onClick={() => bulk('week')}>apply to week {l.week}</button> or <button type="button" className="cursor-pointer underline" onClick={() => bulk('module')}>apply to this module</button>. Files are not copied.</p>}
      </CardBody>
    </Card>
  )
}

function HowCard({ v, rid, l, a, onEdit, act }: { v: DeliveryView; rid: string; l: Lecture; a: Choices; onEdit: () => void; act: Act }) {
  const st = lectureStatus(v, l.id)
  const bulk = (scope: 'week' | 'module') => act(() => api.post<{ applied: string[] }>(deliveryUrl(rid, '/bulk'), { lid: l.id, scope }),
    (r) => r.applied.length ? `Applied to ${plural(r.applied.length, 'lecture')} without choices: ${r.applied.join(', ')}` : 'Every lecture there already has choices; nothing changed.', 'Could not apply')
  return (
    <Card>
      <CardHeader title="How you’ll teach it" actions={<>
        <Button size="sm" variant="ghost" onClick={() => bulk('week')}>Apply to week {l.week}</Button>
        <Button size="sm" variant="ghost" onClick={() => bulk('module')}>Apply to this module</Button>
        <Button size="sm" onClick={onEdit}>Change</Button>
      </>} />
      <CardBody>
        <ul className="flex flex-wrap gap-1.5">{CHOICES.filter((c) => yes(a, c.key)).map((c) => <li key={c.key}><Badge tone="iris" icon={<Check aria-hidden />}>{c.short}</Badge></li>)}</ul>
        <p className="mt-3 flex flex-wrap items-center gap-2 text-sm text-ink-3">
          <Badge tone={st.tone} icon={st.busy ? <Spinner className="!size-3 !border-[1.5px]" /> : undefined}>{st.label}</Badge>
          {a.confidence ? <span>Your confidence: {a.confidence} of 5</span> : null}
          {a.note ? <span>Note: “{a.note}”</span> : null}
        </p>
      </CardBody>
    </Card>
  )
}

// ------------------------------------------------------------------ what is being made
function ProgressCard({ v, rid, l, act }: { v: DeliveryView; rid: string; l: Lecture; act: Act }) {
  const a = v.survey[l.id]!, j = v.jobs?.lectures?.[l.id], r = v.results[l.id], mj = v.jobs?.material?.[l.id], m = v.material?.[l.id]
  const log = v.log?.[l.id] ?? []
  const clean = (s: string) => s.replace(/^\d\d:\d\d:\d\d\s+/, '')
  const start = () => act(() => api.post<{ started: string[] }>(deliveryUrl(rid, '/start'), { lectures: [l.id], refresh: false }), (x) => x.started.length ? 'The search has started.' : 'Nothing to search: choose resources or a guest first.')
  const gen = () => act(() => api.post(deliveryUrl(rid, `/material/${enc(l.id)}/generate`), { ai_review: false, force: false }), 'Making the slides. This takes about 2–3 minutes.', 'Could not start')
  const rows: { label: string; state: React.ReactNode; note: React.ReactNode }[] = []
  const done = <Badge tone="mint" icon={<Check aria-hidden />}>Done</Badge>
  if (yes(a, 'own_material')) rows.push({ label: 'Own material', state: <Badge tone="mint" icon={<Check aria-hidden />}>Covered</Badge>, note: '' })
  if (yes(a, 'attach_material')) rows.push({ label: 'Working with your material', state: <Badge>Not connected yet</Badge>, note: 'Your files and tasks are saved for it.' })
  if (yes(a, 'generate_material')) {
    const label = 'Making slides and notes'
    if (mj?.state === 'running') rows.push({ label, state: <Cradle size={18} />, note: `Writing and checking the slides (about 2–3 minutes)… ${clean(log.filter((x) => /lecture material|slides:/.test(x)).slice(-1)[0] ?? '')}` })
    else if (mj?.state === 'queued') rows.push({ label, state: <Badge>Waiting to start</Badge>, note: 'Another job is running; this one starts after it.' })
    else if (mj?.state === 'error') rows.push({ label, state: <Badge tone="rose">Stopped</Badge>, note: <>{mj.error} <Button size="sm" className="ml-2" onClick={gen}>Generate again</Button></> })
    else if (m) rows.push({ label, state: done, note: `${plural(m.slides, 'slide')} · ${plural(m.errors, 'error')} · ${plural(m.warnings, 'warning')}. Review them under Results → Slides.` })
    else rows.push({ label, state: <Badge>Not started</Badge>, note: <Button size="sm" variant="primary" onClick={gen}>Generate the slides</Button> })
  }
  if (yes(a, 'assistance') || yes(a, 'guest_lecture')) {
    const label = [yes(a, 'assistance') ? 'Finding resources' : '', yes(a, 'guest_lecture') ? 'finding guest speakers' : ''].filter(Boolean).join(' and ').replace(/^./, (x) => x.toUpperCase())
    if (j?.state === 'running') rows.push({ label, state: <Cradle size={18} />, note: clean(log.slice(-1)[0] ?? '') || 'Starting…' })
    else if (j?.state === 'queued') rows.push({ label, state: <Badge>Waiting to start</Badge>, note: 'Another search is running; this one starts after it.' })
    else if (j?.state === 'error') rows.push({ label, state: <Badge tone="rose">Stopped</Badge>, note: <>{j.error} <Button size="sm" className="ml-2" onClick={start}>Try again</Button></> })
    else if (r?.partial) rows.push({ label, state: <Badge tone="amber">Partial</Badge>, note: <>{r.partial.reason || 'Some videos could not be checked against their transcripts'}. Their coverage was judged from title and description. <Button size="sm" className="ml-2" onClick={start}>Finish the search</Button></> })
    else if (r) rows.push({ label, state: done, note: r.generated_at ? `Last run ${stamp(r.generated_at)}` : '' })
    else rows.push({ label, state: <Badge>Not started</Badge>, note: <Button size="sm" variant="primary" onClick={start}>Start the search</Button> })
  }
  return (
    <Card>
      <CardHeader title="Progress" description="Finding resources and speakers takes about 1.5–3 minutes a lecture. You can leave this page; the work continues." />
      <CardBody>
        <ul aria-live="polite" className="divide-y divide-line">
          {rows.map((x) => (
            <li key={x.label} className="grid items-center gap-x-4 gap-y-1 py-2.5 sm:grid-cols-[14rem_7.5rem_1fr]">
              <span className="text-base font-medium text-ink-1">{x.label}</span><span>{x.state}</span><span className="text-sm text-ink-3 [overflow-wrap:anywhere]">{x.note}</span>
            </li>
          ))}
        </ul>
        {log.length > 0 && <Disclosure className="mt-3" summary="What the search did (technical log)"><pre className="max-h-56 overflow-auto rounded-lg border border-line bg-sunken p-3 font-mono text-xs leading-relaxed text-ink-2 whitespace-pre-wrap">{log.join('\n')}</pre></Disclosure>}
      </CardBody>
    </Card>
  )
}

// ------------------------------------------------------------------ what came back
type TabId = 'own' | 'attach' | 'gen' | 'plan' | 'res' | 'clips' | 'guest'
function ResultsCard({ v, rid, base, l, a, act }: { v: DeliveryView; rid: string; base: string; l: Lecture; a: Choices; act: Act }) {
  const r = v.results[l.id], j = v.jobs?.lectures?.[l.id], mix = v.mix?.lectures?.[l.id], mj = v.jobs?.mix?.[l.id]
  const mixBusy = !!mj && (mj.state === 'queued' || mj.state === 'running')
  const hasPlan = !!(r?.components?.length || mix)
  const tabs: TabItem<TabId>[] = []
  if ((yes(a, 'assistance') && hasPlan) || mix) tabs.push({ id: 'plan', label: 'Lecture plan' })
  if (yes(a, 'assistance')) tabs.push({ id: 'res', label: 'Resources', count: r ? (reviewCounts(v, l.id)?.pending || undefined) : undefined })
  if (yes(a, 'generate_material') || v.material?.[l.id]) tabs.push({ id: 'gen', label: 'Slides' })
  if (yes(a, 'guest_lecture')) tabs.push({ id: 'guest', label: 'Guest speakers' })
  if (yes(a, 'assistance') && yes(a, 'want_clips') && !hasPlan) tabs.push({ id: 'clips', label: 'Clip playlist' })
  if (yes(a, 'own_material')) tabs.push({ id: 'own', label: 'My material' })
  if (yes(a, 'attach_material')) tabs.push({ id: 'attach', label: 'Attached material' })
  const [tab, setTab] = useState<TabId | null>(null)
  if (!tabs.length) return null
  const cur = tabs.some((t) => t.id === tab) ? tab! : tabs[0].id
  const running = !!j && (j.state === 'queued' || j.state === 'running')
  const cnt = r && !running && !['gen', 'attach'].includes(cur) ? reviewCounts(v, l.id) : null
  let body: React.ReactNode
  if (cur === 'own') body = <><p className="text-base text-ink-2">Covered by your own material.</p><div className="mt-4"><OwnLinks v={v} rid={rid} lid={l.id} act={act} /></div></>
  else if (cur === 'attach') body = (
    <div className="space-y-3">
      <p className="text-base text-ink-2"><b className="font-semibold text-ink-1">Your material: </b>{a.attachments.length ? a.attachments.map((x) => x.split('/').pop()).join(', ') : 'none yet'}</p>
      <p className="text-base text-ink-2"><b className="font-semibold text-ink-1">Tasks: </b>{a.attach_tasks.map((t) => TASKS.find((x) => x[0] === t)?.[1] ?? t).join(', ') || 'none'}</p>
      <Callout tone="neutral">Working with your files is not connected yet. When it is, its slides, summary, quiz or gap report appear here. Your files are kept in this course’s delivery folder.</Callout>
    </div>
  )
  else if (cur === 'gen') body = <SlidesTab v={v} rid={rid} l={l} act={act} />
  else if (running) body = <div role="status" className="flex items-center gap-3 py-6 text-base text-ink-2"><Cradle />Still searching. The results appear here when the search is done; the page stays usable meanwhile.</div>
  else if (cur === 'plan' && (mix || mixBusy)) body = <MixTab v={v} rid={rid} base={base} l={l} r={r} act={act} />
  else if (!r) body = <p className="py-2 text-base text-ink-3">No results yet. {j?.state === 'error' ? 'The last search stopped; see Progress above.' : 'Start the search under Progress.'}</p>
  else if (cur === 'plan') body = <PlanTab v={v} rid={rid} base={base} l={l} r={r} act={act} />
  else if (cur === 'res') body = r.has_resources ? <ResourcesTab v={v} rid={rid} l={l} a={a} r={r} act={act} /> : <p className="text-base text-ink-3">This lecture was searched for guest speakers only. Save your choices again to search for resources too.</p>
  else if (cur === 'clips') body = <ClipsTab r={r} />
  else body = <GuestTab v={v} rid={rid} base={base} l={l} r={r} act={act} />
  return (
    <Card id="results">
      <div className="flex flex-wrap items-center justify-between gap-3 px-5 pt-4">
        <h2 className="text-md font-semibold text-ink-1">Results</h2>
        {cnt && <p className="text-sm text-ink-3"><b className="font-semibold text-mint-300">{cnt.approved}</b> approved · <b className="font-semibold text-amber-300">{cnt.pending}</b> waiting for you · <b className="font-semibold text-ink-2">{cnt.removed}</b> replaced or rejected</p>}
      </div>
      <div className="px-5"><Tabs label="Results for this lecture" tabs={tabs} value={cur} onChange={setTab} className="mt-1" /></div>
      <CardBody className="pt-5" role="tabpanel">{body}</CardBody>
    </Card>
  )
}

function DeadLinks({ v, rid, lid, act }: { v: DeliveryView; rid: string; lid: string; act: Act }) {
  const dead = (v.health?.dead ?? []).filter((x) => x.lecture === lid)
  return <>{dead.map((x) => (
    <Callout key={x.url} tone="amber" title={`“${x.title}” is no longer available`} actions={<>
      {x.replacement_available && <Button size="sm" onClick={() => act(() => api.post(deliveryUrl(rid, '/review'), { lid, kind: x.kind, key: x.url, decision: 'replace', reason: 'The link no longer works', title: x.title }), 'Replaced with the next-best item')}>Replace it</Button>}
      <Button size="sm" variant="ghost" onClick={() => act(() => api.post(deliveryUrl(rid, '/health/dismiss'), { url: x.url }))}>Dismiss</Button>
    </>}>Checked {stamp(v.health.checked_at)}. {x.replacement_available ? 'Replace it with the next-best item?' : 'There is no next-best item to replace it with.'}</Callout>
  ))}</>
}

export function LecturePage() {
  const { run, rid, base } = useCourse()
  const { lid = '' } = useParams()
  const approved = run.status === 'done'
  const { data: v, isLoading, error, refetch } = useDelivery(rid, approved)
  const act = useDeliveryAction(rid)
  const [editing, setEditing] = useState(false)
  useEffect(() => { setEditing(false) }, [lid])

  if (!approved) return <NotApproved />
  if (isLoading) return <PageBody width="wide"><Loading label="Loading the lecture" /></PageBody>
  if (!v) return <PageBody><EmptyState title="Lecture planning is not available" actions={<Button onClick={() => refetch()}>Try again</Button>}>{problemOf(error)}</EmptyState></PageBody>
  const L = v.lectures, l = L.find((x) => x.id === lid)
  if (!l) return <PageBody><EmptyState title="Lecture not found" actions={<Button to={`${base}/lectures`}>Back to the lectures</Button>} /></PageBody>
  const i = L.indexOf(l), prev = L[i - 1], next = L[i + 1]
  const a = v.survey[l.id], r = v.results[l.id]
  const parts = classTime(v, l.id)
  const novel = novelIsUseful(L)

  return (
    <PageBody width="wide">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Button size="sm" variant="ghost" to={`${base}/lectures`} icon={<ArrowLeft aria-hidden />} className="-ml-2">All lectures</Button>
        <div className="flex gap-2">
          {prev ? <Button size="sm" to={lectureUrl(base, prev.id)} icon={<ArrowLeft aria-hidden />}>{prev.id}</Button> : <Button size="sm" disabled icon={<ArrowLeft aria-hidden />}>Previous</Button>}
          {next ? <Button size="sm" to={lectureUrl(base, next.id)} iconRight={<ArrowRight aria-hidden />}>{next.id}</Button> : <Button size="sm" disabled iconRight={<ArrowRight aria-hidden />}>Next</Button>}
        </div>
      </div>
      <header className="mt-4">
        <p className="text-sm text-ink-3"><span className="font-mono text-iris-300">{l.id}</span> · Week {l.week} · lecture {l.slot} · {Math.round(l.hours * 60)} min · {l.module}</p>
        <h2 className="h-display mt-1.5 text-2xl text-ink-1 sm:text-3xl [text-wrap:balance]">{l.topic}</h2>
        <div className="mt-2 flex flex-wrap gap-1.5">
          {l.novel && novel && <Badge tone="amber" icon={<Star aria-hidden />}>New topic</Badge>}
          {l.continues && <Badge>Continues in the next lecture</Badge>}
          {r?.continuation_of && <Badge>Continues {r.continuation_of}</Badge>}
        </div>
        {l.summary && <p className="mt-3 max-w-[50rem] text-md leading-relaxed text-ink-2">{l.summary}</p>}
      </header>

      <div className="mt-6 grid items-start gap-6 xl:grid-cols-[minmax(0,1fr)_21rem]">
        <div className="min-w-0 space-y-5">
          <DeadLinks v={v} rid={rid} lid={l.id} act={act} />
          {parts && <TimeCard parts={parts} />}
          {!a || editing ? <ChoicesCard key={l.id} v={v} rid={rid} l={l} saved={!!a} onDone={() => setEditing(false)} act={act} /> : <HowCard v={v} rid={rid} l={l} a={a} onEdit={() => setEditing(true)} act={act} />}
          {a && needsProgress(v, l.id) && <ProgressCard v={v} rid={rid} l={l} act={act} />}
          {a && <ResultsCard key={l.id + '-r'} v={v} rid={rid} base={base} l={l} a={a} act={act} />}
          <SimCard v={v} rid={rid} l={l} act={act} />
        </div>
        <aside className="min-w-0 xl:sticky xl:top-20"><About l={l} novel={novel} /></aside>
      </div>
    </PageBody>
  )
}
