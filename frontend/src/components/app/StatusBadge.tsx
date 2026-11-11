import { Check, CircleAlert, Hourglass, Pause, Square, UserRound } from 'lucide-react'
import { Badge, Spinner } from '@/components/ui'
import { STATUS, statusLabel } from '@/lib/status'
import type { RunStatus, RunSummary } from '@/lib/types'

const icon: Record<RunStatus, React.ReactNode> = {
  queued: <Hourglass aria-hidden />,
  running: <Spinner className="!size-3 !border-[1.5px]" />,
  waiting: <UserRound aria-hidden />,
  paused: <Pause aria-hidden />,
  error: <CircleAlert aria-hidden />,
  done: <Check aria-hidden />,
  stopped: <Square aria-hidden />,
}

/** Where a course stands, in the app's fixed vocabulary. */
export function RunStatusBadge({ run }: { run: Pick<RunSummary, 'status' | 'gate'> }) {
  const s = STATUS[run.status] ?? { tone: 'neutral' as const }
  return <Badge tone={s.tone} icon={icon[run.status]}>{statusLabel(run)}</Badge>
}
