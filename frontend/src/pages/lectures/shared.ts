import { useQueryClient } from '@tanstack/react-query'
import { problemOf } from '@/lib/api'
import { keys } from '@/lib/queries'
import { toast } from '@/lib/toast'

/** Do something to the lecture plan on the server, say so, and refresh what the page shows. */
export function useDeliveryAction(rid: string) {
  const qc = useQueryClient()
  return async <T,>(fn: () => Promise<T>, done?: string | ((r: T) => string | void), fallback = 'Could not save'): Promise<T | undefined> => {
    try {
      const r = await fn()
      const msg = typeof done === 'function' ? done(r) : done
      if (msg) toast(msg)
      await qc.invalidateQueries({ queryKey: keys.delivery(rid) })
      return r
    } catch (e) {
      toast.error(problemOf(e, fallback))
      await qc.invalidateQueries({ queryKey: keys.delivery(rid) })
      return undefined
    }
  }
}
export const lectureUrl = (base: string, lid: string, rest = '') => `${base}/lectures/${encodeURIComponent(lid)}${rest}`
