// The frame around every screen: the sidebar (a drawer on small screens), the place pages render, and the app-wide
// layers (toasts, confirmations, the command palette, the simulation window).
import { useEffect, useState, type ReactNode } from 'react'
import * as D from '@radix-ui/react-dialog'
import { Link, NavLink, Outlet, useLocation } from 'react-router-dom'
import { Activity, ChevronRight, Database, FlaskConical, KeyRound, LayoutGrid, Menu as MenuIcon, Plus, Search } from 'lucide-react'
import { cn } from '@/lib/cn'
import { useHealth, useRuns } from '@/lib/queries'
import { STATUS, statusLabel } from '@/lib/status'
import { ConfirmHost, Kbd, Skeleton, StatusDot, Toaster, Tip } from '@/components/ui'
import { CommandPalette, openPalette } from './CommandPalette'
import { SimPreviewHost } from './SimPreview'

export function Logo({ size = 28 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden className="shrink-0">
      <defs>
        <linearGradient id="lg-logo" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#1b2030" />
          <stop offset="1" stopColor="#0e1118" />
        </linearGradient>
      </defs>
      <rect width="32" height="32" rx="8" fill="url(#lg-logo)" stroke="rgb(255 255 255 / 0.12)" />
      <path d="M10 22.5V10h6.6a4.4 4.4 0 0 1 0 8.8H13" fill="none" stroke="#8f9bff" strokeWidth="2.3" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="22.4" cy="21.6" r="2" fill="#45d6a4" />
    </svg>
  )
}

const navCls = ({ isActive }: { isActive: boolean }) =>
  cn('group relative flex h-9 items-center gap-2.5 rounded-md px-2.5 text-base font-medium no-underline transition-colors duration-150 [&_svg]:size-[18px]',
    isActive ? 'bg-white/[0.07] text-ink-1' : 'text-ink-2 hover:bg-white/[0.04] hover:text-ink-1')

function SystemStatus() {
  const { data: h } = useHealth()
  if (!h) return <div className="space-y-2 px-1"><Skeleton className="h-3 w-32" /><Skeleton className="h-3 w-24" /></div>
  const kgOk = h.kg_backend === 'neo4j' ? !!h.neo4j : true
  const keys = h.keys.gemini + h.keys.groq
  const rows: { icon: ReactNode; label: string; value: string; tone: 'mint' | 'amber' | 'rose' | 'iris' | 'neutral'; hint: string }[] = [
    { icon: <Database />, label: 'Course database', value: h.kg_backend === 'neo4j' ? (h.neo4j ? 'Connected' : 'Not running') : 'Sample data', tone: h.kg_backend === 'neo4j' ? (kgOk ? 'mint' : 'rose') : 'amber',
      hint: h.kg_backend === 'neo4j' ? (h.neo4j ? 'Neo4j is running with the IIIT-D course graph.' : 'Open Neo4j Desktop and start the ProfsAgent database.') : 'Using the 17-course sample graph, not the full IIIT-D graph.' },
    { icon: <KeyRound />, label: 'AI access', value: keys ? `${keys} key${keys === 1 ? '' : 's'}` : 'No keys', tone: keys ? 'mint' : 'rose', hint: keys ? 'AI keys were found in .env.' : 'Add GEMINI_API_KEYS (and GROQ_API_KEYS) to the .env file, then restart the app.' },
    { icon: <Activity />, label: 'Activity', value: h.working_on ? 'Working' : h.queued ? `${h.queued} waiting` : 'Idle', tone: h.working_on ? 'iris' : 'neutral', hint: h.working_on ? 'A course is being worked on right now.' : 'Nothing is running.' },
  ]
  return (
    <dl className="space-y-1.5">
      {rows.map((r) => (
        <Tip key={r.label} label={r.hint} side="right">
          <div tabIndex={0} className="flex items-center justify-between gap-2 rounded px-1 text-xs">
            <dt className="flex items-center gap-2 text-ink-3 [&_svg]:size-3.5">{r.icon}{r.label}</dt>
            <dd className="flex items-center gap-1.5 text-ink-2"><StatusDot tone={r.tone} label={r.value} pulse={r.tone === 'iris'} />{r.value}</dd>
          </div>
        </Tip>
      ))}
    </dl>
  )
}

function SidebarBody({ onNavigate }: { onNavigate?: () => void }) {
  const { data: runs, isLoading } = useRuns()
  const recent = (runs ?? []).slice(0, 8)
  return (
    <div className="flex h-full flex-col">
      <Link to="/" onClick={onNavigate} className="flex h-[3.25rem] items-center gap-2.5 px-4 no-underline">
        <Logo />
        <span className="flex flex-col leading-none">
          <span className="text-md font-semibold tracking-tight text-ink-1">ProfsAgent</span>
          <span className="mt-1 text-2xs font-medium uppercase tracking-[0.1em] text-ink-3">IIIT-Delhi</span>
        </span>
      </Link>

      <div className="px-3 pt-2">
        <button type="button" onClick={() => { onNavigate?.(); openPalette() }}
          className="flex h-9 w-full cursor-pointer items-center gap-2 rounded-md border border-line bg-white/[0.03] px-2.5 text-sm text-ink-3 transition-colors hover:border-line-strong hover:text-ink-2">
          <Search aria-hidden className="size-4" />
          <span className="flex-1 text-left">Search or jump to…</span>
          <span className="flex gap-0.5" aria-hidden><Kbd>Ctrl</Kbd><Kbd>K</Kbd></span>
        </button>
      </div>

      <nav aria-label="Main" className="mt-4 space-y-0.5 px-3">
        <NavLink to="/" end className={navCls} onClick={onNavigate}><LayoutGrid aria-hidden />Courses</NavLink>
        <NavLink to="/simulations" className={navCls} onClick={onNavigate}><FlaskConical aria-hidden />Simulations</NavLink>
      </nav>

      <div className="mt-6 flex min-h-0 flex-1 flex-col px-3">
        <div className="flex items-center justify-between px-2.5 pb-1.5">
          <span className="label-caps">Your courses</span>
          <Tip label="New course"><Link to="/new" onClick={onNavigate} aria-label="New course" className="flex size-6 items-center justify-center rounded text-ink-3 hover:bg-white/[0.07] hover:text-ink-1"><Plus className="size-3.5" /></Link></Tip>
        </div>
        <ul className="min-h-0 flex-1 space-y-0.5 overflow-y-auto pb-2">
          {isLoading && [0, 1, 2].map((i) => <li key={i} className="px-2.5 py-2"><Skeleton className="h-3 w-full" /></li>)}
          {!isLoading && !recent.length && <li className="px-2.5 py-1 text-sm text-ink-3">None yet</li>}
          {recent.map((r) => {
            const s = STATUS[r.status] ?? STATUS.queued
            return (
              <li key={r.run_id}>
                <NavLink to={`/courses/${encodeURIComponent(r.run_id)}`} onClick={onNavigate}
                  className={({ isActive }) => cn('flex h-8 items-center gap-2.5 rounded-md px-2.5 text-sm no-underline transition-colors', isActive ? 'bg-white/[0.07] text-ink-1' : 'text-ink-2 hover:bg-white/[0.04] hover:text-ink-1')}>
                  <StatusDot tone={s.tone} label={statusLabel(r)} pulse={r.status === 'running'} />
                  <span className="truncate">{r.title}</span>
                </NavLink>
              </li>
            )
          })}
        </ul>
      </div>

      <div className="border-t border-line px-3 py-3">
        <SystemStatus />
      </div>
    </div>
  )
}

export function Shell() {
  const [drawer, setDrawer] = useState(false)
  const loc = useLocation()
  useEffect(() => { window.scrollTo(0, 0) }, [loc.pathname])
  return (
    <>
      <div className="app-bg" aria-hidden />
      <a href="#main" onClick={(e) => { e.preventDefault(); document.getElementById('main')?.focus() }} className="sr-only focus:not-sr-only focus:fixed focus:left-3 focus:top-3 focus:z-[90] focus:rounded-md focus:bg-iris-600 focus:px-3 focus:py-2 focus:text-white">Skip to the content</a>

      <aside aria-label="Sidebar" className="glass fixed inset-y-0 left-0 z-30 hidden w-[16rem] border-r border-line lg:block">
        <SidebarBody />
      </aside>

      <header className="glass sticky top-0 z-30 flex h-[3.25rem] items-center gap-2 border-b border-line px-3 lg:hidden">
        <D.Root open={drawer} onOpenChange={setDrawer}>
          <D.Trigger aria-label="Open the menu" className="flex size-9 cursor-pointer items-center justify-center rounded-md text-ink-2 hover:bg-white/[0.07]"><MenuIcon className="size-5" /></D.Trigger>
          <D.Portal>
            <D.Overlay className="fixed inset-0 z-50 bg-black/60 backdrop-blur-[2px] data-[state=open]:animate-fade-in" />
            <D.Content className="glass-strong fixed inset-y-0 left-0 z-50 w-[17rem] max-w-[86vw] border-r border-line-strong shadow-3 outline-none data-[state=open]:animate-fade-in">
              <D.Title className="sr-only">Menu</D.Title>
              <D.Description className="sr-only">Sections and your courses</D.Description>
              <SidebarBody onNavigate={() => setDrawer(false)} />
            </D.Content>
          </D.Portal>
        </D.Root>
        <Link to="/" className="flex items-center gap-2 no-underline"><Logo size={24} /><span className="text-md font-semibold text-ink-1">ProfsAgent</span></Link>
        <button type="button" aria-label="Search" onClick={openPalette} className="ml-auto flex size-9 cursor-pointer items-center justify-center rounded-md text-ink-2 hover:bg-white/[0.07]"><Search className="size-[18px]" /></button>
      </header>

      <div className="lg:pl-[16rem]">
        <main id="main" tabIndex={-1} className="min-h-dvh outline-none">
          <Outlet />
        </main>
      </div>

      <Toaster />
      <ConfirmHost />
      <CommandPalette />
      <SimPreviewHost />
    </>
  )
}

// ------------------------------------------------------------------ what every page is made of
export interface Crumb { label: string; to?: string }

/** The sticky strip at the top of a page: where you are, and the page's own actions. */
export function TopBar({ crumbs, actions }: { crumbs: Crumb[]; actions?: ReactNode }) {
  return (
    <div className="glass sticky top-[3.25rem] z-20 flex min-h-[3.25rem] flex-wrap items-center justify-between gap-x-4 gap-y-1 border-b border-line px-4 py-2 sm:px-6 lg:top-0">
      <nav aria-label="Breadcrumb" className="min-w-0">
        <ol className="flex min-w-0 items-center gap-1 text-sm">
          {crumbs.map((c, i) => (
            <li key={i} className="flex min-w-0 items-center gap-1">
              {i > 0 && <ChevronRight aria-hidden className="size-3.5 shrink-0 text-ink-4" />}
              {c.to ? <Link to={c.to} className="truncate rounded px-1 text-ink-3 no-underline hover:text-ink-1">{c.label}</Link>
                : <span aria-current="page" className="truncate px-1 font-medium text-ink-1">{c.label}</span>}
            </li>
          ))}
        </ol>
      </nav>
      {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
    </div>
  )
}

export function PageBody({ children, width = 'page', className }: { children: ReactNode; width?: 'page' | 'wide' | 'read'; className?: string }) {
  return <div className={cn('mx-auto w-full px-4 pb-32 pt-6 sm:px-6 lg:pt-8', width === 'wide' ? 'max-w-[84rem]' : width === 'read' ? 'max-w-[50rem]' : 'max-w-[70rem]', className)}>{children}</div>
}

/** The page's name in the display face, a line about it, and the one or two things to do. */
export function PageHeader({ eyebrow, title, description, actions, meta }: { eyebrow?: ReactNode; title: ReactNode; description?: ReactNode; actions?: ReactNode; meta?: ReactNode }) {
  return (
    <header className="flex flex-wrap items-end justify-between gap-x-6 gap-y-4">
      <div className="min-w-0 max-w-3xl">
        {eyebrow && <p className="label-caps mb-2">{eyebrow}</p>}
        <h1 className="h-display text-3xl text-ink-1 sm:text-4xl [text-wrap:balance]">{title}</h1>
        {description && <p className="mt-2 text-md text-ink-2">{description}</p>}
        {meta && <div className="mt-3 flex flex-wrap items-center gap-2">{meta}</div>}
      </div>
      {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
    </header>
  )
}
