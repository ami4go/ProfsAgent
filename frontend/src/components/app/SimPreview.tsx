// The simulation window. A simulation runs in a sandboxed frame (its own origin, no network) and reports its setup;
// the professor can keep that setup as the class example students start from.
import { useEffect, useRef, useState, useSyncExternalStore } from 'react'
import * as D from '@radix-ui/react-dialog'
import { useQueryClient } from '@tanstack/react-query'
import { ArrowUpRight, RotateCw, X } from 'lucide-react'
import { api, deliveryUrl, enc, problemOf } from '@/lib/api'
import { keys } from '@/lib/queries'
import { toast } from '@/lib/toast'
import { Badge, Button } from '@/components/ui'

export interface SimOpen {
  id: string
  title: string
  state?: string
  lecture?: string
  student?: boolean
  example?: { state: string; summary?: string } | null
  /** set when opened from a lecture page: where a class example would be saved */
  ctx?: { rid: string; lid: string; canSave: boolean; example: { state: string; summary?: string } | null } | null
}

let current: SimOpen | null = null
const listeners = new Set<() => void>()
const emit = () => listeners.forEach((l) => l())
export function openSim(o: SimOpen) { current = o; emit() }
const close = () => { current = null; emit() }

const pageUrl = (id: string, state?: string, fresh?: number) => `/api/simulations/${enc(id)}/page${fresh ? `?r=${fresh}` : ''}${state ? `#${state}` : ''}`

export function SimPreviewHost() {
  const o = useSyncExternalStore((l) => { listeners.add(l); return () => listeners.delete(l) }, () => current)
  return o ? <SimWindow key={o.id + (o.lecture ?? '')} o={o} /> : null
}

function SimWindow({ o }: { o: SimOpen }) {
  const qc = useQueryClient()
  const frame = useRef<HTMLIFrameElement>(null)
  const [nonce, setNonce] = useState(() => Date.now())
  const [cur, setCur] = useState<{ state: string; summary: string } | null>(null)
  const [example, setExample] = useState(o.ctx?.example ?? null)
  const [start, setStart] = useState(o.state ?? '')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    const onMsg = (ev: MessageEvent) => {
      if (!frame.current || ev.source !== frame.current.contentWindow) return
      const d = ev.data as { type?: string; state?: unknown; summary?: unknown } | null
      if (!d || d.type !== 'profsagent-sim-state' || typeof d.state !== 'string' || d.state.length > 6000) return
      setCur({ state: d.state, summary: String(d.summary ?? '').slice(0, 300) })
    }
    window.addEventListener('message', onMsg)
    return () => window.removeEventListener('message', onMsg)
  }, [])

  const same = !!example && cur?.state === example.state
  const canSave = !!o.ctx?.canSave && !o.student
  async function save() {
    if (!o.ctx || !cur) return
    setSaving(true)
    try {
      await api.post(deliveryUrl(o.ctx.rid, `/simulations/${enc(o.ctx.lid)}/class-example`), { sim: o.id, state: cur.state, summary: cur.summary })
      setExample({ state: cur.state, summary: cur.summary })
      setStart(cur.state)
      toast.success('Saved. Students start from this setup.')
      qc.invalidateQueries({ queryKey: keys.delivery(o.ctx.rid) })
    } catch (e) {
      toast.error(problemOf(e, 'Could not save'))
    } finally {
      setSaving(false)
    }
  }

  let line: React.ReactNode = null
  if (o.student) line = o.example ? <>Starts at the class example: {o.example.summary || 'set by your professor'}</> : null
  else if (canSave) line = (
    <>
      <span><b className="font-semibold text-ink-1">Class example:</b> {example ? example.summary || 'saved' : 'none yet, so students start from the default'}</span>
      <span><b className="font-semibold text-ink-1">On screen now:</b> {cur == null ? 'waiting for the simulation…' : cur.summary || 'your setup'} {same && <Badge tone="mint">this is the class example</Badge>}</span>
    </>
  )
  else if (o.ctx) line = <>This simulation cannot keep a class example yet, so students start from its default.</>

  return (
    <D.Root open onOpenChange={(v) => !v && close()}>
      <D.Portal>
        <D.Overlay className="fixed inset-0 z-[65] bg-black/70 backdrop-blur-[3px] data-[state=open]:animate-fade-in" />
        <D.Content className="fixed inset-2 z-[65] mx-auto flex max-w-[92rem] flex-col overflow-hidden rounded-2xl border border-line-strong bg-surface-1 shadow-3 outline-none data-[state=open]:animate-rise sm:inset-4">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line px-4 py-2.5">
            <div className="min-w-0">
              <D.Title className="truncate text-md font-semibold text-ink-1">{o.title}</D.Title>
              <D.Description className="text-xs text-ink-3">{o.lecture ? `Lecture ${o.lecture} · ` : ''}Simulation, running in a sandbox</D.Description>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              {canSave && <Button size="sm" variant="primary" disabled={cur == null || same} loading={saving} onClick={save}>Use this setup as the class example</Button>}
              <Button size="sm" icon={<RotateCw aria-hidden />} onClick={() => { setCur(null); setNonce(Date.now()) }}>Start over</Button>
              <Button size="sm" href={pageUrl(o.id, cur?.state ?? start)} external iconRight={<ArrowUpRight aria-hidden />}>New tab</Button>
              <D.Close asChild><Button size="sm" variant="ghost" icon={<X aria-hidden />}>Close</Button></D.Close>
            </div>
          </div>
          {line && <div className="flex flex-col gap-0.5 border-b border-line bg-white/[0.025] px-4 py-2 text-sm text-ink-2">{line}</div>}
          <iframe ref={frame} key={nonce} title={o.title} sandbox="allow-scripts allow-downloads" src={pageUrl(o.id, start, nonce)} className="min-h-0 w-full flex-1 border-0 bg-[#0f1117]" />
        </D.Content>
      </D.Portal>
    </D.Root>
  )
}
