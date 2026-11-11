import { forwardRef, type ButtonHTMLAttributes, type ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { cn } from '@/lib/cn'
import { Tip } from './Tooltip'

export type ButtonVariant = 'primary' | 'glow' | 'secondary' | 'ghost' | 'danger' | 'success'
export type ButtonSize = 'sm' | 'md' | 'lg'

const base =
  'inline-flex items-center justify-center gap-2 font-medium whitespace-nowrap select-none no-underline cursor-pointer ' +
  'transition-[background-color,border-color,color,transform,box-shadow,opacity] duration-150 ease-out active:scale-[0.98] ' +
  'disabled:opacity-45 disabled:pointer-events-none aria-disabled:opacity-45 aria-disabled:pointer-events-none'
const sizes: Record<ButtonSize, string> = {
  sm: 'h-8 px-3 text-sm rounded-md [&_svg]:size-3.5',
  md: 'h-9 px-3.5 text-base rounded-md [&_svg]:size-4',
  lg: 'h-11 px-5 text-md rounded-lg [&_svg]:size-[18px]',
}
const variants: Record<ButtonVariant, string> = {
  primary: 'bg-iris-600 text-white hover:bg-iris-500 shadow-[inset_0_1px_0_rgb(255_255_255/0.18),0_1px_2px_rgb(0_0_0/0.4)]',
  glow: 'btn-glow bg-iris-600 text-white hover:bg-iris-500 shadow-[inset_0_1px_0_rgb(255_255_255/0.2)]',
  secondary: 'bg-surface-2 text-ink-1 border border-line-strong hover:bg-surface-3 hover:border-white/20 shadow-1',
  ghost: 'text-ink-2 hover:text-ink-1 hover:bg-white/[0.06]',
  danger: 'text-rose-300 border border-rose-line hover:bg-rose-soft',
  success: 'text-mint-300 border border-mint-line hover:bg-mint-soft',
}

interface Common {
  variant?: ButtonVariant
  size?: ButtonSize
  icon?: ReactNode
  iconRight?: ReactNode
  loading?: boolean
  className?: string
  children?: ReactNode
}
type AsButton = Common & Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'className' | 'children'> & { to?: undefined; href?: undefined }
type AsLink = Common & { to: string; href?: undefined; disabled?: boolean; 'aria-label'?: string; onClick?: () => void }
type AsAnchor = Common & { href: string; to?: undefined; download?: boolean | string; external?: boolean; disabled?: boolean; 'aria-label'?: string }
export type ButtonProps = AsButton | AsLink | AsAnchor

/** The one button of the app. `glow` is for the single action a screen exists for. */
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(props, ref) {
  const { variant = 'secondary', size = 'md', icon, iconRight, loading, className, children, ...rest } = props
  const cls = cn(base, sizes[size], variants[variant], className)
  const inner = (
    <>
      {loading ? <span className="spinner" aria-hidden /> : icon}
      {children}
      {iconRight}
    </>
  )
  if ('to' in rest && rest.to !== undefined) {
    const { to, disabled, ...a } = rest as AsLink
    return <Link to={to} className={cls} aria-disabled={disabled || undefined} tabIndex={disabled ? -1 : undefined} {...a}>{inner}</Link>
  }
  if ('href' in rest && rest.href !== undefined) {
    const { href, external, disabled, ...a } = rest as AsAnchor
    return <a href={href} className={cls} aria-disabled={disabled || undefined} {...(external ? { target: '_blank', rel: 'noopener noreferrer' } : {})} {...a}>{inner}</a>
  }
  const b = rest as AsButton
  return <button ref={ref} type="button" className={cls} {...b} disabled={b.disabled || loading}>{inner}</button>
})

interface IconButtonProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'children'> {
  label: string
  children: ReactNode
  size?: 'sm' | 'md'
  tone?: 'neutral' | 'danger'
}
/** A square button with only an icon; its label is read by screen readers and shown as a tooltip. */
export const IconButton = forwardRef<HTMLButtonElement, IconButtonProps>(function IconButton({ label, children, size = 'md', tone = 'neutral', className, ...rest }, ref) {
  return (
    <Tip label={label}>
      <button
        ref={ref} type="button" aria-label={label}
        className={cn('inline-flex items-center justify-center rounded-md transition-colors duration-150 cursor-pointer disabled:opacity-40 disabled:pointer-events-none [&_svg]:size-4',
          size === 'sm' ? 'size-7' : 'size-8', tone === 'danger' ? 'text-ink-3 hover:text-rose-300 hover:bg-rose-soft' : 'text-ink-3 hover:text-ink-1 hover:bg-white/[0.07]', className)}
        {...rest}
      >
        {children}
      </button>
    </Tip>
  )
})

/** A link that looks like text and does something (not navigation). */
export function TextButton({ className, ...rest }: ButtonHTMLAttributes<HTMLButtonElement>) {
  return <button type="button" className={cn('text-iris-300 hover:text-iris-200 underline decoration-iris-line underline-offset-[3px] hover:decoration-current text-sm font-medium cursor-pointer disabled:opacity-45', className)} {...rest} />
}
