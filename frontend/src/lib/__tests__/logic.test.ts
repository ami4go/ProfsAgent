import { describe, expect, it } from 'vitest'
import { classTime, lectureStatus, novelIsUseful, reviewCounts, slidesStatus } from '../delivery'
import { ago, hms, plural, until } from '../format'
import { stageStates, stageStatesOf, statusLabel } from '../status'
import type { Choices, DeliveryView, Lecture, Run, RunSummary } from '../types'

const choices = (p: Partial<Choices>): Choices => ({
  own_material: 'no', attach_material: 'no', generate_material: 'no', assistance: 'no', guest_lecture: 'no', attachments: [], attach_tasks: [],
  want_videos: 'yes', want_readings: 'yes', want_practice: 'no', want_recorded_lecture: 'no', want_clips: 'no', confidence: null, note: '', ...p,
})
const lecture = (id: string, p: Partial<Lecture> = {}): Lecture => ({
  id, week: 1, slot: 1, hours: 2, topic: 'T', module: 'M', continues: false, novel: false, match: null, summary: null, los: [], cos: [], builds_on: [], prereq: [], leads_to: [], assessed: [], labs: [], hands_on: null, outside: null, ...p,
})
const view = (p: Partial<DeliveryView>): DeliveryView => ({
  run: { id: 'app-x-01', course: 'C', title: 'C', code: null, example_of: null }, lectures: [lecture('W01.L1')], survey: {}, results: {}, kits: [], notebooklm: [], log: {},
  jobs: { lectures: {} }, own: {}, actions: {}, ratings: {}, health: { checked_at: null, dead: [] }, keys: { youtube: true, openalex: true, tavily: true }, material: {},
  material_connected: { generate: true, attach: false }, simulations: { state: 'ready', error: null, lectures: {} }, mix: { lectures: {}, quiz: {}, style: 'mix' }, ...p,
})
const resource = (key: string, approved: boolean) => ({ key, url: key, title: key, source: null, tier: null, dur: null, year: null, captions: null, licence: null, embeddable: true, yt: null, total: null, scores: null, rationale: null, rank: 1, warnings: [], review: { text: null, use_as: null, issues: [] }, cover: [], evidence: null, approved })
const result = (items: ReturnType<typeof resource>[]) => ({ generated_at: null, continuation_of: null, note: null, counts: null, partial: null, has_resources: true, items: { video: items }, reserve: {}, rejected: [], clips: [], experts: null, components: [], timeline: [], notebooklm: null })

describe('one status per lecture', () => {
  it('a lecture with no saved choices is an action, not a state', () => {
    expect(lectureStatus(view({ survey: { 'W01.L1': null } }), 'W01.L1')).toMatchObject({ label: 'Not planned yet', tone: 'neutral' })
  })
  it('own material alone is covered', () => {
    expect(lectureStatus(view({ survey: { 'W01.L1': choices({ own_material: 'yes' }) } }), 'W01.L1').tone).toBe('mint')
  })
  it('a running search wins over everything else', () => {
    const v = view({ survey: { 'W01.L1': choices({ assistance: 'yes' }) }, jobs: { lectures: { 'W01.L1': { state: 'running' } } } })
    expect(lectureStatus(v, 'W01.L1')).toMatchObject({ label: 'Searching', busy: true })
  })
  it('results with pending items are ready to review, and say how many', () => {
    const v = view({ survey: { 'W01.L1': choices({ assistance: 'yes' }) }, results: { 'W01.L1': result([resource('a', false), resource('b', true)]) } })
    expect(reviewCounts(v, 'W01.L1')).toEqual({ pending: 1, approved: 1, removed: 0 })
    expect(lectureStatus(v, 'W01.L1')).toMatchObject({ label: 'Ready to review · 1', tone: 'amber', review: true })
  })
  it('only the kinds the professor asked for are counted', () => {
    const v = view({ survey: { 'W01.L1': choices({ assistance: 'yes', want_videos: 'no' }) }, results: { 'W01.L1': result([resource('a', false)]) } })
    expect(lectureStatus(v, 'W01.L1').label).toBe('Reviewed')
  })
  it('slides have their own status only when slides were asked for', () => {
    expect(slidesStatus(view({ survey: { 'W01.L1': choices({ own_material: 'yes' }) } }), 'W01.L1')).toBeNull()
    expect(slidesStatus(view({ survey: { 'W01.L1': choices({ generate_material: 'yes' }) } }), 'W01.L1')?.label).toBe('Slides: not made')
  })
})

describe('the class-time bar', () => {
  it('has no plan until there is something to show', () => {
    expect(classTime(view({ survey: { 'W01.L1': null } }), 'W01.L1')).toBeNull()
  })
  it('own material fills the whole lecture with slides', () => {
    expect(classTime(view({ survey: { 'W01.L1': choices({ own_material: 'yes' }) } }), 'W01.L1')).toEqual([{ way: 'slides', minutes: 120, title: 'Your own material' }])
  })
  it('the teaching plan adds the recap and the closing quiz around its parts', () => {
    const mix = { lecture_id: 'W01.L1', status: 'proposed', preset: null, recap_minutes: 5, quiz_minutes: 10, totals: {}, prep_minutes: 0, checks: [], note: '',
      parts: [{ component: 'C1', title: 'A', minutes: 20, way: 'youtube' as const, when: 'pre_class' as const }, { component: 'C2', title: 'B', minutes: 30, way: 'simulation' as const, when: 'in_class' as const }] }
    const parts = classTime(view({ mix: { lectures: { 'W01.L1': mix }, quiz: {}, style: 'mix' } }), 'W01.L1')!
    expect(parts.map((p) => p.way)).toEqual(['quiz', 'video', 'sim', 'quiz'])
    expect(parts[1].pre).toBe(true)
    expect(parts.reduce((s, p) => s + p.minutes, 0)).toBe(65)
  })
  it('a "new topic" tag is hidden when most lectures carry it', () => {
    expect(novelIsUseful([lecture('a', { novel: true }), lecture('b', { novel: true }), lecture('c')])).toBe(false)
    expect(novelIsUseful([lecture('a', { novel: true }), lecture('b'), lecture('c')])).toBe(true)
  })
})

describe('where a course stands', () => {
  const run = (p: Partial<Run>): Run => ({ run_id: 'r', title: 't', by: 'P', created_at: 0, status: 'waiting', gate: 'gate1_context', error: null, resume_at: null, history: [], queue_position: 0,
    progress: { steps: [], current: null, current_label: null, done: 0, total: 1, log: [], ai_calls: 0 }, approvals: [], phase: 'design', view: null, ...p })
  it('the waiting check is current, earlier ones approved, later ones upcoming', () => {
    const st = stageStates(run({ approvals: [{ gate: 'gate0_details', decision: 'approve', by: 'P' }] }))
    expect(st).toEqual({ gate0_details: 'approved', gate1_context: 'current', gate2_outcomes: 'upcoming', gate3_proposal: 'upcoming' })
  })
  it('a working run shows the next check as being worked on', () => {
    const st = stageStates(run({ status: 'running', approvals: [{ gate: 'gate0_details', decision: 'approve', by: 'P' }, { gate: 'gate1_context', decision: 'approve', by: 'P' }] }))
    expect(st.gate2_outcomes).toBe('working')
  })
  it('a rejected check is where the run stopped, not an approval', () => {
    const st = stageStates(run({ status: 'stopped', gate: 'gate2_outcomes', approvals: [{ gate: 'gate0_details', decision: 'approve', by: 'P' }, { gate: 'gate1_context', decision: 'approve', by: 'P' }, { gate: 'gate2_outcomes', decision: 'reject', by: 'P' }] }))
    expect(st.gate2_outcomes).toBe('stopped')
  })
  it('a list row estimates the same from its last check', () => {
    const r = (p: Partial<RunSummary>): RunSummary => ({ run_id: 'r', title: 't', by: 'P', created_at: 0, status: 'waiting', gate: 'gate2_outcomes', resume_at: null, ...p })
    expect(stageStatesOf(r({}))).toEqual({ gate0_details: 'approved', gate1_context: 'approved', gate2_outcomes: 'current', gate3_proposal: 'upcoming' })
    expect(stageStatesOf(r({ status: 'done' })).gate3_proposal).toBe('approved')
    expect(stageStatesOf(r({ status: 'error', gate: null })).gate0_details).toBe('problem')
    expect(statusLabel(r({}))).toBe('Needs you: Outcomes')
  })
})

describe('words for numbers', () => {
  it('formats video positions, waits and counts', () => {
    expect(hms(263)).toBe('4:23')
    expect(hms(3725)).toBe('1:02:05')
    expect(until(1000 + 42 * 60, 1000)).toBe('in 42 min')
    expect(until(1000 + 3600 + 300, 1000)).toBe('in 1 h 5 min')
    expect(until(900, 1000)).toBe('any moment now')
    expect(ago(1000 - 7200, 1000)).toBe('2 h ago')
    expect(plural(1, 'lecture')).toBe('1 lecture')
    expect(plural(3, 'thing was', 'things were')).toBe('3 things were')
  })
})
