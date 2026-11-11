import type { HTMLAttributes, ReactNode } from 'react'
import { cn } from '@/lib/cn'

/** The surface every block of content sits on. */
export function Card({ className, ...rest }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('rounded-xl border border-line bg-surface-1 shadow-1', className)} {...rest} />
}

interface HeadProps { title: ReactNode; description?: ReactNode; actions?: ReactNode; icon?: ReactNode; as?: 'h2' | 'h3'; className?: string }
export function CardHeader({ title, description, actions, icon, as: H = 'h2', className }: HeadProps) {
  return (
    <div className={cn('flex flex-wrap items-start justify-between gap-x-4 gap-y-2 px-5 pt-4 pb-3', className)}>
      <div className="min-w-0 flex items-start gap-3">
        {icon && <span aria-hidden className="mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-md bg-white/[0.05] text-ink-2 [&_svg]:size-4">{icon}</span>}
        <div className="min-w-0">
          <H className="text-md font-semibold text-ink-1 leading-6">{title}</H>
          {description && <p className="mt-0.5 text-sm text-ink-3">{description}</p>}
        </div>
      </div>
      {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
    </div>
  )
}
export const CardBody = ({ className, ...rest }: HTMLAttributes<HTMLDivElement>) => <div className={cn('px-5 pb-5', className)} {...rest} />

/** One line of a list inside a card: content on the left, a status or an action on the right. */
export function Row({ children, aside, className }: { children: ReactNode; aside?: ReactNode; className?: string }) {
  return (
    <div className={cn('flex items-start justify-between gap-4 py-3 border-t border-line first:border-t-0 first:pt-0 last:pb-0', className)}>
      <div className="min-w-0 flex-1">{children}</div>
      {aside && <div className="shrink-0 flex flex-wrap items-center justify-end gap-2">{aside}</div>}
    </div>
  )
}

/** A number that matters, with its name. No decoration: a tile is a figure, not a chart. */
export function StatTile({ label, value, hint, icon, tone = 'neutral' }: { label: string; value: ReactNode; hint?: ReactNode; icon?: ReactNode; tone?: 'neutral' | 'iris' | 'mint' | 'amber' | 'rose' }) {
  const ring = { neutral: 'text-ink-3 bg-white/[0.05]', iris: 'text-iris-300 bg-iris-soft', mint: 'text-mint-300 bg-mint-soft', amber: 'text-amber-300 bg-amber-soft', rose: 'text-rose-300 bg-rose-soft' }[tone]
  return (
    <div className="rounded-xl border border-line bg-surface-1 shadow-1 px-4 py-3.5 min-w-0">
      <div className="flex items-center justify-between gap-2">
        <span className="text-sm text-ink-3 truncate">{label}</span>
        {icon && <span aria-hidden className={cn('flex size-6 items-center justify-center rounded-md [&_svg]:size-3.5', ring)}>{icon}</span>}
      </div>
      <div className="mt-1.5 text-2xl font-semibold tracking-tight text-ink-1 leading-8">{value}</div>
      {hint && <div className="mt-0.5 text-xs text-ink-3">{hint}</div>}
    </div>
  )
}
