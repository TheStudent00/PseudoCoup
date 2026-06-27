# _deprecated/ — frozen, not deleted

The old UI-mapping / connectivity subsystem. Superseded, kept as **donor parts** for
one new unified mapper (see PROJECT_MAP.md §5). Nothing here is active; internal path
references (absolute paths, `../../uimap`) are stale by design — rewire on reactivation.

Frozen here (2026-06-27):
- `interactive_map/`, `uimap/` — two static UI-map renders (sidebyside/index html + md)
- `runtime_uimap/` — dynamic runtime-map output (spider/tracer artifacts)
- `dynamic_mapper/` — the runtime mapping spider (spider, tracer_dye, aggregate, …)
- `connectivity/` — static connectivity probes (auto_discover, probe)
- `run_mapper.sh` — old driver for the dynamic mapper
- `implementation_plan.md`, `connectivity_audit_results.md` — stale work-products

**The replacement** (deferred): ONE mapper carrying sizing/positioning (relative +
absolute) and one-degree connectivity, assembled from these parts + the dualgraph edge
check (`WFL_PseudoCoup/tools/dualgraph`).

Not here, and still active: `../core/` (the Flow/coroutine shim runtime the transpiler
emits) was never part of this subsystem.
