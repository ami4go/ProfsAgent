// Check 4 of 4, the final course sheet: the weekly plan, assessment, books, the evaluation, and the documents.
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import DOMPurify from 'dompurify'
import { BookOpenCheck, CalendarDays, CircleCheck, Clock, Percent, TriangleAlert } from 'lucide-react'
import { api, runUrl } from '@/lib/api'
import { plural } from '@/lib/format'
import type { EditBook, EditComp, EditLab, EditModule, Gate3View } from '@/lib/types'
import { Badge, Button, Card, CardBody, CardHeader, Checkbox, Code, DataTable, EditedBadge, Ext, Field, FieldError, FileLink, Input, Meter, Modal, Row, Select, Skeleton, StatTile, Td, Textarea, Th, Tr } from '@/components/ui'
import { BarList } from '@/components/app/Charts'
import { EvaluationSummary } from '@/components/app/RunPanels'
import { AddButton, EditRow, EditorDialog, RowTools, del, move, upd, useEditor, weekOptions, type SaveFn } from './editing'

// ------------------------------------------------------------------ editors
function WeeksEditor({ v, save, onClose }: { v: Gate3View; save: SaveFn; onClose: () => void }) {
  const [d, setD] = useState<EditModule[]>(() => structuredClone(v.edit.weeks))
  const ed = useEditor(save, onClose)
  const total = d.reduce((s, m) => s + m.topics.reduce((a, t) => a + (parseFloat(String(t.hours)) || 0), 0), 0)
  const over = !!v.hours.available && total > v.hours.available
  const setTopics = (i: number, topics: EditModule['topics']) => setD(upd(d, i, { topics }))
  return (
    <EditorDialog title="Edit topics and hours" size="xl" onClose={onClose} onSave={() => ed.submit('weeks', d)} busy={ed.busy} error={ed.err('_')}
      description={<>Change modules, topics, their order and hours. The {v.edit.n_weeks} weeks are then planned again by the same scheduler. <span className={over ? 'text-rose-300' : 'text-mint-300'}>Planned: {Math.round(total * 10) / 10} h{v.hours.available ? ` of ${v.hours.available} h` : ''}</span></>}>
      <div className="space-y-4">
        {d.map((m, i) => (
          <div key={i} className="rounded-xl border border-line-strong bg-white/[0.02] p-3">
            <div className="flex items-end gap-3">
              <Field className="flex-1" label={`Module ${i + 1}`} htmlFor={`m-${i}`} error={ed.err(`${i}.title`)}><Input id={`m-${i}`} value={m.title} placeholder="Module name" onChange={(e) => setD(upd(d, i, { title: e.target.value }))} /></Field>
              <RowTools i={i} n={d.length} what="this module" onMove={(x) => setD(move(d, i, x))} onRemove={() => setD(del(d, i))} />
            </div>
            <div className="mt-3 space-y-2">
              {m.topics.map((t, j) => {
                const p = `${i}.topics.${j}.`
                return (
                  <EditRow key={j} tools={<RowTools i={j} n={m.topics.length} what="this topic" onMove={(x) => setTopics(i, move(m.topics, j, x))} onRemove={() => setTopics(i, del(m.topics, j))} />}>
                    <Input aria-label="Topic" value={t.title} invalid={!!ed.err(p + 'title')} placeholder="Topic" onChange={(e) => setTopics(i, upd(m.topics, j, { title: e.target.value }))} />
                    <div className="grid gap-3 sm:grid-cols-[7rem_1fr]">
                      <label className="text-xs text-ink-3">Hours<Input className="mt-1" type="number" min={0} step={0.5} value={t.hours} invalid={!!ed.err(p + 'hours')} onChange={(e) => setTopics(i, upd(m.topics, j, { hours: e.target.value }))} /></label>
                      <label className="text-xs text-ink-3">Learning outcomes it teaches<Input className="mt-1" value={t.serves_los} placeholder="e.g. CO1.LO1, CO1.LO2" invalid={!!ed.err(p + 'serves_los')} onChange={(e) => setTopics(i, upd(m.topics, j, { serves_los: e.target.value }))} /></label>
                    </div>
                    <FieldError>{ed.err(p + 'title') ?? ed.err(p + 'hours') ?? ed.err(p + 'serves_los')}</FieldError>
                  </EditRow>
                )
              })}
            </div>
            <AddButton onClick={() => setTopics(i, [...m.topics, { title: '', hours: 1.5, serves_los: '' }])}>Add a topic</AddButton>
          </div>
        ))}
      </div>
      <AddButton onClick={() => setD([...d, { title: '', topics: [{ title: '', hours: 1.5, serves_los: '' }] }])}>Add a module</AddButton>
    </EditorDialog>
  )
}

function LabsEditor({ v, save, onClose }: { v: Gate3View; save: SaveFn; onClose: () => void }) {
  const [d, setD] = useState<EditLab[]>(() => structuredClone(v.edit.labs))
  const ed = useEditor(save, onClose)
  return (
    <EditorDialog title="Edit labs" size="md" onClose={onClose} onSave={() => ed.submit('labs', d)} busy={ed.busy} error={ed.err('_')}>
      <div className="space-y-3">
        {!d.length && <p className="text-base text-ink-3">No labs.</p>}
        {d.map((l, i) => (
          <EditRow key={i} tools={<RowTools i={i} n={d.length} what="this lab" onRemove={() => setD(del(d, i))} />}>
            <div className="grid gap-3 sm:grid-cols-[1fr_9rem]">
              <Input aria-label="What the lab is about" value={l.title} invalid={!!ed.err(`${i}.title`)} placeholder="What the lab is about" onChange={(e) => setD(upd(d, i, { title: e.target.value }))} />
              <Select aria-label="Week" value={l.week} onChange={(e) => setD(upd(d, i, { week: +e.target.value }))}>{weekOptions(v.edit.n_weeks).map((k) => <option key={k} value={k}>Week {k}</option>)}</Select>
            </div>
            <FieldError>{ed.err(`${i}.title`) ?? ed.err(`${i}.week`)}</FieldError>
          </EditRow>
        ))}
      </div>
      <AddButton onClick={() => setD([...d, { title: '', week: 1 }])}>Add a lab</AddButton>
    </EditorDialog>
  )
}

function AssessmentEditor({ v, save, onClose }: { v: Gate3View; save: SaveFn; onClose: () => void }) {
  const [d, setD] = useState<EditComp[]>(() => structuredClone(v.edit.assessment))
  const ed = useEditor(save, onClose)
  const total = d.reduce((s, c) => s + (parseFloat(String(c.weight)) || 0), 0)
  const ok = Math.abs(total - 100) < 0.01
  return (
    <EditorDialog title="Edit assessment" onClose={onClose} onSave={() => ed.submit('assessment', d)} busy={ed.busy} error={ed.err('_')}
      description={<span className={ok ? 'text-mint-300' : 'text-amber-300'}>Total: {Math.round(total * 100) / 100}% (should be 100%)</span>}>
      <div className="space-y-3">
        {d.map((c, i) => (
          <EditRow key={i} tools={<RowTools i={i} n={d.length} what="this assessment" onRemove={() => setD(del(d, i))} />}>
            <div className="flex flex-wrap items-end gap-4">
              {c.key != null ? <p className="min-w-32 pb-2 font-semibold text-ink-1">{c.name}</p>
                : <label className="min-w-44 text-xs text-ink-3">Kind<Select className="mt-1" value={c.type} onChange={(e) => setD(upd(d, i, { type: e.target.value }))}>{v.edit.assess_types.map((x) => <option key={x.type} value={x.type}>{x.name}</option>)}</Select></label>}
              <label className="w-28 text-xs text-ink-3">Weight %<Input className="mt-1" type="number" min={0} step={1} value={c.weight} invalid={!!ed.err(`${i}.weight`)} onChange={(e) => setD(upd(d, i, { weight: e.target.value }))} /></label>
              <div className="pb-2"><Checkbox checked={c.invigilated} onChange={(x) => setD(upd(d, i, { invigilated: x }))}>Invigilated</Checkbox></div>
            </div>
            <FieldError>{ed.err(`${i}.weight`) ?? ed.err(`${i}.type`)}</FieldError>
            <div>
              <p className="text-xs text-ink-3">Due</p>
              <div className="mt-1 flex flex-wrap gap-2">
                {c.due.map((w, j) => <Select key={j} className="!w-28" aria-label={`Due week ${j + 1}`} value={w} onChange={(e) => setD(upd(d, i, { due: c.due.map((x, k) => (k === j ? +e.target.value : x)) }))}>{weekOptions(v.edit.n_weeks).map((k) => <option key={k} value={k}>Week {k}</option>)}</Select>)}
              </div>
            </div>
          </EditRow>
        ))}
      </div>
      <AddButton onClick={() => setD([...d, { key: null, type: 'quiz', weight: 0, invigilated: false, due: [v.edit.n_weeks] }])}>Add an assessment</AddButton>
    </EditorDialog>
  )
}

function BooksEditor({ v, save, onClose }: { v: Gate3View; save: SaveFn; onClose: () => void }) {
  const [d, setD] = useState<EditBook[]>(() => structuredClone(v.edit.books))
  const ed = useEditor(save, onClose)
  return (
    <EditorDialog title="Edit books and papers" description="A new book or paper is looked up online by its ISBN or DOI, and added only if it is found." onClose={onClose} onSave={() => ed.submit('books', d)} busy={ed.busy} error={ed.err('_')}>
      <div className="space-y-3">
        {d.map((b, i) => (
          <EditRow key={i} tools={<RowTools i={i} n={d.length} what="this item" onRemove={() => setD(del(d, i))} />}>
            {b.id ? <p className="text-base text-ink-1">{b.title}</p>
              : <Input aria-label="ISBN or DOI" value={b.ident ?? ''} invalid={!!ed.err(`${i}.ident`)} placeholder="ISBN or DOI, e.g. 9781098166304 or 10.1145/3540250" onChange={(e) => setD(upd(d, i, { ident: e.target.value }))} />}
            <FieldError>{ed.err(`${i}.ident`)}</FieldError>
            <Select className="!w-48" aria-label="Role" value={b.role || 'reference'} onChange={(e) => setD(upd(d, i, { role: e.target.value }))}><option value="primary">Textbook</option><option value="reference">Reference</option><option value="reading">Reading</option></Select>
          </EditRow>
        ))}
      </div>
      <AddButton onClick={() => setD([...d, { ident: '', role: 'reference' }])}>Add a book or paper</AddButton>
    </EditorDialog>
  )
}

function DescriptionEditor({ v, save, onClose }: { v: Gate3View; save: SaveFn; onClose: () => void }) {
  const [t, setT] = useState(v.edit.description.text)
  const ed = useEditor(save, onClose)
  return (
    <EditorDialog title="Edit the course description" size="md" onClose={onClose} onSave={() => ed.submit('description', { text: t })} busy={ed.busy} error={ed.err('_') ?? ed.err('text')}>
      <Textarea aria-label="Course description" rows={8} value={t} onChange={(e) => setT(e.target.value)} />
    </EditorDialog>
  )
}

/** The full proposal as the server wrote it from Markdown; cleaned before it is put on the page. */
export function ProposalDialog({ rid, open, onClose }: { rid: string; open: boolean; onClose: () => void }) {
  const { data, isLoading, error } = useQuery({ queryKey: ['proposal', rid], queryFn: () => api.get<{ html: string }>(runUrl(rid, '/proposal')), enabled: open, staleTime: 0 })
  return (
    <Modal open={open} onOpenChange={(o) => !o && onClose()} size="xl" title="The full proposal" description="Everything in one document, with the appendices on evidence and checks">
      {isLoading && <div className="space-y-3"><Skeleton className="h-6 w-1/2" /><Skeleton className="h-3 w-full" /><Skeleton className="h-3 w-full" /><Skeleton className="h-3 w-2/3" /></div>}
      {error && <p className="text-base text-ink-3">The proposal isn’t written yet.</p>}
      {data && <div className="prose-app" dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(data.html) }} />}
    </Modal>
  )
}

// ------------------------------------------------------------------ the view
type Section = 'description' | 'weeks' | 'labs' | 'assessment' | 'books'
const ROLE: Record<string, string> = { primary: 'Textbook', reference: 'Reference', reading: 'Reading' }

export function FinalSheetView({ v, rid, save, final }: { v: Gate3View; rid: string; save?: SaveFn; final?: boolean }) {
  const [editing, setEditing] = useState<Section | null>(null)
  const [proposal, setProposal] = useState(false)
  const edit = (s: Section, label = 'Edit') => save && <Button size="sm" onClick={() => setEditing(s)}>{label}</Button>
  const mark = (...k: string[]) => { const c = k.flatMap((x) => v.edited?.[x] ?? []); return c.length ? <EditedBadge changes={c} /> : null }
  const close = () => setEditing(null)
  const checked = v.books.filter((b) => b.verified && v.recheck?.[b.title]?.status !== 'mismatch').length
  const hoursOver = v.hours.planned != null && v.hours.available != null && v.hours.planned > v.hours.available
  const invOk = v.invigilated_pct >= 40

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatTile label="Teaching weeks" value={v.weeks.length} icon={<CalendarDays />} />
        <StatTile label="Lecture hours planned" icon={<Clock />} tone={hoursOver ? 'rose' : 'neutral'}
          value={<>{v.hours.planned ?? '–'}{v.hours.available ? <span className="text-lg font-normal text-ink-3"> / {v.hours.available}</span> : null}</>} hint={hoursOver ? 'More than the hours available' : 'of the hours available'} />
        <StatTile label="Assessment total" value={`${v.assessment_total}%`} icon={<Percent />} tone={Math.abs(v.assessment_total - 100) < 0.01 ? 'neutral' : 'amber'} hint={`${v.invigilated_pct}% invigilated`} />
        <StatTile label="Books checked online" value={<>{checked}<span className="text-lg font-normal text-ink-3"> / {v.books.length}</span></>} icon={<BookOpenCheck />} tone={checked === v.books.length ? 'mint' : 'amber'} hint="ISBN or DOI found, title matches" />
      </div>

      {v.evaluation && <EvaluationSummary ev={v.evaluation} final={final} />}

      {(v.description || save) && (
        <Card>
          <CardHeader title="Course description" actions={<>{mark('description')}{edit('description')}</>} />
          <CardBody><p className="max-w-[46rem] text-md leading-relaxed text-ink-2">{v.description || 'Not written yet.'}</p></CardBody>
        </Card>
      )}

      <Card>
        <CardHeader title="Weekly plan" description={`${plural(v.weeks.length, 'week')}, with the hours each topic takes`} actions={<>{mark('weeks', 'labs')}{edit('labs', 'Edit labs')}{edit('weeks', 'Edit topics and hours')}</>} />
        <CardBody>
          <DataTable caption="Weekly plan: topics, hours and labs for each week">
            <thead><tr><Th className="w-16">Week</Th><Th>Topics</Th><Th className="w-20 text-right">Hours</Th><Th className="w-[32%]">Lab</Th></tr></thead>
            <tbody>
              {v.weeks.map((w) => (
                <Tr key={w.week}>
                  <Td className="font-mono text-sm text-ink-3 tnum">W{String(w.week).padStart(2, '0')}</Td>
                  <Td>
                    <ul className="space-y-1">{w.topics.map((t, i) => <li key={i} className="text-ink-1">{t.title}</li>)}</ul>
                    {w.midsem_after && <Badge tone="amber" className="mt-2">Mid-sem exam after this week</Badge>}
                  </Td>
                  <Td className="text-right tnum"><ul className="space-y-1">{w.topics.map((t, i) => <li key={i}>{t.hours} h</li>)}</ul></Td>
                  <Td className="text-sm">{w.labs.join('; ') || <span className="text-ink-4">–</span>}</Td>
                </Tr>
              ))}
            </tbody>
          </DataTable>
        </CardBody>
      </Card>

      <Card>
        <CardHeader title="Assessment" description="Components, their weight, and how the marks spread over the outcomes" actions={<>{mark('assessment')}{edit('assessment')}</>} />
        <CardBody>
          <div className="grid gap-6 lg:grid-cols-[minmax(0,1.3fr)_minmax(0,1fr)]">
            <DataTable caption="Assessment components">
              <thead><tr><Th>Component</Th><Th className="text-right">Weight</Th><Th>How many</Th><Th>Invigilated</Th></tr></thead>
              <tbody>
                {v.assessment.map((a) => (
                  <Tr key={a.name}>
                    <Td className="font-medium text-ink-1">{a.name}</Td>
                    <Td className="text-right tnum">{a.weight}%</Td>
                    <Td>{a.count}{a.due.length > 0 && <span className="text-xs text-ink-3"> · week {a.due.join(', ')}</span>}</Td>
                    <Td>{a.invigilated ? <span className="inline-flex items-center gap-1 text-ink-1"><CircleCheck aria-hidden className="size-3.5 text-mint-400" />Yes</span> : 'No'}</Td>
                  </Tr>
                ))}
              </tbody>
            </DataTable>
            <div className="space-y-5">
              <div>
                <p className="label-caps mb-2">Weight by component</p>
                <BarList label="Weight by component" rows={v.assessment.map((a) => ({ name: a.name, value: a.weight }))} max={Math.max(...v.assessment.map((a) => a.weight), 1)} />
              </div>
              <div>
                <div className="flex items-center justify-between gap-2 text-sm">
                  <span className={`flex items-center gap-1.5 ${invOk ? 'text-mint-300' : 'text-amber-300'}`}>{invOk ? <CircleCheck aria-hidden className="size-4" /> : <TriangleAlert aria-hidden className="size-4" />}{v.invigilated_pct}% invigilated</span>
                  <span className="text-xs text-ink-3">at least 40% needed</span>
                </div>
                <Meter className="mt-1.5" value={v.invigilated_pct} tone={invOk ? 'mint' : 'amber'} label="Invigilated share of the marks" />
              </div>
              {Object.keys(v.co_marks).length > 0 && (
                <div>
                  <p className="label-caps mb-2">Marks per course outcome</p>
                  <BarList label="Marks per course outcome" rows={Object.entries(v.co_marks).map(([k, x]) => ({ name: k, value: Math.round(x) }))} />
                </div>
              )}
            </div>
          </div>
        </CardBody>
      </Card>

      <Card>
        <CardHeader title="Books and papers" description="Each one was looked up by its ISBN or DOI, then checked a second time" actions={<>{mark('books')}{edit('books')}</>} />
        <CardBody>
          {v.books.map((b) => {
            const rc = v.recheck?.[b.title] ?? { status: '' }
            const bad = rc.status === 'mismatch'
            return (
              <Row key={b.title} aside={<>
                {b.role && <Badge>{ROLE[b.role] ?? b.role}</Badge>}
                {!b.verified ? <Badge tone="amber" icon={<TriangleAlert aria-hidden />}>Not checked</Badge> : bad ? <Badge tone="amber" icon={<TriangleAlert aria-hidden />}>Check failed</Badge> : <Badge tone="mint" icon={<CircleCheck aria-hidden />}>Found online</Badge>}
              </>}>
                <p className="font-medium"><Ext href={b.link} quiet>{b.title}</Ext></p>
                <p className="mt-0.5 text-sm text-ink-3">{[b.authors, b.year].filter(Boolean).join(' · ')}{b.id && <> · <Code>{b.id}</Code></>}</p>
                {bad && <p className="mt-1.5 rounded-md border border-amber-line bg-amber-soft px-2.5 py-1.5 text-sm text-amber-300">Second check: {rc.record}. Please check this book before using it.</p>}
              </Row>
            )
          })}
          {!v.books.length && <p className="text-base text-ink-3">No books or papers.</p>}
          {v.books_rejected > 0 && <p className="mt-3 border-t border-line pt-3 text-xs text-ink-3">{plural(v.books_rejected, 'book')} removed: not found online.</p>}
        </CardBody>
      </Card>

      <Card>
        <CardHeader title="Documents" description={final ? 'The approved course sheet' : 'Drafts until you approve; they are written again after every change'} actions={<Button size="sm" onClick={() => setProposal(true)}>Read the full proposal</Button>} />
        <CardBody>
          <div className="grid gap-2 sm:grid-cols-3">
            <FileLink href={runUrl(rid, '/download/pdf')} newTab name="Course sheet" meta="PDF · official layout" />
            {v.files['course_template.xlsx'] && <FileLink href={runUrl(rid, '/download/xlsx')} name="IIIT-D course template" meta="Excel · filled in" />}
            {v.files['proposal.md'] && <FileLink href={runUrl(rid, '/download/md')} name="Full proposal" meta="Markdown · with appendices" />}
          </div>
        </CardBody>
      </Card>

      <ProposalDialog rid={rid} open={proposal} onClose={() => setProposal(false)} />
      {save && editing === 'weeks' && <WeeksEditor v={v} save={save} onClose={close} />}
      {save && editing === 'labs' && <LabsEditor v={v} save={save} onClose={close} />}
      {save && editing === 'assessment' && <AssessmentEditor v={v} save={save} onClose={close} />}
      {save && editing === 'books' && <BooksEditor v={v} save={save} onClose={close} />}
      {save && editing === 'description' && <DescriptionEditor v={v} save={save} onClose={close} />}
    </div>
  )
}
