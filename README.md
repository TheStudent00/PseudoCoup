# PseudoCoup

> Write an application **once**, in one good notation — disciplined, intentful
> pseudo-code — and render it to **any** platform through **any** target, staying
> as future-safe as possible.

PseudoCoup is the umbrella: a coup against un-portable, un-intentful design. It
owns nothing technical itself; it is the altitude above all targets. You write
*disciplined Python* (one notation, platform-agnostic); each target is a
transpiler + a UI kit underneath.

This repo is the thin meta-layer — thesis, decisions, and the map below. The work
lives in the sibling repos. Authoritative orientation and decision history are in
[`DevComms/`](DevComms): the [handoff report](DevComms/PseudoCoup_handoff_report.md)
(read first), the [communication protocol](DevComms/LLM_communication_protocol.md),
and the brainstorm logs.

## The map

```
PseudoCoup                  the umbrella (this repo): thesis + decisions + index
  |
  +-- PyHaxe                target: disciplined Python -> Haxe source
  |     +-- PyHaxeUI        UI kit over Haxe (Kivy debug path + drawn widgets)
  |           +-- PyHaxeUI-Android   native Android Views ship path — PROVEN
  |           +-- PyHaxeUI-iOS       planned, not started
  |
  +-- PseudoDart            target: disciplined Python -> Dart source
        +-- PseudoFlutter   UI kit over Dart (Flutter widgets) — not started
```

| Repo | What it is | Status |
|------|-----------|--------|
| **PyHaxe** | Python→Haxe transpiler (the original tool) | working, proven end-to-end |
| **PyHaxeUI** | UI kit over the Haxe target | Kivy debug path + native Android proven |
| **PyHaxeUI-Android** | native Android Views ship path | PROVEN (on-emulator) |
| **PseudoDart** | Python→Dart transpiler | working spine, maturing on WFL |
| **PseudoFlutter** | UI kit over the Dart target | not started |
| **WFL_PyHaxe** | a real app (fitness) on the Haxe target | source 224/225 files clean |
| **WFL_PseudoCoup** | the same app on the Dart target | Stage 1: 3 oracles green in Dart |

## The two ideas that carry the project

- **intent, not mechanism** — the code describes what the app *wants*, never how a
  toolkit does it. Intent survives churn because it never names the mechanism.
- **discipline** — a Python subset chosen so translation is mechanical. It's a
  floor, not dogma: a lighter target (Dart) gets a lighter discipline.

## License

OTU-GL — see the bundled license PDF.
