// Check 3 of 4, the outcomes: course outcomes read as sentences with their learning outcomes; the programme mapping is
// one quiet line per outcome, and a full matrix on demand.
import { useState } from 'react'
import { Plus, Trash2 } from 'lucide-react'
import type { CoCard, EditCo, EditLo, Gate2View } from '@/lib/types'
import { plural } from '@/lib/format'
import { Badge, Button, Card, CardBody, CardHeader, EditedBadge, Field, FieldError, Input, Row, Segmented, Select, Textarea, Tip, ToggleChip, confirm } from '@/components/ui'
import { CoPoMatrix } from '@/components/app/Charts'
import { IssueList } from '@/components/app/Findings'
import { AddButton, EditRow, EditorDialog, RowTools, del, move, upd, useEditor, type SaveFn } from './editing'

const ACTION: Record<string, string> = { add: 'Add', drop: 'Drop', merge: 'Merge', reorder: 'Reorder' }
const words = (s: string) => s.replace(/_/g, ' ')
const newCo = (): EditCo => ({ statement: '', bloom_level: 3, condition: '', degree: '', covers_topic_groups: [], evidence_types: [], los: [], pos: [] })
const newLo = (): EditLo => ({ statement: '', bloom_level: 3, condition: '', degree: '', suggested_task_type: 'exam_question' })

function Strength({ n }: { n: number | null }) {
  return (
    <span aria-label={`strength ${n ?? 0} of 3`} className="inline-flex gap-0.5">
      {[1, 2, 3].map((i) => <span key={i} aria-hidden className={`size-1.5 rounded-full ${i <= (n ?? 0) ? 'bg-iris-400' : 'bg-white/15'}`} />)}
    </span>
  )
}

function CoEditor({ v, id, save, onClose }: { v: Gate2View; id: string | null; save: SaveFn; onClose: () => void }) {
  const E = v.edit
  const [d, setD] = useState<EditCo>(() => (id ? structuredClone(E.cos[id]) : newCo()))
  const [pick, setPick] = useState('')
  const ed = useEditor(save, onClose)
  const set = (patch: Partial<EditCo>) => setD((x) => ({ ...x, ...patch }))
  const levels = [1, 2, 3, 4, 5, 6].map((n) => <option key={n} value={n}>{n} · {E.bloom[String(n)]}</option>)
  const toggle = (k: 'covers_topic_groups' | 'evidence_types', x: string) => set({ [k]: d[k].includes(x) ? d[k].filter((y) => y !== x) : [...d[k], x] })
  const remove = async () => {
    if (!(await confirm({ title: `Remove ${id}?`, body: 'Its learning outcomes are removed with it.', confirm: `Remove ${id}`, danger: true }))) return
    ed.submit('co_delete', { id })
  }
  return (
    <EditorDialog title={id ? `Edit ${id}` : 'New course outcome'} size="xl" onClose={onClose} onSave={() => ed.submit('co', d)} busy={ed.busy} error={ed.err('_')}
      left={id ? <Button variant="danger" size="sm" icon={<Trash2 aria-hidden />} disabled={ed.busy} onClick={remove}>Remove {id}</Button> : undefined}>
      <div className="space-y-4">
        <Field label="Statement" htmlFor="co-st" hint="Starts with its verb." error={ed.err('co.statement')}><Textarea id="co-st" rows={2} value={d.statement} placeholder="Design …" onChange={(e) => set({ statement: e.target.value })} /></Field>
        <div className="grid gap-4 sm:grid-cols-3">
          <Field label="Bloom level" htmlFor="co-bl" error={ed.err('co.bloom_level')}><Select id="co-bl" value={d.bloom_level} onChange={(e) => set({ bloom_level: +e.target.value })}>{levels}</Select></Field>
          <Field label="Under what conditions" htmlFor="co-cond" error={ed.err('co.condition')}><Input id="co-cond" value={d.condition} placeholder="given a small web application" onChange={(e) => set({ condition: e.target.value })} /></Field>
          <Field label="To what standard" htmlFor="co-deg" error={ed.err('co.degree')}><Input id="co-deg" value={d.degree} placeholder="so that all its tests pass" onChange={(e) => set({ degree: e.target.value })} /></Field>
        </div>
        {E.topic_groups.length > 0 && (
          <Field label="Topic groups it covers"><div className="flex flex-wrap gap-1.5">{E.topic_groups.map((g) => <ToggleChip key={g.id} on={d.covers_topic_groups.includes(g.id)} onClick={() => toggle('covers_topic_groups', g.id)}>{g.title}</ToggleChip>)}</div></Field>
        )}
        <Field label="How students show it"><div className="flex flex-wrap gap-1.5">{E.evidence.map((x) => <ToggleChip key={x} on={d.evidence_types.includes(x)} onClick={() => toggle('evidence_types', x)}>{words(x)}</ToggleChip>)}</div></Field>

        <div>
          <h3 className="text-md font-semibold text-ink-1">Learning outcomes</h3>
          <div className="mt-2 space-y-3">
            {!d.los.length && <p className="text-base text-ink-3">None yet.</p>}
            {d.los.map((l, j) => {
              const p = `los.${j}.`
              const setLo = (patch: Partial<EditLo>) => set({ los: upd(d.los, j, patch) })
              return (
                <EditRow key={j} tools={<RowTools i={j} n={d.los.length} what="this learning outcome" onMove={(x) => set({ los: move(d.los, j, x) })} onRemove={() => set({ los: del(d.los, j) })} />}>
                  <p className="label-caps">{l.id ?? 'New'}</p>
                  <Textarea aria-label="Learning outcome" rows={2} value={l.statement} invalid={!!ed.err(p + 'statement')} placeholder="Implement …" onChange={(e) => setLo({ statement: e.target.value })} />
                  <FieldError>{ed.err(p + 'statement') ?? ed.err(p + 'bloom_level')}</FieldError>
                  <div className="grid gap-3 sm:grid-cols-2">
                    <Select aria-label="Bloom level" value={l.bloom_level} onChange={(e) => setLo({ bloom_level: +e.target.value })}>{levels}</Select>
                    <Select aria-label="Assessed by" value={l.suggested_task_type ?? 'exam_question'} onChange={(e) => setLo({ suggested_task_type: e.target.value })}>{E.evidence.map((x) => <option key={x} value={x}>Assessed by: {words(x)}</option>)}</Select>
                    <Input aria-label="Condition" value={l.condition} placeholder="Condition (given …)" onChange={(e) => setLo({ condition: e.target.value })} />
                    <Input aria-label="Standard" value={l.degree} placeholder="Standard (so that …)" onChange={(e) => setLo({ degree: e.target.value })} />
                  </div>
                </EditRow>
              )
            })}
          </div>
          <AddButton onClick={() => set({ los: [...d.los, newLo()] })}>Add a learning outcome</AddButton>
        </div>

        <div>
          <h3 className="text-md font-semibold text-ink-1">Programme outcomes it supports</h3>
          <div className="mt-2 space-y-2">
            {!d.pos.length && <p className="text-base text-ink-3">None yet.</p>}
            {d.pos.map((p, j) => {
              const po = E.pos.find((x) => x.uid === p.po_uid) ?? { label: p.po_uid, text: '' }
              return (
                <div key={p.po_uid} className="flex items-center gap-3 rounded-lg border border-line bg-white/[0.02] px-3 py-2">
                  <p className="min-w-0 flex-1 text-sm"><b className="font-semibold text-ink-1">{po.label}</b> <span className="text-ink-3">{po.text}</span></p>
                  <Select className="!w-44 shrink-0" aria-label={`Strength for ${po.label}`} value={p.strength ?? 2} onChange={(e) => set({ pos: upd(d.pos, j, { strength: +e.target.value }) })}>
                    <option value={1}>Strength 1 · low</option><option value={2}>Strength 2 · medium</option><option value={3}>Strength 3 · high</option>
                  </Select>
                  <RowTools i={j} n={d.pos.length} what={po.label} onRemove={() => set({ pos: del(d.pos, j) })} />
                </div>
              )
            })}
          </div>
          <div className="mt-2 flex gap-2">
            <Select aria-label="Programme outcome to add" value={pick} onChange={(e) => setPick(e.target.value)}>
              <option value="">Add a programme outcome…</option>
              {E.pos.filter((x) => !d.pos.some((p) => p.po_uid === x.uid)).map((x) => <option key={x.uid} value={x.uid}>{x.label} · {x.text}</option>)}
            </Select>
            <Button disabled={!pick} onClick={() => { set({ pos: [...d.pos, { po_uid: pick, strength: 2 }] }); setPick('') }}>Add</Button>
          </div>
        </div>
      </div>
    </EditorDialog>
  )
}

function CoBlock({ c, onEdit }: { c: CoCard; onEdit?: () => void }) {
  return (
    <Card>
      <div className="flex flex-wrap items-center justify-between gap-2 px-5 pt-4">
        <div className="flex flex-wrap items-center gap-2">
          <span className="font-mono text-sm font-semibold text-ink-1">{c.id}</span>
          <Tip label="Bloom level: the kind of thinking this outcome asks for"><span tabIndex={0}><Badge tone="iris">{c.level}</Badge></span></Tip>
          {c.edited && <EditedBadge changes={['You changed this outcome at this step']} />}
        </div>
        {onEdit && <Button size="sm" onClick={onEdit}>Edit</Button>}
      </div>
      <CardBody className="pt-2">
        <p className="text-md text-ink-1">{c.statement}</p>
        <IssueList issues={c.issues} />
        {c.los.length > 0 && (
          <>
            <p className="label-caps mt-4">Learning outcomes</p>
            <ul className="mt-1.5 space-y-1.5">
              {c.los.map((l) => (
                <li key={l.id} className="grid grid-cols-[4.75rem_1fr] gap-2 text-base">
                  <span className="pt-0.5 font-mono text-xs font-medium text-ink-3">{l.id}</span>
                  <span className="text-ink-2">{l.statement} <span className="whitespace-nowrap text-xs text-ink-3">· {l.level}</span></span>
                </li>
              ))}
            </ul>
          </>
        )}
        {c.pos.length > 0 && (
          <>
            <p className="label-caps mt-4">Programme outcomes it supports</p>
            <ul className="mt-1.5 flex flex-wrap gap-1.5">
              {c.pos.map((p, i) => (
                <li key={i}><Tip label={<>{p.text || p.short}<br /><span className="text-ink-2">Strength {p.strength ?? 0} of 3</span></>}>
                  <span tabIndex={0} className="inline-flex h-6 items-center gap-1.5 rounded-md border border-line bg-white/[0.03] px-2 text-xs text-ink-2">{p.programme} <span className="font-mono text-ink-1">{p.short}</span><Strength n={p.strength} /></span>
                </Tip></li>
              ))}
            </ul>
          </>
        )}
      </CardBody>
    </Card>
  )
}

export function OutcomesView({ v, save }: { v: Gate2View; save?: SaveFn }) {
  const [mode, setMode] = useState<'cards' | 'matrix'>('cards')
  const [editing, setEditing] = useState<string | null | undefined>(undefined)   // a CO id, null = a new one, undefined = closed
  const nlo = v.cos.reduce((n, c) => n + c.los.length, 0)
  const reject = async (i: number) => {
    if (await confirm({ title: 'Reject this proposed change to the topics?', confirm: 'Reject it', danger: true })) await save!('proposals', { reject: [i] })
  }
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-base text-ink-2">{plural(v.cos.length, 'course outcome')}, {plural(nlo, 'learning outcome')}</p>
        <Segmented label="How to show the outcomes" value={mode} onChange={setMode} options={[{ id: 'cards', label: 'Outcomes' }, { id: 'matrix', label: 'Programme mapping' }]} />
      </div>

      {(v.proposals.length > 0 || v.no_topics_given) && (
        <Card>
          <CardHeader title="Changes to the topics ProfsAgent proposes" actions={<EditedBadge changes={v.edited?.proposals} />} />
          <CardBody>
            {v.proposals.length ? v.proposals.map((p) => (
              <Row key={p.i} aside={save && <Button size="sm" variant="danger" onClick={() => reject(p.i)}>Reject</Button>}>
                <p className="text-ink-1"><Badge tone="iris" className="mr-2">{ACTION[p.action] ?? p.action}</Badge>{p.proposal || p.targets.join(', ')}</p>
                {p.reason && <p className="mt-1 text-sm text-ink-3">{p.reason}</p>}
              </Row>
            )) : <p className="text-base text-ink-3">None. You didn’t list topics, so the topics are planned from these outcomes in the next step; you see them in the weekly plan.</p>}
          </CardBody>
        </Card>
      )}

      {mode === 'matrix' ? (
        <Card>
          <CardHeader title="Programme mapping" description="How strongly each course outcome supports each programme outcome. Point at a cell to read the programme outcome." />
          <CardBody><CoPoMatrix cos={v.cos} /></CardBody>
        </Card>
      ) : (
        <>
          {v.cos.map((c) => <CoBlock key={c.id} c={c} onEdit={save ? () => setEditing(c.id) : undefined} />)}
          {save && <Button variant="ghost" icon={<Plus aria-hidden />} className="border border-dashed border-line-strong" onClick={() => setEditing(null)}>Add a course outcome</Button>}
        </>
      )}
      {save && editing !== undefined && <CoEditor v={v} id={editing} save={save} onClose={() => setEditing(undefined)} />}
    </div>
  )
}
