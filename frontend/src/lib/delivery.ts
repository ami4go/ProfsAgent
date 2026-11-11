// What the lecture screens show, worked out from the delivery view (the same rules the first app used).
import type { Choices, ChoiceKey, DeliveryView, Job, Lecture, Mix, MixWay, ResourceKind, SimItem, WantKey } from './types'
import type { Tone } from './status'

export const CHOICES: { key: ChoiceKey; label: string; help: string; short: string }[] = [
  { key: 'own_material', label: 'I’ll teach it with my own material', help: '', short: 'Your own material' },
  { key: 'attach_material', label: 'I’ll attach my material; work with it', help: 'Upload files or paste links.', short: 'Your files, worked on' },
  { key: 'generate_material', label: 'Make the slides for me', help: 'Slides, speaker notes and a quiz.', short: 'Slides made for you' },
  { key: 'assistance', label: 'Find learning resources for me', help: 'Videos, readings and practice.', short: 'Learning resources' },
  { key: 'guest_lecture', label: 'Suggest a guest speaker to invite', help: 'With an invitation draft.', short: 'A guest speaker' },
]
export const WANTS: { key: WantKey; label: string }[] = [
  { key: 'want_videos', label: 'Videos (short explainers, talks)' },
  { key: 'want_readings', label: 'Readings (articles, docs, book chapters)' },
  { key: 'want_practice', label: 'Practice (notebooks, exercises, datasets)' },
  { key: 'want_recorded_lecture', label: 'A full recorded lecture (for a flipped class)' },
  { key: 'want_clips', label: 'Clip playlists (only the minutes that matter)' },
]
export const TASKS: [string, string][] = [['slides', 'Make slides'], ['summary', 'Summary'], ['quiz', 'Quiz'], ['gap_check', 'Check what it misses'], ['enrich', 'Add examples and references']]
export const KINDS: { kind: ResourceKind; name: string; want: WantKey }[] = [
  { kind: 'video', name: 'Videos', want: 'want_videos' },
  { kind: 'recorded_lecture', name: 'Recorded lecture', want: 'want_recorded_lecture' },
  { kind: 'reading', name: 'Readings', want: 'want_readings' },
  { kind: 'practice', name: 'Practice', want: 'want_practice' },
]
export const USE_AS: Record<string, string> = { professor_prep: 'For your preparation', pre_class: 'Before class', in_class_clip: 'In-class clip', after_class: 'After class', flipped_class: 'Flipped class', lab: 'Lab', practice: 'Practice' }
export const EXPERT_KIND: Record<string, string> = { academic: 'Researcher', industry: 'Industry', iiitd: 'IIIT-D faculty' }
export const TALK_FORMAT: Record<string, string> = { live_remote_60: 'Live online talk, 60 min', live_in_person: 'In person', recorded_talk: 'Recorded talk', panel: 'Panel', qa_after_recorded: 'Recorded talk, then live Q&A' }
export const LINK_NAME: Record<string, string> = { openalex: 'OpenAlex', orcid: 'ORCID', scholar_search: 'Google Scholar search', dblp: 'DBLP', github: 'GitHub', website: 'Website', page: 'Profile page', talk: 'Talk' }
export const SIM_MAX = 2

export const yes = (a: Choices | null | undefined, k: ChoiceKey | WantKey) => !!a && a[k] === 'yes'
export const blankChoices = (): Choices => ({
  own_material: null, attach_material: null, generate_material: null, assistance: null, guest_lecture: null, attachments: [], attach_tasks: [],
  want_videos: 'yes', want_readings: 'yes', want_practice: 'no', want_recorded_lecture: 'no', want_clips: 'no', confidence: null, note: '',
})
const active = (j?: Job | null) => !!j && (j.state === 'queued' || j.state === 'running')

// ------------------------------------------------------------------ the class-time bar
export type Way = 'slides' | 'video' | 'nlm' | 'inclass' | 'sim' | 'quiz'
export const WAY_NAME: Record<Way, string> = { slides: 'Slides', video: 'Video', nlm: 'NotebookLM', inclass: 'In class', sim: 'Simulation', quiz: 'Recap and quiz' }
export const WAY_ORDER: Way[] = ['slides', 'video', 'nlm', 'inclass', 'sim', 'quiz']
export const MIX_WAY: Record<MixWay, Way> = { slides: 'slides', youtube: 'video', youtube_bridge: 'video', notebooklm: 'nlm', in_class: 'inclass', simulation: 'sim' }
export const MIX_LABEL: Record<MixWay, string> = { slides: 'Slides', youtube: 'YouTube clip', youtube_bridge: 'YouTube + slides', notebooklm: 'NotebookLM video', in_class: 'In class', simulation: 'Simulation' }
export const MIX_PRESETS: [string, string][] = [['slides_only', 'Slides only'], ['slides_clips', 'Slides + clips'], ['slides_notebooklm', 'Slides + NotebookLM'], ['flipped', 'Flipped'], ['full_mix', 'Full mix']]

export interface TimePart { way: Way; minutes: number; title: string; pre?: boolean }

/** How a lecture's minutes are spent: from the approved or proposed plan, else from the search's part list. */
export function classTime(v: DeliveryView, lid: string): TimePart[] | null {
  const m: Mix | undefined = v.mix?.lectures?.[lid]
  if (m && m.parts?.length) {
    const out: TimePart[] = []
    if (m.recap_minutes) out.push({ way: 'quiz', minutes: m.recap_minutes, title: 'Recap of the last lecture' })
    for (const p of m.parts) out.push({ way: MIX_WAY[p.way] ?? 'slides', minutes: p.minutes, pre: p.when === 'pre_class', title: p.title })
    if (m.quiz_minutes) out.push({ way: 'quiz', minutes: m.quiz_minutes, title: 'Closing quiz' })
    return out
  }
  const r = v.results[lid]
  if (r && r.components?.length) {
    const tl = Object.fromEntries((r.timeline ?? []).map((x) => [x.component, x]))
    const nlm = r.notebooklm?.components ?? []
    return r.components.map((c) => {
      const t = tl[c.id]
      const way: Way = t?.delivery === 'video' ? 'video' : t?.delivery === 'notebooklm' || (!t?.delivery && nlm.includes(c.id)) ? 'nlm' : t?.delivery === 'in_class' || c.in_class ? 'inclass' : 'slides'
      return { way, minutes: c.minutes || 0, title: c.title || '' }
    })
  }
  const a = v.survey[lid]
  const l = v.lectures.find((x) => x.id === lid)
  if (a && yes(a, 'own_material') && !yes(a, 'assistance') && l) return [{ way: 'slides', minutes: Math.round(l.hours * 60), title: 'Your own material' }]
  return null
}

// ------------------------------------------------------------------ one status per lecture, in words
export function reviewCounts(v: DeliveryView, lid: string) {
  const r = v.results[lid]
  if (!r) return null
  const a = v.survey[lid]
  let pending = 0, approved = 0
  if (yes(a, 'assistance')) for (const k of KINDS) if (yes(a, k.want)) for (const x of r.items[k.kind] ?? []) x.approved ? approved++ : pending++
  if (yes(a, 'guest_lecture') && r.experts && 'experts' in r.experts) for (const x of r.experts.experts) x.approved ? approved++ : pending++
  approved += (v.own?.[lid] ?? []).length
  return { pending, approved, removed: (v.actions?.[lid] ?? []).filter((x) => x.decision !== 'approve').length }
}

export interface LectureStatus { label: string; tone: Tone; busy?: boolean; review?: boolean }

export function lectureStatus(v: DeliveryView, lid: string): LectureStatus {
  const a = v.survey[lid]
  if (!a) return { label: 'Not planned yet', tone: 'neutral' }
  const j = v.jobs?.lectures?.[lid]
  if (j?.state === 'running') return { label: 'Searching', tone: 'iris', busy: true }
  if (j?.state === 'queued') return { label: 'Waiting to start', tone: 'neutral', busy: true }
  if (j?.state === 'error') return { label: 'Problem', tone: 'rose' }
  const wantsSearch = yes(a, 'assistance') || yes(a, 'guest_lecture')
  if (wantsSearch && v.results[lid]) {
    const c = reviewCounts(v, lid)!
    const partial = !!v.results[lid].partial
    if (c.pending) return { label: `${partial ? 'Partial · ' : ''}Ready to review · ${c.pending}`, tone: 'amber', review: true }
    return partial ? { label: 'Partial · reviewed', tone: 'amber' } : { label: 'Reviewed', tone: 'mint' }
  }
  if (wantsSearch) return { label: 'Not started', tone: 'neutral' }
  if (yes(a, 'generate_material')) {
    const m = v.material?.[lid], mj = v.jobs?.material?.[lid]
    if (active(mj)) return { label: 'Making slides', tone: 'iris', busy: true }
    if (mj?.state === 'error') return { label: 'Problem', tone: 'rose' }
    if (m) return m.status === 'approved' ? { label: 'Slides approved', tone: 'mint' } : m.status === 'rejected' ? { label: 'Slides rejected', tone: 'neutral' } : { label: 'Slides ready to review', tone: 'amber', review: true }
    return { label: 'Not started', tone: 'neutral' }
  }
  if (yes(a, 'attach_material')) return { label: 'Saved; working with files comes later', tone: 'neutral' }
  return { label: 'Covered: your own material', tone: 'mint' }
}

export const MATERIAL_STATUS: Record<string, { label: string; short: string; tone: Tone }> = {
  draft: { label: 'Draft: not reviewed yet', short: 'draft', tone: 'amber' },
  'ai-reviewed': { label: 'Checked by a second AI, not by you', short: 'AI-checked', tone: 'iris' },
  approved: { label: 'Approved by you', short: 'approved', tone: 'mint' },
  redo: { label: 'Being redone', short: 'being redone', tone: 'iris' },
  rejected: { label: 'Rejected', short: 'rejected', tone: 'neutral' },
}

export function slidesStatus(v: DeliveryView, lid: string): LectureStatus | null {
  if (!yes(v.survey[lid], 'generate_material')) return null
  const j = v.jobs?.material?.[lid], m = v.material?.[lid]
  if (j?.state === 'running') return { label: 'Slides: making', tone: 'iris', busy: true }
  if (j?.state === 'queued') return { label: 'Slides: waiting', tone: 'neutral' }
  if (j?.state === 'error') return { label: 'Slides: problem', tone: 'rose' }
  if (m) return { label: `Slides: ${MATERIAL_STATUS[m.status]?.short ?? m.status}`, tone: MATERIAL_STATUS[m.status]?.tone ?? 'neutral' }
  return { label: 'Slides: not made', tone: 'neutral' }
}

export const simApproved = (i: SimItem) => i.decision?.decision === 'approve'
export const simsOf = (v: DeliveryView, lid: string) => v.simulations?.lectures?.[lid] ?? { items: [] as SimItem[], kind: null }

/** Is anything being made for this course right now? (decides whether the page keeps refreshing) */
export function deliveryBusy(v: DeliveryView): boolean {
  const j = v.jobs ?? { lectures: {} }
  return (
    ['preparing', 'not started'].includes(v.simulations?.state) ||
    Object.values(j.mix ?? {}).some(active) || Object.values(j.lectures ?? {}).some(active) || Object.values(j.material ?? {}).some(active) || active(j.health)
  )
}

/** A "new topic" tag on most lectures tells nothing, so it is only shown when it is rare. */
export const novelIsUseful = (ls: Lecture[]) => ls.filter((l) => l.novel).length <= ls.length / 2

export function needsProgress(v: DeliveryView, lid: string): boolean {
  const a = v.survey[lid], j = v.jobs?.lectures?.[lid], mj = v.jobs?.material?.[lid], r = v.results[lid]
  if ((j && j.state !== 'done') || (mj && mj.state !== 'done')) return true
  if ((yes(a, 'assistance') || yes(a, 'guest_lecture')) && (!r || r.partial)) return true
  return yes(a, 'generate_material') && !v.material?.[lid]
}
