// Toasts: a tiny store outside React, so any handler can call toast() without a provider.
import { useSyncExternalStore } from 'react'

export type ToastTone = 'neutral' | 'success' | 'error'
export interface ToastItem { id: number; message: string; tone: ToastTone }

let items: ToastItem[] = []
let next = 1
const listeners = new Set<() => void>()
const emit = () => listeners.forEach((l) => l())

export function dismiss(id: number) {
  items = items.filter((t) => t.id !== id)
  emit()
}

export function toast(message: string, tone: ToastTone = 'neutral') {
  const id = next++
  items = [...items.slice(-2), { id, message, tone }]
  emit()
  setTimeout(() => dismiss(id), tone === 'error' ? 7000 : 4500)
}
toast.success = (m: string) => toast(m, 'success')
toast.error = (m: string) => toast(m, 'error')

export const useToasts = () =>
  useSyncExternalStore(
    (l) => {
      listeners.add(l)
      return () => listeners.delete(l)
    },
    () => items,
  )
