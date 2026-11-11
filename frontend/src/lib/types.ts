// Shapes of the app's JSON API (src/profsagent/app/server.py, views.py, delivery.py, simulations.py).

export type RunStatus = 'queued' | 'running' | 'waiting' | 'paused' | 'error' | 'done' | 'stopped'
export type Gate = 'gate0_details' | 'gate1_context' | 'gate2_outcomes' | 'gate3_proposal'

export interface Health {
  kg_backend: 'neo4j' | 'stub' | string
  neo4j: boolean | null
  keys: { gemini: number; groq: number }
  working_on: string | null
  queued: number
  now: number
}

export interface FormOptions {
  departments: string[]
  programmes: string[]
  years: string[]
  credits: string[]
  assessments: string[]
  example: CourseForm
}

export interface CourseForm {
  name: string
  description: string
  topics: string
  topics_flexible: boolean
  intent_question: string
  intent_emphasis: string
  intent_avoid: string
  department: string
  credits: string
  l: string
  t: string
  p: string
  weeks: string
  weekly_effort: string
  programmes: string[]
  year: string
  background: string
  lab: string
  lab_infra: string
  assess_pref: string[]
  assess_avoid: string[]
  assess_why: string
  special: string
  external_research: boolean
}
export type FormErrors = Partial<Record<keyof CourseForm | 'ltp' | '_', string>>

export interface RunSummary {
  run_id: string
  title: string
  by: string | null
  created_at: number
  status: RunStatus
  gate: Gate | null
  resume_at: number | null
}

export interface ProgressStep { id: string; label: string; done: boolean; gate: boolean }
export interface Progress {
  steps: ProgressStep[]
  current: string | null
  current_label: string | null
  done: number
  total: number
  log: string[]
  ai_calls: number
}

export interface Approval {
  gate: Gate
  decision: 'approve' | 'reject'
  by: string
  comment?: string | null
  at?: number | null
  override?: { codes?: string[]; errors: number; reason?: string } | null
  edits?: string[]
  suggested?: number
  changed?: number
}

export interface ProblemItem { message: string; code: string; where: string; who: string }
export interface ProblemGroup { code: string; plain: string | null; items: ProblemItem[] }
export interface Problems {
  blocked: boolean
  errors: number
  warnings: number
  problem: string | null
  items: ProblemItem[]
  groups: ProblemGroup[]
}

export interface CourseSummary {
  name: string | null
  credits: number | string | null
  ltp: string
  weeks: number | null
  level: number | null
  department: string | null
}

export interface Ref { code: string | null; name: string | null; url: string | null }

// ---- gate 0: details
export interface FilledField {
  value: string | string[]
  reason: string
  sources: { text: string; url?: string | null }[]
  corrected: string | null
}
export interface DetailsView {
  form: CourseForm
  filled: Record<string, FilledField>
  unfilled: string[]
  similar: Ref[]
  given: string[]
  needed: string[]
}

// ---- gate 1: context
export interface TopicGroup { id?: string; title: string; topics: string[] }
export interface Assumption { id: string; what: string; value: string | number; basis?: string; confirm_with?: string; status: string }
export interface Rule {
  text: string
  kind: 'include' | 'exclude'
  hard: boolean
  ref: string | null
  source: { text: string; url: string | null } | null
  tag: string | null
  ids: string[]
}
export interface EditAssumption { id: string; what: string; value: string | number | null; status: string; editable: boolean; confirm?: boolean }
export interface EditWish { ids: string[]; kind: 'include' | 'exclude'; text: string; text_editable: boolean; hard: boolean; said: string; locked?: boolean }
export interface EditPrereq { code: string; kind: 'mandatory' | 'desirable' | string }
export interface Gate1View {
  course: CourseSummary
  edited: Record<string, string[]>
  overlaps_before_topic_edit: boolean
  edit: {
    topics: TopicGroup[]
    assumptions: EditAssumption[]
    wishes: EditWish[]
    prerequisites: EditPrereq[]
    levels: number[]
    weeks: number
  }
  assumptions: Assumption[]
  wishes: Rule[]
  rules: Rule[]
  untranslatable: string[]
  constraint_conflicts: (string | { message?: string; detail?: string })[]
  form_conflicts: (string | { description?: string; message?: string })[]
  existence: { verdict: string; closest?: string[]; reason: string } | null
  prerequisites: (Ref & { kind: string; relied_topics: string[]; why: string | null; alternatives: Ref[] })[]
  overlaps: (Ref & { pct: number; verdict: string | null; shared: string[]; difference: string | null })[]
  anti_requisites: Ref[]
  comparable: { title: string; where: string | null; url: string | null; take: string | null; avoid: string | null }[]
  topics: TopicGroup[]
  topics_treatment: string | null
  concerns: string[]
}

// ---- gate 2: outcomes
export interface Issue { severity: string; message: string; code: string }
export interface CoPo { programme: string; short: string; text: string; strength: number | null }
export interface CoCard {
  id: string
  statement: string
  level: string
  los: { id: string; statement: string; level: string }[]
  pos: CoPo[]
  issues: Issue[]
  edited: boolean
}
export interface EditLo { id?: string; statement: string; bloom_level: number; condition: string; degree: string; suggested_task_type: string | null }
export interface EditCo {
  id?: string
  statement: string
  bloom_level: number
  condition: string
  degree: string
  covers_topic_groups: string[]
  evidence_types: string[]
  los: EditLo[]
  pos: { po_uid: string; strength: number | null }[]
}
export interface Gate2View {
  course: CourseSummary
  cos: CoCard[]
  co_count_target: unknown
  band: unknown
  proposals: { i: number; action: string; targets: string[]; proposal: string | null; reason: string | null }[]
  no_topics_given: boolean
  edited: Record<string, string[]>
  edit: {
    cos: Record<string, EditCo>
    topic_groups: { id: string; title: string }[]
    evidence: string[]
    pos: { uid: string; label: string; text: string }[]
    bloom: Record<string, string>
  }
}

// ---- gate 3: the final sheet
export interface Book {
  title: string
  authors: string
  year: number | null
  role: string | null
  link: string | null
  id: string | null
  verified: boolean
  note: string | null
}
export interface EditModule { id?: string; title: string; topics: { id?: string; title: string; hours: number | string; serves_los: string }[] }
export interface EditLab { id?: string; title: string; week: number }
export interface EditComp { key: number | null; type: string; name?: string; weight: number | string; invigilated: boolean; due: number[]; instances?: string[] }
export interface EditBook { id?: string | null; role: string; title?: string; ident?: string }
export interface Evaluation {
  verdict: 'PASS' | 'REVIEW' | 'FAIL' | string
  errors?: number
  regulation_ok?: boolean
  alignment_min_pct?: number
  hard_constraints_satisfied_pct?: number
  review_reasons?: string[]
}
export interface Gate3View {
  course: CourseSummary
  edited: Record<string, string[]>
  edit: {
    weeks: EditModule[]
    labs: EditLab[]
    assessment: EditComp[]
    books: EditBook[]
    description: { text: string }
    assess_types: { type: string; name: string }[]
    n_weeks: number
    los: string[]
  }
  description: string | null
  weeks: { week: number; topics: { title: string; hours: number }[]; labs: string[]; midsem_after: boolean }[]
  hours: { planned: number | null; available: number | null }
  assessment: { name: string; weight: number; invigilated: boolean; count: number; due: number[] }[]
  assessment_total: number
  invigilated_pct: number
  co_marks: Record<string, number>
  books: Book[]
  books_rejected: number
  recheck: Record<string, { status: string; record?: string }>
  evaluation: Evaluation | null
  files: Record<string, boolean>
}

export type GateView = DetailsView | Gate1View | Gate2View | Gate3View

export interface Run {
  run_id: string
  title: string
  by: string | null
  created_at: number
  status: RunStatus
  gate: Gate | null
  error: { message: string; detail?: string } | null
  resume_at: number | null
  history: { at: number; event: string }[]
  queue_position: number
  progress: Progress
  approvals: Approval[]
  phase: 'details' | 'design'
  view: GateView | null
  problems?: Problems
  course?: CourseSummary
}

export interface StageView { gate: Gate; view: GateView; editable: boolean }

export interface EditResult { changes: string[]; open_before: number; open_after: number; note?: string | null; run: Run }

// ================================================================== lecture delivery
export type YesNo = 'yes' | 'no' | null
export interface Choices {
  own_material: YesNo
  attach_material: YesNo
  generate_material: YesNo
  assistance: YesNo
  guest_lecture: YesNo
  attachments: string[]
  attach_tasks: string[]
  want_videos: YesNo
  want_readings: YesNo
  want_practice: YesNo
  want_recorded_lecture: YesNo
  want_clips: YesNo
  confidence: number | null
  note: string
  _ai_review?: boolean
}
export type ChoiceKey = 'own_material' | 'attach_material' | 'generate_material' | 'assistance' | 'guest_lecture'
export type WantKey = 'want_videos' | 'want_readings' | 'want_practice' | 'want_recorded_lecture' | 'want_clips'

export interface Lecture {
  id: string
  week: number
  slot: number | null
  hours: number
  topic: string
  module: string
  continues: boolean
  novel: boolean
  match: { topic: string; similarity: number } | null
  summary: string | null
  los: { id: string; text: string; bloom: string; co?: string }[]
  cos: { id: string; text: string }[]
  builds_on: { topic: string; week?: number }[]
  prereq: { course: string; kind?: string; relied_topics?: string[] }[]
  leads_to: { topic: string; week?: number }[]
  assessed: { id: string; type: string; due_week: number | string }[]
  labs: { title: string; week: number | string; tools?: string[] }[]
  hands_on: boolean | null
  outside: number | null
}

export type ResourceKind = 'video' | 'recorded_lecture' | 'reading' | 'practice'
export interface Resource {
  key: string
  url: string
  title: string
  source: string | null
  tier: string | null
  dur: number | null
  year: string | null
  captions: boolean | null
  licence: string | null
  embeddable: boolean
  yt: string | null
  total: number | null
  scores: Record<string, number> | null
  rationale: string | null
  rank: number | null
  warnings: string[]
  review: { text: string | null; use_as: string | null; issues: string[] }
  cover: { label: string; segs: [number, number][] }[]
  evidence: unknown
  approved: boolean
}
export interface Expert {
  key: string
  name: string
  kind: string | null
  role: string | null
  affiliation: string | null
  country: string | null
  links: Record<string, string | null>
  total: number | null
  scores: Record<string, number> | null
  fit: string | null
  why: string | null
  rank: number | null
  evidence: { kind: string | null; title: string; year: number | string | null; url: string | null; venue: string | null }[]
  format: string | null
  verified: string | null
  approved: boolean
  warnings: string[]
}
export interface Component {
  id: string
  title: string
  teaches: string
  key_terms?: string[]
  kind?: string
  minutes: number
  in_class?: boolean
}
export interface Segment {
  url: string
  start: string
  end: string
  video: string
  minutes?: number
  verdict?: string
  coverage?: number | null
  block?: string
  evidence?: { at?: string; quote: string }[]
  limitations?: string[]
}
export interface TimelineItem {
  component: string
  delivery: 'video' | 'notebooklm' | 'in_class' | null
  segments: Segment[]
  gap?: { video_minutes: number; missing?: string[] } | null
}
export interface LectureResult {
  generated_at: string | null
  continuation_of: string | null
  note: string | null
  counts: Record<string, number> | null
  partial: { reason?: string } | null
  has_resources: boolean
  items: Partial<Record<ResourceKind, Resource[]>>
  reserve: Partial<Record<ResourceKind, Resource[]>>
  rejected: { title: string; url: string; why: string[] }[]
  clips: { url: string; start: string; end: string; video: string; target: string; minutes: number }[]
  experts: null | { same_as: string } | { experts: Expert[]; reserve: Expert[]; rejected: { name: string; why: string[] }[]; counts: Record<string, number> | null }
  components: Component[]
  timeline: TimelineItem[]
  blocks?: { block: string; parts?: unknown[] }[]
  notebooklm: { pack?: string; components?: string[]; sources?: number } | null
}

export type JobState = 'queued' | 'running' | 'done' | 'error'
export interface Job { state: JobState; error?: string | null; action?: string; at?: number }

export interface MaterialSummary {
  status: 'draft' | 'ai-reviewed' | 'approved' | 'redo' | 'rejected' | string
  slides: number
  content_slides: number
  minutes: number
  errors: number
  warnings: number
  generated_at: string
  ai_verdict: string | null
  files: string[]
}
export interface Figure { kind: 'none' | 'flow' | 'code' | 'table' | string; caption?: string; steps?: string[]; code?: string; language?: string; rows?: string[][] }
export interface Slide {
  number: number
  kind: string
  minutes: number
  title: string
  bullets?: string[]
  los?: string[]
  figure?: Figure | null
  quiz?: { question: string; options: string[]; answer: number; explanation?: string } | null
  sources?: string[]
  notes?: string
}
export interface MaterialDetail {
  lecture_id: string
  title: string
  status: string
  generated_at: string
  slides_total: number
  minutes: number
  errors: number
  warnings: number
  findings: { code: string; severity: string; where: string; message: string }[]
  sources: Record<string, { title?: string; url?: string }>
  cited: string[]
  ai_review: { verdict?: string } | null
  feedback: string | null
  slides: Slide[]
  files: string[]
}

export type MixWay = 'slides' | 'youtube' | 'youtube_bridge' | 'notebooklm' | 'in_class' | 'simulation'
export interface MixPart {
  component: string
  title: string
  minutes: number
  way: MixWay
  when: 'in_class' | 'pre_class'
  reason?: string
  alternative?: { way?: MixWay; reason?: string } | null
  allowed?: MixWay[]
  locked?: boolean
  segments?: Segment[]
  bridge?: string[]
  uncovered?: string[]
  simulation?: { id?: string; title: string; url?: string } | null
}
export interface Mix {
  lecture_id: string
  status: string
  preset: string | null
  parts: MixPart[]
  recap_minutes: number
  quiz_minutes: number
  totals: Record<string, number>
  prep_minutes: number
  checks: { code: string; message: string }[]
  note: string
  approved_at?: string
}
export interface MixQuiz {
  questions: { question: string; options?: string[]; answer: string; explanation?: string }[] | null
  recap: unknown[] | null
}

export interface SimDecision { decision: 'approve' | 'reject' | 'replace'; reason?: string; version?: string; at?: string; outdated?: boolean }
export interface SimItem {
  id: string
  title: string
  summary: string
  version: string | null
  external?: boolean
  url?: string
  site_name?: string
  shows_code: boolean
  class_example: boolean
  checked: { ok: boolean; at?: string; version?: string; current: boolean } | null
  source?: 'added' | 'suggested' | 'external' | 'decided'
  added_by?: string
  close?: boolean
  decision: SimDecision | null
  retired: boolean
  example: { state: string; summary?: string } | null
}
export interface SimKind { id: string; name?: string; does?: string }

export interface DeliveryView {
  run: { id: string; course: string; title: string; code: string | null; example_of: string | null }
  lectures: Lecture[]
  survey: Record<string, Choices | null>
  results: Record<string, LectureResult>
  kits: string[]
  notebooklm: string[]
  log: Record<string, string[]>
  jobs: { lectures: Record<string, Job>; material?: Record<string, Job>; mix?: Record<string, Job>; health?: Job }
  own: Record<string, { title: string; url: string; kind: ResourceKind }[]>
  actions: Record<string, { kind: string; key: string; title: string; decision: string; reason: string }[]>
  ratings: Record<string, Record<string, { r: number; c: string }>>
  health: { checked_at: string | null; dead: { lecture: string; title: string; url: string; kind: string; replacement_available?: boolean }[] }
  keys: { youtube: boolean; openalex: boolean; tavily: boolean }
  material: Record<string, MaterialSummary>
  material_connected: { generate: boolean; attach: boolean }
  simulations: { state: 'ready' | 'preparing' | 'not started' | 'error' | string; error: string | null; lectures: Record<string, { items: SimItem[]; kind: SimKind | null }> }
  mix: { lectures: Record<string, Mix>; quiz: Record<string, MixQuiz>; style: string }
}

export interface DeliveryCourse {
  run_id: string
  title: string
  code: string | null
  created_at: number
  example: boolean
  lectures: number | null
  decided: number
  with_results: number
}

// ================================================================== simulations
export interface SimEntry {
  id: string
  title: string
  summary: string
  version: string
  status: string
  types: { id: string; name: string }[]
  courses: { code: string; name: string }[]
  topics: string[]
  class_example: boolean
  shows_code: boolean
  checked: { ok: boolean; current: boolean } | null
  used?: { run_id: string; course: string; lecture: string; topic?: string }[]
}
export interface SimExternal { id: string; site_name: string; title: string; url: string; summary: string; shows_code: boolean; text: string }
export interface SimFound {
  n: number
  kind: 'ours' | 'link'
  id?: string
  url?: string
  title: string
  site?: string
  summary?: string
  shot?: string | null
  shows_code?: boolean
  decision?: 'approve' | 'reject' | null
}
export type RequestStatus = 'requested' | 'queued' | 'searching' | 'review' | 'chosen' | 'build_queued' | 'building' | 'ready' | 'approved' | 'needs_team' | 'paused'
export interface SimRequest {
  id: string
  at: string
  topic: string
  what: string
  course: string | null
  run_id: string | null
  lecture: string | null
  status: RequestStatus
  reason?: string
  sim_id?: string
  build?: { attempt?: number; of?: number }
  found?: SimFound[]
}
export interface SimTopicGroup {
  key: string
  title: string
  items: ({ kind: 'ours'; id: string; shows_code: boolean } | { kind: 'link'; url: string; title: string; site_name: string; shows_code: boolean; summary: string })[]
}
export interface SimCatalogue {
  entries: SimEntry[]
  pending: SimEntry[]
  topics: SimTopicGroup[]
  types: { id: string; name: string; does: string; count: number }[]
  requests: SimRequest[]
  external: { sites: string[]; entries: SimExternal[] }
}
