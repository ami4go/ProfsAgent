// Server state: one hook per resource. A page that shows work in progress keeps itself fresh while that work runs.
import { useQuery, useQueryClient, type QueryClient } from '@tanstack/react-query'
import { api, deliveryUrl, runUrl } from './api'
import { deliveryBusy } from './delivery'
import type { DeliveryCourse, DeliveryView, FormOptions, Gate, Health, MaterialDetail, Run, RunSummary, SimCatalogue, StageView } from './types'

export const keys = {
  health: ['health'] as const,
  options: ['options'] as const,
  runs: ['runs'] as const,
  run: (rid: string) => ['run', rid] as const,
  stage: (rid: string, gate: Gate) => ['run', rid, 'stage', gate] as const,
  deliveryCourses: ['delivery-courses'] as const,
  delivery: (rid: string) => ['delivery', rid] as const,
  material: (rid: string, lid: string) => ['delivery', rid, 'material', lid] as const,
  sims: ['simulations'] as const,
}

export const useHealth = () => useQuery({ queryKey: keys.health, queryFn: () => api.get<Health>('/api/health'), refetchInterval: 15_000 })
export const useOptions = () => useQuery({ queryKey: keys.options, queryFn: () => api.get<FormOptions>('/api/options'), staleTime: Infinity })

export const useRuns = () =>
  useQuery({
    queryKey: keys.runs,
    queryFn: () => api.get<RunSummary[]>('/api/runs'),
    refetchInterval: (q) => (q.state.data?.some((r) => r.status === 'queued' || r.status === 'running') ? 5_000 : 30_000),
  })

export const useRun = (rid: string) =>
  useQuery({
    queryKey: keys.run(rid),
    queryFn: () => api.get<Run>(runUrl(rid)),
    refetchInterval: (q) => {
      const s = q.state.data?.status
      return s === 'queued' || s === 'running' ? 2_500 : s === 'paused' ? 30_000 : false
    },
    retry: false,
  })

export const useStage = (rid: string, gate: Gate, enabled: boolean) =>
  useQuery({ queryKey: keys.stage(rid, gate), queryFn: () => api.get<StageView>(runUrl(rid, `/stage/${gate}`)), enabled, retry: false })

export const useDeliveryCourses = () =>
  useQuery({ queryKey: keys.deliveryCourses, queryFn: () => api.get<{ courses: DeliveryCourse[]; example_available: boolean }>('/api/delivery') })

export const useDelivery = (rid: string, enabled = true) =>
  useQuery({
    queryKey: keys.delivery(rid),
    queryFn: () => api.get<DeliveryView>(deliveryUrl(rid)),
    enabled,
    retry: false,
    refetchInterval: (q) => (q.state.data && deliveryBusy(q.state.data) ? 4_000 : false),
  })

export const useMaterial = (rid: string, lid: string, stamp: string | undefined) =>
  useQuery({
    queryKey: [...keys.material(rid, lid), stamp],
    queryFn: () => api.get<MaterialDetail>(deliveryUrl(rid, `/material/${encodeURIComponent(lid)}`)),
    enabled: !!stamp,
    retry: false,
  })

export const useSims = (poll = false) =>
  useQuery({ queryKey: keys.sims, queryFn: () => api.get<SimCatalogue>('/api/simulations'), refetchInterval: poll ? 5_000 : false })

/** After something changed on the server: refresh what the screens show. */
export function refresh(qc: QueryClient, ...which: (readonly unknown[])[]) {
  return Promise.all(which.map((queryKey) => qc.invalidateQueries({ queryKey })))
}
export const useRefresh = () => {
  const qc = useQueryClient()
  return (...which: (readonly unknown[])[]) => refresh(qc, ...which)
}
