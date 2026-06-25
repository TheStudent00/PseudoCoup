from dataclasses import dataclass, field, asdict
import hashlib
import json

@dataclass(frozen=True)
class SemanticState:
    """
    Represents a high-level, normalized state of an application.
    This serves as the data for a UI graph node.
    """
    # IDENTITY FIELDS (Used for graph node identity)
    training_experience: str = "BEGINNER"
    weight_unit: str = "KG"
    enrolled_program_id: str = "none"
    active_path_id: str = "none"
    onboarding_completed: bool = False
    current_screen: str = "unknown"
    # UI CONTEXT (Extracted from hierarchy)
    ui_buttons: tuple[str, ...] = field(default_factory=tuple)
    
    # UNIFIED BASIS VECTORS (Based on BODY_PARTS)
    restriction_vector: dict[str, float] = field(default_factory=dict)
    goal_vector: dict[str, float] = field(default_factory=dict)
    program_load_vector: dict[str, float] = field(default_factory=dict)

    # METADATA FIELDS
    db_version: int = 0
    workout_sessions: int = 0

    def get_identity_hash(self) -> str:
        """
        Returns a stable hash for the logical identity of the state.
        Excludes monotonically increasing metadata to ensure graph convergence.
        """
        identity_data = {
            "exp": self.training_experience,
            "unit": self.weight_unit,
            "prog_id": self.enrolled_program_id,
            "path_id": self.active_path_id,
            "done": self.onboarding_completed,
            "screen": self.current_screen,
            "buttons": self.ui_buttons,
            "rest": self.restriction_vector,
            "goal": self.goal_vector,
            "load": self.program_load_vector
        }
        state_str = json.dumps(identity_data, sort_keys=True)
        return hashlib.sha256(state_str.encode()).hexdigest()
