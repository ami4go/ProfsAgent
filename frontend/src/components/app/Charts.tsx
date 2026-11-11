// The app's two charts. Both follow the same rules: thin marks, a 2px gap in the surface colour between touching marks,
// a legend whenever there is more than one series, values on hover and on keyboard focus, and never colour alone.
import { useLayoutEffect, useRef, useState } from 'react'
import { cn } from '@/lib/cn'
import { WAY_NAME, WAY_ORDER, type TimePart, type Way } from '@/lib/delivery'
import type { CoCard } from '@/lib/types'
import { Tip } from '@/components/ui'

// ------------------------------------------------------------------ the class-time bar: one lecture, split into its parts
const WAY_FILL: Record<Way, string> = { slides: 'bg-way-slides', video: 'bg-way-video', nlm: 'bg-way-nlm', inclass: 'bg-way-inclass', sim: 'bg-way-inclass hatch-45', quiz: 'bg-way-quiz' }

const describe = (parts: TimePart[]) => parts.map((p) => `${p.minutes} min ${WAY_NAME[p.way]}${p.pre ? ' (before class)' : ''}`).join(', ')

export function ClassTimeBar({ parts, tall, className }: { parts: TimePart[] | null; tall?: boolean; className?: string }) {
  const ref = useRef<HTMLDivElement>(null)
  const [width, setWidth] = useState(0)
  useLayoutEffect(() => {
    if (!tall || !ref.current) return
    const el = ref.current
    const ro = new ResizeObserver(() => setWidth(el.clientWidth))
    ro.observe(el)
    setWidth(el.clientWidth)
    return () => ro.disconnect()
  }, [tall])

  if (!parts || !parts.length) {
    return <div role="img" aria-label="No time plan yet" title="No time plan yet: it appears once learning resources are found for this lecture"
      className={cn('w-full rounded-full border border-dashed border-line-strong', tall ? 'h-7 rounded-md' : 'h-2', className)} />
  }
  const total = parts.reduce((s, p) => s + Math.max(1, p.minutes), 0)
  if (!tall) {
    return (
      <div role="img" aria-label={`How the class time is spent: ${describe(parts)}`} title={describe(parts)} className={cn('flex h-2 w-full gap-[2px] overflow-hidden rounded-full', className)}>
        {parts.map((p, i) => <span key={i} className={cn('h-full min-w-[3px]', WAY_FILL[p.way], p.pre && 'hatch-135')} style={{ flex: Math.max(1, p.minutes) }} />)}
      </div>
    )
  }
  return (
    <div ref={ref} role="list" aria-label={`How the class time is spent: ${describe(parts)}`} className={cn('flex h-7 w-full gap-[2px]', className)}>
      {parts.map((p, i) => {
        const text = `${WAY_NAME[p.way]} · ${p.minutes}`
        const px = (width - 2 * (parts.length - 1)) * (Math.max(1, p.minutes) / total)
        const fits = px >= text.length * 6.4 + 16
        return (
          <Tip key={i} label={<><b className="font-semibold">{p.minutes} min</b> · {WAY_NAME[p.way]}{p.pre ? ', watched before class' : ''}<br /><span className="text-ink-2">{p.title}</span></>}>
            <div role="listitem" tabIndex={0} aria-label={`${p.title}: ${p.minutes} minutes, ${WAY_NAME[p.way]}${p.pre ? ', before class' : ''}`}
              className={cn('flex h-full min-w-[4px] items-center rounded-[4px] px-2 text-xs font-semibold text-white outline-offset-2 transition-[filter] hover:brightness-125 focus-visible:brightness-125', WAY_FILL[p.way], p.pre && 'hatch-135')}
              style={{ flex: Math.max(1, p.minutes) }}>
              {fits && <span className="truncate [text-shadow:0_1px_1px_rgb(0_0_0/0.35)]">{text}</span>}
            </div>
          </Tip>
        )
      })}
    </div>
  )
}

/** Names the colours the bars on screen use (only those), in a fixed order. */
export function WayLegend({ ways, pre, className }: { ways: Way[]; pre?: boolean; className?: string }) {
  const used = WAY_ORDER.filter((w) => ways.includes(w))
  if (!used.length) return null
  return (
    <ul aria-label="Legend" className={cn('flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-ink-2', className)}>
      {used.map((w) => <li key={w} className="flex items-center gap-1.5"><span aria-hidden className={cn('size-2.5 rounded-[3px]', WAY_FILL[w])} />{WAY_NAME[w]}</li>)}
      {pre && <li className="flex items-center gap-1.5"><span aria-hidden className="size-2.5 rounded-[3px] bg-ink-3 hatch-135" />Before class</li>}
    </ul>
  )
}

// ------------------------------------------------------------------ the CO–PO mapping matrix: a heat table
const HEAT = ['', 'bg-heat-1 text-white', 'bg-heat-2 text-white', 'bg-heat-3 text-[#0b0d12]']
const STRENGTH = ['', 'low', 'medium', 'high']

/** Course outcomes against programme outcomes. Each cell prints its strength (1–3); the colour only repeats it. */
export function CoPoMatrix({ cos }: { cos: CoCard[] }) {
  const cols: { key: string; programme: string; short: string; text: string }[] = []
  for (const c of cos) for (const p of c.pos) {
    const key = `${p.programme}|${p.short}`
    if (!cols.some((x) => x.key === key)) cols.push({ key, programme: p.programme, short: p.short, text: p.text })
  }
  if (!cols.length) return <p className="text-base text-ink-3">No programme outcomes are mapped yet.</p>
  const order = [...new Set(cols.map((c) => c.programme))]
  cols.sort((a, b) => order.indexOf(a.programme) - order.indexOf(b.programme) || a.short.localeCompare(b.short, undefined, { numeric: true }))
  const groups = order.map((p) => ({ programme: p, n: cols.filter((c) => c.programme === p).length }))
  return (
    <div>
      <div role="region" aria-label="Course outcomes mapped to programme outcomes" tabIndex={0} className="overflow-x-auto rounded-lg border border-line">
        <table className="border-separate border-spacing-0 text-xs">
          <caption className="sr-only">Strength of each course outcome's support for each programme outcome, from 1 (low) to 3 (high)</caption>
          <thead>
            <tr>
              <th scope="col" rowSpan={2} className="sticky left-0 z-10 border-b border-r border-line bg-surface-2 px-3 py-2 text-left label-caps">Outcome</th>
              {groups.map((g) => <th key={g.programme} scope="colgroup" colSpan={g.n} className="border-b border-l border-line bg-surface-2 px-2 py-1.5 text-left text-xs font-semibold whitespace-nowrap text-ink-1 first:border-l-0">{g.programme}</th>)}
            </tr>
            <tr>
              {cols.map((c, i) => (
                <th key={c.key} scope="col" title={c.text} className={cn('border-b border-line bg-surface-2 px-1 py-1.5 text-center font-mono text-2xs font-medium text-ink-3', i > 0 && cols[i - 1].programme !== c.programme && 'border-l')}>
                  {c.short}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {cos.map((co) => (
              <tr key={co.id}>
                <th scope="row" title={co.statement} className="sticky left-0 z-10 whitespace-nowrap border-b border-r border-line bg-surface-1 px-3 py-1.5 text-left font-mono text-xs font-semibold text-ink-1">{co.id}</th>
                {cols.map((c, i) => {
                  const m = co.pos.find((p) => `${p.programme}|${p.short}` === c.key)
                  const s = m?.strength ?? 0
                  return (
                    <td key={c.key} className={cn('border-b border-line p-[2px] text-center', i > 0 && cols[i - 1].programme !== c.programme && 'border-l')}>
                      {s ? (
                        <Tip label={<><b className="font-semibold">{co.id} → {c.programme} {c.short}</b> · strength {s} ({STRENGTH[s]})<br /><span className="text-ink-2">{c.text}</span></>}>
                          <span tabIndex={0} className={cn('flex h-7 min-w-7 items-center justify-center rounded-[4px] font-semibold tnum transition-[filter] hover:brightness-125 focus-visible:brightness-125', HEAT[s])}>{s}</span>
                        </Tip>
                      ) : <span aria-label="not mapped" className="flex h-7 min-w-7 items-center justify-center text-ink-4">·</span>}
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <ul aria-label="Legend" className="mt-2.5 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-ink-2">
        <li className="text-ink-3">Strength of support</li>
        {[1, 2, 3].map((s) => <li key={s} className="flex items-center gap-1.5"><span aria-hidden className={cn('flex size-4 items-center justify-center rounded-[3px] text-2xs font-semibold', HEAT[s])}>{s}</span>{STRENGTH[s]}</li>)}
        <li className="flex items-center gap-1.5 text-ink-3"><span aria-hidden>·</span>not mapped</li>
      </ul>
    </div>
  )
}

/** A ranked list of bars: one hue, the value printed at the tip. Used for assessment weights and marks per outcome. */
export function BarList({ rows, max, unit = '%', label }: { rows: { name: string; value: number; note?: React.ReactNode }[]; max?: number; unit?: string; label: string }) {
  const top = max ?? Math.max(1, ...rows.map((r) => r.value))
  return (
    <ul aria-label={label} className="space-y-2">
      {rows.map((r) => (
        <li key={r.name} className="grid grid-cols-[minmax(6rem,11rem)_1fr] items-center gap-3 text-sm">
          <span className="truncate text-ink-2" title={r.name}>{r.name}</span>
          <span className="flex items-center gap-2.5">
            <span className="h-3.5 rounded-r-[4px] bg-way-slides transition-[width] duration-500 ease-out" style={{ width: `calc(${(100 * r.value) / top}% - 3.5rem)`, minWidth: r.value ? 3 : 0 }} />
            <span className="whitespace-nowrap font-medium text-ink-1 tnum">{Math.round(r.value * 10) / 10}{unit}</span>
            {r.note}
          </span>
        </li>
      ))}
    </ul>
  )
}
