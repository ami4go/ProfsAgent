// One small fetch wrapper for the app's JSON API. A failed request throws ApiError, which carries the server's own
// words: `problem` (a sentence to show) or `errors` (messages by field).

export class ApiError extends Error {
  status: number
  problem: string
  errors: Record<string, string>
  constructor(status: number, data: unknown) {
    const d = (data ?? {}) as { problem?: string; detail?: unknown; errors?: Record<string, string> }
    const problem = d.problem || (typeof d.detail === 'string' ? d.detail : '') ||
      (status === 0 ? 'The app is not responding. Is it still running on this laptop?' : status >= 500 ? 'The app stopped on a problem on its side. The detail is in the terminal where it runs.' : '')
    super(problem || `Request failed (${status})`)
    this.status = status
    this.problem = problem
    this.errors = d.errors ?? {}
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response
  try {
    res = await fetch(path, init)
  } catch {
    throw new ApiError(0, null)
  }
  let data: unknown = null
  try {
    data = await res.json()
  } catch {
    /* an empty or non-JSON body */
  }
  if (!res.ok) throw new ApiError(res.status, data)
  return data as T
}

const json = (method: string, body?: unknown): RequestInit => ({
  method,
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(body ?? {}),
})

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) => request<T>(path, json('POST', body)),
  put: <T>(path: string, body?: unknown) => request<T>(path, json('PUT', body)),
  del: <T>(path: string) => request<T>(path, { method: 'DELETE' }),
  upload: <T>(path: string, form: FormData) => request<T>(path, { method: 'POST', body: form }),
}

/** The sentence to show for any thrown error. */
export const problemOf = (e: unknown, fallback = 'Something went wrong') =>
  e instanceof ApiError ? e.problem || Object.values(e.errors)[0] || fallback : fallback

export const enc = encodeURIComponent
export const runUrl = (rid: string, rest = '') => `/api/runs/${enc(rid)}${rest}`
export const deliveryUrl = (rid: string, rest = '') => `/api/delivery/${enc(rid)}${rest}`

/** Fetch a file and hand it to the browser as a download; a failure throws ApiError instead of opening an error page. */
export async function download(href: string, fallbackName: string): Promise<void> {
  let res: Response
  try {
    res = await fetch(href)
  } catch {
    throw new ApiError(0, null)
  }
  if (!res.ok) {
    let data: unknown = null
    try { data = await res.json() } catch { /* not JSON */ }
    throw new ApiError(res.status, data)
  }
  const name = /filename\*?=(?:UTF-8'')?"?([^";]+)"?/i.exec(res.headers.get('content-disposition') ?? '')?.[1]
  const url = URL.createObjectURL(await res.blob())
  const a = Object.assign(document.createElement('a'), { href: url, download: name ? decodeURIComponent(name) : fallbackName })
  document.body.appendChild(a)
  a.click()
  a.remove()
  setTimeout(() => URL.revokeObjectURL(url), 10_000)
}
