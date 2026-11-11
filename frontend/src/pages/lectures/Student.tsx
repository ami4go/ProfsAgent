// What students see: only what the professor approved. Shown to the professor as a preview, with a rating per item.
import { Eye } from 'lucide-react'
import { api, deliveryUrl, enc } from '@/lib/api'
import { KINDS, USE_AS, simApproved, simsOf } from '@/lib/delivery'
import { hms } from '@/lib/format'
import { useDelivery } from '@/lib/queries'
import { problemOf } from '@/lib/api'
import type { DeliveryView, Lecture, Resource } from '@/lib/types'
import { Badge, Callout, Card, CardBody, EmptyState, Ext, Loading, Row, Stars, TextButton } from '@/components/ui'
import { openSim } from '@/components/app/SimPreview'
import { PageBody } from '@/components/app/Shell'
import { useCourse } from '../course/Layout'
import { NotApproved } from './Lectures'
import { useDeliveryAction } from './shared'

type Item = Partial<Resource> & { key: string; url: string; title: string; kindName: string }

function approvedItems(v: DeliveryView, lid: string): Item[] {
  const r = v.results[lid], out: Item[] = []
  if (r) for (const k of KINDS) for (const x of r.items[k.kind] ?? []) if (x.approved) out.push({ ...x, kindName: k.name.replace(/s$/, '') })
  for (const x of v.own?.[lid] ?? []) out.push({ key: x.url, url: x.url, title: x.title, kindName: (KINDS.find((k) => k.kind === x.kind)?.name ?? 'Reading').replace(/s$/, '') })
  return out
}

export function StudentPage() {
  const { run, rid } = useCourse()
  const approved = run.status === 'done'
  const { data: v, isLoading, error } = useDelivery(rid, approved)
  const act = useDeliveryAction(rid)
  if (!approved) return <NotApproved />
  if (isLoading) return <PageBody><Loading label="Loading the student view" /></PageBody>
  if (!v) return <PageBody><EmptyState title="The student view is not available">{problemOf(error)}</EmptyState></PageBody>
  const rows = v.lectures.map((l) => ({ l, items: approvedItems(v, l.id), sims: simsOf(v, l.id).items.filter(simApproved), slides: v.material?.[l.id]?.status === 'approved' }))
    .filter((x) => x.items.length || x.sims.length || x.slides)
  const rate = (l: Lecture, x: Item, n: number) => act(() => api.post(deliveryUrl(rid, '/rate'), { lid: l.id, key: x.key, title: x.title, rating: n }), 'Rating saved. Thank you.')
  return (
    <PageBody width="read">
      <Callout tone="iris" icon={<Eye className="text-iris-300" />} title="Preview: what students see">Only what you approved appears here. Nothing ProfsAgent suggested reaches students before your approval.</Callout>
      <header className="mt-8">
        <p className="label-caps mb-2">Learning resources by lecture</p>
        <h2 className="h-display text-3xl text-ink-1">{v.run.course}</h2>
      </header>
      {!rows.length && <EmptyState className="mt-6" title="Nothing has been released yet">Approve resources, slides or a simulation on a lecture page and they appear here.</EmptyState>}
      <div className="mt-6 space-y-4">
        {rows.map(({ l, items, sims, slides }) => (
          <Card key={l.id}>
            <div className="px-5 pt-4"><p className="text-sm text-ink-3">Week {l.week} · <span className="font-mono">{l.id}</span></p><h3 className="mt-0.5 text-lg font-semibold text-ink-1">{l.topic}</h3></div>
            <CardBody className="pt-3">
              {sims.map((i) => (
                <Row key={i.id}>
                  {i.external ? <Ext href={i.url} quiet className="font-medium">{i.title}</Ext>
                    : <TextButton className="!text-base !font-medium" onClick={() => openSim({ id: i.id, title: i.title, state: i.example?.state ?? '', lecture: l.id, student: true, example: i.example })}>{i.title}</TextButton>}
                  <p className="mt-1 flex flex-wrap items-center gap-2 text-sm text-ink-3"><Badge tone="iris">Simulation</Badge>{i.external && <Badge>{i.site_name}</Badge>}<span>{i.summary}</span></p>
                </Row>
              ))}
              {slides && <Row><a className="font-medium text-ink-1 underline decoration-white/20 underline-offset-[3px]" href={deliveryUrl(rid, `/material/${enc(l.id)}/file/slides.pptx`)}>Lecture slides (.pptx)</a><p className="mt-1"><Badge tone="iris">For class</Badge></p></Row>}
              {items.map((x) => {
                const seg = x.yt ? x.cover?.find((c) => c.segs.length) : undefined
                const rt = v.ratings?.[l.id]?.[x.key]
                return (
                  <Row key={x.key} aside={<div className="text-right"><Stars label={`Rate ${x.title}`} value={rt?.r ?? 0} onChange={(n) => rate(l, x, n)} /><p className="text-xs text-ink-3">{rt?.r ? 'Rating saved' : 'Rate it'}</p></div>}>
                    <Ext href={x.url} quiet className="font-medium">{x.title}</Ext>
                    <p className="mt-1 flex flex-wrap items-center gap-2 text-sm text-ink-3">
                      {x.review?.use_as ? <Badge tone="iris">{USE_AS[x.review.use_as] ?? x.review.use_as}</Badge> : <Badge>{x.kindName}</Badge>}
                      {seg && <span>Watch <Ext href={`${x.url}&t=${seg.segs[0][0]}s`}>{hms(seg.segs[0][0])}–{hms(seg.segs[0][1])}</Ext></span>}
                      {x.dur ? <span className="tnum">{hms(x.dur)}</span> : null}
                    </p>
                  </Row>
                )
              })}
            </CardBody>
          </Card>
        ))}
      </div>
    </PageBody>
  )
}
