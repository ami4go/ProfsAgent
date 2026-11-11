// A course's lectures, week by week: which are planned, how their class time is spent, and what waits for review.
import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import DOMPurify from 'dompurify'
import { ArrowRight, Check, FileText, FlaskConical, Layers, Link2, Sparkles, Star } from 'lucide-react'
import { api, deliveryUrl, problemOf } from '@/lib/api'
import { classTime, lectureStatus, novelIsUseful, simApproved, simsOf, slidesStatus, type Way } from '@/lib/delivery'
import { plural, store } from '@/lib/format'
import { useBusy } from '@/lib/hooks'
import { useDelivery } from '@/lib/queries'
import type { DeliveryView, Lecture } from '@/lib/types'
import { Badge, Button, Callout, Checkbox, EmptyState, Loading, Modal, Segmented, Select, Skeleton, Spinner } from '@/components/ui'
import { ClassTimeBar, WayLegend } from '@/components/app/Charts'
import { PageBody } from '@/components/app/Shell'
import { useCourse } from '../course/Layout'
import { lectureUrl, useDeliveryAction } from './shared'

type StatusFilter = 'all' | 'undecided' | 'review' | 'decided'
interface Filter { status: StatusFilter; week: string; module: string; novel: boolean }

export function NotApproved() {
  const { base } = useCourse()
  return <PageBody><EmptyState icon={<Layers />} title="Lecture planning opens once the design is approved" actions={<Button to={`${base}/design`}>Go to the design</Button>}>Approve the final course sheet first; then every lecture of the weekly plan can be planned here.</EmptyState></PageBody>
}

function WeeksDialog({ v, rid, open, onClose, preset }: { v: DeliveryView; rid: string; open: boolean; onClose: () => void; preset: number[] }) {
  const act = useDeliveryAction(rid)
  const weeks = [...new Set(v.lectures.map((l) => l.week))]
  const [picked, setPicked] = useState<number[]>(preset)
  const [material, setMaterial] = useState(true)
  const [resources, setResources] = useState(true)
  const [ai, setAi] = useState(false)
  const [busy, go] = useBusy()
  const [err, setErr] = useState('')
  useEffect(() => { if (open) { setPicked(preset); setErr('') } }, [open])  // eslint-disable-line react-hooks/exhaustive-deps
  const n = v.lectures.filter((l) => picked.includes(l.week)).length
  const start = () => go(async () => {
    const r = await api.post<{ started_slides: string[]; started_resources: string[]; skipped: unknown[] }>(deliveryUrl(rid, '/weeks'), { weeks: picked, material, resources, ai_review: material && ai })
    const s = r.started_slides.length, c = r.started_resources.length
    await act(async () => r, (s || c ? `Started: ${[s ? `slides for ${s}` : '', c ? `resources for ${c}` : ''].filter(Boolean).join(', ')} lecture${s + c === 1 ? '' : 's'}.` : 'Nothing new to start: those lectures already have it.') + (r.skipped.length ? ` Skipped ${r.skipped.length}.` : ''))
    onClose()
  }, (e) => setErr(problemOf(e, 'Could not start')))
  return (
    <Modal open={open} onOpenChange={(o) => !o && onClose()} title="Make material for chosen weeks" size="md"
      description="Every lecture in the weeks you tick gets what you choose below. Choices already saved for a lecture are kept; slides already made are not made again."
      footer={<><Button variant="ghost" onClick={onClose}>Cancel</Button><Button variant="primary" loading={busy} disabled={!n || !(material || resources)} onClick={start}>{n ? `Start for ${plural(n, 'lecture')}` : 'Choose weeks first'}</Button></>}>
      <fieldset>
        <legend className="label-caps mb-2">Weeks</legend>
        <div className="grid grid-cols-2 gap-x-4 gap-y-2 sm:grid-cols-3">
          {weeks.map((k) => {
            const ls = v.lectures.filter((l) => l.week === k), made = ls.filter((l) => v.material?.[l.id]).length
            return <Checkbox key={k} checked={picked.includes(k)} onChange={(c) => setPicked(c ? [...new Set([...picked, k])] : picked.filter((x) => x !== k))} description={`${plural(ls.length, 'lecture')}${made ? `, ${made} with slides` : ''}`}>Week {k}</Checkbox>
          })}
        </div>
        <div className="mt-3 flex gap-2"><Button size="sm" variant="ghost" onClick={() => setPicked(weeks)}>All weeks</Button><Button size="sm" variant="ghost" onClick={() => setPicked([])}>None</Button></div>
      </fieldset>
      <fieldset className="mt-5 space-y-2.5 border-t border-line pt-4">
        <legend className="label-caps float-left mb-2 w-full">What to make</legend>
        <Checkbox checked={material} onChange={setMaterial} description="About 2–3 minutes a lecture">Slides, notes and quiz</Checkbox>
        <Checkbox checked={resources} onChange={setResources} description="About 3–6 minutes a lecture">Videos and readings, and the lecture plan</Checkbox>
        {material && <Checkbox checked={ai} onChange={setAi}>Have a second AI check the slides</Checkbox>}
      </fieldset>
      {err && <p role="alert" className="mt-3 text-sm text-rose-300">{err}</p>}
    </Modal>
  )
}

function ReportDialog({ rid, open, onClose }: { rid: string; open: boolean; onClose: () => void }) {
  const { data, isLoading, error } = useQuery({ queryKey: ['delivery-report', rid], queryFn: () => api.get<{ html: string }>(deliveryUrl(rid, '/report')), enabled: open, retry: false, staleTime: 0 })
  return (
    <Modal open={open} onOpenChange={(o) => !o && onClose()} size="xl" title="Course report" description="What was searched, found and chosen for each lecture">
      {isLoading && <div className="space-y-3"><Skeleton className="h-5 w-1/2" /><Skeleton className="h-3 w-full" /><Skeleton className="h-3 w-3/4" /></div>}
      {error && <p className="text-base text-ink-3">No course report yet: it is written after the first search.</p>}
      {data && <div className="prose-app" dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(data.html) }} />}
    </Modal>
  )
}

function LectureRow({ l, v, base, bar, novel }: { l: Lecture; v: DeliveryView; base: string; bar: boolean; novel: boolean }) {
  const a = v.survey[l.id], st = lectureStatus(v, l.id), sl = a && st.label.startsWith('Slides') ? null : slidesStatus(v, l.id)
  const sims = simsOf(v, l.id).items
  return (
    <li>
      <Link to={lectureUrl(base, l.id)} className="group grid grid-cols-[1fr_auto] items-center gap-x-4 gap-y-2 rounded-xl border border-line bg-surface-1 px-4 py-3 no-underline shadow-1 transition-[border-color,background-color] duration-150 hover:border-line-strong hover:bg-surface-2 md:grid-cols-[4.5rem_minmax(0,1fr)_3.5rem_minmax(7rem,13rem)_auto]">
        <span className="hidden font-mono text-sm font-medium text-iris-300 md:block">{l.id}</span>
        <span className="min-w-0">
          <span className="block truncate text-base font-medium text-ink-1">{l.topic}</span>
          <span className="mt-0.5 flex flex-wrap items-center gap-x-2 gap-y-1 text-sm text-ink-3">
            <span className="font-mono text-xs md:hidden">{l.id}</span>
            <span className="truncate">{l.module}{l.continues ? ' · continues in the next lecture' : ''}</span>
            {l.novel && novel && <Badge tone="amber" icon={<Star aria-hidden />} title="No IIIT-D course teaches a close match, so it likely needs the most preparation">New topic</Badge>}
          </span>
        </span>
        <span className="hidden whitespace-nowrap text-sm text-ink-3 tnum md:block">{Math.round(l.hours * 60)} min</span>
        {bar ? <ClassTimeBar parts={classTime(v, l.id)} className="col-span-2 row-start-2 md:col-span-1 md:row-start-auto" /> : <span className="hidden md:block" />}
        <span className="col-start-2 row-start-1 flex max-w-[22rem] flex-wrap items-center justify-end gap-1.5 md:col-start-auto md:row-start-auto">
          {a ? <Badge tone={st.tone} icon={st.busy ? <Spinner className="!size-3 !border-[1.5px]" /> : undefined}>{st.label}</Badge>
            : <span className="inline-flex items-center gap-1 text-sm font-medium text-iris-300">Plan <ArrowRight aria-hidden className="size-3.5 transition-transform group-hover:translate-x-0.5" /></span>}
          {sl && <Badge tone={sl.tone}>{sl.label}</Badge>}
          {sims.some(simApproved) ? <Badge tone="mint" icon={<Check aria-hidden />}>Simulation</Badge> : sims.some((i) => !i.decision && !i.retired) ? <Badge tone="iris" icon={<FlaskConical aria-hidden />}>Simulation suggested</Badge> : null}
        </span>
      </Link>
    </li>
  )
}

export function LecturesPage() {
  const { run, rid, base } = useCourse()
  const approved = run.status === 'done'
  const { data: v, isLoading, error, refetch } = useDelivery(rid, approved)
  const act = useDeliveryAction(rid)
  const [f, setF] = useState<Filter>(() => ({ status: 'all', week: 'all', module: 'all', novel: false, ...store.json<Partial<Filter>>(`profsagent-dfilter-${rid}`, {}) }))
  const [weeksOpen, setWeeksOpen] = useState(false)
  const [reportOpen, setReportOpen] = useState(false)
  const set = (p: Partial<Filter>) => setF((x) => { const n = { ...x, ...p }; store.set(`profsagent-dfilter-${rid}`, JSON.stringify(n)); return n })

  if (!approved) return <NotApproved />
  if (isLoading) return <PageBody width="wide"><Loading label="Loading the lectures" /></PageBody>
  if (!v) return <PageBody><EmptyState title="Lecture planning is not available" actions={<Button onClick={() => refetch()}>Try again</Button>}>{problemOf(error, 'The lectures could not be loaded.')}</EmptyState></PageBody>

  const L = v.lectures
  const isReview = (l: Lecture) => !!lectureStatus(v, l.id).review
  const counts = { all: L.length, undecided: L.filter((l) => !v.survey[l.id]).length, review: L.filter(isReview).length, decided: L.filter((l) => v.survey[l.id]).length }
  const mods = [...new Set(L.map((l) => l.module))]
  const showNovel = novelIsUseful(L)
  const list = L.filter((l) => (f.week === 'all' || String(l.week) === f.week) && (f.module === 'all' || l.module === f.module) && (!f.novel || l.novel) &&
    (f.status === 'all' || (f.status === 'undecided' ? !v.survey[l.id] : f.status === 'review' ? isReview(l) : !!v.survey[l.id])))
  const weeks = [...new Set(list.map((l) => l.week))]
  const parts = L.flatMap((l) => classTime(v, l.id) ?? [])
  const used = [...new Set(parts.map((p) => p.way))] as Way[]
  const hj = v.jobs?.health
  const checking = hj?.state === 'queued' || hj?.state === 'running'
  const dead = v.health?.dead ?? []
  const style = async (value: string) => {
    const first = L[0]?.id
    if (!first) return
    await act(() => api.post(deliveryUrl(rid, `/mix/${encodeURIComponent(first)}`), { action: 'style', style: value }), 'New lecture plans start in this style')
  }

  return (
    <PageBody width="wide">
      <header className="flex flex-wrap items-end justify-between gap-x-6 gap-y-4">
        <div>
          <h2 className="h-display text-2xl text-ink-1 sm:text-3xl">Lectures</h2>
          <p className="mt-1 text-base text-ink-3">{plural(L.length, 'lecture')} over {plural(new Set(L.map((l) => l.week)).size, 'week')} · {counts.decided} planned{counts.review ? ` · ${counts.review} ready for your review` : ''}{v.run.example_of ? ' · example copy' : ''}</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <label className="flex items-center gap-2 text-sm text-ink-3">Teaching style
            <Select className="!w-28" value={v.mix?.style ?? 'mix'} onChange={(e) => style(e.target.value)} aria-label="Teaching style for this course"><option value="slides">Slides</option><option value="mix">Mix</option><option value="flipped">Flipped</option></Select>
          </label>
          <Button variant="ghost" icon={checking ? <Spinner /> : <Link2 aria-hidden />} disabled={checking} onClick={() => act(() => api.post(deliveryUrl(rid, '/health')), 'Checking every approved link. This takes a minute.')}>{checking ? 'Checking links…' : 'Check approved links'}</Button>
          <Button variant="ghost" icon={<FileText aria-hidden />} onClick={() => setReportOpen(true)}>Course report</Button>
          <Button variant="primary" icon={<Sparkles aria-hidden />} onClick={() => setWeeksOpen(true)}>Make material for chosen weeks</Button>
        </div>
      </header>

      <div className="mt-5 space-y-3">
        {!v.keys.youtube && <Callout tone="amber" title="Video search is off on this laptop">Add a free YouTube Data API key to .env as YOUTUBE_API_KEY and restart the app. Until then, searches find readings, practice and guest speakers, but no videos, recorded lectures or clips.</Callout>}
        {hj?.state === 'error' && <Callout tone="rose">The link check stopped: {hj.error}</Callout>}
        {dead.length > 0 && <Callout tone="amber">{plural(dead.length, 'approved link')} {dead.length === 1 ? 'is' : 'are'} no longer available: {dead.map((x, i) => <span key={i}>{i > 0 && ', '}<Link className="text-iris-300 underline" to={lectureUrl(base, x.lecture)}>{x.lecture}</Link></span>)}. Open the lecture to replace {dead.length === 1 ? 'it' : 'them'}.</Callout>}
      </div>

      <div className="mt-6 flex flex-wrap items-center gap-3">
        <Segmented label="Show lectures" value={f.status} onChange={(s) => set({ status: s })} options={[{ id: 'all', label: 'All', count: counts.all }, { id: 'undecided', label: 'To plan', count: counts.undecided }, { id: 'review', label: 'Ready to review', count: counts.review }, { id: 'decided', label: 'Planned', count: counts.decided }]} />
        <Select className="!w-36" aria-label="Week" value={f.week} onChange={(e) => set({ week: e.target.value })}><option value="all">All weeks</option>{[...new Set(L.map((l) => l.week))].map((w) => <option key={w} value={w}>Week {w}</option>)}</Select>
        {mods.length > 1 && <Select className="!w-64 max-w-full" aria-label="Module" value={f.module} onChange={(e) => set({ module: e.target.value })}><option value="all">All modules</option>{mods.map((m) => <option key={m}>{m}</option>)}</Select>}
        {showNovel && <Checkbox checked={f.novel} onChange={(c) => set({ novel: c })}>New topics only</Checkbox>}
        {used.length > 0 && <WayLegend className="ml-auto" ways={used} pre={parts.some((p) => p.pre)} />}
      </div>

      {list.length ? weeks.map((w) => (
        <section key={w} aria-labelledby={`week-${w}`} className="mt-6">
          <h3 id={`week-${w}`} className="label-caps mb-2">Week {w}</h3>
          <ul className="space-y-2">{list.filter((l) => l.week === w).map((l) => <LectureRow key={l.id} l={l} v={v} base={base} bar={used.length > 0} novel={showNovel} />)}</ul>
        </section>
      )) : <EmptyState className="mt-6" title="No lectures match these filters" actions={<Button onClick={() => set({ status: 'all', week: 'all', module: 'all', novel: false })}>Clear the filters</Button>} />}

      <WeeksDialog v={v} rid={rid} open={weeksOpen} onClose={() => setWeeksOpen(false)} preset={f.week !== 'all' ? [+f.week] : []} />
      <ReportDialog rid={rid} open={reportOpen} onClose={() => setReportOpen(false)} />
    </PageBody>
  )
}
