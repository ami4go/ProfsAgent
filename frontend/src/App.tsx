import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MotionConfig } from 'motion/react'
import { HashRouter, Navigate, Route, Routes, useParams } from 'react-router-dom'
import { TooltipProvider } from '@/components/ui'
import { Shell } from '@/components/app/Shell'
import { CoursesPage } from '@/pages/Courses'
import { NewCoursePage } from '@/pages/NewCourse'
import { CourseLayout } from '@/pages/course/Layout'
import { OverviewPage } from '@/pages/course/Overview'
import { DesignPage } from '@/pages/design/Design'
import { KitPage, NotebookPage } from '@/pages/lectures/Documents'
import { LecturePage } from '@/pages/lectures/Lecture'
import { LecturesPage } from '@/pages/lectures/Lectures'
import { StudentPage } from '@/pages/lectures/Student'
import { SimulationsPage } from '@/pages/Simulations'
import { EmptyState, Button } from '@/components/ui'
import { PageBody, TopBar } from '@/components/app/Shell'

const client = new QueryClient({ defaultOptions: { queries: { staleTime: 1500, refetchOnWindowFocus: true, retry: 1 } } })

// links from the first app (#/run/…, #/delivery/…) keep working
function OldRun() {
  const { rid = '' } = useParams()
  return <Navigate replace to={`/courses/${encodeURIComponent(rid)}/design`} />
}
function OldDelivery() {
  const p = useParams()
  const rest = (p['*'] ?? '').split('/').filter(Boolean)
  const tail = rest[0] === 'student' ? '/student' : rest.length ? `/lectures/${rest.map(encodeURIComponent).join('/')}` : '/lectures'
  return <Navigate replace to={`/courses/${encodeURIComponent(p.rid ?? '')}${tail}`} />
}

function NotFound() {
  return (
    <>
      <TopBar crumbs={[{ label: 'Courses', to: '/' }, { label: 'Not found' }]} />
      <PageBody><EmptyState title="This page does not exist" actions={<Button to="/">Your courses</Button>}>The link may be old, or the course may have been deleted.</EmptyState></PageBody>
    </>
  )
}

export function App() {
  return (
    <QueryClientProvider client={client}>
      <MotionConfig reducedMotion="user">
        <TooltipProvider>
          <HashRouter>
            <Routes>
              <Route element={<Shell />}>
                <Route index element={<CoursesPage />} />
                <Route path="new" element={<NewCoursePage />} />
                <Route path="courses/:rid" element={<CourseLayout />}>
                  <Route index element={<OverviewPage />} />
                  <Route path="design" element={<DesignPage />} />
                  <Route path="design/:stage" element={<DesignPage />} />
                  <Route path="lectures" element={<LecturesPage />} />
                  <Route path="lectures/:lid" element={<LecturePage />} />
                  <Route path="lectures/:lid/kit" element={<KitPage />} />
                  <Route path="lectures/:lid/notebooklm" element={<NotebookPage />} />
                  <Route path="student" element={<StudentPage />} />
                </Route>
                <Route path="simulations" element={<SimulationsPage />} />
                <Route path="run/:rid" element={<OldRun />} />
                <Route path="delivery" element={<Navigate replace to="/" />} />
                <Route path="delivery/:rid/*" element={<OldDelivery />} />
                <Route path="*" element={<NotFound />} />
              </Route>
            </Routes>
          </HashRouter>
        </TooltipProvider>
      </MotionConfig>
    </QueryClientProvider>
  )
}
