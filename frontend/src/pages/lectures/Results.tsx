// What the search found for one lecture: resources and guest speakers as evidence cards. Each card says why it is
// suggested, shows where that claim comes from, and waits for the professor's decision (approve, replace, reject).
import { useState } from 'react'
import { Check, Play, Plus, TriangleAlert } from 'lucide-react'
import { api, deliveryUrl } from '@/lib/api'
import { EXPERT_KIND, KINDS, LINK_NAME, TALK_FORMAT, USE_AS, yes } from '@/lib/delivery'
import { hms, regionName, sentence } from '@/lib/format'
import type { Choices, DeliveryView, Expert, Lecture, LectureResult, Resource, ResourceKind } from '@/lib/types'
import { ApprovedBadge, Badge, Button, Callout, Disclosure, Ext, Field, Input, Meter, Select, TextButton, Textarea } from '@/components/ui'
import { Link } from 'react-router-dom'
import { lectureUrl, useDeliveryAction } from './shared'

type Act = ReturnType<typeof useDeliveryAction>

/** Approve · Replace · Reject, with a required reason for the last two. */
function ReviewActions({ rid, lid, kind, itemKey, title, approved, expert, act }: { rid: string; lid: string; kind: string; itemKey: string; title: string; approved: boolean; expert?: boolean; act: Act }) {
  const [ask, setAsk] = useState<null | 'replace' | 'reject'>(null)
  const [text, setText] = useState('')
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)
  const send = async (decision: string, reason = '') => {
    setBusy(true)
    const r = await act(() => api.post(deliveryUrl(rid, '/review'), { lid, kind, key: itemKey, decision, reason, title }),
      decision === 'approve' ? (expert ? 'Shortlisted' : 'Approved') : decision === 'replace' ? 'Replaced with the next-best item' : 'Rejected')
    setBusy(false)
    if (r) setAsk(null)
  }
  if (approved) return (
    <div className="mt-3 flex items-center gap-3">
      <ApprovedBadge>{expert ? 'Shortlisted by you' : 'Approved by you'}</ApprovedBadge>
      <TextButton onClick={() => act(() => api.post(deliveryUrl(rid, '/undo'), { lid, kind, key: itemKey }), 'Back to waiting for your decision')}>Undo</TextButton>
    </div>
  )
  if (ask) return (
    <div className="mt-3 rounded-lg border border-line bg-white/[0.02] p-3">
      <Field label={`Why ${ask} this?`} htmlFor={`why-${itemKey}`} error={err}>
        <Textarea id={`why-${itemKey}`} rows={2} autoFocus value={text} invalid={!!err} placeholder="Too long for a 2-hour lecture" onChange={(e) => { setText(e.target.value); setErr('') }} />
      </Field>
      <div className="mt-2.5 flex gap-2">
        <Button size="sm" variant={ask === 'replace' ? 'primary' : 'danger'} loading={busy} onClick={() => (text.trim() ? send(ask, text.trim()) : setErr('Write a short reason first'))}>{ask === 'replace' ? 'Replace with the next best' : 'Reject'}</Button>
        <Button size="sm" variant="ghost" onClick={() => setAsk(null)}>Cancel</Button>
      </div>
    </div>
  )
  return (
    <div className="mt-3 flex flex-wrap gap-2">
      <Button size="sm" variant="success" icon={<Check aria-hidden />} loading={busy} onClick={() => send('approve')}>{expert ? 'Shortlist' : 'Approve'}</Button>
      <Button size="sm" onClick={() => { setText(''); setErr(''); setAsk('replace') }}>Replace</Button>
      <Button size="sm" variant="danger" onClick={() => { setText(''); setErr(''); setAsk('reject') }}>Reject</Button>
    </div>
  )
}

const Warning = ({ children }: { children: React.ReactNode }) => (
  <p className="mt-2 flex gap-2 rounded-md border border-amber-line bg-amber-soft px-2.5 py-1.5 text-sm text-amber-300"><TriangleAlert aria-hidden className="mt-0.5 size-3.5 shrink-0" /><span>{children}</span></p>
)

/** How the ranking was worked out: every criterion from 0 to 1, as the pipeline scored it. */
function Scores({ scores, total }: { scores: Record<string, number> | null; total: number | null }) {
  if (!scores || !Object.keys(scores).length) return null
  return (
    <Disclosure className="mt-2" summary="How it was ranked">
      <dl className="grid max-w-md grid-cols-[8rem_1fr_2.5rem] items-center gap-x-3 gap-y-1.5 text-xs">
        {Object.entries(scores).map(([k, n]) => (
          <div key={k} className="contents"><dt className="text-ink-3">{sentence(k.replace(/_/g, ' '))}</dt><dd><Meter value={n * 100} tone="neutral" label={k} /></dd><dd className="text-right text-ink-2 tnum">{n.toFixed(2)}</dd></div>
        ))}
        {total != null && <div className="contents font-semibold"><dt className="text-ink-2">Overall</dt><dd><Meter value={total * 100} tone="iris" label="Overall" /></dd><dd className="text-right text-ink-1 tnum">{total.toFixed(2)}</dd></div>}
      </dl>
    </Disclosure>
  )
}

function CardShell({ approved, children }: { approved: boolean; children: React.ReactNode }) {
  return <article className={`rounded-xl border p-4 transition-colors ${approved ? 'border-mint-line bg-mint-soft/40' : 'border-line bg-surface-2/50'}`}>{children}</article>
}

function ResourceCard({ x, kind, rid, lid, act }: { x: Resource; kind: ResourceKind; rid: string; lid: string; act: Act }) {
  const [play, setPlay] = useState(false)
  const watch = x.yt ? x.cover.filter((c) => c.segs.length) : []
  return (
    <CardShell approved={x.approved}>
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h4 className="text-md font-medium leading-snug"><Ext href={x.url} quiet>{x.title}</Ext></h4>
          <p className="mt-1 flex flex-wrap items-center gap-x-2.5 gap-y-1 text-sm text-ink-3">
            {x.source && <span>{x.source}</span>}{x.dur ? <span className="tnum">{hms(x.dur)}</span> : null}{x.year && <span>{x.year}</span>}
            {x.captions === true ? <span>Captions</span> : x.captions === false ? <span>No captions</span> : null}
            {x.licence && !/standard youtube/i.test(x.licence) && <span>{x.licence}</span>}
          </p>
        </div>
        {x.rank != null && <span className="shrink-0 rounded-md bg-white/[0.06] px-1.5 py-0.5 font-mono text-xs font-medium text-ink-2" title="Rank among what passed the checks">#{x.rank}</span>}
      </div>
      {x.warnings.map((w, i) => <Warning key={i}>{w}</Warning>)}
      {x.review?.text && (
        <div className="mt-2.5 rounded-lg border border-iris-line bg-iris-soft px-3 py-2 text-sm text-ink-2">
          <p><span className="mr-2 text-xs font-semibold text-iris-300">AI review</span>{x.review.use_as && <Badge tone="iris" className="mr-2">{USE_AS[x.review.use_as] ?? x.review.use_as}</Badge>}{x.review.text}</p>
          {x.review.issues?.length > 0 && <p className="mt-1 text-xs text-ink-3">Note: {x.review.issues.join('; ')}</p>}
        </div>
      )}
      {watch.length > 0 && (
        <p className="mt-2.5 text-sm text-ink-2"><b className="font-semibold text-ink-1">Watch: </b>
          {watch.map((c, i) => <span key={i}>{i > 0 && ' · '}{c.label} at {c.segs.map((s, j) => <span key={j}>{j > 0 && ', '}<Ext href={`${x.url}&t=${s[0]}s`}>{hms(s[0])}–{hms(s[1])}</Ext></span>)}</span>)}
        </p>
      )}
      <Scores scores={x.scores} total={x.total} />
      {x.yt && x.embeddable !== false && (play
        ? <iframe className="mt-3 aspect-video w-full max-w-xl rounded-lg border border-line" src={`https://www.youtube-nocookie.com/embed/${encodeURIComponent(x.yt)}`} title={x.title} allowFullScreen loading="lazy" />
        : <Button size="sm" variant="ghost" className="mt-2 -ml-2" icon={<Play aria-hidden />} onClick={() => setPlay(true)}>Play here</Button>)}
      <ReviewActions rid={rid} lid={lid} kind={kind} itemKey={x.key} title={x.title} approved={x.approved} act={act} />
    </CardShell>
  )
}

function Gone({ v, lid, kind }: { v: DeliveryView; lid: string; kind: string }) {
  const rows = (v.actions?.[lid] ?? []).filter((x) => x.kind === kind && x.decision !== 'approve')
  if (!rows.length) return null
  return <ul className="mt-2 space-y-1">{rows.map((x, i) => <li key={i} className="text-sm text-ink-3">You {x.decision === 'replace' ? 'replaced' : 'rejected'} “{x.title}”: {x.reason}</li>)}</ul>
}

const GroupTitle = ({ children, aside }: { children: React.ReactNode; aside?: React.ReactNode }) => (
  <div className="mb-2.5 flex flex-wrap items-baseline justify-between gap-2"><h3 className="text-md font-semibold text-ink-1">{children}</h3>{aside}</div>
)

export function OwnLinks({ v, rid, lid, act }: { v: DeliveryView; rid: string; lid: string; act: Act }) {
  const own = v.own?.[lid] ?? []
  const [open, setOpen] = useState(false)
  const [f, setF] = useState({ title: '', url: '', kind: 'reading' })
  const add = async () => { if (await act(() => api.post(deliveryUrl(rid, '/own'), { lid, ...f }), 'Added as approved', 'Could not add')) { setOpen(false); setF({ title: '', url: '', kind: 'reading' }) } }
  return (
    <div>
      <GroupTitle aside={!open && <Button size="sm" variant="ghost" icon={<Plus aria-hidden />} onClick={() => setOpen(true)}>Add my own link</Button>}>Your own links</GroupTitle>
      <div className="space-y-2">
        {own.map((x, i) => (
          <CardShell key={i} approved>
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0"><h4 className="text-md font-medium"><Ext href={x.url} quiet>{x.title}</Ext></h4>
                <p className="mt-1.5 flex flex-wrap gap-2"><Badge>{KINDS.find((k) => k.kind === x.kind)?.name ?? 'Reading'}</Badge><ApprovedBadge>Added and approved by you</ApprovedBadge></p></div>
              <TextButton onClick={() => act(() => api.post(deliveryUrl(rid, '/own'), { lid, remove: i }))}>Remove</TextButton>
            </div>
          </CardShell>
        ))}
        {!own.length && !open && <p className="text-sm text-ink-3">None. A link you add counts as approved and appears in the student view.</p>}
        {open && (
          <div className="rounded-xl border border-line bg-surface-2/50 p-4">
            <div className="grid gap-3 sm:grid-cols-2">
              <Field label="Title" htmlFor="own-t"><Input id="own-t" value={f.title} onChange={(e) => setF({ ...f, title: e.target.value })} /></Field>
              <Field label="Link" htmlFor="own-u"><Input id="own-u" placeholder="https://…" value={f.url} onChange={(e) => setF({ ...f, url: e.target.value })} /></Field>
            </div>
            <Field className="mt-3 max-w-xs" label="Kind" htmlFor="own-k"><Select id="own-k" value={f.kind} onChange={(e) => setF({ ...f, kind: e.target.value })}>{KINDS.map((k) => <option key={k.kind} value={k.kind}>{k.name}</option>)}</Select></Field>
            <div className="mt-3 flex gap-2"><Button size="sm" variant="primary" onClick={add}>Add as approved</Button><Button size="sm" variant="ghost" onClick={() => setOpen(false)}>Cancel</Button></div>
          </div>
        )}
      </div>
    </div>
  )
}

export function ResourcesTab({ v, rid, l, a, r, act }: { v: DeliveryView; rid: string; l: Lecture; a: Choices; r: LectureResult; act: Act }) {
  const [show, setShow] = useState<Record<string, boolean>>({})
  return (
    <div>
      <div className="mb-4 space-y-2">
        {r.partial && <Callout tone="amber" title="Partial results">Press “Finish the search” under Progress.</Callout>}
        {r.continuation_of && <Callout tone="iris">Continues {r.continuation_of}: these are the next-best items.</Callout>}
        {r.note && <Callout tone="neutral">{r.note}</Callout>}
      </div>
      {KINDS.filter((k) => yes(a, k.want)).map(({ kind, name }) => {
        const shown = r.items[kind] ?? [], reserve = r.reserve[kind] ?? []
        return (
          <section key={kind} className="mb-7">
            <GroupTitle aside={reserve.length > 0 && <TextButton onClick={() => setShow((s) => ({ ...s, [kind]: !s[kind] }))}>{show[kind] ? 'Hide' : 'Show'} the next-best {reserve.length}</TextButton>}>{name}</GroupTitle>
            {shown.length ? <div className="space-y-2.5">{shown.map((x) => <ResourceCard key={x.key} x={x} kind={kind} rid={rid} lid={l.id} act={act} />)}</div>
              : <p className="text-sm text-ink-3">No {name.toLowerCase()} passed the quality checks for this lecture.{(kind === 'video' || kind === 'recorded_lecture') && !v.keys.youtube ? ' (Video search is off on this laptop.)' : ''}</p>}
            {show[kind] && <ul className="mt-2 space-y-1.5 border-l-2 border-line pl-3">{reserve.map((x) => <li key={x.key} className="text-sm"><Ext href={x.url}>{x.title}</Ext> <span className="text-ink-3">· {x.source}</span></li>)}</ul>}
            <Gone v={v} lid={l.id} kind={kind} />
          </section>
        )
      })}
      <OwnLinks v={v} rid={rid} lid={l.id} act={act} />
      {r.rejected?.length > 0 && (
        <Disclosure className="mt-6 border-t border-line pt-4" summary={`Why not these? ${r.rejected.length} were removed by the checks`}>
          <ul className="space-y-1.5">{r.rejected.map((x, i) => <li key={i} className="text-sm"><Ext href={x.url}>{x.title}</Ext> <span className="text-ink-3">· {(x.why ?? []).join('; ')}</span></li>)}</ul>
        </Disclosure>
      )}
    </div>
  )
}

function ExpertCard({ x, rid, lid, act }: { x: Expert; rid: string; lid: string; act: Act }) {
  const links = Object.entries(x.links ?? {}).filter(([, u]) => u) as [string, string][]
  return (
    <CardShell approved={x.approved}>
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h4 className="text-md font-semibold text-ink-1">{x.name}</h4>
          <p className="mt-0.5 text-sm text-ink-3">{[x.role, x.affiliation || 'affiliation unknown'].filter(Boolean).join(', ')}{x.country ? ` · ${regionName(x.country)}` : ''}</p>
          <p className="mt-2 flex flex-wrap gap-1.5">
            <Badge>{EXPERT_KIND[x.kind ?? ''] ?? sentence(x.kind ?? '')}</Badge>
            {x.fit && <Badge tone={x.fit === 'strong' ? 'mint' : 'amber'}>{x.fit === 'strong' ? 'Strong fit' : 'Moderate fit'}</Badge>}
          </p>
        </div>
        {x.rank != null && <span className="shrink-0 rounded-md bg-white/[0.06] px-1.5 py-0.5 font-mono text-xs font-medium text-ink-2">#{x.rank}</span>}
      </div>
      {x.warnings.map((w, i) => <Warning key={i}>{w}</Warning>)}
      {x.why && <p className="mt-2.5 text-base text-ink-2"><b className="font-semibold text-ink-1">Why: </b>{x.why}</p>}
      {x.evidence.length > 0 && (
        <>
          <p className="label-caps mt-3">Evidence</p>
          <ul className="mt-1 space-y-1">{x.evidence.map((ev, i) => <li key={i} className="text-sm text-ink-2"><Ext href={ev.url}>{ev.title}</Ext> <span className="text-ink-3">· {[ev.kind, ev.venue, ev.year].filter(Boolean).join(', ')}</span></li>)}</ul>
        </>
      )}
      <p className="mt-2.5 text-sm text-ink-2">
        {x.format && <><b className="font-semibold text-ink-1">Suggested format: </b>{TALK_FORMAT[x.format] ?? x.format}{links.length > 0 && ' · '}</>}
        {links.map(([k, u], i) => <span key={k}>{i > 0 && ' · '}<Ext href={u}>{LINK_NAME[k] ?? k}</Ext></span>)}
      </p>
      {x.verified && <p className="mt-1 text-xs text-ink-3">Identity checked against: {x.verified}</p>}
      <Scores scores={x.scores} total={x.total} />
      <ReviewActions rid={rid} lid={lid} kind="experts" itemKey={x.key} title={x.name} approved={x.approved} expert act={act} />
    </CardShell>
  )
}

export function GuestTab({ v, rid, base, l, r, act }: { v: DeliveryView; rid: string; base: string; l: Lecture; r: LectureResult; act: Act }) {
  const e = r.experts
  if (!e) return <p className="text-base text-ink-3">This lecture was searched for resources only. Save your choices again to search for a guest too.</p>
  if ('same_as' in e) return <Callout tone="iris">Same guest list as {e.same_as}, because this lecture continues that topic. <Link className="text-iris-300 underline" to={lectureUrl(base, e.same_as)}>Open {e.same_as}</Link></Callout>
  return (
    <div>
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm text-ink-3">You send invitations yourself; ProfsAgent never contacts anyone.</p>
        {v.kits.includes(l.id) && <Button size="sm" to={lectureUrl(base, l.id, '/kit')}>Open the guest-lecture kit</Button>}
      </div>
      {e.experts.length ? <div className="space-y-2.5">{e.experts.map((x) => <ExpertCard key={x.key} x={x} rid={rid} lid={l.id} act={act} />)}</div> : <p className="text-sm text-ink-3">No speaker passed the checks.</p>}
      <Gone v={v} lid={l.id} kind="experts" />
      {e.rejected?.length > 0 && (
        <Disclosure className="mt-6 border-t border-line pt-4" summary={`Why not these? ${e.rejected.length} people were removed by the checks`}>
          <ul className="space-y-1.5">{e.rejected.map((x, i) => <li key={i} className="text-sm text-ink-2">{x.name} <span className="text-ink-3">· {(x.why ?? []).join('; ')}</span></li>)}</ul>
        </Disclosure>
      )}
    </div>
  )
}

export function ClipsTab({ r }: { r: LectureResult }) {
  if (!r.clips?.length) return <p className="text-base text-ink-3">No clip playlist was built for this lecture.</p>
  return (
    <ol className="space-y-2">
      {r.clips.map((x, i) => <li key={i} className="flex gap-3 text-base text-ink-2"><span className="font-mono text-xs text-ink-3 pt-1">{i + 1}</span><span>Watch <Ext href={x.url}>{x.start}–{x.end}</Ext> of <i>{x.video}</i> for {x.target} <span className="text-ink-3">({x.minutes} min)</span></span></li>)}
    </ol>
  )
}
