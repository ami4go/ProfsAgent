import type { ReactNode } from 'react'
import { Check, PencilLine, Sparkles } from 'lucide-react'
import { cn } from '@/lib/cn'
import type { Tone } from '@/lib/status'

const tones: Record<Tone, string> = {
  neutral: 'bg-white/[0.06] text-ink-2 border-line',
  iris: 'bg-iris-soft text-iris-300 border-iris-line',
  mint: 'bg-mint-soft text-mint-300 border-mint-line',
  amber: 'bg-amber-soft text-amber-300 border-amber-line',
  rose: 'bg-rose-soft text-rose-300 border-rose-line',
}
const dots: Record<Tone, string> = { neutral: 'bg-ink-3', iris: 'bg-iris-400', mint: 'bg-mint-400', amber: 'bg-amber-400', rose: 'bg-rose-400' }

interface BadgeProps {
  tone?: Tone
  icon?: ReactNode
  dot?: boolean
  pulse?: boolean
  title?: string
  className?: string
  children: ReactNode
}
/** A status in words. Colour repeats the meaning; it never carries it alone. */
export function Badge({ tone = 'neutral', icon, dot, pulse, title, className, children }: BadgeProps) {
  return (
    <span title={title} className={cn('inline-flex items-center gap-1.5 h-[22px] px-2 rounded-full border text-xs font-medium whitespace-nowrap [&_svg]:size-3 [&_svg]:shrink-0', tones[tone], className)}>
      {dot && <span aria-hidden className={cn('size-1.5 rounded-full', dots[tone], pulse && 'animate-pulse')} />}
      {icon}
      {children}
    </span>
  )
}

/** Marks text ProfsAgent wrote that nobody has approved yet. */
export const GeneratedBadge = ({ children = 'Written by ProfsAgent' }: { children?: ReactNode }) => <Badge tone="iris" icon={<Sparkles aria-hidden />}>{children}</Badge>
/** Marks what the professor approved. */
export const ApprovedBadge = ({ children = 'Approved by you' }: { children?: ReactNode }) => <Badge tone="mint" icon={<Check aria-hidden />}>{children}</Badge>
/** Marks what the professor changed by hand; the changes are listed in the title. */
export const EditedBadge = ({ changes }: { changes?: string[] }) =>
  changes && changes.length ? <Badge tone="mint" icon={<PencilLine aria-hidden />} title={changes.join('\n')}>Changed by you</Badge> : null

/** A small coloured dot with a label for screen readers (dense lists). */
export const StatusDot = ({ tone, label, pulse }: { tone: Tone; label: string; pulse?: boolean }) => (
  <span role="img" aria-label={label} title={label} className={cn('inline-block size-2 rounded-full shrink-0', dots[tone], pulse && 'animate-pulse')} />
)
