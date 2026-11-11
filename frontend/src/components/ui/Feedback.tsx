// Loading, empty, and "something needs saying" states — one pattern each, used everywhere.
import type { ReactNode } from 'react'
import { CircleAlert, CircleCheck, Info, Sparkles, TriangleAlert } from 'lucide-react'
import { cn } from '@/lib/cn'
import type { Tone } from '@/lib/status'

/** The working indicator: ProfsAgent is doing something that takes a while. */
export const Cradle = ({ size = 26, className }: { size?: number; className?: string }) => (
  <span aria-hidden className={cn('cradle', className)} style={{ ['--size' as string]: `${size}px` }}><i /><i /><i /><i /></span>
)
export const Spinner = ({ className }: { className?: string }) => <span aria-hidden className={cn('spinner', className)} />

export const Skeleton = ({ className }: { className?: string }) => <div aria-hidden className={cn('skeleton', className)} />
/** A placeholder with the shape of what is loading, so the page does not jump when it arrives. */
export function SkeletonCard({ lines = 3, className }: { lines?: number; className?: string }) {
  return (
    <div className={cn('rounded-xl border border-line bg-surface-1 p-5', className)} aria-hidden>
      <Skeleton className="h-4 w-2/5" />
      <div className="mt-4 space-y-2.5">
        {Array.from({ length: lines }, (_, i) => <Skeleton key={i} className={cn('h-3', i === lines - 1 ? 'w-3/5' : 'w-full')} />)}
      </div>
    </div>
  )
}
export const Loading = ({ label = 'Loading' }: { label?: string }) => (
  <div role="status" aria-live="polite" className="space-y-4">
    <span className="sr-only">{label}…</span>
    <SkeletonCard lines={2} />
    <SkeletonCard lines={4} />
  </div>
)

const calloutTone: Record<Tone, { box: string; icon: ReactNode }> = {
  neutral: { box: 'border-line bg-white/[0.03]', icon: <Info className="text-ink-3" /> },
  iris: { box: 'border-iris-line bg-iris-soft', icon: <Sparkles className="text-iris-300" /> },
  mint: { box: 'border-mint-line bg-mint-soft', icon: <CircleCheck className="text-mint-400" /> },
  amber: { box: 'border-amber-line bg-amber-soft', icon: <TriangleAlert className="text-amber-400" /> },
  rose: { box: 'border-rose-line bg-rose-soft', icon: <CircleAlert className="text-rose-400" /> },
}
/** A message that belongs to the page (not a toast): what happened, and what to do about it. */
export function Callout({ tone = 'neutral', title, children, actions, icon, className }: { tone?: Tone; title?: ReactNode; children?: ReactNode; actions?: ReactNode; icon?: ReactNode; className?: string }) {
  const t = calloutTone[tone]
  return (
    <div role={tone === 'rose' ? 'alert' : 'note'} className={cn('flex gap-3 rounded-xl border px-4 py-3', t.box, className)}>
      <span aria-hidden className="mt-0.5 shrink-0 [&_svg]:size-[18px]">{icon ?? t.icon}</span>
      <div className="min-w-0 flex-1 text-base text-ink-2">
        {title && <p className="font-semibold text-ink-1">{title}</p>}
        {children && <div className={cn(title && 'mt-0.5')}>{children}</div>}
        {actions && <div className="mt-2.5 flex flex-wrap gap-2">{actions}</div>}
      </div>
    </div>
  )
}

/** Nothing here yet: say so, and offer the one thing to do next. */
export function EmptyState({ icon, title, children, actions, className }: { icon?: ReactNode; title: string; children?: ReactNode; actions?: ReactNode; className?: string }) {
  return (
    <div className={cn('flex flex-col items-center rounded-xl border border-dashed border-line-strong bg-white/[0.015] px-6 py-12 text-center', className)}>
      {icon && <span aria-hidden className="mb-4 flex size-12 items-center justify-center rounded-full border border-line bg-surface-2 text-ink-2 shadow-1 [&_svg]:size-5">{icon}</span>}
      <h3 className="text-md font-semibold text-ink-1">{title}</h3>
      {children && <p className="mt-1 max-w-md text-base text-ink-3">{children}</p>}
      {actions && <div className="mt-5 flex flex-wrap justify-center gap-2">{actions}</div>}
    </div>
  )
}

/** A value on a track. `tone` says how to read it (the caller decides what counts as good). */
export function Meter({ value, max = 100, tone = 'iris', label, className }: { value: number; max?: number; tone?: Tone; label: string; className?: string }) {
  const pct = Math.max(0, Math.min(100, max ? (100 * value) / max : 0))
  const fill = { neutral: 'bg-ink-3', iris: 'bg-iris-500', mint: 'bg-mint-500', amber: 'bg-amber-400', rose: 'bg-rose-400' }[tone]
  const track = { neutral: 'bg-white/[0.07]', iris: 'bg-iris-500/15', mint: 'bg-mint-500/15', amber: 'bg-amber-400/15', rose: 'bg-rose-400/15' }[tone]
  return (
    <div role="meter" aria-label={label} aria-valuemin={0} aria-valuemax={max} aria-valuenow={value} className={cn('h-1.5 w-full overflow-hidden rounded-full', track, className)}>
      <div className={cn('h-full rounded-full transition-[width] duration-500 ease-out', fill)} style={{ width: `${pct}%` }} />
    </div>
  )
}
