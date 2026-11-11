// Editing at a check. Everything ProfsAgent wrote can be changed: "Save and check again" applies the change to the
// course, runs the same rule checks again (no AI) and refreshes the open problems. Nothing restarts.
import { useState, type ReactNode } from 'react'
import { ArrowDown, ArrowUp, Plus, X } from 'lucide-react'
import { Button, IconButton, Modal } from '@/components/ui'

/** Saves one part of the waiting check. Resolves to null when saved, or to the messages by field. */
export type SaveFn = (section: string, value: unknown) => Promise<Record<string, string> | null>

export function useEditor(save: SaveFn, onClose: () => void) {
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [busy, setBusy] = useState(false)
  const submit = async (section: string, value: unknown) => {
    setBusy(true)
    const errs = await save(section, value)
    setBusy(false)
    if (errs) {
      setErrors(errs)
      requestAnimationFrame(() => document.querySelector('[role="dialog"] [role="alert"]')?.scrollIntoView({ block: 'center', behavior: 'smooth' }))
    } else onClose()
  }
  return { errors, busy, submit, err: (path: string) => errors[path], clear: () => setErrors({}) }
}

export function EditorDialog({ title, description, onClose, onSave, busy, error, size = 'lg', left, children }: {
  title: string; description?: ReactNode; onClose: () => void; onSave: () => void; busy: boolean; error?: string; size?: 'md' | 'lg' | 'xl'; left?: ReactNode; children: ReactNode
}) {
  return (
    <Modal open onOpenChange={(o) => !o && onClose()} sticky size={size} title={title} description={description}
      footer={<>
        {left && <div className="mr-auto">{left}</div>}
        <Button variant="ghost" onClick={onClose}>Cancel</Button>
        <Button variant="primary" loading={busy} onClick={onSave}>{busy ? 'Checking…' : 'Save and check again'}</Button>
      </>}>
      {children}
      {error && <p role="alert" className="mt-3 rounded-md border border-rose-line bg-rose-soft px-3 py-2 text-sm text-rose-300">{error}</p>}
    </Modal>
  )
}

// ---- lists inside editors
export const upd = <T,>(a: T[], i: number, patch: Partial<T>): T[] => a.map((x, k) => (k === i ? { ...x, ...patch } : x))
export const del = <T,>(a: T[], i: number): T[] => a.filter((_, k) => k !== i)
export const move = <T,>(a: T[], i: number, d: -1 | 1): T[] => {
  const j = i + d
  if (j < 0 || j >= a.length) return a
  const b = [...a]
  ;[b[i], b[j]] = [b[j], b[i]]
  return b
}

export function RowTools({ i, n, onMove, onRemove, what }: { i: number; n: number; onMove?: (d: -1 | 1) => void; onRemove: () => void; what: string }) {
  return (
    <div className="flex shrink-0 gap-0.5">
      {onMove && <IconButton size="sm" label="Move up" disabled={i === 0} onClick={() => onMove(-1)}><ArrowUp /></IconButton>}
      {onMove && <IconButton size="sm" label="Move down" disabled={i === n - 1} onClick={() => onMove(1)}><ArrowDown /></IconButton>}
      <IconButton size="sm" tone="danger" label={`Remove ${what}`} onClick={onRemove}><X /></IconButton>
    </div>
  )
}
export const AddButton = ({ onClick, children }: { onClick: () => void; children: ReactNode }) => (
  <Button size="sm" variant="ghost" icon={<Plus aria-hidden />} onClick={onClick} className="mt-2 border border-dashed border-line-strong">{children}</Button>
)
/** One editable item in a list: a soft box with its tools on the right. */
export const EditRow = ({ children, tools }: { children: ReactNode; tools?: ReactNode }) => (
  <div className="flex items-start gap-3 rounded-lg border border-line bg-white/[0.02] p-3">
    <div className="min-w-0 flex-1 space-y-2.5">{children}</div>
    {tools}
  </div>
)
export const weekOptions = (n: number) => Array.from({ length: Math.max(0, n) }, (_, k) => k + 1)
