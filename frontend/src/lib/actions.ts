// Things the professor can do to a course from more than one screen.
import type { QueryClient } from '@tanstack/react-query'
import { api, problemOf, runUrl } from './api'
import { store } from './format'
import { keys } from './queries'
import { toast } from './toast'
import { confirm } from '@/components/ui'

export async function deleteCourse(qc: QueryClient, rid: string, title: string): Promise<boolean> {
  const ok = await confirm({
    title: `Delete “${title}”?`,
    body: 'It is moved to the Deleted folder (runs/_deleted), so it can be recovered, and removed from the course database. If it is being worked on, that work stops.',
    confirm: 'Delete the course', danger: true,
  })
  if (!ok) return false
  try {
    await api.del(runUrl(rid))
    toast('Deleted. It is in runs/_deleted if you need it back.')
    await Promise.all([qc.invalidateQueries({ queryKey: keys.runs }), qc.invalidateQueries({ queryKey: keys.deliveryCourses })])
    return true
  } catch (e) {
    toast.error(problemOf(e, 'Could not delete'))
    return false
  }
}

/** "Start again with changes": the form of this run becomes the draft of a new course. */
export async function startAgain(rid: string, go: (to: string) => void) {
  try {
    const form = await api.get<Record<string, unknown>>(runUrl(rid, '/form'))
    store.set('profsagent-draft', JSON.stringify(form))
    go('/new')
    toast('The form is filled in from this course. Change what you need.')
  } catch (e) {
    toast.error(problemOf(e, 'Could not read the form of this course'))
  }
}
