// Your courses: what needs you first (oldest first, one primary action), then every course as a card.
import { useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowRight, BookOpen, CircleCheck, Ellipsis, GraduationCap, Hourglass, ListChecks, Plus, RotateCw, Sparkles, Trash2, UserRound } from 'lucide-react'
import { api, problemOf, runUrl } from '@/lib/api'
import { deleteCourse } from '@/lib/actions'
import { ago, plural, time } from '@/lib/format'
import { useBusy, useDocumentTitle } from '@/lib/hooks'
import { keys, useDeliveryCourses, useHealth, useRefresh, useRuns } from '@/lib/queries'
import { GATES, GATE_ABOUT, GATE_NAME, stageStatesOf } from '@/lib/status'
import { toast } from '@/lib/toast'
import type { DeliveryCourse, RunSummary } from '@/lib/types'
import { Button, Callout, Card, EmptyState, IconButton, Menu, SectionTitle, SkeletonCard, StatTile } from '@/components/ui'
import { PageBody, PageHeader, TopBar } from '@/components/app/Shell'
import { StageDots } from '@/components/app/StageRail'
import { RunStatusBadge } from '@/components/app/StatusBadge'

const courseUrl = (rid: string, rest = '') => `/courses/${encodeURIComponent(rid)}${rest}`

function HealthNotes() {
  const { data: h } = useHealth()
  if (!h) return null
  if (h.kg_backend === 'neo4j' && !h.neo4j) return <Callout tone="rose" title="The course database (Neo4j) isn’t running">Open Neo4j Desktop and start the ProfsAgent database before starting a course. Courses that need it wait with a “Try again” button.</Callout>
  if (!h.keys.gemini && !h.keys.groq) return <Callout tone="amber" title="No AI keys found">Add GEMINI_API_KEYS (and GROQ_API_KEYS) to the .env file, then restart the app. Courses that are already designed can still be read.</Callout>
  return null
}

function NeedsYou({ runs }: { runs: RunSummary[] }) {
  const refresh = useRefresh()
  const [busy, run] = useBusy()
  const queue = runs.filter((r) => r.status === 'waiting' || r.status === 'error').sort((a, b) => a.created_at - b.created_at)
  if (!queue.length) return null
  const retry = (rid: string) => run(async () => { await api.post(runUrl(rid, '/retry')); toast('Trying again.'); await refresh(keys.runs, keys.run(rid)) }, (e) => toast.error(problemOf(e, 'Could not restart')))
  return (
    <section aria-labelledby="needs-you">
      <SectionTitle aside={`${plural(queue.length, 'item')}, oldest first`}><span id="needs-you">Needs you</span></SectionTitle>
      <Card className="mt-3 divide-y divide-line">
        {queue.map((r, i) => (
          <div key={r.run_id} className="flex flex-wrap items-center justify-between gap-x-4 gap-y-2 px-5 py-3.5">
            <div className="flex min-w-0 items-center gap-3">
              <span aria-hidden className={`flex size-9 shrink-0 items-center justify-center rounded-lg ${r.status === 'error' ? 'bg-rose-soft text-rose-300' : 'bg-amber-soft text-amber-300'}`}>
                {r.status === 'error' ? <RotateCw className="size-4" /> : <UserRound className="size-4" />}
              </span>
              <div className="min-w-0">
                <p className="truncate text-base font-medium text-ink-1">{r.title}</p>
                <p className="truncate text-sm text-ink-3">
                  {r.status === 'error' ? 'Stopped on a problem; nothing is lost' : r.gate ? `Your check: ${GATE_NAME[r.gate]} · ${GATE_ABOUT[r.gate]}` : 'Waiting for you'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {r.status === 'error' && <Button size="sm" loading={busy} onClick={() => retry(r.run_id)}>Try again</Button>}
              <Button size="sm" variant={i === 0 ? 'glow' : 'secondary'} to={courseUrl(r.run_id, '/design')} iconRight={<ArrowRight aria-hidden />}>{r.status === 'error' ? 'Open' : 'Review now'}</Button>
            </div>
          </div>
        ))}
      </Card>
    </section>
  )
}

function CourseCard({ r, delivery }: { r: RunSummary; delivery?: DeliveryCourse }) {
  const qc = useQueryClient()
  const states = stageStatesOf(r)
  const done = GATES.filter((g) => states[g] === 'approved').length
  const stepLine =
    r.status === 'done' ? 'All four checks approved'
    : r.status === 'waiting' && r.gate ? `Step ${GATES.indexOf(r.gate) + 1} of 4 · ${GATE_NAME[r.gate]}`
    : r.status === 'paused' ? (r.resume_at ? `Continues by itself at ${time(r.resume_at)}` : 'Continues later')
    : r.status === 'stopped' ? (r.gate ? `Stopped at ${GATE_NAME[r.gate]}` : 'Stopped')
    : `${done} of 4 checks approved`
  return (
    <article className="group relative flex flex-col rounded-xl border border-line bg-surface-1 shadow-1 transition-[border-color,box-shadow,transform] duration-200 hover:-translate-y-0.5 hover:border-line-strong hover:shadow-2 focus-within:border-line-strong">
      <div className="flex items-start justify-between gap-3 px-5 pt-4">
        <RunStatusBadge run={r} />
        <Menu label={`More for ${r.title}`} trigger={<IconButton label="More" size="sm" className="relative z-[1] -mr-2 -mt-1"><Ellipsis /></IconButton>}
          items={[{ label: 'Delete the course', icon: <Trash2 />, danger: true, onSelect: () => deleteCourse(qc, r.run_id, r.title) }]} />
      </div>
      <div className="flex-1 px-5 pt-3">
        <h3 className="h-display text-xl leading-7 text-ink-1 [text-wrap:balance]">
          <Link to={courseUrl(r.run_id)} className="no-underline outline-none after:absolute after:inset-0 after:rounded-xl focus-visible:after:outline-2 focus-visible:after:outline-iris-400">{r.title}</Link>
        </h3>
        <p className="mt-1 text-sm text-ink-3">Started {ago(r.created_at)}{r.by ? ` · ${r.by}` : ''}</p>
      </div>
      <div className="mt-4 flex items-center justify-between gap-3 px-5">
        <StageDots states={states} />
        <span className="truncate text-xs text-ink-3">{stepLine}</span>
      </div>
      <div className="relative z-[1] mt-4 flex items-center justify-between gap-2 border-t border-line px-5 py-3">
        <span className="min-w-0 truncate text-xs text-ink-3">
          {r.status === 'done' ? (delivery?.lectures ? `${plural(delivery.lectures, 'lecture')} · ${delivery.decided} planned` : 'Lectures not planned yet') : r.status === 'running' ? 'ProfsAgent is working' : ' '}
        </span>
        {r.status === 'done'
          ? <Button size="sm" to={courseUrl(r.run_id, '/lectures')} icon={<ListChecks aria-hidden />}>Plan the lectures</Button>
          : <Button size="sm" variant={r.status === 'waiting' ? 'primary' : 'secondary'} to={courseUrl(r.run_id, '/design')} iconRight={<ArrowRight aria-hidden />}>{r.status === 'waiting' ? 'Review now' : 'Open'}</Button>}
      </div>
    </article>
  )
}

export function CoursesPage() {
  useDocumentTitle('Courses')
  const nav = useNavigate()
  const refresh = useRefresh()
  const { data: runs, isLoading, error } = useRuns()
  const { data: dc } = useDeliveryCourses()
  const [busy, run] = useBusy()
  const byId = Object.fromEntries((dc?.courses ?? []).map((c) => [c.run_id, c]))
  const n = (pred: (r: RunSummary) => boolean) => (runs ?? []).filter(pred).length
  const waiting = n((r) => r.status === 'waiting' || r.status === 'error')
  const openExample = () => run(async () => {
    const r = await api.post<{ run_id: string }>('/api/delivery/example')
    await refresh(keys.runs, keys.deliveryCourses)
    nav(courseUrl(r.run_id, '/lectures'))
  }, (e) => toast.error(problemOf(e, 'Could not copy the example')))
  const exampleBtn = dc?.example_available && <Button variant="secondary" loading={busy} icon={<Sparkles aria-hidden />} onClick={openExample}>Open the CS-601 example</Button>

  return (
    <>
      <TopBar crumbs={[{ label: 'Courses' }]} actions={<Button size="sm" variant="primary" to="/new" icon={<Plus aria-hidden />}>New course</Button>} />
      <PageBody width="wide">
        <PageHeader title="Your courses" description="Design a course with ProfsAgent in four checked steps, then plan how each lecture is taught." />
        <div className="mt-6 space-y-8">
          <HealthNotes />
          {error && <Callout tone="rose" title="The courses could not be loaded">{problemOf(error)}</Callout>}
          {isLoading && <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3"><SkeletonCard /><SkeletonCard /><SkeletonCard /></div>}
          {runs && runs.length === 0 && (
            <EmptyState icon={<GraduationCap />} title="No courses yet"
              actions={<><Button variant="glow" to="/new" icon={<Plus aria-hidden />}>New course</Button>{exampleBtn}</>}>
              Describe a course in a few lines. ProfsAgent drafts the outcomes, weekly plan, assessment and reading list, and you approve each step.
            </EmptyState>
          )}
          {runs && runs.length > 0 && (
            <>
              <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
                <StatTile label="Needs you" value={waiting} tone={waiting ? 'amber' : 'neutral'} icon={<UserRound />} hint={waiting ? 'Waiting for your decision' : 'Nothing is waiting'} />
                <StatTile label="In progress" value={n((r) => ['queued', 'running', 'paused'].includes(r.status))} tone="iris" icon={<Hourglass />} hint="Being designed" />
                <StatTile label="Approved" value={n((r) => r.status === 'done')} tone="mint" icon={<CircleCheck />} hint="Ready for lecture planning" />
                <StatTile label="All courses" value={runs.length} icon={<BookOpen />} hint={`${n((r) => r.status === 'stopped')} stopped by you`} />
              </div>
              <NeedsYou runs={runs} />
              <section aria-labelledby="all-courses">
                <SectionTitle aside={exampleBtn || undefined}><span id="all-courses">All courses</span></SectionTitle>
                <div className="focus-group mt-3 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                  {runs.map((r) => <CourseCard key={r.run_id} r={r} delivery={byId[r.run_id]} />)}
                </div>
              </section>
            </>
          )}
        </div>
      </PageBody>
    </>
  )
}
