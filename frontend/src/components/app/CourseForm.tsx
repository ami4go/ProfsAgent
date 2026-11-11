// The course form. Used three ways: the professor's first form ("new"), the completed form to check before any design
// starts ("review": what ProfsAgent filled in is marked, with its reason and sources), and read-only after it is confirmed.
import { useQuery } from '@tanstack/react-query'
import type { ReactNode } from 'react'
import { BookOpen, CircleAlert, CircleCheck, Compass, FlaskConical, LayoutList, Users } from 'lucide-react'
import { api } from '@/lib/api'
import { useDebounced } from '@/lib/hooks'
import type { CourseForm as Form, FilledField, FormErrors, FormOptions, Ref } from '@/lib/types'
import { Card, CardBody, CardHeader, Checkbox, Ext, Field, FieldError, GeneratedBadge, Input, Select, Textarea, ToggleChip } from '@/components/ui'

export const blankForm = (): Form => ({
  name: '', description: '', topics: '', topics_flexible: true, intent_question: '', intent_emphasis: '', intent_avoid: '', department: '', credits: '', l: '', t: '', p: '',
  weeks: '', weekly_effort: '', programmes: [], year: '', background: '', lab: '', lab_infra: '', assess_pref: [], assess_avoid: [], assess_why: '', special: '', external_research: true,
})

export const FORM_SECTIONS = [
  { id: 'about', title: 'About the course', icon: <BookOpen /> },
  { id: 'intent', title: 'Course intent', icon: <Compass /> },
  { id: 'structure', title: 'Structure', icon: <LayoutList /> },
  { id: 'students', title: 'Students', icon: <Users /> },
  { id: 'lab', title: 'Lab and assessment', icon: <FlaskConical /> },
] as const

/** Why ProfsAgent suggested a value, and what it was based on. */
function AiNote({ fields }: { fields: (FilledField | undefined)[] }) {
  const s = fields.filter(Boolean) as FilledField[]
  if (!s.length) return null
  const reasons = [...new Set(s.map((x) => x.reason).filter(Boolean))]
  const fixes = s.map((x) => x.corrected).filter(Boolean) as string[]
  const sources = s.flatMap((x) => x.sources ?? []).filter((x, i, a) => a.findIndex((y) => y.text === x.text) === i)
  return (
    <div className="mt-2 rounded-lg border border-iris-line bg-iris-soft px-3 py-2 text-sm text-ink-2">
      <div className="flex flex-wrap items-center gap-2"><GeneratedBadge>Filled in by ProfsAgent</GeneratedBadge><span>{reasons.join(' ')}</span></div>
      {fixes.map((f) => <p key={f} className="mt-1 text-amber-300">{f}</p>)}
      {!!sources.length && <p className="mt-1 text-xs text-ink-3">Based on: {sources.map((x, i) => <span key={x.text}>{i > 0 && ' · '}{x.url ? <Ext href={x.url}>{x.text}</Ext> : x.text}</span>)}</p>}
    </div>
  )
}

function CatalogueLookup({ text }: { text: string }) {
  const codes = [...new Set((useDebounced(text).toUpperCase().match(/[A-Z]{2,4}\s?\d{3}[A-Z]?/g) ?? []).map((c) => c.replace(/\s/g, '')))]
  const { data } = useQuery({ queryKey: ['catalogue', codes.join(',')], queryFn: () => api.get<(Ref & { found: boolean })[]>(`/api/catalogue?codes=${encodeURIComponent(codes.join(','))}`), enabled: codes.length > 0, staleTime: 60_000 })
  if (!codes.length || !data) return null
  return (
    <ul className="mt-1.5 space-y-0.5">
      {data.map((c) => (
        <li key={c.code} className="flex items-center gap-1.5 text-sm">
          {c.found ? <><CircleCheck aria-hidden className="size-3.5 text-mint-400" /><Ext href={c.url}>{c.code} {c.name}</Ext></>
            : <><CircleAlert aria-hidden className="size-3.5 text-amber-400" /><span className="text-amber-300">{c.code} is not in the IIIT-D catalogue</span></>}
        </li>
      ))}
    </ul>
  )
}

interface Props {
  value: Form
  onChange: (patch: Partial<Form>) => void
  errors: FormErrors
  options: FormOptions
  mode: 'new' | 'review' | 'read'
  filled?: Record<string, FilledField>
}

export function CourseForm({ value: f, onChange, errors: e, options: o, mode, filled = {} }: Props) {
  const fresh = mode === 'new', read = mode === 'read'
  const ph = (s: string) => (fresh ? s : '')
  const ai = (...k: string[]) => !read && k.some((x) => filled[x])
  const note = (...k: string[]) => (read ? null : <AiNote fields={k.map((x) => filled[x])} />)
  const text = (k: keyof Form, placeholder = '') => (
    <Input id={`f-${k}`} value={String(f[k] ?? '')} placeholder={ph(placeholder)} disabled={read} invalid={!!e[k]} ai={ai(k)} onChange={(ev) => onChange({ [k]: ev.target.value })} />
  )
  const area = (k: keyof Form, rows: number, placeholder = '') => (
    <Textarea id={`f-${k}`} rows={rows} value={String(f[k] ?? '')} placeholder={ph(placeholder)} disabled={read} invalid={!!e[k]} ai={ai(k)} onChange={(ev) => onChange({ [k]: ev.target.value })} />
  )
  const select = (k: keyof Form, values: string[], labels?: string[]) => (
    <Select id={`f-${k}`} value={String(f[k] ?? '')} disabled={read} invalid={!!e[k]} ai={ai(k)} onChange={(ev) => onChange({ [k]: ev.target.value })}>
      <option value="">{fresh ? 'Leave blank: ProfsAgent fills it in' : 'Not set'}</option>
      {values.map((v, i) => <option key={v} value={v}>{labels ? labels[i] : v}</option>)}
    </Select>
  )
  const toggle = (k: 'programmes' | 'assess_pref' | 'assess_avoid', v: string) => {
    const has = f[k].includes(v)
    const patch: Partial<Form> = { [k]: has ? f[k].filter((x) => x !== v) : [...f[k], v] }
    if (!has && k === 'assess_pref') patch.assess_avoid = f.assess_avoid.filter((x) => x !== v)   // a kind of assessment is preferred or avoided, never both
    if (!has && k === 'assess_avoid') patch.assess_pref = f.assess_pref.filter((x) => x !== v)
    onChange(patch)
  }
  const chips = (k: 'programmes' | 'assess_pref' | 'assess_avoid', values: string[], label: string) => (
    <div role="group" aria-label={label} className="flex flex-wrap gap-1.5">
      {values.map((v) => read
        ? f[k].includes(v) && <span key={v} className="flex h-8 items-center rounded-full border border-line-strong px-3 text-sm text-ink-1">{v}</span>
        : <ToggleChip key={v} on={f[k].includes(v)} ai={ai(k)} onClick={() => toggle(k, v)}>{v}</ToggleChip>)}
      {read && !f[k].length && <span className="text-sm text-ink-3">None</span>}
    </div>
  )
  const section = (i: number, children: ReactNode) => {
    const s = FORM_SECTIONS[i]
    return (
      <Card id={`section-${s.id}`} className="scroll-mt-28">
        <CardHeader title={s.title} icon={s.icon} />
        <CardBody className="space-y-4">{children}</CardBody>
      </Card>
    )
  }
  const opt = fresh

  return (
    <div className="space-y-4">
      {section(0, <>
        <Field label="Course name" htmlFor="f-name" error={e.name}>{text('name', 'Software Development using AI')}</Field>
        <Field label="Short description" htmlFor="f-description" error={e.description} hint={fresh ? 'What the course is about and what students can do at the end (3–6 sentences).' : undefined}>{area('description', 4)}</Field>
        <div>
          <Field label="Topics" htmlFor="f-topics" optional={opt} error={e.topics} hint={fresh ? 'One group per line, for example “A. AI-native development: AI-assisted coding, coding agents”.' : undefined}>
            {area('topics', fresh ? 5 : 7, 'A. AI-native development: AI-assisted coding, coding agents\nB. Engineering practice: automated testing, deployment')}
          </Field>
          {note('topics')}
          <Checkbox className="mt-3" checked={f.topics_flexible} disabled={read} onChange={(v) => onChange({ topics_flexible: v })}>ProfsAgent may change these topics</Checkbox>
        </div>
      </>)}

      {section(1, <>
        <div><Field label="The central question the course answers" htmlFor="f-intent_question" optional={opt}>{text('intent_question', 'How do you design, build and test a multi-component program?')}</Field>{note('intent_question')}</div>
        <div><Field label="Teaching emphasis" htmlFor="f-intent_emphasis" optional={opt}>{text('intent_emphasis', 'Design thinking before coding; learning by building')}</Field>{note('intent_emphasis')}</div>
        <div><Field label="This course should not become" htmlFor="f-intent_avoid" optional={opt} hint={read ? undefined : 'One per line.'}>{area('intent_avoid', 2, 'A Java language features course')}</Field>{note('intent_avoid')}</div>
      </>)}

      {section(2, <>
        <div>
          <div className="grid gap-4 sm:grid-cols-3">
            <Field label="Proposing department" htmlFor="f-department" error={e.department}>{select('department', o.departments)}</Field>
            <Field label="Credits" htmlFor="f-credits" error={e.credits}>{select('credits', o.credits)}</Field>
            <Field label="Teaching weeks" htmlFor="f-weeks" error={e.weeks}>{text('weeks', 'e.g. 13')}</Field>
          </div>
          {note('department', 'credits', 'weeks')}
        </div>
        <div>
          <fieldset>
            <legend className="mb-1.5 text-sm font-medium text-ink-1">Hours per week</legend>
            <div className="grid max-w-md grid-cols-3 gap-3">
              {(['l', 't', 'p'] as const).map((k, i) => (
                <label key={k} className="text-xs text-ink-3">
                  {['Lecture', 'Tutorial', 'Lab'][i]}
                  <Input className="mt-1" inputMode="decimal" value={f[k]} disabled={read} invalid={!!e.ltp} ai={ai(k)} placeholder={ph(['3', '1', '0'][i])} onChange={(ev) => onChange({ [k]: ev.target.value })} />
                </label>
              ))}
            </div>
            <FieldError>{e.ltp}</FieldError>
          </fieldset>
          {note('l', 't', 'p')}
        </div>
        <div><Field className="max-w-md" label="Student work outside lectures, hours a week" htmlFor="f-weekly_effort" optional={opt}>{text('weekly_effort', 'e.g. 10-12')}</Field>{note('weekly_effort')}</div>
      </>)}

      {section(3, <>
        <div><Field label="Programmes" optional={opt} error={e.programmes}>{chips('programmes', o.programmes, 'Programmes')}</Field>{note('programmes')}</div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div><Field label="Year" htmlFor="f-year" error={e.year}>{select('year', o.years)}</Field>{note('year')}</div>
          <div>
            <Field label="Students should already know" htmlFor="f-background" optional={opt}>{text('background', 'CSE201 Advanced Programming; basic software engineering')}</Field>
            {!read && <CatalogueLookup text={f.background} />}
            {note('background')}
          </div>
        </div>
      </>)}

      {section(4, <>
        <div className="grid gap-4 sm:grid-cols-2">
          <div><Field label="Lab" htmlFor="f-lab" error={e.lab}>{select('lab', ['weekly', 'none'], ['A lab every week', 'No lab'])}</Field>{note('lab')}</div>
          <div><Field label="Lab infrastructure" htmlFor="f-lab_infra" optional={opt}>{text('lab_infra', 'Students’ laptops, GPUs on the cluster, TA support')}</Field>{note('lab_infra')}</div>
        </div>
        <div><Field label="Assessment you prefer" optional={opt}>{chips('assess_pref', o.assessments, 'Assessment you prefer')}</Field>{note('assess_pref')}</div>
        <div><Field label="Assessment to avoid" optional={opt}>{chips('assess_avoid', o.assessments, 'Assessment to avoid')}</Field>{note('assess_avoid')}</div>
        <div><Field label="Why this assessment" htmlFor="f-assess_why" optional={opt}>{text('assess_why', 'Most of the grade should come from programming work')}</Field>{note('assess_why')}</div>
        <div><Field label="Anything else ProfsAgent should know" htmlFor="f-special" optional={opt}>{area('special', 2, 'Project in pairs; must produce a working application')}</Field>{note('special')}</div>
        <Checkbox checked={f.external_research} disabled={read} onChange={(v) => onChange({ external_research: v })} description="Looks at comparable courses at other universities. Slower.">Also compare with other universities</Checkbox>
      </>)}
    </div>
  )
}
