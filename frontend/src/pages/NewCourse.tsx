import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, Wand2 } from 'lucide-react'
import { ApiError, api, problemOf } from '@/lib/api'
import { store } from '@/lib/format'
import { useBusy, useDocumentTitle } from '@/lib/hooks'
import { keys, useOptions, useRefresh } from '@/lib/queries'
import { toast } from '@/lib/toast'
import type { CourseForm as Form, FormErrors } from '@/lib/types'
import { Button, Callout, Loading } from '@/components/ui'
import { CourseForm, FORM_SECTIONS, blankForm } from '@/components/app/CourseForm'
import { PageBody, PageHeader, TopBar } from '@/components/app/Shell'

const DRAFT = 'profsagent-draft'

export function SectionNav() {
  return (
    <nav aria-label="Sections of the form" className="sticky top-24 hidden w-48 shrink-0 self-start xl:block">
      <p className="label-caps mb-2 px-2">On this page</p>
      <ul className="space-y-0.5">
        {FORM_SECTIONS.map((s) => (
          <li key={s.id}>
            <a href={`#section-${s.id}`} onClick={(e) => { e.preventDefault(); document.getElementById(`section-${s.id}`)?.scrollIntoView({ behavior: 'smooth' }) }}
              className="flex h-8 items-center gap-2 rounded-md px-2 text-sm text-ink-3 no-underline hover:bg-white/[0.04] hover:text-ink-1 [&_svg]:size-3.5">{s.icon}{s.title}</a>
          </li>
        ))}
      </ul>
    </nav>
  )
}

export function NewCoursePage() {
  useDocumentTitle('New course')
  const nav = useNavigate()
  const refresh = useRefresh()
  const { data: options } = useOptions()
  const [form, setForm] = useState<Form>(() => ({ ...blankForm(), ...store.json<Partial<Form>>(DRAFT, {}) }))
  const [errors, setErrors] = useState<FormErrors>({})
  const [busy, run] = useBusy()
  useEffect(() => { store.set(DRAFT, JSON.stringify(form)) }, [form])

  const change = (patch: Partial<Form>) => {
    setForm((f) => ({ ...f, ...patch }))
    setErrors((e) => { const n = { ...e }; for (const k of Object.keys(patch)) { delete n[k as keyof FormErrors]; if (['l', 't', 'p'].includes(k)) delete n.ltp } return n })
  }
  const start = () => run(async () => {
    const r = await api.post<{ run_id: string }>('/api/runs', form)
    store.set(DRAFT, '')
    await refresh(keys.runs)
    nav(`/courses/${encodeURIComponent(r.run_id)}/design`)
  }, (e) => {
    if (e instanceof ApiError && e.status === 422) {
      setErrors(e.errors)
      toast.error('Please fix the marked fields')
      requestAnimationFrame(() => document.querySelector('[aria-invalid="true"]')?.scrollIntoView({ block: 'center', behavior: 'smooth' }))
    } else toast.error(problemOf(e, 'Could not start'))
  })

  return (
    <>
      <TopBar crumbs={[{ label: 'Courses', to: '/' }, { label: 'New course' }]}
        actions={<Button size="sm" variant="ghost" icon={<Wand2 aria-hidden />} onClick={() => { if (options) { setForm({ ...blankForm(), ...options.example }); setErrors({}); toast('Example filled in. Change anything you like.') } }}>Fill with an example</Button>} />
      <PageBody>
        <PageHeader eyebrow="Step 1 of 4 · Details" title="Describe your course"
          description="Only the name and the description are required. ProfsAgent fills in what you leave blank, and you check the complete form before anything is designed." />
        {Object.keys(errors).length > 0 && <Callout tone="rose" className="mt-6" title="Some fields need another look">They are marked below.</Callout>}
        <div className="mt-8 flex gap-8">
          <SectionNav />
          <div className="min-w-0 flex-1">
            {options ? <CourseForm value={form} onChange={change} errors={errors} options={options} mode="new" /> : <Loading label="Loading the form" />}
            <p className="mt-4 text-sm text-ink-3">A full design takes about 30–45 minutes in all, with three short checks from you. You can close this page meanwhile.</p>
          </div>
        </div>
      </PageBody>
      <div className="fixed inset-x-0 bottom-0 z-20 lg:left-[16rem]">
        <div className="glass-strong border-t border-line-strong">
          <div className="mx-auto flex max-w-[70rem] items-center justify-between gap-3 px-4 py-3 sm:px-6">
            <Button variant="ghost" to="/">Cancel</Button>
            <div className="flex items-center gap-3">
              <span className="hidden text-xs text-ink-3 sm:block">Your draft is kept on this laptop</span>
              <Button variant="glow" size="lg" loading={busy} iconRight={<ArrowRight aria-hidden />} onClick={start}>Continue</Button>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
