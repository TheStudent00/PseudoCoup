# Kotlin to Python Conversion Assessment

## Overview
This assessment evaluates the remaining work required to complete the conversion of the Kotlin (Compose) application to Python (`WFL_PseudoCoup`). This encompasses both the automated transpiler toolchain (`dualgraph` and `ingest.py`) and the hand-wiring of the UI screens using the `PseudoCoup` toolkit.

## 1. Automated Toolchain (Transpiler) Status
The `dualgraph` toolchain is currently functional and serves as the structural alignment gate. 

**Completed:**
- Tree parser (`KotlinParser`) and Compose traversal (`ui_call_tree`).
- Safe length-gated substring matching (`text_match`).
- Connectivity metrics (`connectivity_gate.py`) properly tracking gaps.
- Complex component inline expansion (e.g., `ExecutionContent`).

**Remaining Work:**
- **Widget Vocabulary Expansion**: We must map any newly discovered Compose primitives and structural wrappers (e.g., specific constraint variants) to the PseudoCoup `KNOWN_CUSTOM` registry in `ingest.py`.
- **Attribute & Handler Mapping**: Currently, we align structural topology (e.g. `onClick->onJumpToSet`). Expanding attribute mapping to capture nuanced state-binds or deep arguments will be necessary for a complete automated conversion.
- **Robustness against arbitrary Kotlin layout extensions**: Complex UI scoping (`WflCompactDensity`, `AnimatedContent`, etc.) was just handled, but edge-case lambda nesting or highly custom layout modifiers might still hide elements. 

## 2. Hand-Wiring (PseudoCoup Screen Ports) Status
We have a baseline of ~44% connectivity across 50+ screens. 

**Completed:**
- PseudoCoup widget classes created for the majority of the basic layout.
- Initial structural stubs written for the UI surface of all screens.

**Remaining Work:**
- **Closing the Gap**: The remaining 56% connectivity gap indicates that the hand-wired PseudoCoup screens are missing structural counterparts to the Kotlin blueprint (e.g., missing dividers, specific textual units, icons).
- **State Logic & ViewModels**: Hand-wiring the `Python` screens currently only covers the structural facade (`matched` / `kt_only` slots). The underlying state machinery, reducers, and ViewModel business logic from the Kotlin side needs to be hand-ported into Python controllers.
- **Micro-Animations & Modifiers**: Jetpack Compose modifiers (padding, layout alignment) and `AnimatedVisibility` transitions are largely bypassed by the structural alignment tool. Hand-wiring must implement these visual details using the PseudoCoup toolkit layout mechanics.
- **Screen-by-Screen Hardening**: For each of the remaining poorly aligned screens (like `onboarding_screen` or `settings_notifications_screen`), a developer needs to manually inspect the `align.py` output and add the missing Python widgets to the respective file.
