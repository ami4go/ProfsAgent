import * as D from '@radix-ui/react-dialog'
import { useSyncExternalStore, type ReactNode } from 'react'
import { X } from 'lucide-react'
import { cn } from '@/lib/cn'
import { Button } from './Button'

const widths = { sm: 'max-w-md', md: 'max-w-xl', lg: 'max-w-3xl', xl: 'max-w-5xl' }

interface ModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  title: ReactNode
  description?: ReactNode
  size?: keyof typeof widths
  footer?: ReactNode
  banner?: ReactNode
  children?: ReactNode
  /** keep the dialog open when the backdrop is clicked (forms with unsaved text) */
  sticky?: boolean
}
/** A dialog: focus is trapped inside, Escape closes it, and focus returns to what opened it. */
export function Modal({ open, onOpenChange, title, description, size = 'md', footer, banner, children, sticky }: ModalProps) {
  return (
    <D.Root open={open} onOpenChange={onOpenChange}>
      <D.Portal>
        <D.Overlay className="fixed inset-0 z-50 bg-black/60 backdrop-blur-[3px] data-[state=open]:animate-fade-in" />
        <D.Content
          onPointerDownOutside={(e) => sticky && e.preventDefault()}
          aria-describedby={description ? undefined : undefined}
          className={cn('fixed left-1/2 top-1/2 z-50 flex max-h-[min(88dvh,60rem)] w-[calc(100vw-1.5rem)] -translate-x-1/2 -translate-y-1/2 flex-col overflow-hidden rounded-2xl border border-line-strong glass-strong shadow-3 outline-none data-[state=open]:animate-rise', widths[size])}>
          {banner}
          <div className="flex items-start justify-between gap-4 px-6 pt-5 pb-3">
            <div className="min-w-0">
              <D.Title className="text-lg font-semibold text-ink-1">{title}</D.Title>
              {description ? <D.Description className="mt-1 text-sm text-ink-3">{description}</D.Description> : <D.Description className="sr-only">{typeof title === 'string' ? title : 'Dialog'}</D.Description>}
            </div>
            <D.Close aria-label="Close" className="-mr-2 -mt-1 flex size-8 shrink-0 cursor-pointer items-center justify-center rounded-md text-ink-3 hover:bg-white/[0.07] hover:text-ink-1">
              <X className="size-4" />
            </D.Close>
          </div>
          {children && <div className="min-h-0 flex-1 overflow-y-auto px-6 pb-5">{children}</div>}
          {footer && <div className="flex flex-wrap items-center justify-end gap-2 border-t border-line bg-black/20 px-6 py-3.5">{footer}</div>}
        </D.Content>
      </D.Portal>
    </D.Root>
  )
}

// ------------------------------------------------------------------ "are you sure?" — asked once, for things that cannot be undone here
interface Ask { title: string; body?: ReactNode; confirm: string; danger?: boolean; resolve: (ok: boolean) => void }
let current: Ask | null = null
const listeners = new Set<() => void>()
const emit = () => listeners.forEach((l) => l())

export function confirm(q: Omit<Ask, 'resolve'>): Promise<boolean> {
  return new Promise((resolve) => {
    current = { ...q, resolve }
    emit()
  })
}
function answer(ok: boolean) {
  current?.resolve(ok)
  current = null
  emit()
}
export function ConfirmHost() {
  const q = useSyncExternalStore((l) => { listeners.add(l); return () => listeners.delete(l) }, () => current)
  return (
    <Modal open={!!q} onOpenChange={(o) => !o && answer(false)} title={q?.title ?? ''} size="sm"
      footer={<>
        <Button variant="ghost" onClick={() => answer(false)}>Cancel</Button>
        <Button variant={q?.danger ? 'danger' : 'primary'} onClick={() => answer(true)} autoFocus>{q?.confirm}</Button>
      </>}>
      {q?.body && <div className="text-base text-ink-2">{q.body}</div>}
    </Modal>
  )
}
