// The four checks of a course design as a rail: where the course is, what is behind it, what comes next.
import { Link } from 'react-router-dom'
import { Check, CircleAlert, Lock, Square, UserRound } from 'lucide-react'
import { cn } from '@/lib/cn'
import { GATES, GATE_ABOUT, GATE_NAME, GATE_SLUG, type StageState } from '@/lib/status'
import type { Gate } from '@/lib/types'
import { Spinner } from '@/components/ui'

const STATE_WORD: Record<StageState, string> = { approved: 'Approved', current: 'Needs you', working: 'ProfsAgent is working', problem: 'Needs attention', stopped: 'Stopped here', upcoming: 'Not started' }

function Mark({ state, n, size = 'md' }: { state: StageState; n: number; size?: 'sm' | 'md' }) {
  const box = size === 'sm' ? 'size-5 text-2xs [&_svg]:size-3' : 'size-7 text-xs [&_svg]:size-3.5'
  const cls = {
    approved: 'bg-mint-soft border-mint-line text-mint-300',
    current: 'bg-amber-soft border-amber-line text-amber-300',
    working: 'bg-iris-soft border-iris-line text-iris-300',
    problem: 'bg-rose-soft border-rose-line text-rose-300',
    stopped: 'bg-white/[0.06] border-line-strong text-ink-2',
    upcoming: 'bg-transparent border-line-strong text-ink-4',
  }[state]
  return (
    <span aria-hidden className={cn('flex shrink-0 items-center justify-center rounded-full border font-semibold', box, cls)}>
      {state === 'approved' ? <Check strokeWidth={3} /> : state === 'current' ? <UserRound /> : state === 'working' ? <Spinner className="!size-3 !border-[1.5px]" /> : state === 'problem' ? <CircleAlert /> : state === 'stopped' ? <Square /> : n}
    </span>
  )
}

/** Compact: four marks in a row, for cards and lists. */
export function StageDots({ states }: { states: Record<Gate, StageState> }) {
  return (
    <ol className="flex items-center" aria-label="Design steps">
      {GATES.map((g, i) => (
        <li key={g} className="flex items-center">
          {i > 0 && <span aria-hidden className={cn('h-px w-4 sm:w-5', states[g] === 'upcoming' ? 'bg-line-strong' : 'bg-mint-line')} />}
          <span title={`${GATE_NAME[g]}: ${STATE_WORD[states[g]]}`}><Mark state={states[g]} n={i + 1} size="sm" /></span>
          <span className="sr-only">{GATE_NAME[g]}: {STATE_WORD[states[g]]}</span>
        </li>
      ))}
    </ol>
  )
}

/** Full: the stage navigation of the design workspace. Every step that has something to show is a link. */
export function StageNav({ rid, states, active, available, by }: {
  rid: string; states: Record<Gate, StageState>; active: Gate; available: Record<Gate, boolean>; by: Partial<Record<Gate, string>>
}) {
  return (
    <nav aria-label="Design steps">
      <ol className="flex gap-2 overflow-x-auto pb-1 lg:flex-col lg:gap-1 lg:overflow-visible lg:pb-0">
        {GATES.map((g, i) => {
          const st = states[g], on = g === active, can = available[g]
          const body = (
            <>
              <Mark state={st} n={i + 1} />
              <span className="min-w-0 flex-1">
                <span className="flex items-center gap-1.5 text-base font-medium text-ink-1">{GATE_NAME[g]}{!can && <Lock aria-hidden className="size-3 text-ink-4" />}</span>
                <span className={cn('block truncate text-xs', st === 'current' ? 'text-amber-300' : st === 'approved' ? 'text-ink-3' : st === 'working' ? 'text-iris-300' : st === 'problem' ? 'text-rose-300' : 'text-ink-4')}>
                  {st === 'approved' && by[g] ? `Approved by ${by[g]}` : STATE_WORD[st]}
                </span>
              </span>
            </>
          )
          const cls = cn('relative flex min-w-[11.5rem] items-center gap-3 rounded-lg border px-3 py-2.5 text-left no-underline transition-colors duration-150 lg:min-w-0',
            on ? 'border-line-strong bg-surface-2 shadow-1' : 'border-transparent hover:bg-white/[0.04]', !can && 'cursor-not-allowed opacity-60 hover:bg-transparent')
          return (
            <li key={g} className="shrink-0 lg:shrink">
              {can ? <Link to={`/courses/${encodeURIComponent(rid)}/design/${GATE_SLUG[g]}`} aria-current={on ? 'step' : undefined} title={GATE_ABOUT[g]} className={cls}>{body}</Link>
                : <span aria-disabled="true" title="Nothing to show yet" className={cls}>{body}</span>}
            </li>
          )
        })}
      </ol>
    </nav>
  )
}
