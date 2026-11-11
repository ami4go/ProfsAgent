// Simulations for one lecture: what ProfsAgent suggests from the catalogue and from other sites, what the professor
// approved (at most two), and the class example students start from.
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Check, FlaskConical } from 'lucide-react'
import { api, deliveryUrl, enc, problemOf } from '@/lib/api'
import { SIM_MAX, simApproved, simsOf } from '@/lib/delivery'
import { useSims } from '@/lib/queries'
import type { DeliveryView, Lecture, SimItem } from '@/lib/types'
import { ApprovedBadge, Badge, Button, Callout, Card, CardBody, CardHeader, Cradle, Disclosure, Ext, Field, Select, TextButton, Textarea, confirm } from '@/components/ui'
import { openSim } from '@/components/app/SimPreview'
import type { useDeliveryAction } from './shared'

type Act = ReturnType<typeof useDeliveryAction>

/** Carried to the Simulations page when the professor asks for a new one from a lecture. */
export interface SimRequestDraft { topic: string; what: string; kind: string; course: string; run_id?: string; lecture?: string }
export const simDraft: { current: SimRequestDraft | null } = { current: null }

export const SimChecked = ({ c }: { c: Pick<SimItem, 'checked'> }) =>
  !c.checked ? null : !c.checked.ok ? <Badge tone="rose">Its last check failed</Badge> : !c.checked.current ? <Badge tone="amber">Changed since its last check</Badge> : null
export const WithCode = ({ on }: { on?: boolean }) => (on ? <Badge tone="iris" title="Shows the algorithm's code beside it">With code</Badge> : null)

export function SimCard({ v, rid, l, act }: { v: DeliveryView; rid: string; l: Lecture; act: Act }) {
  const nav = useNavigate()
  const { data: cat } = useSims()
  const S = v.simulations ?? { state: 'error', error: null, lectures: {} }
  const x = simsOf(v, l.id), items = x.items ?? []
  const [reason, setReason] = useState<{ sim: string; text: string; err: string } | null>(null)
  const [add, setAdd] = useState('')
  const url = deliveryUrl(rid, `/simulations/${enc(l.id)}`)

  const ours = items.filter((i) => !i.external), links = items.filter((i) => i.external)
  const approved = ours.filter(simApproved), pending = ours.filter((i) => !i.decision && !i.retired)
  const linksShown = links.filter((i) => !i.decision || simApproved(i)), aside = items.filter((i) => i.decision && !simApproved(i))
  const cur = pending[0], waiting = ['preparing', 'not started'].includes(S.state), nApproved = items.filter(simApproved).length
  const withCode = cur && !cur.shows_code ? pending.find((i) => i.shows_code) : undefined
  const full = nApproved >= SIM_MAX
  const others = (cat?.entries ?? []).filter((e) => !items.some((i) => i.id === e.id))

  const decide = (sim: string, decision: string) => act(() => api.post(url, { sim, decision }),
    decision === 'approve' ? 'Approved. Students see it in the student view.' : decision === 'replace' ? 'Set aside; here is the next suggestion.' : 'Undone')
  const reject = async () => {
    if (!reason) return
    if (!reason.text.trim()) return setReason({ ...reason, err: 'Write a short reason first' })
    try {
      await api.post(url, { sim: reason.sim, decision: 'reject', reason: reason.text })
      setReason(null)
      await act(async () => null, 'Rejected. If nothing here fits, ask for a new simulation and say what you need.')
    } catch (e) { setReason({ ...reason, err: problemOf(e, 'Could not save') }) }
  }
  const open = (i: SimItem) => openSim({ id: i.id, title: i.title, state: i.example?.state ?? '', lecture: l.id, example: i.example, ctx: { rid, lid: l.id, canSave: i.class_example, example: i.example } })
  const request = () => {
    const rej = items.filter((i) => i.decision?.decision === 'reject' && i.decision.reason).sort((a, b) => String(b.decision!.at).localeCompare(String(a.decision!.at)))[0]
    simDraft.current = { topic: l.topic, what: rej?.decision?.reason ?? '', kind: x.kind && x.kind.id !== 'none' ? x.kind.id : '', course: v.run.course ?? '', run_id: rid, lecture: l.id }
    nav('/simulations')
  }
  const clearExample = async (sim: string) => {
    if (!(await confirm({ title: 'Remove the class example?', body: 'Students then start from the default example.', confirm: 'Remove it' }))) return
    act(() => api.post(`${url}/class-example`, { sim, clear: true }), 'Class example removed', 'Could not remove')
  }

  const reasonBox = (i: SimItem) => reason?.sim === i.id && (
    <div className="mt-3 rounded-lg border border-line bg-white/[0.02] p-3">
      <Field label="Why is it not right for this lecture?" htmlFor={`simwhy-${i.id}`} error={reason.err}><Textarea id={`simwhy-${i.id}`} rows={2} autoFocus value={reason.text} invalid={!!reason.err} onChange={(e) => setReason({ ...reason, text: e.target.value, err: '' })} /></Field>
      <div className="mt-2.5 flex gap-2"><Button size="sm" variant="danger" onClick={reject}>Reject</Button><Button size="sm" variant="ghost" onClick={() => setReason(null)}>Cancel</Button></div>
    </div>
  )
  const item = (i: SimItem) => {
    const ap = simApproved(i), d = i.decision
    const match = i.source === 'added' ? (i.added_by === 'machine' ? 'From your request' : 'Added by you') : i.source === 'suggested' ? (i.close ? 'Close match' : 'Possible match') : ''
    return (
      <article key={i.id} className={`rounded-xl border p-4 ${ap ? 'border-mint-line bg-mint-soft/40' : 'border-line bg-surface-2/50'}`}>
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <h3 className="text-md font-medium text-ink-1">{i.external ? <Ext href={i.url} quiet>{i.title}</Ext> : i.title}</h3>
            <p className="mt-1.5 flex flex-wrap items-center gap-1.5 text-sm text-ink-3">
              {i.external && <Badge tone="neutral">{i.site_name}</Badge>}<WithCode on={i.shows_code} /><SimChecked c={i} />{match && <span>{match}</span>}
            </p>
          </div>
          {ap && <ApprovedBadge />}
        </div>
        {i.summary && <p className="mt-2 text-base text-ink-2">{i.summary}</p>}
        {i.retired && <p className="mt-2 rounded-md border border-amber-line bg-amber-soft px-2.5 py-1.5 text-sm text-amber-300">This simulation was retired from the catalogue. Students can still open it; consider another one.</p>}
        {ap && d?.outdated && <p className="mt-2 rounded-md border border-amber-line bg-amber-soft px-2.5 py-1.5 text-sm text-amber-300">Updated since you approved it (you approved v{d.version}; it is now v{i.version}). Try it again, then approve the new version.</p>}
        {!i.external && i.class_example && (i.example
          ? <p className="mt-2 text-sm text-ink-2"><b className="font-semibold text-ink-1">Class example: </b>{i.example.summary || 'saved'} <TextButton onClick={() => clearExample(i.id)}>Remove</TextButton></p>
          : <p className="mt-2 text-sm text-ink-3">No class example yet: set one in Try it.</p>)}
        <div className="mt-3 flex flex-wrap gap-2">
          {i.external ? <Button size="sm" href={i.url!} external>Open</Button> : <Button size="sm" icon={<FlaskConical aria-hidden />} onClick={() => open(i)}>Try it</Button>}
          {ap ? (
            <>
              {d?.outdated && <Button size="sm" variant="success" icon={<Check aria-hidden />} onClick={() => decide(i.id, 'approve')}>Approve v{i.version}</Button>}
              <Button size="sm" variant="ghost" onClick={() => decide(i.id, 'undo')}>Undo approval</Button>
            </>
          ) : (
            <>
              {!full && <Button size="sm" variant="success" icon={<Check aria-hidden />} onClick={() => decide(i.id, 'approve')}>Approve</Button>}
              {!i.external && pending.length > 1 && <Button size="sm" title="Set it aside and show the next suggestion" onClick={() => decide(i.id, 'replace')}>Replace</Button>}
              <Button size="sm" variant="danger" onClick={() => setReason({ sim: i.id, text: '', err: '' })}>Reject</Button>
            </>
          )}
        </div>
        {reasonBox(i)}
      </article>
    )
  }
  const nothing = !approved.length && !cur && !linksShown.length
  return (
    <Card id="simulation">
      <CardHeader title="Simulation" icon={<FlaskConical />} description="Something students can try for themselves: at most two per lecture"
        actions={nApproved ? <Badge tone="mint">{nApproved} of {SIM_MAX} approved</Badge> : cur || linksShown.length ? <Badge tone="amber">Waiting for your decision</Badge> : <Badge>None chosen</Badge>} />
      <CardBody>
        <div className="space-y-2.5">
          {approved.map(item)}{cur && item(cur)}{withCode && item(withCode)}
        </div>
        {full && <p className="mt-2 text-sm text-ink-3">To approve another, undo one first.</p>}
        {waiting ? <div role="status" className="mt-2 flex items-center gap-3 text-sm text-ink-2"><Cradle size={18} />Looking for simulations…</div>
          : S.state === 'error' ? <Callout tone="amber" className="mt-2" title="Simulations could not be suggested for this course">You can still add one from the catalogue below, or ask for a new one.{S.error && <Disclosure className="mt-1" summary="Technical detail"><span className="font-mono text-xs text-ink-3 [overflow-wrap:anywhere]">{S.error}</span></Disclosure>}</Callout>
          : nothing ? <p className="text-sm text-ink-3">{x.kind && x.kind.id !== 'none' ? `None fits yet. A ${(x.kind.name ?? '').toLowerCase()} would suit this topic.` : 'None fits, and this topic may not need one.'}</p> : null}
        {linksShown.length > 0 && <><p className="label-caps mt-5 mb-2">On other sites</p><div className="space-y-2.5">{linksShown.map(item)}</div></>}
        {aside.length > 0 && (
          <Disclosure className="mt-4" summary={`Set aside (${aside.length})`}>
            <ul className="divide-y divide-line">
              {aside.map((i) => <li key={i.id} className="flex items-center justify-between gap-3 py-2 text-sm"><span><b className="font-medium text-ink-1">{i.title}</b> <span className="text-ink-3">{i.decision!.decision === 'reject' ? `rejected: ${i.decision!.reason}` : 'replaced'}</span></span><Button size="sm" variant="ghost" onClick={() => decide(i.id, 'undo')}>Undo</Button></li>)}
            </ul>
          </Disclosure>
        )}
        <div className="mt-4 flex flex-wrap items-center gap-2 border-t border-line pt-4">
          <Button size="sm" variant={!waiting && nothing ? 'primary' : 'secondary'} onClick={request}>Ask for a new simulation</Button>
          {others.length > 0 && (
            <>
              <Select className="!w-64 max-w-full" aria-label="Add a simulation from the catalogue" value={add} onChange={(e) => setAdd(e.target.value)}><option value="">Add one of ours…</option>{others.map((e) => <option key={e.id} value={e.id}>{e.title}</option>)}</Select>
              <Button size="sm" disabled={!add} onClick={async () => { if (await act(() => api.post(url, { sim: add, decision: 'add' }), 'Added. Try it, then approve or reject it.', 'Could not add')) setAdd('') }}>Add</Button>
            </>
          )}
          <Button size="sm" variant="ghost" to="/simulations">Browse all simulations</Button>
        </div>
      </CardBody>
    </Card>
  )
}
