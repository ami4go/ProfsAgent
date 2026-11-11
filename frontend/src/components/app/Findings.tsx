// Validation findings: what the checks found, in a sentence each, grouped so that twelve of the same read as one line.
import { CircleAlert, CircleCheck, ShieldCheck, TriangleAlert, UserRound, Wrench } from 'lucide-react'
import { Badge, Callout, Card, Code, Disclosure } from '@/components/ui'
import { plural } from '@/lib/format'
import type { Issue, ProblemGroup, Problems } from '@/lib/types'

function Group({ g }: { g: ProblemGroup }) {
  const first = g.items[0]
  const yours = first.who === 'Needs your decision'
  const line = g.plain || first.message
  return (
    <li className="flex gap-3 border-t border-line py-3 first:border-t-0 first:pt-0 last:pb-0">
      <CircleAlert aria-hidden className="mt-0.5 size-4 shrink-0 text-rose-400" />
      <div className="min-w-0 flex-1">
        <p className="text-base text-ink-1">
          {line}
          {g.items.length > 1 && <span className="ml-2 rounded-full bg-rose-soft px-1.5 py-px text-xs font-semibold text-rose-300 tnum">{g.items.length}</span>}
        </p>
        <div className="mt-1.5 flex flex-wrap items-center gap-2">
          {first.who && <Badge tone={yours ? 'amber' : 'neutral'} icon={yours ? <UserRound aria-hidden /> : <Wrench aria-hidden />}>{first.who}</Badge>}
          {g.items.length === 1 && first.where && <span className="text-xs text-ink-3">In {first.where}</span>}
        </div>
        {(g.items.length > 1 || g.plain) && (
          <Disclosure className="mt-2" summary={g.items.length === 1 ? 'Show the detail' : `Show all ${g.items.length}`}>
            <ul className="space-y-1.5 border-l border-line pl-3">
              {g.items.map((x, i) => (
                <li key={i} className="text-sm text-ink-2">{x.message}{x.where && <span className="text-ink-3"> · {x.where}</span>}</li>
              ))}
            </ul>
            <p className="mt-2 text-xs text-ink-3">Check reference <Code>{g.code}</Code></p>
          </Disclosure>
        )}
      </div>
    </li>
  )
}

/** The panel at the top of a check: what stands between this step and approval. */
export function Findings({ problems, canEdit }: { problems?: Problems; canEdit: boolean }) {
  const p = problems
  if (!p || (!p.items.length && !p.problem)) {
    return (
      <Callout tone="mint" icon={<ShieldCheck className="text-mint-400" />} title="No open problems">
        Every rule check passed for this step.{p && p.warnings > 0 && <> {plural(p.warnings, 'smaller note')} {p.warnings === 1 ? 'does' : 'do'} not block approval; they are listed in the full proposal.</>}
      </Callout>
    )
  }
  return (
    <Card className={p.blocked ? 'border-rose-line' : 'border-amber-line'}>
      <div className="flex flex-wrap items-start justify-between gap-3 px-5 pt-4">
        <div className="flex items-start gap-3">
          <span aria-hidden className={`mt-0.5 flex size-7 items-center justify-center rounded-md ${p.blocked ? 'bg-rose-soft text-rose-300' : 'bg-amber-soft text-amber-300'}`}><TriangleAlert className="size-4" /></span>
          <div>
            <h2 className="text-md font-semibold text-ink-1">{p.blocked ? plural(p.errors, 'open problem') : 'Things to look at'}</h2>
            <p className="mt-0.5 text-sm text-ink-3">
              {p.blocked ? (canEdit ? 'Fix them with Edit on the part concerned, or approve with a reason that is recorded on the course sheet.' : 'Approve with a recorded reason, or stop the run.') : 'None of these block approval.'}
            </p>
          </div>
        </div>
        {p.warnings > 0 && <Badge tone="neutral">{plural(p.warnings, 'smaller note')}</Badge>}
      </div>
      <ul className="px-5 pb-4 pt-3">{(p.groups ?? []).map((g) => <Group key={g.code} g={g} />)}</ul>
      {p.problem && <p className="border-t border-line px-5 py-3 text-sm text-amber-300">{p.problem}</p>}
    </Card>
  )
}

// Technical notes on programme-outcome strengths are for the team; a professor sees errors and plain warnings.
const isMappingNote = (i: Issue) => /^VCOPO/.test(i.code) || (i.code === 'V23' && i.severity !== 'error')

/** Findings attached to one item (a course outcome, a slide deck). */
export function IssueList({ issues, showCodes }: { issues: Issue[]; showCodes?: boolean }) {
  const list = issues.filter((i) => !isMappingNote(i))
  if (!list.length) return null
  return (
    <ul className="mt-3 space-y-1.5">
      {list.map((i, k) => {
        const err = i.severity === 'error'
        return (
          <li key={k} title={i.code} className={`flex gap-2 rounded-md border px-2.5 py-1.5 text-sm ${err ? 'border-rose-line bg-rose-soft text-rose-300' : 'border-amber-line bg-amber-soft text-amber-300'}`}>
            {err ? <CircleAlert aria-hidden className="mt-0.5 size-3.5 shrink-0" /> : <TriangleAlert aria-hidden className="mt-0.5 size-3.5 shrink-0" />}
            <span className="min-w-0">{i.message}{showCodes && <> <Code>{i.code}</Code></>}</span>
          </li>
        )
      })}
    </ul>
  )
}

export const ChecksPassed = ({ children }: { children: React.ReactNode }) => (
  <p className="mt-3 flex items-center gap-2 text-sm text-mint-300"><CircleCheck aria-hidden className="size-4" />{children}</p>
)
