import os
import sys
import io
import json
import uuid
import platform
import hashlib
from datetime import datetime

# Sentinel constants and their hashes
NO_CONFIGURATION_SENTINEL = "NO_CONFIGURATION"
NO_CONFIGURATION_HASH = hashlib.sha256(NO_CONFIGURATION_SENTINEL.encode('utf-8')).hexdigest()

NO_EXTERNAL_INPUTS_SENTINEL = "NO_EXTERNAL_INPUTS"
NO_EXTERNAL_INPUTS_HASH = hashlib.sha256(NO_EXTERNAL_INPUTS_SENTINEL.encode('utf-8')).hexdigest()

class Tee(object):
    def __init__(self, original_stream):
        self.original_stream = original_stream
        self.buffer = io.StringIO()
        
    def write(self, data):
        self.original_stream.write(data)
        self.buffer.write(data)
        
    def flush(self):
        self.original_stream.flush()

# Setup stdout and stderr capture immediately upon import
sys.stdout = Tee(sys.stdout)
sys.stderr = Tee(sys.stderr)

def get_file_sha256(filepath):
    if not os.path.exists(filepath):
        return None
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def log_run(attack_id, full_packet, exit_code=0, termination_reason="COMPLETED"):
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    short_hash = uuid.uuid4().hex[:8]
    run_id = f"RUN-{attack_id}-{timestamp}-{short_hash}"
    
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    run_dir = os.path.join(workspace_dir, "run_outputs", attack_id, run_id)
    
    # Immutability policy check: raise error if run directory already exists
    if os.path.exists(run_dir):
        raise FileExistsError(f"Immutability violation: run directory {run_dir} already exists.")
        
    os.makedirs(run_dir)
    
    # Save stdout and stderr captures
    stdout_content = sys.stdout.buffer.getvalue()
    stderr_content = sys.stderr.buffer.getvalue()
    
    stdout_path = os.path.join(run_dir, "stdout.txt")
    with open(stdout_path, "w", encoding="utf-8") as f:
        f.write(stdout_content)
        
    stderr_path = os.path.join(run_dir, "stderr.txt")
    with open(stderr_path, "w", encoding="utf-8") as f:
        f.write(stderr_content)
        
    stdout_sha = hashlib.sha256(stdout_content.encode('utf-8')).hexdigest()
    stderr_sha = hashlib.sha256(stderr_content.encode('utf-8')).hexdigest()
    
    # Save the output packet
    output_path = os.path.join(run_dir, "outputs.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(full_packet, f, indent=2)
    output_sha = get_file_sha256(output_path)
    
    # Environment info
    env_info = {
        "python_version": platform.python_version(),
        "operating_system": platform.platform(),
        "cpu": platform.processor(),
        "working_directory": os.getcwd(),
        "sys_path": sys.path
    }
    env_path = os.path.join(run_dir, "environment.json")
    with open(env_path, "w", encoding="utf-8") as f:
        json.dump(env_info, f, indent=2)
        
    # Command info
    cmd_info = " ".join(sys.argv)
    cmd_path = os.path.join(run_dir, "command.txt")
    with open(cmd_path, "w", encoding="utf-8") as f:
        f.write(cmd_info)
        
    # Source hash
    source_script = sys.argv[0]
    source_sha = get_file_sha256(source_script)
    if not source_sha:
        source_sha = "unknown"

    # Dependency lock hash. The lock path and its digest travel with every run
    # so a replay can distinguish the declared environment from ambient state.
    dependency_lock_path = os.path.join(workspace_dir, "requirements.lock")
    dependency_lock_sha = get_file_sha256(dependency_lock_path)
    if not dependency_lock_sha:
        dependency_lock_sha = "unknown"
        
    # Inputs/Configuration hashes (following sentinel policy)
    config_sha = NO_CONFIGURATION_HASH
    input_sha = NO_EXTERNAL_INPUTS_HASH
    
    # Empty inputs.json placeholder
    inputs_path = os.path.join(run_dir, "inputs.json")
    with open(inputs_path, "w", encoding="utf-8") as f:
        json.dump({"configuration": NO_CONFIGURATION_SENTINEL, "inputs": NO_EXTERNAL_INPUTS_SENTINEL}, f, indent=2)
        
    # Build run record
    run_record = {
        "run_id": run_id,
        "attack_id": attack_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "python_version": platform.python_version(),
        "dependency_lock_path": "requirements.lock",
        "dependency_lock_sha256": dependency_lock_sha,
        "operating_system": platform.platform(),
        "runtime_information": env_info,
        "tool_versions": {"python": platform.python_version()},
        "random_seeds": [42],
        "source_sha256": source_sha,
        "configuration_sha256": config_sha,
        "input_sha256": input_sha,
        "exact_command": cmd_info,
        "working_directory": os.getcwd(),
        "runtime_limit": 60,
        "candidate_limit": 100,
        "search_depth_limit": 10,
        "termination_reason": termination_reason,
        "stdout_path": "stdout.txt",
        "stderr_path": "stderr.txt",
        "exit_code": exit_code,
        "output_paths": ["outputs.json"],
        "output_sha256": [output_sha],
        "run_record_sha256": ""
    }
    
    # Calculate run_record_sha256 excluding own field
    record_bytes = json.dumps(run_record, indent=2).encode('utf-8')
    record_sha = hashlib.sha256(record_bytes).hexdigest()
    run_record["run_record_sha256"] = record_sha
    
    record_path = os.path.join(run_dir, "run_record.json")
    with open(record_path, "w", encoding="utf-8") as f:
        json.dump(run_record, f, indent=2)
        
    # Write latest pointer in campaigns
    pointer = {
        "attack_id": attack_id,
        "run_id": run_id,
        "relative_output_path": f"run_outputs/{attack_id}/{run_id}/outputs.json",
        "output_sha256": output_sha
    }
    pointer_path = os.path.join(workspace_dir, "campaigns", "latest_run_pointer.json")
    with open(pointer_path, "w", encoding="utf-8") as f:
        json.dump(pointer, f, indent=2)
        
    print(f"\n[run_logger] Captured run logged successfully to {run_dir}")
