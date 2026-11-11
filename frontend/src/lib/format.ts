// Dates, durations and counts, written the same way everywhere.

export const time = (t: number) => new Date(t * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
export const day = (t: number) => new Date(t * 1000).toLocaleDateString([], { day: 'numeric', month: 'short' })
export const dayTime = (t: number) => `${day(t)}, ${time(t)}`

/** "3 min ago", "2 h ago", "4 days ago"; a date once it is more than a week old. */
export function ago(t: number, now = Date.now() / 1000): string {
  const s = Math.max(0, now - t)
  if (s < 90) return 'just now'
  if (s < 3600) return `${Math.round(s / 60)} min ago`
  if (s < 86400) return `${Math.round(s / 3600)} h ago`
  if (s < 7 * 86400) return `${Math.round(s / 86400)} day${Math.round(s / 86400) === 1 ? '' : 's'} ago`
  return day(t)
}

/** Seconds as m:ss or h:mm:ss (video positions). */
export function hms(s: number | null | undefined): string {
  if (s == null) return ''
  s = Math.round(s)
  const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), x = s % 60
  return (h ? `${h}:${String(m).padStart(2, '0')}` : String(m)) + ':' + String(x).padStart(2, '0')
}

/** "in 1 h 12 min", "in 5 min", "any moment now". */
export function until(t: number, now = Date.now() / 1000): string {
  const s = Math.max(0, Math.round(t - now))
  if (s <= 0) return 'any moment now'
  const h = Math.floor(s / 3600), m = Math.max(1, Math.floor((s % 3600) / 60))
  return `in ${h ? `${h} h ` : ''}${m} min`
}

export const plural = (n: number, one: string, many = one + 's') => `${n} ${n === 1 ? one : many}`
export const stamp = (s: string | null | undefined) => String(s ?? '').replace('T', ' ').slice(0, 16)
export const sentence = (s: string) => (s ? s.charAt(0).toUpperCase() + s.slice(1) : s)
export const num = (n: number | null | undefined, digits = 1) => (n == null ? '–' : String(Math.round(n * 10 ** digits) / 10 ** digits))

export function regionName(code: string): string {
  try {
    return new Intl.DisplayNames(['en'], { type: 'region' }).of(code) ?? code
  } catch {
    return code
  }
}

/** localStorage that never throws (private windows, blocked storage). */
export const store = {
  get(k: string): string | null {
    try {
      return localStorage.getItem(k)
    } catch {
      return null
    }
  },
  set(k: string, v: string) {
    try {
      localStorage.setItem(k, v)
    } catch {
      /* not available */
    }
  },
  json<T>(k: string, fallback: T): T {
    try {
      const v = localStorage.getItem(k)
      return v ? (JSON.parse(v) as T) : fallback
    } catch {
      return fallback
    }
  },
}
