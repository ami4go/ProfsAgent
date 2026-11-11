// A small Markdown reader for the documents the pipeline writes (guest-lecture kits, NotebookLM packs): headings,
// lists, bold and links. Everything is rendered as React nodes, so nothing in the text can become markup.
import type { ReactNode } from 'react'

function inline(t: string, key: string): ReactNode[] {
  const out: ReactNode[] = []
  const re = /\*\*(.+?)\*\*|\[([^\]]+)\]\((https?:[^)\s]+)\)/g
  let last = 0, m: RegExpExecArray | null, i = 0
  while ((m = re.exec(t))) {
    if (m.index > last) out.push(t.slice(last, m.index))
    out.push(m[1] != null ? <b key={`${key}-${i++}`}>{m[1]}</b> : <a key={`${key}-${i++}`} href={m[3]} target="_blank" rel="noopener noreferrer">{m[2]}</a>)
    last = m.index + m[0].length
  }
  if (last < t.length) out.push(t.slice(last))
  return out
}

export function Markdown({ source }: { source: string }) {
  const blocks: ReactNode[] = []
  let para: string[] = []
  let list: { type: 'ul' | 'ol'; items: { text: string; sub: string[] }[] } | null = null
  let k = 0
  const flush = () => {
    if (para.length) { blocks.push(<p key={k++}>{inline(para.join(' '), `p${k}`)}</p>); para = [] }
    if (list) {
      const L = list.type
      blocks.push(<L key={k++}>{list.items.map((it, i) => <li key={i}>{inline(it.text, `l${k}-${i}`)}{it.sub.map((s, j) => <span key={j} className="block text-sm text-ink-3">{inline(s, `s${k}-${i}-${j}`)}</span>)}</li>)}</L>)
      list = null
    }
  }
  for (const ln of source.split('\n')) {
    let m: RegExpMatchArray | null
    if (/^#\s/.test(ln)) { flush(); blocks.push(<h1 key={k++}>{inline(ln.slice(2), `h${k}`)}</h1>) }
    else if (/^##\s/.test(ln)) { flush(); blocks.push(<h2 key={k++}>{inline(ln.slice(3), `h${k}`)}</h2>) }
    else if (/^###\s/.test(ln)) { flush(); blocks.push(<h3 key={k++}>{inline(ln.slice(4), `h${k}`)}</h3>) }
    else if ((m = ln.match(/^\s*-\s+(.*)/))) { if (para.length || list?.type !== 'ul') flush(); list ??= { type: 'ul', items: [] }; list.items.push({ text: m[1], sub: [] }) }
    else if ((m = ln.match(/^\d+\.\s+(.*)/))) { if (para.length || list?.type !== 'ol') flush(); list ??= { type: 'ol', items: [] }; list.items.push({ text: m[1], sub: [] }) }
    else if (/^\s{2,}\S/.test(ln) && list?.items.length) list.items[list.items.length - 1].sub.push(ln.trim())
    else if (!ln.trim()) flush()
    else para.push(ln.trim())
  }
  flush()
  return <div className="prose-app">{blocks}</div>
}
