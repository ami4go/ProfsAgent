// Two documents ProfsAgent writes for a lecture: the guest-lecture kit (with an invitation the professor sends) and the
// NotebookLM pack (prompts to paste into NotebookLM).
import { useQuery } from '@tanstack/react-query'
import { useParams } from 'react-router-dom'
import { ArrowLeft, Copy } from 'lucide-react'
import { api, deliveryUrl, enc } from '@/lib/api'
import { Markdown } from '@/lib/md'
import { toast } from '@/lib/toast'
import { Button, Card, CardBody, CardHeader, EmptyState, Loading } from '@/components/ui'
import { PageBody } from '@/components/app/Shell'
import { useCourse } from '../course/Layout'
import { lectureUrl } from './shared'

async function copy(text: string, done: string) {
  try {
    await navigator.clipboard.writeText(text)
    toast.success(done)
  } catch {
    toast.error('Select the text and copy it')
  }
}
const useDoc = (rid: string, lid: string, kind: 'kit' | 'notebooklm') =>
  useQuery({ queryKey: ['delivery', rid, kind, lid], queryFn: () => api.get<{ md: string }>(deliveryUrl(rid, `/${kind}/${enc(lid)}`)), retry: false })

function Back({ base, lid }: { base: string; lid: string }) {
  return <Button size="sm" variant="ghost" className="-ml-2" to={lectureUrl(base, lid)} icon={<ArrowLeft aria-hidden />}>Back to {lid}</Button>
}

export function KitPage() {
  const { rid, base } = useCourse()
  const { lid = '' } = useParams()
  const { data, isLoading } = useDoc(rid, lid, 'kit')
  const src = data?.md ?? ''
  const i = src.indexOf('## Invitation draft')
  const body = i >= 0 ? src.slice(0, i) : src
  const invite = i >= 0 ? src.slice(src.indexOf('\n', i) + 1).trim() : ''
  return (
    <PageBody width="read">
      <Back base={base} lid={lid} />
      <p className="label-caps mb-2 mt-4">Guest-lecture kit · {lid}</p>
      {isLoading ? <Loading /> : !src ? <EmptyState title={`No guest-lecture kit for ${lid} yet`}>It is written when the speaker search finishes.</EmptyState> : (
        <div className="space-y-4">
          <Card><CardBody className="pt-5"><Markdown source={body} /></CardBody></Card>
          {invite && (
            <Card>
              <CardHeader title="Invitation draft" description="Edit it and send it yourself from your own email. ProfsAgent never contacts anyone and stores no email addresses."
                actions={<Button size="sm" variant="primary" icon={<Copy aria-hidden />} onClick={() => copy(invite, 'Invitation copied. Paste it into your email.')}>Copy invitation</Button>} />
              <CardBody><pre className="whitespace-pre-wrap rounded-lg border border-line bg-sunken p-4 font-sans text-base leading-relaxed text-ink-2">{invite}</pre></CardBody>
            </Card>
          )}
        </div>
      )}
    </PageBody>
  )
}

export function NotebookPage() {
  const { rid, base } = useCourse()
  const { lid = '' } = useParams()
  const { data, isLoading } = useDoc(rid, lid, 'notebooklm')
  const src = data?.md ?? ''
  const parts = src.split(/^```(?:text)?\s*$/m)
  return (
    <PageBody width="read">
      <Back base={base} lid={lid} />
      <p className="label-caps mb-2 mt-4">NotebookLM pack · {lid}</p>
      {isLoading ? <Loading /> : !src ? <EmptyState title={`No NotebookLM pack for ${lid} yet`}>It is written when the resource search finishes.</EmptyState> : (
        <Card>
          <CardBody className="space-y-4 pt-5">
            {parts.map((p, i) => i % 2 ? (
              <div key={i} className="rounded-lg border border-line bg-sunken">
                <div className="flex items-center justify-between border-b border-line px-3 py-1.5"><span className="label-caps">Prompt</span><Button size="sm" variant="ghost" icon={<Copy aria-hidden />} onClick={() => copy(p.trim(), 'Copied. Paste it into NotebookLM.')}>Copy</Button></div>
                <pre className="whitespace-pre-wrap p-3 font-sans text-base leading-relaxed text-ink-2">{p.trim()}</pre>
              </div>
            ) : p.trim() ? <Markdown key={i} source={p} /> : null)}
          </CardBody>
        </Card>
      )}
    </PageBody>
  )
}
