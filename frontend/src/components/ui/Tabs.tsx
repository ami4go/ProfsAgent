import { useId, useRef, type KeyboardEvent, type ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'motion/react'
import { cn } from '@/lib/cn'
import { Tip } from './Tooltip'

export interface TabItem<T extends string = string> { id: T; label: ReactNode; count?: number; to?: string; disabled?: boolean; hint?: string; icon?: ReactNode }

function useArrows(n: number) {
  const refs = useRef<(HTMLElement | null)[]>([])
  const onKeyDown = (e: KeyboardEvent, i: number) => {
    const step = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : e.key === 'Home' ? -i : e.key === 'End' ? n - 1 - i : 0
    if (!step) return
    e.preventDefault()
    for (let k = 1; k <= n; k++) {
      const el = refs.current[(i + step * k + n * k) % n]
      if (el && el.getAttribute('aria-disabled') !== 'true') {
        el.focus()
        if (el.getAttribute('role') === 'tab' && !el.hasAttribute('href')) el.click()
        break
      }
    }
  }
  return { refs, onKeyDown }
}

/** Sections of one page: an underline that glides to the chosen tab. Tabs with `to` are links (the URL changes). */
export function Tabs<T extends string>({ tabs, value, onChange, label, className }: { tabs: TabItem<T>[]; value: T; onChange?: (v: T) => void; label: string; className?: string }) {
  const id = useId()
  const { refs, onKeyDown } = useArrows(tabs.length)
  return (
    <div role="tablist" aria-label={label} className={cn('flex gap-1 overflow-x-auto border-b border-line -mb-px [scrollbar-width:none]', className)}>
      {tabs.map((t, i) => {
        const on = t.id === value
        const cls = cn('relative flex h-10 shrink-0 items-center gap-2 px-3 text-base font-medium whitespace-nowrap cursor-pointer transition-colors duration-150 no-underline [&_svg]:size-4',
          on ? 'text-ink-1' : 'text-ink-3 hover:text-ink-1', t.disabled && 'opacity-45 cursor-not-allowed hover:text-ink-3')
        const inner = (
          <>
            {t.icon}
            {t.label}
            {t.count != null && <span className={cn('rounded-full px-1.5 text-2xs tnum leading-4', on ? 'bg-iris-soft text-iris-300' : 'bg-white/[0.07] text-ink-3')}>{t.count}</span>}
            {on && <motion.span layoutId={`${id}-line`} aria-hidden className="absolute inset-x-2 -bottom-px h-0.5 rounded-full bg-iris-400" transition={{ type: 'spring', stiffness: 500, damping: 40 }} />}
          </>
        )
        const common = { role: 'tab', 'aria-selected': on, 'aria-disabled': t.disabled || undefined, tabIndex: on ? 0 : -1, className: cls, onKeyDown: (e: KeyboardEvent) => onKeyDown(e, i) } as const
        const el = t.to && !t.disabled
          ? <Link key={t.id} to={t.to} ref={(n) => { refs.current[i] = n }} {...common}>{inner}</Link>
          : <button key={t.id} type="button" ref={(n) => { refs.current[i] = n }} {...common} onClick={() => !t.disabled && onChange?.(t.id)}>{inner}</button>
        return t.hint ? <Tip key={t.id} label={t.hint}>{el}</Tip> : el
      })}
    </div>
  )
}

/** A short set of choices where one is always on: the pill glides to it. */
export function Segmented<T extends string>({ options, value, onChange, label, size = 'md', disabled }: {
  options: { id: T; label: ReactNode; count?: number }[]; value: T; onChange: (v: T) => void; label: string; size?: 'sm' | 'md'; disabled?: boolean
}) {
  const id = useId()
  return (
    <div role="group" aria-label={label} className="inline-flex max-w-full overflow-x-auto rounded-lg border border-line bg-sunken/70 p-0.5 [scrollbar-width:none]">
      {options.map((o) => {
        const on = o.id === value
        return (
          <button key={o.id} type="button" aria-pressed={on} disabled={disabled} onClick={() => onChange(o.id)}
            className={cn('relative shrink-0 rounded-md font-medium whitespace-nowrap cursor-pointer transition-colors duration-150 disabled:opacity-50 disabled:cursor-default',
              size === 'sm' ? 'h-7 px-2.5 text-sm' : 'h-8 px-3 text-sm', on ? 'text-ink-1' : 'text-ink-3 hover:text-ink-1')}>
            {on && <motion.span layoutId={`${id}-pill`} aria-hidden className="absolute inset-0 rounded-md bg-surface-3 border border-line-strong shadow-1" transition={{ type: 'spring', stiffness: 520, damping: 42 }} />}
            <span className="relative inline-flex items-center gap-1.5">
              {o.label}
              {o.count != null && <span className={cn('text-2xs tnum', on ? 'text-ink-2' : 'text-ink-4')}>{o.count}</span>}
            </span>
          </button>
        )
      })}
    </div>
  )
}
