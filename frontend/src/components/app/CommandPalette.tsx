// Ctrl/⌘ K: jump to a course, its lectures, or a section, without hunting through the sidebar.
import { useEffect, useSyncExternalStore } from 'react'
import { Command } from 'cmdk'
import { useNavigate } from 'react-router-dom'
import { BookOpen, FlaskConical, LayoutGrid, ListChecks, Plus, Search } from 'lucide-react'
import { useRuns } from '@/lib/queries'
import { statusLabel } from '@/lib/status'

let open = false
const listeners = new Set<() => void>()
const set = (v: boolean) => { open = v; listeners.forEach((l) => l()) }
export const openPalette = () => set(true)

const item = 'flex h-10 cursor-pointer select-none items-center gap-3 rounded-md px-3 text-base text-ink-2 data-[selected=true]:bg-white/[0.08] data-[selected=true]:text-ink-1 [&_svg]:size-4 [&_svg]:text-ink-3'

export function CommandPalette() {
  const isOpen = useSyncExternalStore((l) => { listeners.add(l); return () => listeners.delete(l) }, () => open)
  const { data: runs } = useRuns()
  const nav = useNavigate()
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); set(!open) }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])
  const go = (to: string) => { set(false); nav(to) }
  return (
    <Command.Dialog open={isOpen} onOpenChange={set} label="Search or jump to" loop
      overlayClassName="fixed inset-0 z-[60] bg-black/60 backdrop-blur-[3px] data-[state=open]:animate-fade-in"
      contentClassName="fixed left-1/2 top-[14vh] z-[60] w-[calc(100vw-1.5rem)] max-w-xl -translate-x-1/2 outline-none data-[state=open]:animate-rise">
      <div className="glow-field shadow-3">
        <div className="glow-inner glass-strong overflow-hidden">
          <div className="flex items-center gap-3 border-b border-line px-4">
            <Search aria-hidden className="size-4 text-ink-3" />
            <Command.Input placeholder="Search courses, or type a place to go…" className="h-12 flex-1 bg-transparent text-md text-ink-1 outline-none placeholder:text-ink-4" />
          </div>
          <Command.List className="max-h-[min(60vh,26rem)] overflow-y-auto p-2">
            <Command.Empty className="px-3 py-8 text-center text-base text-ink-3">Nothing matches.</Command.Empty>
            <Command.Group heading="Go to" className="[&_[cmdk-group-heading]]:label-caps [&_[cmdk-group-heading]]:px-3 [&_[cmdk-group-heading]]:py-1.5">
              <Command.Item className={item} onSelect={() => go('/new')}><Plus />New course</Command.Item>
              <Command.Item className={item} onSelect={() => go('/')}><LayoutGrid />Courses</Command.Item>
              <Command.Item className={item} onSelect={() => go('/simulations')}><FlaskConical />Simulations</Command.Item>
            </Command.Group>
            {!!runs?.length && (
              <Command.Group heading="Courses" className="mt-1 [&_[cmdk-group-heading]]:label-caps [&_[cmdk-group-heading]]:px-3 [&_[cmdk-group-heading]]:py-1.5">
                {runs.map((r) => (
                  <Command.Item key={r.run_id} value={`${r.title} ${r.run_id}`} className={item} onSelect={() => go(`/courses/${encodeURIComponent(r.run_id)}`)}>
                    <BookOpen /><span className="min-w-0 flex-1 truncate">{r.title}</span><span className="text-xs text-ink-3">{statusLabel(r)}</span>
                  </Command.Item>
                ))}
                {runs.filter((r) => r.status === 'done').map((r) => (
                  <Command.Item key={r.run_id + '-l'} value={`${r.title} lectures ${r.run_id}`} className={item} onSelect={() => go(`/courses/${encodeURIComponent(r.run_id)}/lectures`)}>
                    <ListChecks /><span className="min-w-0 flex-1 truncate">{r.title}</span><span className="text-xs text-ink-3">Lectures</span>
                  </Command.Item>
                ))}
              </Command.Group>
            )}
          </Command.List>
        </div>
      </div>
    </Command.Dialog>
  )
}
