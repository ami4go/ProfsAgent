import { forwardRef, useId, type InputHTMLAttributes, type ReactNode, type SelectHTMLAttributes, type TextareaHTMLAttributes } from 'react'
import { Check, ChevronDown } from 'lucide-react'
import { cn } from '@/lib/cn'

const control =
  'w-full rounded-md border bg-sunken/70 text-ink-1 placeholder:text-ink-4 outline-none transition-[border-color,box-shadow,background-color] duration-150 ' +
  'border-line-strong hover:border-white/20 focus:border-iris-500 focus:ring-[3px] focus:ring-iris-500/20 disabled:opacity-50 ' +
  'aria-[invalid=true]:border-rose-400 aria-[invalid=true]:focus:ring-rose-400/20 data-[ai=true]:border-iris-line data-[ai=true]:bg-iris-soft/40'

type Extra = { invalid?: boolean; ai?: boolean }

export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement> & Extra>(function Input({ className, invalid, ai, ...rest }, ref) {
  return <input ref={ref} type="text" aria-invalid={invalid || undefined} data-ai={ai || undefined} className={cn(control, 'h-9 px-3 text-base', className)} {...rest} />
})

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaHTMLAttributes<HTMLTextAreaElement> & Extra>(function Textarea({ className, invalid, ai, rows = 3, ...rest }, ref) {
  return <textarea ref={ref} rows={rows} aria-invalid={invalid || undefined} data-ai={ai || undefined} className={cn(control, 'px-3 py-2 text-base leading-relaxed resize-y min-h-[2.25rem]', className)} {...rest} />
})

export const Select = forwardRef<HTMLSelectElement, SelectHTMLAttributes<HTMLSelectElement> & Extra>(function Select({ className, invalid, ai, children, ...rest }, ref) {
  return (
    <span className={cn('relative inline-block w-full', className)}>
      <select ref={ref} aria-invalid={invalid || undefined} data-ai={ai || undefined} className={cn(control, 'h-9 pl-3 pr-8 text-base appearance-none cursor-pointer')} {...rest}>
        {children}
      </select>
      <ChevronDown aria-hidden className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 size-4 text-ink-3" />
    </span>
  )
})

/** A label, the control, an optional hint, and the error under it. */
export function Field({ label, optional, hint, error, htmlFor, children, className }: {
  label: ReactNode; optional?: boolean; hint?: ReactNode; error?: string; htmlFor?: string; children: ReactNode; className?: string
}) {
  return (
    <div className={cn('min-w-0', className)}>
      <label htmlFor={htmlFor} className="mb-1.5 flex items-baseline gap-1.5 text-sm font-medium text-ink-1">
        {label}
        {optional && <span className="font-normal text-ink-3">optional</span>}
      </label>
      {children}
      {error ? <p role="alert" className="mt-1.5 text-sm text-rose-300">{error}</p> : hint ? <p className="mt-1.5 text-xs text-ink-3">{hint}</p> : null}
    </div>
  )
}
export const FieldError = ({ children }: { children?: ReactNode }) => (children ? <p role="alert" className="mt-1.5 text-sm text-rose-300">{children}</p> : null)

interface CheckProps { checked: boolean; onChange: (v: boolean) => void; children: ReactNode; description?: ReactNode; disabled?: boolean; className?: string }
/** A checkbox whose box lights up when ticked. The real input stays in the page for keyboards and screen readers. */
export function Checkbox({ checked, onChange, children, description, disabled, className }: CheckProps) {
  const id = useId()
  return (
    <label htmlFor={id} className={cn('group flex items-start gap-2.5 cursor-pointer select-none', disabled && 'opacity-50 pointer-events-none', className)}>
      <span className="relative mt-[3px] flex size-4 shrink-0">
        <input id={id} type="checkbox" className="peer absolute inset-0 opacity-0 cursor-pointer" checked={checked} disabled={disabled} onChange={(e) => onChange(e.target.checked)} />
        <span aria-hidden className={cn('flex size-4 items-center justify-center rounded-[5px] border transition-all duration-150 peer-focus-visible:outline-2 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-iris-400',
          checked ? 'border-iris-500 bg-iris-600 shadow-[0_0_12px_-2px_rgb(110_124_247/0.7)]' : 'border-line-strong bg-sunken group-hover:border-white/30')}>
          {checked && <Check className="size-3 text-white" strokeWidth={3} />}
        </span>
      </span>
      <span className="min-w-0 text-base text-ink-1">
        {children}
        {description && <span className="block text-sm text-ink-3">{description}</span>}
      </span>
    </label>
  )
}

/** On / off, for a setting that takes effect at once. */
export function Switch({ checked, onChange, label, disabled }: { checked: boolean; onChange: (v: boolean) => void; label: string; disabled?: boolean }) {
  return (
    <button type="button" role="switch" aria-checked={checked} aria-label={label} disabled={disabled} onClick={() => onChange(!checked)}
      className={cn('relative inline-flex h-5 w-9 shrink-0 cursor-pointer items-center rounded-full border transition-colors duration-200 disabled:opacity-50',
        checked ? 'bg-iris-600 border-iris-500 shadow-[0_0_14px_-3px_rgb(110_124_247/0.8)]' : 'bg-surface-3 border-line-strong')}>
      <span aria-hidden className={cn('inline-block size-3.5 rounded-full bg-white shadow transition-transform duration-200 ease-out', checked ? 'translate-x-[18px]' : 'translate-x-[3px]')} />
    </button>
  )
}

/** A chip that is either on or off (pick several from a short list). */
export function ToggleChip({ on, onClick, children, ai }: { on: boolean; onClick: () => void; children: ReactNode; ai?: boolean }) {
  return (
    <button type="button" aria-pressed={on} onClick={onClick}
      className={cn('h-8 px-3 rounded-full border text-sm font-medium cursor-pointer transition-colors duration-150',
        on ? 'bg-iris-soft border-iris-line text-iris-200' : 'bg-transparent border-line-strong text-ink-2 hover:text-ink-1 hover:border-white/25', on && ai && 'border-dashed')}>
      {children}
    </button>
  )
}
