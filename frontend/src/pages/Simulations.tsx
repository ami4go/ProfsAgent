// The simulation library: ours (checked, runnable offline) and links to trusted sites, grouped so that several
// simulations of the same thing share one card; and the professor's requests for new ones, with their progress.
import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { Check, FlaskConical, Plus, Search } from 'lucide-react'
import { ApiError, api, enc, problemOf } from '@/lib/api'
import { SIM_MAX } from '@/lib/delivery'
import { store } from '@/lib/format'
import { useBusy, useDocumentTitle } from '@/lib/hooks'
import { keys, useRefresh, useSims } from '@/lib/queries'
import { toast } from '@/lib/toast'
import type { RequestStatus, SimCatalogue, SimEntry, SimFound, SimRequest } from '@/lib/types'
import type { Tone } from '@/lib/status'
import { Badge, Button, Callout, Card, CardBody, Cradle, EmptyState, Ext, Field, Input, Loading, Modal, Textarea } from '@/components/ui'
import { PageBody, PageHeader, TopBar } from '@/components/app/Shell'
import { openSim } from '@/components/app/SimPreview'
import { SimChecked, WithCode, simDraft, type SimRequestDraft } from './lectures/SimCard'

const PAGE = 10
interface Link { id: string; title: string; url: string; site_name: string; shows_code: boolean; summary: string }
type It = { c: SimEntry; x?: undefined } | { x: Link; c?: undefined }
interface Group { key: string; title?: string; items: It[] }

// simulations of the same thing share a key: the title without "step by step", "· try it yourself", "(…)" and the like
export const simKey = (t: string) => String(t || '').toLowerCase().split(/[·(|–]/)[0]
  .replace(/\b(step by step|try it yourself|visuali[sz](ed|ation)|simulations?|simulator|demo|interactive|animation|algorithms?)\b/g, ' ')
  .replace(/[^a-z0-9+#]+/g, ' ').trim()
const simText = (c: SimEntry) => [c.title, c.summary, (c.topics ?? []).join(' '), (c.courses ?? []).map((x) => `${x.code} ${x.name}`).join(' ')].join(' ').toLowerCase()

export function groupSims(ours: SimEntry[], links: Link[]): Group[] {
  const gs: Group[] = []
  const starts = (a: string, b: string) => a === b || a.startsWith(b + ' ')
  for (const it of [...ours.map((c) => ({ c }) as It), ...links.map((x) => ({ x }) as It)]) {
    const e = it.c ?? it.x!
    const k = simKey(e.title) || e.id
    const g = gs.find((g) => starts(k, g.key) || starts(g.key, k))
    if (g) { g.items.push(it); if (k.length < g.key.length) g.key = k } else gs.push({ key: k, items: [it] })
  }
  return gs
}

function Pager({ n, cur, onChange }: { n: number; cur: number; onChange: (p: number) => void }) {
  if (n < 2) return null
  const show = [...new Set([1, cur - 1, cur, cur + 1, n])].filter((x) => x >= 1 && x <= n).sort((a, b) => a - b)
  return (
    <nav aria-label="Pages" className="mt-4 flex flex-wrap items-center justify-center gap-1.5">
      <Button size="sm" variant="ghost" disabled={cur <= 1} aria-label="Previous page" onClick={() => onChange(cur - 1)}>‹</Button>
      {show.map((x, i) => <span key={x} className="flex items-center gap-1.5">{i > 0 && x - show[i - 1] > 1 && <span className="text-ink-4">…</span>}<Button size="sm" variant={x === cur ? 'primary' : 'secondary'} aria-current={x === cur ? 'page' : undefined} onClick={() => onChange(x)}>{x}</Button></span>)}
      <Button size="sm" variant="ghost" disabled={cur >= n} aria-label="Next page" onClick={() => onChange(cur + 1)}>›</Button>
    </nav>
  )
}

function Used({ c }: { c: SimEntry }) {
  if (!c.used?.length) return null
  return <p className="mt-2 text-sm text-ink-2"><b className="font-semibold text-ink-1">In your lectures: </b>{c.used.map((u, i) => <span key={i}>{i > 0 && '; '}<Link className="text-iris-300 underline decoration-iris-line underline-offset-[3px]" to={`/courses/${enc(u.run_id)}/lectures/${enc(u.lecture)}`}>{u.course}, {u.lecture}</Link></span>)}</p>
}
const tryIt = (c: SimEntry) => openSim({ id: c.id, title: c.title, state: '' })

function GroupCard({ g }: { g: Group }) {
  const [open, setOpen] = useState(false)
  const items = g.items.slice(0, 3)
  if (items.length === 1) {
    const it = items[0]
    return it.c ? (
      <Card className="flex flex-col p-4">
        <div className="flex items-start justify-between gap-3"><h3 className="min-w-0 text-md font-semibold text-ink-1">{it.c.title}</h3><span className="flex shrink-0 flex-wrap justify-end gap-1.5"><WithCode on={it.c.shows_code} /><SimChecked c={it.c} /></span></div>
        <p className="mt-1.5 flex-1 text-base text-ink-2">{it.c.summary}</p>
        <Used c={it.c} />
        <div className="mt-3"><Button size="sm" icon={<FlaskConical aria-hidden />} onClick={() => tryIt(it.c)}>Try it</Button></div>
      </Card>
    ) : (
      <Card className="flex flex-col p-4">
        <div className="flex items-start justify-between gap-3"><h3 className="min-w-0 text-md font-semibold text-ink-1">{it.x.title}</h3><span className="flex shrink-0 flex-wrap justify-end gap-1.5"><WithCode on={it.x.shows_code} /><Badge>{it.x.site_name}</Badge></span></div>
        {it.x.summary && <p className="mt-1.5 flex-1 text-base text-ink-2">{it.x.summary}</p>}
        <div className="mt-3"><Button size="sm" href={it.x.url} external>Open</Button></div>
      </Card>
    )
  }
  const shortest = [...items].sort((a, b) => (a.c ?? a.x!).title.length - (b.c ?? b.x!).title.length)[0]
  const head = (items.find((it) => it.c) ?? shortest), h = head.c ?? head.x!
  const title = g.title || h.title
  const src = (it: It) => (it.c ? 'ours' : it.x!.site_name)
  const same = (it: It) => items.filter((o) => src(o) === src(it) && (o.c ?? o.x!).title === (it.c ?? it.x!).title).length > 1
  return (
    <Card className="flex flex-col p-4">
      <div className="flex items-start justify-between gap-3"><h3 className="min-w-0 text-md font-semibold text-ink-1">{title}</h3><Badge>{items.length} options</Badge></div>
      {h.summary && <p className="mt-1.5 flex-1 text-base text-ink-2">{h.summary}</p>}
      {items.map((it) => it.c && <Used key={it.c.id} c={it.c} />)}
      {open && (
        <ul className="mt-3 divide-y divide-line border-y border-line">
          {items.map((it, i) => {
            const e = it.c ?? it.x!
            return (
              <li key={i} className="flex flex-wrap items-center gap-2 py-2">
                {it.c ? <Badge tone="mint">Ours</Badge> : <Badge>{it.x!.site_name}</Badge>}<WithCode on={e.shows_code} />
                <span className="min-w-0 flex-1 truncate text-sm text-ink-3">{same(it) ? `Version ${i + 1}` : e.title !== title ? e.title : ''}</span>
                {it.c ? <Button size="sm" onClick={() => tryIt(it.c)}>Try it</Button> : <Button size="sm" href={it.x!.url} external>Open</Button>}
              </li>
            )
          })}
        </ul>
      )}
      <div className="mt-3"><Button size="sm" variant={open ? 'ghost' : 'secondary'} aria-expanded={open} icon={open ? undefined : <FlaskConical aria-hidden />} onClick={() => setOpen(!open)}>{open ? 'Hide the options' : 'Try it'}</Button></div>
    </Card>
  )
}

function RequestDialog({ draft, onClose, onSent }: { draft: SimRequestDraft; onClose: () => void; onSent: () => void }) {
  const [r, setR] = useState(draft)
  const [errs, setErrs] = useState<Record<string, string>>({})
  const [busy, go] = useBusy()
  const send = () => go(async () => { await api.post('/api/simulations/requests', r); toast.success('Request sent. Looking for existing ones first.'); onSent() },
    (e) => (e instanceof ApiError && e.status === 422 ? setErrs(e.errors) : toast.error(problemOf(e, 'Could not send'))))
  return (
    <Modal open onOpenChange={(o) => !o && onClose()} sticky size="md" title="Ask for a new simulation" description={r.lecture ? `For ${r.course}, ${r.lecture}` : 'ProfsAgent first looks for existing ones, then builds one if none fits.'}
      footer={<><Button variant="ghost" onClick={onClose}>Cancel</Button><Button variant="primary" loading={busy} onClick={send}>Send the request</Button></>}>
      <div className="space-y-4">
        <Field label="Topic" htmlFor="sq-topic" error={errs.topic}><Input id="sq-topic" autoFocus={!r.topic} value={r.topic} invalid={!!errs.topic} placeholder="For example: TCP congestion control" onChange={(e) => setR({ ...r, topic: e.target.value })} /></Field>
        <Field label="What should students see or try?" htmlFor="sq-what" error={errs.what}><Textarea id="sq-what" rows={3} autoFocus={!!r.topic} value={r.what} invalid={!!errs.what} placeholder="For example: change the window size and the loss rate, and watch the sending rate rise and fall" onChange={(e) => setR({ ...r, what: e.target.value })} /></Field>
        {!r.run_id && <Field label="Course" htmlFor="sq-course" optional><Input id="sq-course" value={r.course ?? ''} onChange={(e) => setR({ ...r, course: e.target.value })} /></Field>}
      </div>
    </Modal>
  )
}

const RSTATUS: Record<RequestStatus, [Tone, string]> = {
  requested: ['neutral', 'Not started'], queued: ['iris', 'Waiting'], searching: ['iris', 'Looking for existing ones'], review: ['amber', 'Found some: your review'], chosen: ['mint', 'Chosen'],
  build_queued: ['iris', 'Waiting to be built'], building: ['iris', 'Being built'], ready: ['amber', 'Built: your review'], approved: ['mint', 'Approved'], needs_team: ['amber', 'Sent to the team'], paused: ['amber', 'Paused: AI quota used up'],
}
const RBUSY: RequestStatus[] = ['queued', 'searching', 'build_queued', 'building']
const reqDone = (q: SimRequest) => q.status === 'chosen' || q.status === 'approved'

function FoundCard({ q, c, post }: { q: SimRequest; c: SimFound; post: Poster }) {
  const rej = c.decision === 'reject', ok = c.decision === 'approve', open = q.status === 'review' || q.status === 'chosen'
  const full = (q.found ?? []).filter((x) => x.decision === 'approve').length >= SIM_MAX
  const decide = (d: string) => post(`/api/simulations/requests/${enc(q.id)}/found/${c.n}`, { decision: d },
    (r: { lecture_note?: string; request?: SimRequest; start_build?: boolean }) => d === 'approve' ? `Approved.${r.lecture_note ? ' ' + r.lecture_note : r.request?.lecture ? ` It is on ${r.request.lecture}.` : ''}` : d === 'reject' ? (r.start_build ? 'Building a new one (about 2–5 minutes).' : 'Rejected') : 'Undone')
  return (
    <div className={`grid gap-3 rounded-xl border p-3 sm:grid-cols-[10.5rem_1fr] ${ok ? 'border-mint-line bg-mint-soft/40' : 'border-line bg-surface-2/50'} ${rej ? 'opacity-55' : ''}`}>
      {c.shot ? <img alt="" loading="lazy" className="h-[6.5rem] w-full rounded-md border border-line object-cover object-top sm:w-[10.5rem]" src={`/api/simulations/requests/${enc(q.id)}/shot/${enc(c.shot)}`} />
        : <div className="flex h-[6.5rem] items-center justify-center rounded-md border border-line bg-sunken text-xs text-ink-3">{c.kind === 'ours' ? 'In our catalogue' : 'No picture'}</div>}
      <div className="min-w-0">
        <p className="font-medium text-ink-1">{c.title}</p>
        <p className="mt-1 flex flex-wrap gap-1.5">{c.kind === 'ours' ? <Badge tone="mint">Ours</Badge> : <Badge>{c.site}</Badge>}<WithCode on={c.shows_code} /></p>
        {c.summary && <p className="mt-1.5 text-sm text-ink-2">{c.summary}</p>}
        <div className="mt-2.5 flex flex-wrap items-center gap-2">
          {c.kind === 'ours' && c.id ? <Button size="sm" onClick={() => openSim({ id: c.id!, title: c.title, state: '' })}>Try it</Button> : <Button size="sm" href={c.url ?? '#'} external>Open</Button>}
          {open && !c.decision ? <>{!full && <Button size="sm" variant="success" icon={<Check aria-hidden />} onClick={() => decide('approve')}>{q.status === 'chosen' ? 'Also approve' : 'Approve'}</Button>}<Button size="sm" variant="danger" onClick={() => decide('reject')}>Not this</Button></>
            : c.decision ? <><Badge tone={ok ? 'mint' : 'neutral'}>{ok ? 'Approved by you' : 'Rejected'}</Badge>{(open || ok) && <Button size="sm" variant="ghost" onClick={() => decide('undo')}>Undo</Button>}</> : null}
        </div>
      </div>
    </div>
  )
}

type Poster = <T>(path: string, body: unknown, done: string | ((r: T) => string)) => Promise<T | undefined>

function RequestRow({ q, cat, post }: { q: SimRequest; cat: SimCatalogue; post: Poster }) {
  const [tone, label] = RSTATUS[q.status] ?? ['neutral', q.status]
  const [note, setNote] = useState('')
  const [rejecting, setRejecting] = useState(false)
  const [why, setWhy] = useState('')
  const b = q.build ?? {}, found = q.found ?? []
  const sim = q.sim_id ? (cat.entries.find((e) => e.id === q.sim_id) ?? cat.pending.find((e) => e.id === q.sim_id)) : undefined
  const base = `/api/simulations/requests/${enc(q.id)}`
  const build = (n = '') => post(`${base}/build`, { note: n }, q.status === 'requested' ? 'Looking for existing ones (about a minute).' : 'Building a new one (about 2–5 minutes).')
  let line: React.ReactNode = null, action: React.ReactNode = null, more: React.ReactNode = null
  if (q.status === 'queued') line = 'Starting…'
  else if (q.status === 'searching') line = <><Cradle size={16} />Looking for existing ones…</>
  else if (q.status === 'review') {
    line = `Found these. Approve up to ${SIM_MAX}, or press Not this.`
    more = <>
      {found.map((c) => <FoundCard key={c.n} q={q} c={c} post={post} />)}
      <div className="flex flex-wrap gap-2"><Input className="min-w-56 flex-1" aria-label="What is missing" placeholder="What is missing? (optional)" value={note} onChange={(e) => setNote(e.target.value)} /><Button size="sm" className="!h-9" onClick={() => build(note)}>None of these fit: build a new one</Button></div>
    </>
  } else if (q.status === 'chosen') {
    const n = found.filter((c) => c.decision === 'approve').length
    line = `You chose ${n}${q.lecture ? `, approved on ${q.lecture}` : ''}.${n < SIM_MAX && found.some((c) => !c.decision) ? ' You can approve one more.' : ''}`
    more = found.filter((c) => c.decision !== 'reject').map((c) => <FoundCard key={c.n} q={q} c={c} post={post} />)
  } else if (q.status === 'build_queued') line = 'Building starts in a moment.'
  else if (q.status === 'building') line = <><Cradle size={16} />Building a new one (try {b.attempt ?? 1} of {b.of ?? 3})…</>
  else if (q.status === 'ready') {
    line = 'Try it, then approve it or say what is wrong.'
    action = sim && <Button size="sm" onClick={() => openSim({ id: sim.id, title: sim.title, state: '' })}>Try it</Button>
    more = rejecting ? (
      <div className="flex flex-wrap gap-2"><Input className="min-w-56 flex-1" autoFocus aria-label="What is wrong" placeholder="What is wrong? For example: no picture of the points" value={why} onChange={(e) => setWhy(e.target.value)} />
        <Button size="sm" className="!h-9" variant="danger" onClick={() => (why.trim().length < 3 ? toast.error('Write what is wrong first') : post(`${base}/review`, { decision: 'reject', reason: why.trim() }, 'Building it again with your note (about 2–5 minutes).').then(() => setRejecting(false)))}>Reject and build again</Button>
        <Button size="sm" className="!h-9" variant="ghost" onClick={() => setRejecting(false)}>Cancel</Button></div>
    ) : <div className="flex gap-2"><Button size="sm" variant="success" icon={<Check aria-hidden />} onClick={() => post(`${base}/review`, { decision: 'approve' }, 'Approved. It is in the list.')}>Approve</Button><Button size="sm" variant="danger" onClick={() => setRejecting(true)}>Reject</Button></div>
  } else if (q.status === 'needs_team' || q.status === 'paused') { line = q.reason ?? ''; action = <Button size="sm" onClick={() => build()}>Try again</Button> }
  else if (q.status === 'requested') { line = 'Not started.'; action = <Button size="sm" onClick={() => build()}>Find or build it now</Button> }
  return (
    <li className="border-t border-line py-4 first:border-t-0 first:pt-0 last:pb-0">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="font-medium text-ink-1">{q.topic}{q.course && <span className="ml-2 text-sm font-normal text-ink-3">{q.course}{q.lecture ? `, ${q.lecture}` : ''}</span>}</p>
          <p className="mt-0.5 text-sm text-ink-3">{q.what}</p>
          {line && <p className="mt-1.5 flex flex-wrap items-center gap-2 text-sm text-ink-2">{line}</p>}
          <p className="mt-1 text-xs text-ink-4">{String(q.at).slice(0, 16)}</p>
        </div>
        <div className="flex shrink-0 flex-col items-end gap-2"><Badge tone={tone}>{label}</Badge>{action}</div>
      </div>
      {more && <div className="mt-3 space-y-2.5">{more}</div>}
    </li>
  )
}

export function SimulationsPage() {
  useDocumentTitle('Simulations')
  const refresh = useRefresh()
  const [q, setQ] = useState('')
  const [page, setPage] = useState(1)
  const [xpage, setXpage] = useState(1)
  const [draft, setDraft] = useState<SimRequestDraft | null>(null)
  const [busyPoll, setBusyPoll] = useState(false)
  const { data: cat, isLoading, error } = useSims(busyPoll)
  const [reqOpen, setReqOpen] = useState<boolean | null>(() => ({ '1': true, '0': false })[store.get('profsagent-reqopen') ?? ''] ?? null)
  useEffect(() => { if (simDraft.current) { setDraft(simDraft.current); simDraft.current = null } }, [])
  useEffect(() => { setBusyPoll(!!cat?.requests.some((r) => RBUSY.includes(r.status))) }, [cat])

  const { mine, theirs, total } = useMemo(() => {
    if (!cat) return { mine: [] as Group[], theirs: [] as Group[], total: 0 }
    const words = q.trim().toLowerCase().split(/\s+/).filter(Boolean)
    const hit = (t: string) => words.every((w) => t.includes(w))
    // the topics you asked for first (what was built + what was found online), then the rest of ours, grouped by title
    const topics: Group[] = (cat.topics ?? []).map((g) => ({
      key: 'req:' + g.key, title: g.title,
      items: g.items.map((it): It | null => it.kind === 'ours' ? ((c) => (c ? { c } : null))(cat.entries.find((e) => e.id === it.id)) : { x: { id: it.url, title: it.title, url: it.url, site_name: it.site_name, shows_code: it.shows_code, summary: it.summary } }).filter((x): x is It => !!x),
    })).filter((g) => g.items.length)
    const itText = (it: It) => (it.c ? simText(it.c) : [it.x!.title, it.x!.site_name, it.x!.summary].join(' ').toLowerCase())
    const inTopic = new Set(topics.flatMap((g) => g.items.map((it) => (it.c ? it.c.id : it.x!.url))))
    const ours = cat.entries.filter((c) => !inTopic.has(c.id) && hit(simText(c)))
    const links = words.length ? (cat.external?.entries ?? []).filter((x) => !inTopic.has(x.url) && hit(x.text)) : []
    const groups = groupSims(ours, links)
    const mine = [...topics.filter((g) => hit(`${g.title} ${g.items.map(itText).join(' ')}`.toLowerCase())), ...groups.filter((g) => g.items.some((it) => it.c))]
    return { mine, theirs: groups.filter((g) => !g.items.some((it) => it.c)), total: mine.length + groups.filter((g) => !g.items.some((it) => it.c)).length }
  }, [cat, q])
  const pages = (n: number) => Math.max(1, Math.ceil(n / PAGE))
  const cut = <T,>(xs: T[], p: number) => xs.slice((p - 1) * PAGE, p * PAGE)
  const p1 = Math.min(page, pages(mine.length)), p2 = Math.min(xpage, pages(theirs.length))

  const post: Poster = async (path, body, done) => {
    try {
      const r = await api.post<never>(path, body)
      toast(typeof done === 'function' ? done(r) : done)
      await refresh(keys.sims)
      return r
    } catch (e) { toast.error(problemOf(e, 'Could not save')); await refresh(keys.sims); return undefined }
  }
  const openRows = (cat?.requests ?? []).filter((r) => !reqDone(r))
  const needsYou = openRows.length > 0
  const ask = (fromSearch = false) => setDraft({ topic: fromSearch ? q.trim() : '', what: '', kind: '', course: '' })

  return (
    <>
      <TopBar crumbs={[{ label: 'Simulations' }]} actions={<Button size="sm" variant="primary" icon={<Plus aria-hidden />} onClick={() => ask()}>Ask for a new simulation</Button>} />
      <PageBody width="wide">
        <PageHeader title="Simulations" description="Things students can try for themselves. To use one in a lecture, approve it on that lecture’s page." />
        <div className="glow-field mt-6 max-w-2xl">
          <label className="glow-inner flex items-center gap-3 px-4">
            <Search aria-hidden className="size-4 shrink-0 text-ink-3" />
            <span className="sr-only">Search the simulations</span>
            <input type="search" value={q} onChange={(e) => { setQ(e.target.value); setPage(1); setXpage(1) }} placeholder="Search by topic, for example: scheduling, clustering, convolution"
              className="h-11 w-full bg-transparent text-md text-ink-1 outline-none placeholder:text-ink-4 [&::-webkit-search-cancel-button]:appearance-none" />
          </label>
        </div>

        {isLoading && <div className="mt-6"><Loading label="Loading the simulations" /></div>}
        {error && <Callout tone="rose" className="mt-6" title="The simulations could not be loaded">{problemOf(error)}</Callout>}
        {cat && (
          <>
            {openRows.length > 0 && (
              <details className="group/r mt-6 rounded-xl border border-line bg-surface-1 shadow-1" open={reqOpen ?? needsYou} onToggle={(e) => { const o = (e.target as HTMLDetailsElement).open; setReqOpen(o); store.set('profsagent-reqopen', o ? '1' : '0') }}>
                <summary className="flex list-none items-center justify-between gap-3 px-5 py-3.5">
                  <span className="flex items-center gap-2 text-md font-semibold text-ink-1">Your requests <span className="text-sm font-normal text-ink-3">{openRows.length}</span></span>
                  <span className="flex items-center gap-2">{needsYou && <Badge tone="amber" className="group-open/r:hidden">Needs you</Badge>}<span className="text-sm text-ink-3 group-open/r:hidden">Show</span><span className="hidden text-sm text-ink-3 group-open/r:inline">Hide</span></span>
                </summary>
                <CardBody><ul>{openRows.map((r) => <RequestRow key={r.id} q={r} cat={cat} post={post} />)}</ul></CardBody>
              </details>
            )}
            <div className="mt-6 flex items-baseline justify-between"><h2 className="text-lg font-semibold text-ink-1">Library</h2><span className="text-sm text-ink-3">{q.trim() ? `${total} match${total === 1 ? '' : 'es'}` : `${cat.entries.length} of ours · ${cat.external?.entries.length ?? 0} links on trusted sites (search to see them)`}</span></div>
            <div className="mt-3 grid gap-3 md:grid-cols-2">{cut(mine, p1).map((g) => <GroupCard key={g.key} g={g} />)}</div>
            <Pager n={pages(mine.length)} cur={p1} onChange={setPage} />
            {theirs.length > 0 && (
              <>
                <h2 className="mt-8 text-lg font-semibold text-ink-1">On other sites</h2>
                <p className="text-sm text-ink-3">Links to trusted sites; not made or checked by us. <Ext href="https://github.com/ami4go/ProfsAgent/blob/main/simulations/external/sources.yaml">Which sites?</Ext></p>
                <div className="mt-3 grid gap-3 md:grid-cols-2">{cut(theirs, p2).map((g) => <GroupCard key={g.key} g={g} />)}</div>
                <Pager n={pages(theirs.length)} cur={p2} onChange={setXpage} />
              </>
            )}
            {total === 0 && <EmptyState className="mt-3" icon={<FlaskConical />} title="No simulation matches your search yet" actions={<Button variant="primary" onClick={() => ask(true)}>Ask for a new simulation</Button>}>Say what students should see or try; ProfsAgent looks for an existing one first, then builds it.</EmptyState>}
          </>
        )}
      </PageBody>
      {draft && <RequestDialog draft={draft} onClose={() => setDraft(null)} onSent={() => { setDraft(null); refresh(keys.sims) }} />}
    </>
  )
}
