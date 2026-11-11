// The lecture plan: the lecture as parts, and how each part is taught (slides, a checked video clip, a NotebookLM
// video, in class, a simulation). ProfsAgent proposes; the professor changes, locks and approves.
import { useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { Lock, LockOpen, TriangleAlert } from 'lucide-react'
import { api, deliveryUrl, enc, problemOf } from '@/lib/api'
import { MIX_LABEL, MIX_PRESETS } from '@/lib/delivery'
import { sentence, stamp } from '@/lib/format'
import { keys } from '@/lib/queries'
import { toast } from '@/lib/toast'
import type { DeliveryView, Lecture, LectureResult, Mix, MixWay } from '@/lib/types'
import { ApprovedBadge, Badge, Button, Callout, Cradle, DataTable, Disclosure, Ext, GeneratedBadge, Segmented, Select, Td, TextButton, Textarea, Th, Tr } from '@/components/ui'
import { openSim } from '@/components/app/SimPreview'
import { lectureUrl, type useDeliveryAction } from './shared'

type Act = ReturnType<typeof useDeliveryAction>
const TOTALS: [string, string][] = [['slides', 'Slides'], ['video_in_class', 'Video'], ['notebooklm', 'NotebookLM'], ['in_class', 'In class'], ['simulation', 'Simulation']]

export function MixTab({ v, rid, base, l, r, act }: { v: DeliveryView; rid: string; base: string; l: Lecture; r?: LectureResult; act: Act }) {
  const qc = useQueryClient()
  const m: Mix | undefined = v.mix?.lectures?.[l.id]
  const j = v.jobs?.mix?.[l.id]
  const busy = !!j && (j.state === 'queued' || j.state === 'running')
  const [note, setNote] = useState<string | null>(null)
  const url = deliveryUrl(rid, `/mix/${enc(l.id)}`)

  if (!m) return <div role="status" className="flex items-center gap-3 py-6 text-base text-ink-2"><Cradle />Planning how to teach each part (about half a minute)…</div>

  const comps = Object.fromEntries((r?.components ?? []).map((c) => [c.id, c]))
  const approved = m.status === 'approved'
  const q = v.mix?.quiz?.[l.id]
  const checks = (m.checks ?? []).filter((c) => !['L-AI', 'L-RESERVE'].includes(c.code))
  /** a change to one part is saved at once and checked against the evidence (no AI) */
  const change = async (cid: string, ch: Record<string, unknown>) => {
    try {
      const out = await api.post<{ mix: Mix }>(url, { action: 'save', changes: { [cid]: ch } })
      qc.setQueryData<DeliveryView>(keys.delivery(rid), (old) => (old ? { ...old, mix: { ...old.mix, lectures: { ...old.mix.lectures, [l.id]: out.mix } } } : old))
      toast('Saved')
    } catch (e) { toast.error(problemOf(e, 'Could not save')) }
  }
  const queue = (body: Record<string, unknown>, msg: string) => act(() => api.post(url, body), msg)
  const tot = m.totals ?? {}
  const inClass = TOTALS.filter(([k]) => tot[k])

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Segmented size="sm" label="Style of this lecture" value={m.preset ?? ''} disabled={busy} onChange={(p) => queue({ action: 'preset', preset: p }, 'Planning in this style…')} options={MIX_PRESETS.map(([id, label]) => ({ id, label }))} />
        {busy ? <span role="status" className="flex items-center gap-2 text-sm text-ink-2"><Cradle size={18} />{j?.action === 'approve' ? 'Making the NotebookLM prompts and the quiz…' : 'Planning…'}</span>
          : approved ? <ApprovedBadge>Plan approved by you</ApprovedBadge> : <GeneratedBadge>Proposed by ProfsAgent · not approved yet</GeneratedBadge>}
      </div>
      {j?.state === 'error' && <Callout tone="rose" className="mt-3">{j.error}</Callout>}
      {checks.length > 0 && (
        <ul className="mt-3 space-y-1 rounded-lg border border-amber-line bg-amber-soft px-3 py-2">
          {checks.map((c, i) => <li key={i} className="flex gap-2 text-sm text-amber-300"><TriangleAlert aria-hidden className="mt-0.5 size-3.5 shrink-0" />{sentence(c.message.replace(/W\d\d\.L\d+\.C(\d+)/g, 'Part $1'))}</li>)}
        </ul>
      )}

      <DataTable caption="The lecture's parts and how each is taught" className="mt-3">
        <thead><tr><Th>Part</Th><Th className="w-20">Time</Th><Th className="w-52">How</Th><Th className="w-24"><span className="sr-only">Lock</span></Th></tr></thead>
        <tbody>
          {m.recap_minutes > 0 && <Tr className="bg-white/[0.02]"><Td className="font-medium text-ink-1">Recap of the last lecture</Td><Td className="whitespace-nowrap font-mono text-sm">{m.recap_minutes} min</Td><Td colSpan={2} className="text-sm text-ink-3">Questions from the last quiz</Td></Tr>}
          {m.parts.map((p) => {
            const c = comps[p.component]
            const ways = [...new Set<MixWay>(['slides', 'in_class', 'notebooklm', ...(p.allowed ?? [])])]
            const video = p.way === 'youtube' || p.way === 'youtube_bridge'
            const alt = p.alternative?.way && p.alternative.way !== p.way && !approved ? p.alternative : null
            return (
              <Tr key={p.component} className={p.locked ? 'bg-iris-soft/40' : undefined}>
                <Td>
                  <p className="font-medium text-ink-1">{p.title}</p>
                  {c?.teaches && c.teaches !== p.title && <p className="mt-0.5 text-sm text-ink-3">{c.teaches}</p>}
                  {p.reason && <p className="mt-1.5 text-sm text-ink-2"><span className="mr-1.5 text-xs font-semibold text-iris-300">Why</span>{p.reason}</p>}
                  <div className="mt-1.5 space-y-1 text-sm">
                    {video && !!p.segments?.length && <p>{p.segments.map((s, i) => <span key={i}>{i > 0 && ' · '}<Ext href={s.url}>▶ {s.start}–{s.end}</Ext> <span className="text-ink-3">{s.video}</span></span>)}</p>}
                    {p.way === 'youtube_bridge' && !!p.bridge?.length && <p className="text-ink-3">Your slides add: {p.bridge.join('; ')}</p>}
                    {p.way === 'notebooklm' && !!p.uncovered?.length && <p className="text-amber-300">Add a source that covers: {p.uncovered.join(', ')}</p>}
                    {p.way === 'simulation' && p.simulation && (p.simulation.id
                      ? <TextButton onClick={() => openSim({ id: p.simulation!.id!, title: p.simulation!.title, lecture: l.id })}>Try “{p.simulation.title}”</TextButton>
                      : <Ext href={p.simulation.url}>Open “{p.simulation.title}”</Ext>)}
                    {alt && <p className="text-ink-3">Or {MIX_LABEL[alt.way!] ?? alt.way}: {alt.reason} <TextButton disabled={busy} onClick={() => change(p.component, { way: alt.way })}>Use this</TextButton></p>}
                  </div>
                </Td>
                <Td className="whitespace-nowrap font-mono text-sm">{p.minutes} min</Td>
                <Td>
                  <Select aria-label={`How to teach ${p.title}`} value={p.way} disabled={busy} onChange={(e) => change(p.component, { way: e.target.value })}>{ways.map((w) => <option key={w} value={w}>{MIX_LABEL[w]}</option>)}</Select>
                  {(video || p.way === 'notebooklm') && (
                    <Select className="mt-1.5" aria-label="When students watch it" value={p.when === 'pre_class' ? 'pre_class' : 'in_class'} disabled={busy} onChange={(e) => change(p.component, { when: e.target.value })}><option value="in_class">In class</option><option value="pre_class">Before class</option></Select>
                  )}
                </Td>
                <Td>
                  <Button size="sm" variant={p.locked ? 'primary' : 'ghost'} aria-pressed={!!p.locked} disabled={busy} title="A locked part stays as it is when you ask for a new plan"
                    icon={p.locked ? <Lock aria-hidden /> : <LockOpen aria-hidden />} onClick={() => change(p.component, { locked: !p.locked })}>{p.locked ? 'Locked' : 'Lock'}</Button>
                </Td>
              </Tr>
            )
          })}
          {m.quiz_minutes > 0 && <Tr className="bg-white/[0.02]"><Td className="font-medium text-ink-1">Closing quiz</Td><Td className="whitespace-nowrap font-mono text-sm">{m.quiz_minutes} min</Td><Td colSpan={2} className="text-sm text-ink-3">Made when you approve</Td></Tr>}
        </tbody>
      </DataTable>

      <p className="mt-3 text-sm text-ink-2">
        {inClass.length > 0 && <>In class: {inClass.map(([k, t]) => `${t} ${tot[k]} min`).join(' · ')}</>}
        {tot.video_pre_class ? ` · before class: ${tot.video_pre_class} min of video` : ''}{m.prep_minutes ? ` · your preparation: about ${m.prep_minutes} min` : ''}
      </p>

      <div className="mt-4 grid items-end gap-3 md:grid-cols-[1fr_auto]">
        <label className="text-sm text-ink-3">Anything to change?
          <Textarea className="mt-1" rows={2} disabled={busy} value={note ?? m.note ?? ''} placeholder="For example: more in-class work; keep videos short" onChange={(e) => setNote(e.target.value)} />
        </label>
        <div className="flex flex-wrap gap-2">
          <Button disabled={busy} onClick={() => queue({ action: 'propose', note: note ?? m.note ?? '' }, (note ?? '').trim() ? 'Planning again with your note…' : 'Planning how to teach each part…')}>Plan again with my note</Button>
          <Button variant="primary" disabled={busy} onClick={() => queue({ action: 'approve' }, 'Approved. Making the NotebookLM prompts and the quiz…')}>{approved ? 'Approve again' : 'Approve the plan'}</Button>
        </div>
      </div>

      {approved && (
        <div className="mt-4 border-t border-line pt-4">
          <div className="flex flex-wrap items-center gap-3">
            {v.notebooklm.includes(l.id) && m.parts.some((p) => p.way === 'notebooklm') && <Button size="sm" to={lectureUrl(base, l.id, '/notebooklm')}>Open the NotebookLM prompts</Button>}
            <span className="text-sm text-ink-3">Approved {stamp(m.approved_at)}. Slides made from now on follow this plan.</span>
          </div>
          {q?.questions && (
            <Disclosure className="mt-3" summary={`The closing quiz (${q.questions.length} questions)${q.recap?.length ? ` and ${q.recap.length} recap questions` : ''}`}>
              <ol className="space-y-3">
                {q.questions.map((x, i) => (
                  <li key={i} className="border-t border-line pt-3 first:border-t-0 first:pt-0">
                    <p className="text-base text-ink-1"><b className="font-semibold">{i + 1}. </b>{x.question}</p>
                    {!!x.options?.length && <ol className="mt-1 space-y-0.5 text-sm text-ink-2">{x.options.map((o, k) => <li key={k} className="flex gap-2"><span className="font-mono text-xs pt-0.5">{String.fromCharCode(65 + k)}</span>{o}</li>)}</ol>}
                    <p className="mt-1 text-sm text-ink-3">Answer: {x.answer}{x.explanation ? ` · ${x.explanation}` : ''}</p>
                  </li>
                ))}
              </ol>
            </Disclosure>
          )}
        </div>
      )}
    </div>
  )
}

/** The part list as the search made it, for a lecture that has no teaching plan yet. */
export function PlanTab({ v, rid, base, l, r, act }: { v: DeliveryView; rid: string; base: string; l: Lecture; r: LectureResult; act: Act }) {
  const tl = Object.fromEntries((r.timeline ?? []).map((x) => [x.component, x]))
  const nlm = r.notebooklm?.components ?? []
  const j = v.jobs?.mix?.[l.id]
  const total = r.components.reduce((s, c) => s + c.minutes, 0)
  return (
    <div>
      <p className="text-base text-ink-2">This lecture is planned as {r.components.length} parts ({total} min). Each video clip was chosen by one AI and checked word by word by a different one; a video that only partly teaches a part is not suggested.</p>
      <DataTable caption="The lecture's parts and what delivers each" className="mt-3">
        <thead><tr><Th className="w-12">Part</Th><Th>What it teaches</Th><Th className="w-20">Time</Th><Th className="w-[38%]">Delivered by</Th></tr></thead>
        <tbody>
          {r.components.map((c) => {
            const t = tl[c.id] ?? { delivery: c.in_class ? 'in_class' : nlm.includes(c.id) ? 'notebooklm' : null, segments: [], gap: null }
            return (
              <Tr key={c.id}>
                <Td className="font-mono text-sm">{c.id.split('.').pop()}</Td>
                <Td><p className="font-medium text-ink-1">{c.title}</p><p className="mt-0.5 text-sm text-ink-3">{c.teaches}</p>{!!c.key_terms?.length && <p className="mt-0.5 text-xs text-ink-4">{c.key_terms.join(' · ')}</p>}</Td>
                <Td className="whitespace-nowrap font-mono text-sm">{c.minutes} min</Td>
                <Td className="text-sm">
                  {t.delivery === 'video' ? (
                    <div className="space-y-2">
                      {t.segments.map((s, i) => (
                        <div key={i}>
                          <Ext href={s.url}>{s.start}–{s.end}</Ext> of <i>{s.video}</i>{' '}
                          {s.verdict === 'teaches_fully' ? <Badge tone="mint">{s.coverage != null ? `covers ${Math.round(s.coverage * 100)}% of it` : 'teaches it fully'}</Badge> : <Badge tone="amber">teaches part of it</Badge>}
                          {!!s.evidence?.length && <p className="mt-1 text-xs text-ink-3">{s.evidence[0].at ? `${s.evidence[0].at}: ` : ''}“{s.evidence[0].quote}”</p>}
                          {!!s.limitations?.length && <p className="text-xs text-ink-3">Weak spot: {s.limitations[0]}</p>}
                        </div>
                      ))}
                      {t.gap && <p className="text-ink-3"><Badge tone="iris">+ NotebookLM</Badge> {t.gap.video_minutes} of {c.minutes} min on video{t.gap.missing?.length ? `; the video leaves out: ${t.gap.missing.join('; ')}` : ''}</p>}
                    </div>
                  ) : t.delivery === 'notebooklm' ? <><Badge tone="iris">NotebookLM video</Badge> <span className="text-ink-3">no YouTube video teaches it well enough</span></>
                    : t.delivery === 'in_class' ? <><Badge>In class</Badge> <span className="text-ink-3">{(c.kind ?? '').replace('_', ' ')}, taught with your slides</span></>
                    : <span className="text-ink-3">Videos were not asked for</span>}
                </Td>
              </Tr>
            )
          })}
        </tbody>
      </DataTable>
      <div className="mt-4 flex flex-wrap items-center gap-3">
        <Button variant="primary" onClick={() => act(() => api.post(deliveryUrl(rid, `/mix/${enc(l.id)}`), { action: 'propose', note: '' }), 'Planning how to teach each part…')}>Plan how to teach each part</Button>
        {v.notebooklm.includes(l.id) && <Button to={lectureUrl(base, l.id, '/notebooklm')}>Open the NotebookLM pack</Button>}
        {j?.state === 'error' && <span className="text-sm text-rose-300">{j.error}</span>}
      </div>
    </div>
  )
}
