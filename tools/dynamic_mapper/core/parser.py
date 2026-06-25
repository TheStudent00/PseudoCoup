from core.state import SemanticState

class StateParser:
    """
    Parses raw application data (DB diagnostics, UI hierarchy) into a SemanticState.
    """
    @staticmethod
    def parse_diagnostics(diag: dict) -> SemanticState:
        """
        Maps the flat dictionary from DiagnosticsCollector to SemanticState.
        """
        return SemanticState(
            db_version=int(diag.get("dbVersion", 0)),
            training_experience=diag.get("trainingExperience", "BEGINNER"),
            weight_unit=diag.get("weightUnit", "KG"),
            enrolled_program_id=diag.get("enrolledProgram", "none"),
            active_path_id=diag.get("activePath", "none"),
            workout_sessions=int(diag.get("workoutSessions", 0)),
            onboarding_completed=diag.get("onboardingCompleted", "0") == "1",
            current_screen=diag.get("currentScreen", "unknown")
        )

    @staticmethod
    def parse_ui_hierarchy(hierarchy: dict) -> dict:
        """
        Extracts relevant UI context (buttons, titles) from Maestro hierarchy.
        """
        buttons = []
        
        def walk(node):
            attributes = node.get("attributes", {})
            text = attributes.get("text", "") or attributes.get("accessibilityText", "")
            
            clean_text = text.strip()
            # If it's a short text node, consider it a potential button target for Maestro
            if clean_text and len(clean_text) < 30:
                buttons.append(clean_text)
            
            for child in node.get("children", []):
                walk(child)
        
        if hierarchy:
            walk(hierarchy)
            
        return {
            "buttons": tuple(sorted(list(set(buttons))))
        }

    @staticmethod
    def merge_state(diag_state: SemanticState, ui_context: dict) -> SemanticState:
        """
        Combines DB-derived state with UI-derived context.
        """
        from dataclasses import replace
        return replace(diag_state, ui_buttons=ui_context.get("buttons", ()))
