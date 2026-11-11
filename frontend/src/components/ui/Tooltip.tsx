import * as T from '@radix-ui/react-tooltip'
import type { ReactElement, ReactNode } from 'react'

export const TooltipProvider = ({ children }: { children: ReactNode }) => <T.Provider delayDuration={350} skipDelayDuration={200}>{children}</T.Provider>

/** A short hint on hover and on keyboard focus. Never the only place a fact lives. */
export function Tip({ label, children, side = 'top' }: { label: ReactNode; children: ReactElement; side?: 'top' | 'bottom' | 'left' | 'right' }) {
  if (!label) return children
  return (
    <T.Root>
      <T.Trigger asChild>{children}</T.Trigger>
      <T.Portal>
        <T.Content side={side} sideOffset={6} collisionPadding={8}
          className="z-[80] max-w-xs rounded-md border border-line-strong bg-surface-3 px-2.5 py-1.5 text-xs leading-snug text-ink-1 shadow-2 animate-fade-in">
          {label}
        </T.Content>
      </T.Portal>
    </T.Root>
  )
}
