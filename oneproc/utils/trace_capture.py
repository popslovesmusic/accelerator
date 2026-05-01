import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class TraceEntry(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    component: str
    action: str
    status: str
    details: Dict[str, Any] = Field(default_factory=dict)

class TraceLog(BaseModel):
    run_id: str
    start_time: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    entries: List[TraceEntry] = Field(default_factory=list)
    
    def add_entry(self, component: str, action: str, status: str, details: Dict[str, Any] = None):
        entry = TraceEntry(component=component, action=action, status=status, details=details or {})
        self.entries.append(entry)

class TraceCapture:
    def __init__(self, run_id: str, output_dir: str):
        self.run_id = run_id
        self.output_dir = output_dir
        self.log = TraceLog(run_id=run_id)
        os.makedirs(output_dir, exist_ok=True)
        self.file_path = os.path.join(output_dir, f"trace_{run_id}.json")

    def capture(self, component: str, action: str, status: str, details: Dict[str, Any] = None):
        self.log.add_entry(component, action, status, details)
        self.save()

    def save(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write(self.log.model_dump_json(indent=2))

    def get_log(self) -> TraceLog:
        return self.log
