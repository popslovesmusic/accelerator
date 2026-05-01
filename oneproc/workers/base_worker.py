import subprocess
import time
import os
from typing import List, Optional, Dict, Any
from oneproc.schemas.models import WorkerResult
from oneproc.utils.trace_capture import TraceCapture

class BaseWorker:
    def __init__(self, agent_name: str, tracer: Optional[TraceCapture] = None):
        self.agent_name = agent_name
        self.tracer = tracer

    def _run_command(self, command: List[str], cwd: str = ".") -> WorkerResult:
        start_time = time.time()
        
        # Capture git diff before
        diff_before = self._get_git_diff()
        
        process = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            shell=True # Needed for some Windows commands
        )
        
        duration = time.time() - start_time
        
        # Capture git diff after and changed files
        diff_after = self._get_git_diff()
        changed_files = self._get_changed_files()
        
        result = WorkerResult(
            agent_name=self.agent_name,
            command=command,
            cwd=os.path.abspath(cwd),
            return_code=process.returncode,
            stdout=process.stdout,
            stderr=process.stderr,
            duration_seconds=duration,
            git_diff=diff_after if diff_after != diff_before else None,
            changed_files=changed_files
        )
        
        if self.tracer:
            self.tracer.capture(f"worker_{self.agent_name}", "run_command", 
                                "success" if process.returncode == 0 else "failed", 
                                result.model_dump())
            
        return result

    def _get_git_diff(self) -> str:
        try:
            res = subprocess.run(["git", "diff"], capture_output=True, text=True)
            return res.stdout
        except:
            return ""

    def _get_changed_files(self) -> List[str]:
        try:
            res = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
            files = []
            for line in res.stdout.splitlines():
                if line.strip():
                    files.append(line[3:].strip())
            return files
        except:
            return []

class CodexWorker(BaseWorker):
    def __init__(self, tracer: Optional[TraceCapture] = None):
        super().__init__("codex", tracer)

    def ask(self, task: str) -> WorkerResult:
        # Placeholder for real Codex CLI call
        # e.g., subprocess.run(["codex", "ask", task])
        typer_echo_cmd = ["echo", f"Codex task: {task}"]
        return self._run_command(typer_echo_cmd)

class GeminiWorker(BaseWorker):
    def __init__(self, tracer: Optional[TraceCapture] = None):
        super().__init__("gemini", tracer)

    def ask(self, task: str) -> WorkerResult:
        # Placeholder for real Gemini CLI call
        typer_echo_cmd = ["echo", f"Gemini task: {task}"]
        return self._run_command(typer_echo_cmd)
