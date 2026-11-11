import { AnimatePresence, motion } from 'motion/react'
import { CircleAlert, CircleCheck, X } from 'lucide-react'
import { dismiss, useToasts } from '@/lib/toast'
import { cn } from '@/lib/cn'

/** Short confirmations that slide in from the bottom and leave by themselves. Announced politely to screen readers. */
export function Toaster() {
  const items = useToasts()
  return (
    <div aria-live="polite" role="status" className="pointer-events-none fixed inset-x-0 bottom-24 z-[70] flex flex-col items-center gap-2 px-4">
      <AnimatePresence initial={false}>
        {items.map((t) => (
          <motion.div key={t.id} layout initial={{ opacity: 0, y: 14, scale: 0.97 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: 8, scale: 0.98 }} transition={{ duration: 0.22, ease: [0.22, 1, 0.36, 1] }}
            className={cn('pointer-events-auto flex max-w-[min(92vw,34rem)] items-start gap-2.5 rounded-xl border glass-strong px-3.5 py-2.5 text-sm text-ink-1 shadow-3',
              t.tone === 'error' ? 'border-rose-line' : t.tone === 'success' ? 'border-mint-line' : 'border-line-strong')}>
            {t.tone === 'error' ? <CircleAlert aria-hidden className="mt-0.5 size-4 shrink-0 text-rose-400" /> : t.tone === 'success' ? <CircleCheck aria-hidden className="mt-0.5 size-4 shrink-0 text-mint-400" /> : null}
            <span className="min-w-0">{t.message}</span>
            <button type="button" aria-label="Dismiss" onClick={() => dismiss(t.id)} className="-mr-1 ml-1 flex size-5 shrink-0 cursor-pointer items-center justify-center rounded text-ink-3 hover:text-ink-1">
              <X className="size-3.5" />
            </button>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  )
}
