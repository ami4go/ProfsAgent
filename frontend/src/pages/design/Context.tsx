// Check 2 of 4, the course context: the professor's topics, what was assumed, the rules, and how the course fits with
// IIIT-D courses and comparable courses elsewhere. Every item keeps the reference it came from.
import { useState } from 'react'
import { Check, CircleCheck, Lightbulb, ShieldBan, X } from 'lucide-react'
import type { EditAssumption, EditPrereq, EditWish, Gate1View, TopicGroup } from '@/lib/types'
import { plural } from '@/lib/format'
import { ApprovedBadge, Badge, Button, Card, CardBody, CardHeader, Checkbox, Code, Disclosure, EditedBadge, Ext, Field, FieldError, GeneratedBadge, Input, Meter, Row, Select, Textarea } from '@/components/ui'
import { AddButton, EditRow, EditorDialog, RowTools, del, move, upd, useEditor, weekOptions, type SaveFn } from './editing'

const text = (x: unknown): string => (typeof x === 'string' ? x : ((x as Record<string, string>)?.message || (x as Record<string, string>)?.detail || (x as Record<string, string>)?.description || JSON.stringify(x)))
const Warn = ({ children, tone = 'amber' }: { children: React.ReactNode; tone?: 'amber' | 'rose' }) => (
  <p className={`mt-2 rounded-md border px-3 py-2 text-sm ${tone === 'rose' ? 'border-rose-line bg-rose-soft text-rose-300' : 'border-amber-line bg-amber-soft text-amber-300'}`}>{children}</p>
)

// ------------------------------------------------------------------ editors
function TopicsEditor({ v, save, onClose }: { v: Gate1View; save: SaveFn; onClose: () => void }) {
  const [d, setD] = useState<(TopicGroup & { raw: string })[]>(() => v.edit.topics.map((g) => ({ ...g, raw: g.topics.join('\n') })))
  const ed = useEditor(save, onClose)
  const value = () => d.map(({ raw, ...g }) => ({ ...g, topics: raw.split('\n').map((s) => s.trim()).filter(Boolean) }))
  return (
    <EditorDialog title="Edit your topics" description="Group names and the topics in each. The related-course overlaps are not worked out again." onClose={onClose} onSave={() => ed.submit('topics', value())} busy={ed.busy} error={ed.err('_')}>
      <div className="space-y-3">
        {d.map((g, i) => (
          <EditRow key={i} tools={<RowTools i={i} n={d.length} what="this group" onMove={(x) => setD(move(d, i, x))} onRemove={() => setD(del(d, i))} />}>
            <Field label="Topic group" htmlFor={`tg-${i}`} error={ed.err(`${i}.title`)}><Input id={`tg-${i}`} value={g.title} placeholder="Topic group name" onChange={(e) => setD(upd(d, i, { title: e.target.value }))} /></Field>
            <Field label="Topics in it" htmlFor={`tt-${i}`} hint="One per line." error={ed.err(`${i}.topics`)}><Textarea id={`tt-${i}`} rows={Math.max(2, g.raw.split('\n').length)} value={g.raw} onChange={(e) => setD(upd(d, i, { raw: e.target.value }))} /></Field>
          </EditRow>
        ))}
      </div>
      <AddButton onClick={() => setD([...d, { title: '', topics: [], raw: '' }])}>Add a topic group</AddButton>
    </EditorDialog>
  )
}

function AssumptionsEditor({ v, save, onClose }: { v: Gate1View; save: SaveFn; onClose: () => void }) {
  const [d, setD] = useState<EditAssumption[]>(() => v.edit.assumptions.map((a) => ({ ...a })))
  const ed = useEditor(save, onClose)
  return (
    <EditorDialog title="Edit what was filled in for you" size="md" onClose={onClose} onSave={() => ed.submit('assumptions', d)} busy={ed.busy} error={ed.err('_')}>
      <div className="space-y-3">
        {d.map((a, i) => (
          <EditRow key={a.id}>
            <p className="label-caps">{a.what}</p>
            {a.what === 'course level' ? (
              <Select aria-label="Course level" value={String(a.value ?? '')} onChange={(e) => setD(upd(d, i, { value: e.target.value }))}>{v.edit.levels.map((l) => <option key={l} value={l}>Level {l} ({l}xx courses)</option>)}</Select>
            ) : a.what === 'mid-semester exam timing' ? (
              <Select aria-label="Mid-sem week" value={(String(a.value).match(/\d+/) ?? [''])[0]} onChange={(e) => setD(upd(d, i, { value: e.target.value }))}>{weekOptions(v.edit.weeks - 1).map((k) => <option key={k} value={k}>After teaching week {k}</option>)}</Select>
            ) : (
              <p className="text-base text-ink-1"><b className="font-semibold">{a.value == null ? 'Not fixed: estimated in the plan' : String(a.value)}</b> <span className="text-xs text-ink-3">(set in the Details step)</span></p>
            )}
            <FieldError>{ed.err(`${i}.value`)}</FieldError>
            {a.status === 'open' ? <Checkbox checked={!!a.confirm} onChange={(c) => setD(upd(d, i, { confirm: c }))}>Confirm this value</Checkbox> : <ApprovedBadge>{a.status === 'confirmed' ? 'Confirmed by you' : 'Set by you'}</ApprovedBadge>}
          </EditRow>
        ))}
      </div>
    </EditorDialog>
  )
}

function WishesEditor({ v, save, onClose }: { v: Gate1View; save: SaveFn; onClose: () => void }) {
  const [d, setD] = useState<EditWish[]>(() => v.edit.wishes.map((w) => ({ ...w })))
  const ed = useEditor(save, onClose)
  return (
    <EditorDialog title="Edit your wishes, as rules" description="These rules come from your own words. Change the phrase that is checked, make a rule a preference, remove it, or add one." onClose={onClose} onSave={() => ed.submit('wishes', d)} busy={ed.busy} error={ed.err('_')}>
      <div className="space-y-3">
        {d.map((w, i) => w.locked ? (
          <EditRow key={i}>
            <p className="text-base text-ink-1">{w.text}</p>
            <p className="text-xs text-ink-3">Part of the course frame: change it in the Details step{/Mid-sem/.test(w.text) ? ', or as the mid-sem week under “Filled in for you”' : ''}.</p>
          </EditRow>
        ) : (
          <EditRow key={i} tools={<RowTools i={i} n={d.length} what="this rule" onRemove={() => setD(del(d, i))} />}>
            {w.ids.length && !w.text_editable ? <p className="text-base text-ink-1">{w.text}</p> : (
              <>
                {w.ids.length ? <p className="label-caps">{w.kind === 'exclude' ? 'Must not become' : 'Must include'}</p>
                  : <Select aria-label="Kind of rule" value={w.kind} onChange={(e) => setD(upd(d, i, { kind: e.target.value as EditWish['kind'] }))}><option value="exclude">Must not become</option><option value="include">Must include</option></Select>}
                <Input aria-label="Rule" value={w.text} invalid={!!ed.err(`${i}.text`)} placeholder={w.kind === 'exclude' ? 'e.g. a front-end-only design course' : 'e.g. a deployed full-stack project'} onChange={(e) => setD(upd(d, i, { text: e.target.value }))} />
                <FieldError>{ed.err(`${i}.text`) ?? ed.err(`${i}.kind`)}</FieldError>
              </>
            )}
            {w.said && w.said !== w.text && <p className="text-xs text-ink-3">From your form: “{w.said}”</p>}
            <Checkbox checked={w.hard} onChange={(c) => setD(upd(d, i, { hard: c }))}>A must <span className="text-ink-3">(untick: preferred)</span></Checkbox>
          </EditRow>
        ))}
      </div>
      <AddButton onClick={() => setD([...d, { ids: [], kind: 'exclude', text: '', text_editable: true, hard: true, said: '' }])}>Add a rule</AddButton>
    </EditorDialog>
  )
}

function PrereqEditor({ v, save, onClose }: { v: Gate1View; save: SaveFn; onClose: () => void }) {
  const [d, setD] = useState<EditPrereq[]>(() => v.edit.prerequisites.map((p) => ({ ...p })))
  const ed = useEditor(save, onClose)
  return (
    <EditorDialog title="Edit prerequisites" size="md" description="Courses students should have taken. Only IIIT-D course codes from the course database can be added." onClose={onClose} onSave={() => ed.submit('prerequisites', d)} busy={ed.busy} error={ed.err('_')}>
      <div className="space-y-3">
        {d.map((p, i) => (
          <EditRow key={i} tools={<RowTools i={i} n={d.length} what="this course" onRemove={() => setD(del(d, i))} />}>
            <div className="grid gap-3 sm:grid-cols-2">
              <Input aria-label="Course code" value={p.code ?? ''} invalid={!!ed.err(`${i}.code`)} placeholder="Course code, e.g. CSE102" onChange={(e) => setD(upd(d, i, { code: e.target.value }))} />
              <Select aria-label="Kind" value={p.kind} onChange={(e) => setD(upd(d, i, { kind: e.target.value }))}><option value="mandatory">Prerequisite</option><option value="desirable">Recommended</option></Select>
            </div>
            <FieldError>{ed.err(`${i}.code`)}</FieldError>
          </EditRow>
        ))}
        {!d.length && <p className="text-base text-ink-3">No prerequisites.</p>}
      </div>
      <AddButton onClick={() => setD([...d, { code: '', kind: 'mandatory' }])}>Add a course</AddButton>
    </EditorDialog>
  )
}

// ------------------------------------------------------------------ the view
type Section = 'topics' | 'assumptions' | 'wishes' | 'prerequisites'

export function ContextView({ v, save }: { v: Gate1View; save?: SaveFn }) {
  const [editing, setEditing] = useState<Section | null>(null)
  const [confirming, setConfirming] = useState<string | null>(null)
  const edit = (s: Section, label = 'Edit') => save && <Button size="sm" onClick={() => setEditing(s)}>{label}</Button>
  const mark = (k: string) => (v.edited?.[k]?.length ? <EditedBadge changes={v.edited[k]} /> : null)
  const confirm = async (id: string) => { setConfirming(id); await save!('assumptions', [{ id, confirm: true }]); setConfirming(null) }
  const close = () => setEditing(null)

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader title="Your topics" description="The topic groups from your form, as the design will use them" actions={<>{mark('topics')}{edit('topics')}</>} />
        <CardBody>
          {v.topics.length ? v.topics.map((g) => (
            <Row key={g.id ?? g.title}><p className="font-medium text-ink-1">{g.title}</p><p className="mt-0.5 text-sm text-ink-3">{g.topics.join(' · ')}</p></Row>
          )) : <p className="text-base text-ink-3">None listed; ProfsAgent proposes them in the next steps.</p>}
        </CardBody>
      </Card>

      <Card>
        <CardHeader title="Filled in for you" description="Values you did not give, with what each is based on" actions={<>{mark('assumptions')}{edit('assumptions')}</>} />
        <CardBody>
          {v.assumptions.length ? v.assumptions.map((a) => (
            <Row key={a.id} aside={
              a.status === 'confirmed' ? <ApprovedBadge>Confirmed by you</ApprovedBadge> : a.status === 'set by professor' ? <ApprovedBadge>Set by you</ApprovedBadge>
                : <><GeneratedBadge>Assumed: please confirm</GeneratedBadge>{save && <Button size="sm" loading={confirming === a.id} icon={<Check aria-hidden />} onClick={() => confirm(a.id)}>Confirm</Button>}</>}>
              <p className="label-caps">{a.what}</p>
              <p className="mt-0.5 font-semibold text-ink-1">{String(a.value)}</p>
              {a.basis && <p className="mt-0.5 text-sm text-ink-3">{a.basis}</p>}
            </Row>
          )) : <p className="text-base text-ink-3">Nothing: you gave every value.</p>}
        </CardBody>
      </Card>

      <Card>
        <CardHeader title="Your wishes, as rules" description="What you asked for, turned into rules the design is checked against" actions={<>{mark('wishes')}{edit('wishes')}</>} />
        <CardBody>
          {v.wishes.length ? v.wishes.map((w, i) => (
            <Row key={i} aside={<Badge tone={w.hard ? 'iris' : 'neutral'}>{w.hard ? 'Must' : 'Preferred'}</Badge>}>
              <p className="flex items-start gap-2 text-ink-1">
                {w.kind === 'exclude' ? <ShieldBan aria-hidden className="mt-0.5 size-4 shrink-0 text-rose-400" /> : <CircleCheck aria-hidden className="mt-0.5 size-4 shrink-0 text-mint-400" />}
                <span>{w.text}</span>
              </p>
            </Row>
          )) : <p className="text-base text-ink-3">No specific wishes.</p>}
          {v.untranslatable.map((x, i) => <Warn key={i}>Could not turn this into a checkable rule: {x}</Warn>)}
          {v.constraint_conflicts.map((x, i) => <Warn key={i} tone="rose">Conflict: {text(x)}</Warn>)}
        </CardBody>
      </Card>

      <Card>
        <CardHeader title="Rules from the regulations and the course template" description={`${plural(v.rules.length, 'rule')} the design must follow, each with its source`} />
        <CardBody>
          {v.rules.slice(0, 5).map((r, i) => <RuleRow key={i} r={r} />)}
          {v.rules.length > 5 && (
            <Disclosure className="mt-3 border-t border-line pt-3" summary={`Show all ${v.rules.length} rules`}>{v.rules.slice(5).map((r, i) => <RuleRow key={i} r={r} />)}</Disclosure>
          )}
        </CardBody>
      </Card>

      {v.form_conflicts.length > 0 && (
        <Card className="border-amber-line">
          <CardHeader title="Things in the form that contradict each other" />
          <CardBody>{v.form_conflicts.map((x, i) => <Warn key={i}>{text(x)}</Warn>)}</CardBody>
        </Card>
      )}

      <Card>
        <CardHeader title="How it fits with IIIT-D courses" description="From the institutional course graph: what it needs, and what it overlaps with" actions={<>{mark('prerequisites')}{edit('prerequisites', 'Edit prerequisites')}</>} />
        <CardBody>
          {v.existence && (
            <Row aside={<Badge tone={v.existence.verdict === 'distinct' ? 'mint' : 'amber'}>{v.existence.verdict === 'distinct' ? 'A new course' : 'Close to an existing course'}</Badge>}>
              <p className="text-ink-1">{v.existence.reason}</p>
              {!!v.existence.closest?.length && <p className="mt-0.5 text-sm text-ink-3">Closest: {v.existence.closest.join(', ')}</p>}
            </Row>
          )}
          {v.prerequisites.map((p) => (
            <Row key={p.code} aside={<Badge tone="iris">{p.kind === 'mandatory' ? 'Prerequisite' : 'Recommended'}</Badge>}>
              <p className="text-ink-1"><span className="text-ink-3">Needs </span><Ext href={p.url}>{p.code} {p.name ?? ''}</Ext>{p.alternatives.length > 0 && <span className="text-sm text-ink-3"> or {p.alternatives.map((a) => a.code).join(', ')}</span>}</p>
              {p.relied_topics.length > 0 && <p className="mt-0.5 text-sm text-ink-3">Relied on for: {p.relied_topics.join('; ')}</p>}
              {p.why && <p className="mt-0.5 text-sm text-ink-3">{p.why}</p>}
            </Row>
          ))}
          {v.overlaps_before_topic_edit && v.overlaps.length > 0 && <Warn>These overlaps were worked out from your topics before you changed them.</Warn>}
          {v.overlaps.map((o) => (
            <Row key={o.code} aside={o.verdict ? <Badge>{o.verdict}</Badge> : undefined}>
              <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
                <Ext href={o.url}>{o.code} {o.name ?? ''}</Ext>
                <span className="flex items-center gap-2 text-sm text-ink-3"><Meter className="!w-20" value={o.pct} tone={o.pct >= 40 ? 'amber' : 'neutral'} label="Topic overlap" /><span className="tnum">{o.pct}% topic overlap</span></span>
              </div>
              {o.shared.length > 0 && <p className="mt-0.5 text-sm text-ink-3">Shared: {o.shared.slice(0, 6).join('; ')}</p>}
              {o.difference && <p className="mt-0.5 text-sm text-ink-2">{o.difference}</p>}
            </Row>
          ))}
          {v.anti_requisites.length > 0 && <Row><p className="text-ink-1">Can’t be taken together with {v.anti_requisites.map((a, i) => <span key={a.code}>{i > 0 && ', '}<Ext href={a.url}>{a.code}</Ext></span>)}</p></Row>}
          {!v.prerequisites.length && !v.overlaps.length && !v.existence && <p className="text-base text-ink-3">No related IIIT-D course found.</p>}
        </CardBody>
      </Card>

      {v.comparable.length > 0 && (
        <section aria-labelledby="learn-from">
          <div className="mb-3 mt-6 flex flex-wrap items-baseline justify-between gap-2">
            <h2 id="learn-from" className="text-lg font-semibold text-ink-1">Courses to learn from</h2>
            <span className="text-sm text-ink-3">Evidence from IIIT-D and other universities; open any of them to check</span>
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            {v.comparable.map((x, i) => (
              <article key={i} className="rounded-xl border border-line bg-surface-1 p-4 shadow-1">
                <div className="flex items-start justify-between gap-3">
                  <h3 className="min-w-0 text-base font-medium"><Ext href={x.url} quiet>{x.title}</Ext></h3>
                  {x.where && <Badge>{x.where}</Badge>}
                </div>
                <dl className="mt-3 space-y-2 text-sm">
                  {x.take && <div className="flex gap-2"><dt className="flex w-14 shrink-0 items-center gap-1 font-medium text-mint-300"><Check aria-hidden className="size-3.5" />Take</dt><dd className="text-ink-2">{x.take}</dd></div>}
                  {x.avoid && <div className="flex gap-2"><dt className="flex w-14 shrink-0 items-center gap-1 font-medium text-amber-300"><X aria-hidden className="size-3.5" />Avoid</dt><dd className="text-ink-2">{x.avoid}</dd></div>}
                </dl>
              </article>
            ))}
          </div>
        </section>
      )}

      {v.concerns.length > 0 && (
        <Card>
          <CardHeader title="Notes from the system" icon={<Lightbulb />} />
          <CardBody>{v.concerns.map((x, i) => <Warn key={i}>{x}</Warn>)}</CardBody>
        </Card>
      )}

      {save && editing === 'topics' && <TopicsEditor v={v} save={save} onClose={close} />}
      {save && editing === 'assumptions' && <AssumptionsEditor v={v} save={save} onClose={close} />}
      {save && editing === 'wishes' && <WishesEditor v={v} save={save} onClose={close} />}
      {save && editing === 'prerequisites' && <PrereqEditor v={v} save={save} onClose={close} />}
    </div>
  )
}

function RuleRow({ r }: { r: Gate1View['rules'][number] }) {
  return (
    <Row aside={r.source ? (r.source.url ? <Ext href={r.source.url} className="text-sm">{r.source.text}</Ext> : <Code>{r.source.text}</Code>) : undefined}>
      <p className="text-ink-1">{r.text}{!r.hard && <span className="text-sm text-ink-3"> (preferred)</span>}</p>
    </Row>
  )
}
