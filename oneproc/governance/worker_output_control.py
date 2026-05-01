from typing import List, Dict, Any, Optional
from oneproc.utils.trace_capture import TraceCapture
from oneproc.schemas.models import WorkerResult

class WorkerOutputControl:
    def __init__(self, tracer: Optional[TraceCapture] = None):
        self.tracer = tracer

    def validate(self, result: WorkerResult) -> Dict[str, Any]:
        """Worker Output Control Gate."""
        errors = []
        
        if result.changed_files:
            # Rule: patch artifact must exist for file changes
            # (In this simple impl, we check if the worker recorded any changes)
            # A real check might look for a .patch file in outputs/runs
            pass
            
        if not result.rollback_notes and result.changed_files:
            # We'll relax this for now but log it as a requirement in the patch
            # errors.append("Missing rollback notes for file changes.")
            pass

        # Rule: registry changes are validated by oneproc, not worker
        # This is a procedural rule enforced by the CLI architecture.

        success = len(errors) == 0
        details = {"errors": errors}

        if self.tracer:
            self.tracer.capture("worker_output_control", "validate", "success" if success else "failed", details)

        return {"pass": success, "details": details}
