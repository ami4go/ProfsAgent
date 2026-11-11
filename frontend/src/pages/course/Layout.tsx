// A course is the place you work in: one header, four tabs (overview, design, lectures, student view).
import { useQueryClient } from '@tanstack/react-query'
import { Outlet, useLocation, useNavigate, useOutletContext, useParams } from 'react-router-dom'
import { Ellipsis, Eye, LayoutDashboard, ListChecks, PencilRuler, RotateCcw, Trash2 } from 'lucide-react'
import { problemOf } from '@/lib/api'
import { deleteCourse, startAgain } from '@/lib/actions'
import { useDocumentTitle } from '@/lib/hooks'
import { useRun } from '@/lib/queries'
import type { Run } from '@/lib/types'
import { Button, EmptyState, IconButton, Loading, Menu, Tabs, type TabItem } from '@/components/ui'
import { PageBody, TopBar } from '@/components/app/Shell'
import { RunStatusBadge } from '@/components/app/StatusBadge'

export interface CourseCtx { run: Run; rid: string; base: string }
export const useCourse = () => useOutletContext<CourseCtx>()

export function CourseLayout() {
  const { rid = '' } = useParams()
  const qc = useQueryClient()
  const nav = useNavigate()
  const loc = useLocation()
  const { data: run, isLoading, error } = useRun(rid)
  const base = `/courses/${encodeURIComponent(rid)}`
  const name = run?.course?.name || run?.title
  useDocumentTitle(name)

  if (isLoading) return <><TopBar crumbs={[{ label: 'Courses', to: '/' }, { label: '…' }]} /><PageBody width="wide"><Loading label="Loading the course" /></PageBody></>
  if (!run) return (
    <><TopBar crumbs={[{ label: 'Courses', to: '/' }, { label: 'Not found' }]} />
      <PageBody><EmptyState title="Course not found" actions={<Button to="/">Your courses</Button>}>{problemOf(error, 'This course does not exist any more. It may have been deleted.')}</EmptyState></PageBody></>
  )

  const rest = loc.pathname.slice(base.length)
  const tab = rest.startsWith('/design') ? 'design' : rest.startsWith('/lectures') ? 'lectures' : rest.startsWith('/student') ? 'student' : 'overview'
  const approved = run.status === 'done'
  const locked = 'Opens once the course design is approved'
  const tabs: TabItem[] = [
    { id: 'overview', label: 'Overview', to: base, icon: <LayoutDashboard aria-hidden /> },
    { id: 'design', label: 'Design', to: `${base}/design`, icon: <PencilRuler aria-hidden /> },
    { id: 'lectures', label: 'Lectures', to: `${base}/lectures`, icon: <ListChecks aria-hidden />, disabled: !approved, hint: approved ? undefined : locked },
    { id: 'student', label: 'Student view', to: `${base}/student`, icon: <Eye aria-hidden />, disabled: !approved, hint: approved ? undefined : locked },
  ]
  const c = run.course
  const facts = c?.credits ? [`${c.credits} credits`, `L-T-P ${c.ltp}`, c.weeks ? `${c.weeks} weeks` : '', c.department ?? '', c.level ? `Level ${c.level}xx` : ''].filter(Boolean) : []

  return (
    <>
      <TopBar crumbs={[{ label: 'Courses', to: '/' }, { label: name ?? rid }]}
        actions={<Menu label="More for this course" trigger={<IconButton label="More"><Ellipsis /></IconButton>} items={[
          { label: 'Start again with changes', icon: <RotateCcw />, onSelect: () => startAgain(rid, nav) },
          { label: 'Delete the course', icon: <Trash2 />, danger: true, onSelect: async () => { if (await deleteCourse(qc, rid, name ?? rid)) nav('/') } },
        ]} />} />
      <div className="border-b border-line">
        <div className="mx-auto max-w-[84rem] px-4 pt-6 sm:px-6">
          <div className="flex flex-wrap items-start justify-between gap-x-6 gap-y-3">
            <div className="min-w-0">
              <h1 className="h-display text-3xl text-ink-1 [text-wrap:balance]">{name}</h1>
              {facts.length > 0 && (
                <ul className="mt-2 flex flex-wrap items-center gap-x-2 gap-y-1 text-sm text-ink-3" aria-label="Course facts">
                  {facts.map((f, i) => <li key={f} className="flex items-center gap-2">{i > 0 && <span aria-hidden className="size-0.5 rounded-full bg-ink-4" />}{f}</li>)}
                </ul>
              )}
            </div>
            <RunStatusBadge run={run} />
          </div>
          <Tabs className="mt-5 border-b-0" label="Sections of this course" tabs={tabs} value={tab} />
        </div>
      </div>
      <Outlet context={{ run, rid, base } satisfies CourseCtx} />
    </>
  )
}
