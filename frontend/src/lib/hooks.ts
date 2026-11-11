import { useCallback, useEffect, useRef, useState } from 'react'
import { problemOf } from './api'
import { toast } from './toast'

/** Run something that talks to the server: `busy` while it runs; a failure becomes a toast unless `onError` handles it. */
export function useBusy() {
  const [busy, setBusy] = useState(false)
  const alive = useRef(true)
  useEffect(() => () => { alive.current = false }, [])
  const run = useCallback(async <T,>(fn: () => Promise<T>, onError?: (e: unknown) => void): Promise<T | undefined> => {
    setBusy(true)
    try {
      return await fn()
    } catch (e) {
      if (onError) onError(e)
      else toast.error(problemOf(e))
      return undefined
    } finally {
      if (alive.current) setBusy(false)
    }
  }, [])
  return [busy, run] as const
}

/** A value that follows `value` after it has been still for `ms`. */
export function useDebounced<T>(value: T, ms = 400): T {
  const [v, setV] = useState(value)
  useEffect(() => {
    const t = setTimeout(() => setV(value), ms)
    return () => clearTimeout(t)
  }, [value, ms])
  return v
}

/** Re-render on a timer (countdowns). */
export function useTick(ms: number, on = true) {
  const [, set] = useState(0)
  useEffect(() => {
    if (!on) return
    const t = setInterval(() => set((n) => n + 1), ms)
    return () => clearInterval(t)
  }, [ms, on])
}

export function useDocumentTitle(title?: string | null) {
  useEffect(() => {
    document.title = title ? `${title} · ProfsAgent` : 'ProfsAgent'
  }, [title])
}
