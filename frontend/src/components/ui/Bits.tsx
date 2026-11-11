// Small pieces: tables, disclosure, links, files to download, stars, keys, menus.
import * as M from '@radix-ui/react-dropdown-menu'
import { useState, type HTMLAttributes, type MouseEvent, type ReactNode, type TdHTMLAttributes, type ThHTMLAttributes } from 'react'
import { ArrowUpRight, ChevronRight, Download, FileSpreadsheet, FileText, Presentation, Star } from 'lucide-react'
import { download, problemOf } from '@/lib/api'
import { cn } from '@/lib/cn'
import { toast } from '@/lib/toast'

// ---- tables: a caption for screen readers, sideways scrolling on small screens, numbers aligned
export function DataTable({ caption, children, className }: { caption: string; children: ReactNode; className?: string }) {
  return (
    <div role="region" aria-label={caption} tabIndex={0} className={cn('overflow-x-auto rounded-lg border border-line', className)}>
      <table className="w-full border-collapse text-base">
        <caption className="sr-only">{caption}</caption>
        {children}
      </table>
    </div>
  )
}
export const Th = ({ className, ...rest }: ThHTMLAttributes<HTMLTableCellElement>) => (
  <th scope="col" className={cn('label-caps whitespace-nowrap border-b border-line bg-white/[0.025] px-3.5 py-2 text-left', className)} {...rest} />
)
export const Td = ({ className, ...rest }: TdHTMLAttributes<HTMLTableCellElement>) => (
  <td className={cn('border-b border-line px-3.5 py-2.5 align-top text-ink-2 [tr:last-child>&]:border-b-0', className)} {...rest} />
)
export const Tr = ({ className, ...rest }: HTMLAttributes<HTMLTableRowElement>) => <tr className={cn('transition-colors hover:bg-white/[0.02]', className)} {...rest} />

/** Detail that opens on demand. A native <details>, so it works with keyboards and find-in-page. */
export function Disclosure({ summary, children, defaultOpen, className, onToggle }: { summary: ReactNode; children: ReactNode; defaultOpen?: boolean; className?: string; onToggle?: (open: boolean) => void }) {
  return (
    <details className={cn('group/d', className)} open={defaultOpen} onToggle={(e) => onToggle?.((e.target as HTMLDetailsElement).open)}>
      <summary className="inline-flex list-none items-center gap-1.5 rounded text-sm font-medium text-ink-3 hover:text-ink-1">
        <ChevronRight aria-hidden className="size-3.5 transition-transform duration-150 group-open/d:rotate-90" />
        {summary}
      </summary>
      <div className="mt-2">{children}</div>
    </details>
  )
}

/** A link that leaves the app: it opens in a new tab and says so. */
export function Ext({ href, children, className, quiet }: { href?: string | null; children: ReactNode; className?: string; quiet?: boolean }) {
  if (!href) return <span className={className}>{children}</span>
  return (
    <a href={href} target="_blank" rel="noopener noreferrer"
      className={cn('underline underline-offset-[3px] transition-colors', quiet ? 'text-ink-1 decoration-white/20 hover:decoration-white/60' : 'text-iris-300 decoration-iris-line hover:text-iris-200 hover:decoration-current', className)}>
      <span>{children}</span>
      <ArrowUpRight aria-hidden className="ml-0.5 inline-block size-3 align-baseline opacity-70" />
      <span className="sr-only"> (opens in a new tab)</span>
    </a>
  )
}

const fileIcon = (name: string) => (/\.xlsx?$|\.csv$|excel/i.test(name) ? <FileSpreadsheet /> : /\.pptx?$|powerpoint/i.test(name) ? <Presentation /> : <FileText />)
/** A file the professor can take away: what it is, its format, one click. It says so while the file is being made,
 *  and when it cannot be made, instead of opening an error page. */
export function FileLink({ href, name, meta }: { href: string; name: string; meta: string; newTab?: boolean }) {
  const [busy, setBusy] = useState(false)
  const get = async (e: MouseEvent) => {
    e.preventDefault()
    if (busy) return
    setBusy(true)
    try {
      await download(href, name)
    } catch (err) {
      toast.error(`“${name}” could not be prepared. ${problemOf(err, '')}`.trim())
    } finally {
      setBusy(false)
    }
  }
  return (
    <a href={href} onClick={get} aria-busy={busy}
      className="group flex items-center gap-3 rounded-lg border border-line bg-surface-2/60 px-3 py-2.5 no-underline transition-colors hover:border-line-strong hover:bg-surface-2">
      <span aria-hidden className="flex size-9 shrink-0 items-center justify-center rounded-md bg-white/[0.05] text-ink-2 [&_svg]:size-[18px]">{fileIcon(meta + name)}</span>
      <span className="min-w-0 flex-1">
        <span className="block text-base font-medium leading-snug text-ink-1">{name}</span>
        <span className="block text-xs text-ink-3">{busy ? 'Preparing…' : meta}</span>
      </span>
      {busy ? <span className="spinner text-iris-300" aria-hidden /> : <Download aria-hidden className="size-4 shrink-0 text-ink-3 transition-colors group-hover:text-iris-300" />}
    </a>
  )
}

/** One to five stars. Each star is a button; the chosen one is announced. */
export function Stars({ value, onChange, label }: { value: number; onChange: (n: number) => void; label: string }) {
  return (
    <span role="group" aria-label={label} className="inline-flex">
      {[1, 2, 3, 4, 5].map((n) => (
        <button key={n} type="button" aria-label={`${n} of 5`} aria-pressed={value === n} onClick={() => onChange(n)}
          className="flex size-8 cursor-pointer items-center justify-center rounded transition-transform duration-100 hover:scale-110 active:scale-95">
          <Star className={cn('size-[18px] transition-colors', value >= n ? 'fill-amber-400 text-amber-400' : 'text-ink-4')} />
        </button>
      ))}
    </span>
  )
}

export const Kbd = ({ children }: { children: ReactNode }) => (
  <kbd className="inline-flex h-5 min-w-5 items-center justify-center rounded border border-line-strong bg-white/[0.05] px-1 font-sans text-2xs font-medium text-ink-3">{children}</kbd>
)

/** A reference (regulation clause, ISBN, course code) in the mono face, so it reads as an identifier. */
export const Code = ({ children, className }: { children: ReactNode; className?: string }) => (
  <span className={cn('rounded bg-white/[0.06] px-1.5 py-px font-mono text-[0.8em] text-ink-2 [overflow-wrap:anywhere]', className)}>{children}</span>
)

export interface MenuItem { label: string; icon?: ReactNode; onSelect: () => void; danger?: boolean; disabled?: boolean }
/** A menu that opens from its trigger: arrow keys move, Enter chooses, Escape closes. */
export function Menu({ trigger, items, label }: { trigger: ReactNode; items: MenuItem[]; label: string }) {
  return (
    <M.Root>
      <M.Trigger asChild aria-label={label}>{trigger}</M.Trigger>
      <M.Portal>
        <M.Content align="end" sideOffset={6} className="z-[60] min-w-48 rounded-lg border border-line-strong glass-strong p-1 shadow-2 animate-fade-in">
          {items.map((it) => (
            <M.Item key={it.label} disabled={it.disabled} onSelect={it.onSelect}
              className={cn('flex h-8 cursor-pointer select-none items-center gap-2 rounded-md px-2.5 text-sm outline-none data-[disabled]:opacity-40 [&_svg]:size-3.5',
                it.danger ? 'text-rose-300 data-[highlighted]:bg-rose-soft' : 'text-ink-1 data-[highlighted]:bg-white/[0.08]')}>
              {it.icon}
              {it.label}
            </M.Item>
          ))}
        </M.Content>
      </M.Portal>
    </M.Root>
  )
}

/** A quiet heading over a group of cards or rows. */
export const SectionTitle = ({ children, aside, className }: { children: ReactNode; aside?: ReactNode; className?: string }) => (
  <div className={cn('flex flex-wrap items-baseline justify-between gap-2', className)}>
    <h2 className="text-lg font-semibold text-ink-1">{children}</h2>
    {aside && <div className="text-sm text-ink-3">{aside}</div>}
  </div>
)
