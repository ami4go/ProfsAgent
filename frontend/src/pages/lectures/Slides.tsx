// Generated slides for one lecture: a draft until the professor approves it. The page shows the deck as content
// (title, bullets, figure, quiz, notes), what the checks found, and the files.
import { useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { Check } from 'lucide-react'
import { api, deliveryUrl, enc, problemOf } from '@/lib/api'
import { MATERIAL_STATUS } from '@/lib/delivery'
import { plural, stamp } from '@/lib/format'
import { keys, useMaterial } from '@/lib/queries'
import { toast } from '@/lib/toast'
import type { DeliveryView, Figure, Lecture, MaterialDetail, Slide } from '@/lib/types'
import { ApprovedBadge, Badge, Button, Callout, Checkbox, Cradle, Disclosure, Ext, Field, FileLink, Skeleton, Textarea, confirm } from '@/components/ui'
import { ChecksPassed, IssueList } from '@/components/app/Findings'
import type { useDeliveryAction } from './shared'

type Act = ReturnType<typeof useDeliveryAction>
const KIND: Record<string, string> = { concept: 'Concept', example: 'Example', worked_problem: 'Worked problem', activity: 'Activity', check: 'Check', summary: 'Summary' }
const FILES: Record<string, [string, string]> = { 'slides.pptx': ['Slides', 'PowerPoint'], 'notes.md': ['Speaker notes and handout', 'Markdown'], 'quiz.json': ['Quiz', 'JSON'] }

function Fig({ f }: { f?: Figure | null }) {
  if (!f || f.kind === 'none') return null
  const cap = f.caption ? <figcaption className="mt-1.5 text-xs text-ink-3">{f.caption}</figcaption> : null
  if (f.kind === 'flow') return <figure className="mt-3"><ol className="flex flex-wrap items-center gap-1.5 text-sm">{(f.steps ?? []).map((s, i) => <li key={i} className="flex items-center gap-1.5">{i > 0 && <span aria-hidden className="text-ink-4">→</span>}<span className="rounded-md border border-line-strong bg-white/[0.04] px-2 py-1 text-ink-1">{s}</span></li>)}</ol>{cap}</figure>
  if (f.kind === 'code') return <figure className="mt-3"><pre className="overflow-x-auto rounded-lg border border-line bg-sunken p-3 font-mono text-xs leading-relaxed text-ink-2">{f.language && <span className="mb-1 block text-ink-4">{f.language}</span>}{f.code}</pre>{cap}</figure>
  if (f.kind === 'table') return <figure className="mt-3 overflow-x-auto"><table className="border-collapse text-sm"><tbody>{(f.rows ?? []).map((r, i) => <tr key={i}>{r.map((c, j) => <td key={j} className={`border border-line px-2.5 py-1 ${i === 0 ? 'bg-white/[0.04] font-semibold text-ink-1' : 'text-ink-2'}`}>{c}</td>)}</tr>)}</tbody></table>{cap}</figure>
  return null
}

function SlideCard({ s, sources }: { s: Slide; sources: MaterialDetail['sources'] }) {
  return (
    <article className="rounded-xl border border-line bg-surface-2/50 p-4">
      <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-ink-3">
        <span><span className="font-mono text-ink-2">Slide {s.number}</span> · {KIND[s.kind] ?? s.kind} · about {Number(s.minutes || 0).toFixed(0)} min</span>
        <span className="flex flex-wrap gap-1">{(s.los ?? []).map((x) => <span key={x} className="rounded bg-iris-soft px-1.5 font-mono text-2xs text-iris-300">{x}</span>)}</span>
      </div>
      <h4 className="mt-1.5 text-md font-semibold text-ink-1">{s.title}</h4>
      {!!s.bullets?.length && <ul className="mt-2 list-disc space-y-1 pl-5 text-base text-ink-2 marker:text-ink-4">{s.bullets.map((b, i) => <li key={i}>{b}</li>)}</ul>}
      <Fig f={s.figure} />
      {s.quiz && (
        <div className="mt-3 rounded-lg border border-line bg-white/[0.03] p-3 text-base">
          <p className="text-ink-1"><b className="font-semibold">Quiz: </b>{s.quiz.question}</p>
          <ol className="mt-1.5 space-y-0.5 pl-1">{(s.quiz.options ?? []).map((o, i) => <li key={i} className={`flex gap-2 ${i === s.quiz!.answer ? 'font-medium text-mint-300' : 'text-ink-2'}`}><span className="font-mono text-xs pt-0.5">{String.fromCharCode(65 + i)}</span>{o}{i === s.quiz!.answer && <Check aria-label="correct answer" className="mt-1 size-3.5 shrink-0" />}</li>)}</ol>
          {s.quiz.explanation && <p className="mt-1.5 text-sm text-ink-3">{s.quiz.explanation}</p>}
        </div>
      )}
      {!!s.sources?.length && <p className="mt-2.5 text-xs text-ink-3">Sources: {s.sources.map((id, i) => { const x = sources[id] ?? {}; return <span key={id}>{i > 0 && ' · '}{x.url ? <Ext href={x.url}>{x.title || id}</Ext> : x.title || id}</span> })}</p>}
      {s.notes && <Disclosure className="mt-2" summary="Speaker notes"><p className="text-sm text-ink-2">{s.notes}</p></Disclosure>}
    </article>
  )
}

export function SlidesTab({ v, rid, l, act }: { v: DeliveryView; rid: string; l: Lecture; act: Act }) {
  const qc = useQueryClient()
  const m = v.material?.[l.id], j = v.jobs?.material?.[l.id]
  const { data: d, isLoading, error } = useMaterial(rid, l.id, m ? `${m.generated_at}|${m.status}` : undefined)
  const [ai, setAi] = useState(false)
  const [ask, setAsk] = useState<null | 'redo' | 'reject'>(null)
  const [text, setText] = useState('')
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)
  const murl = (rest: string) => deliveryUrl(rid, `/material/${enc(l.id)}${rest}`)

  const generate = async () => {
    const force = m?.status === 'approved'
    if (force && !(await confirm({ title: 'Replace the slides you approved?', body: 'A new version is made and takes their place.', confirm: 'Make a new version' }))) return
    await act(() => api.post(murl('/generate'), { ai_review: ai, force }), 'Making the slides. This takes about 2–3 minutes.', 'Could not start')
  }
  const review = async (decision: string, reason = '') => {
    setBusy(true)
    try {
      await api.post(murl('/review'), { decision, reason, ai_review: ai })
      toast.success(decision === 'approve' ? 'Slides approved' : decision === 'redo' ? 'Making a new version with your instructions.' : 'Slides rejected')
      setAsk(null)
      await qc.invalidateQueries({ queryKey: keys.delivery(rid) })
    } catch (e) {
      if (ask) setErr(problemOf(e, 'Could not save')); else toast.error(problemOf(e, 'Could not save'))
    } finally { setBusy(false) }
  }
  const controls = (again: boolean) => (
    <div className="flex flex-wrap items-center gap-4">
      <Button size="sm" variant={again ? 'secondary' : 'primary'} onClick={generate}>{again ? 'Generate again' : 'Generate the slides'}</Button>
      <Checkbox checked={ai} onChange={setAi}>Have a second AI check them <span className="text-ink-3">(1–2 more AI calls)</span></Checkbox>
    </div>
  )

  if (j && (j.state === 'queued' || j.state === 'running')) return (
    <div role="status" className="flex items-center gap-3 py-6 text-base text-ink-2"><Cradle />{j.state === 'queued' ? 'Waiting for another job to finish, then making the slides.' : 'Making the slides. This takes about 2–3 minutes; the page stays usable.'}</div>
  )
  if (!m) return (
    <div className="space-y-4">
      <p className="text-base text-ink-3">No slides yet for this lecture.{j?.state === 'error' ? ` The last try stopped: ${j.error}` : ''}</p>
      {controls(false)}
    </div>
  )
  if (isLoading) return <div className="space-y-3"><Skeleton className="h-5 w-1/3" /><Skeleton className="h-24 w-full" /><Skeleton className="h-24 w-full" /></div>
  if (!d) return <p className="text-base text-ink-3">{problemOf(error, 'The slides could not be loaded.')}</p>

  const st = MATERIAL_STATUS[d.status] ?? { label: d.status, tone: 'neutral' as const }
  const errs = d.findings.filter((f) => f.severity === 'error').length
  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          {d.status === 'approved' ? <ApprovedBadge /> : <Badge tone={st.tone}>{st.label}</Badge>}
          <span className="text-sm text-ink-3">{plural(d.slides_total, 'slide')} ({d.slides.length} with content) · about {Math.round(d.minutes || 0)} min · made {stamp(d.generated_at)}</span>
        </div>
      </div>
      {d.ai_review?.verdict && <Callout tone="iris" className="mt-3" title="A second AI checked these slides (not you)">{d.ai_review.verdict}</Callout>}
      {d.feedback && <p className="mt-3 text-sm text-ink-3">Made with your instructions: “{d.feedback}”</p>}

      <div className="mt-4">
        {ask ? (
          <div className="rounded-lg border border-line bg-white/[0.02] p-3">
            <Field label={ask === 'redo' ? 'What should change? The AI gets this as instructions.' : 'Why reject these slides?'} htmlFor="mat-why" error={err}>
              <Textarea id="mat-why" rows={2} autoFocus value={text} invalid={!!err} placeholder={ask === 'redo' ? 'Fewer bullets per slide; add a worked example on prompt context' : 'I will use my own slides for this lecture'} onChange={(e) => { setText(e.target.value); setErr('') }} />
            </Field>
            <div className="mt-2.5 flex gap-2">
              <Button size="sm" variant={ask === 'redo' ? 'primary' : 'danger'} loading={busy} onClick={() => (text.trim() ? review(ask, text.trim()) : setErr(ask === 'redo' ? 'Say what should change first' : 'Write a short reason first'))}>{ask === 'redo' ? 'Redo the slides' : 'Reject the slides'}</Button>
              <Button size="sm" variant="ghost" onClick={() => setAsk(null)}>Cancel</Button>
            </div>
          </div>
        ) : d.status === 'approved' ? (
          <p className="text-sm text-ink-3">Protected: a new version replaces them only if you confirm.</p>
        ) : (
          <div className="flex flex-wrap gap-2">
            <Button size="sm" variant="success" icon={<Check aria-hidden />} loading={busy} onClick={() => review('approve')}>Approve the slides</Button>
            <Button size="sm" onClick={() => { setText(''); setErr(''); setAsk('redo') }}>Redo with my instructions</Button>
            <Button size="sm" variant="danger" onClick={() => { setText(''); setErr(''); setAsk('reject') }}>Reject</Button>
          </div>
        )}
      </div>

      <div className="mt-5 grid gap-2 sm:grid-cols-3">
        {d.files.map((f) => <FileLink key={f} href={murl(`/file/${f}`)} name={FILES[f]?.[0] ?? f} meta={FILES[f]?.[1] ?? ''} />)}
      </div>
      <p className="mt-3 text-xs text-ink-3">These slides cite {plural(d.cited.length, 'source')}: the course’s checked books and the resources you had approved when they were made. Approve more resources, then generate again, to cite them.</p>

      <h3 className="mt-6 text-md font-semibold text-ink-1">What the checks found</h3>
      {d.findings.length ? (
        <>
          <p className="mt-1 text-sm text-ink-3">{plural(errs, 'error')} · {plural(d.findings.length - errs, 'warning')}</p>
          <IssueList showCodes issues={d.findings.map((f) => ({ severity: f.severity, message: f.message, code: f.code }))} />
        </>
      ) : <ChecksPassed>No problems found (coverage of the learning outcomes, timing, quiz, code, citations).</ChecksPassed>}

      <div className="mt-6 flex flex-wrap items-baseline justify-between gap-2">
        <h3 className="text-md font-semibold text-ink-1">The slides</h3>
        <span className="text-xs text-ink-3">Slides 1–2 (title, objectives) and the references slide are made by code from the course design.</span>
      </div>
      <div className="mt-2.5 space-y-2.5">{d.slides.map((s) => <SlideCard key={s.number} s={s} sources={d.sources} />)}</div>

      <h3 className="mt-6 mb-2.5 text-md font-semibold text-ink-1">Make them again</h3>
      {controls(true)}
    </div>
  )
}
