import argparse
import json
import os
import sys
import subprocess
import time
import shlex
import datetime
import hashlib
import math
import statistics
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

def log(msg, level="INFO"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {msg}")

def get_git_commit():
    try:
        res = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except:
        return "unknown"

def hash_file(path):
    try:
        hasher = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except:
        return "unknown"

class MultiSimRunner:
    def __init__(self, config_path, dry_run=False, max_workers=None, stop_on_failure=None):
        self.config_path = Path(config_path)
        self.dry_run = dry_run
        self.config = None
        self.manifest = None
        self.output_root = None
        self.max_workers = max_workers
        self.stop_on_failure = stop_on_failure
        self.jobs = []
        self.expanded_jobs = []
        self.results = []
        self.source_commit = get_git_commit()
        self.config_hash = hash_file(config_path)

    def preflight(self):
        log(f"Loading config from {self.config_path} (hash: {self.config_hash[:8]})")
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)

        self.output_root = Path(self.config.get("output_root", f"outputs/{self.config['run_id']}"))
        self.output_root.mkdir(parents=True, exist_ok=True)
        (self.output_root / "logs").mkdir(exist_ok=True)
        (self.output_root / "jobs").mkdir(exist_ok=True)

        manifest_path = Path(self.config.get("manifest_path", "tool_manifest.json"))
        log(f"Loading tool manifest from {manifest_path}")
        with open(manifest_path, 'r') as f:
            self.manifest = json.load(f)
        
        self.tools = {t["name"]: t for t in self.manifest["tools"]}

        if self.max_workers is None:
            self.max_workers = self.config.get("execution", {}).get("max_workers", 4)
        
        if self.stop_on_failure is None:
            self.stop_on_failure = self.config.get("governance", {}).get("stop_on_failure", True)

        self.validate_jobs()
        self.expand_jobs()

        preflight_report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "config_path": str(self.config_path),
            "config_hash": self.config_hash,
            "source_commit": self.source_commit,
            "output_root": str(self.output_root),
            "jobs_count": len(self.config["jobs"]),
            "expanded_jobs_count": len(self.expanded_jobs),
            "status": "ready"
        }
        with open(self.output_root / "preflight_report.json", 'w') as f:
            json.dump(preflight_report, f, indent=2)

        if self.config.get("governance", {}).get("dry_run_first", True) and not self.dry_run:
            self.generate_dry_run_plan()

    def validate_jobs(self):
        log("Validating jobs...")
        governance = self.config.get("governance", {})
        
        readiness = {
            "tools_checked": [],
            "certification_manifest_present": {},
            "validation_dir_present": {},
            "missing_artifacts": {},
            "runner_readiness_status": "ready"
        }

        for job in self.config["jobs"]:
            tool_name = job["tool"]
            if tool_name not in readiness["tools_checked"]:
                readiness["tools_checked"].append(tool_name)
            
            if tool_name not in self.tools:
                msg = f"Tool '{tool_name}' not found in manifest."
                log(msg, "ERROR")
                readiness["runner_readiness_status"] = "blocked"
                readiness["missing_artifacts"][tool_name] = readiness["missing_artifacts"].get(tool_name, []) + ["manifest_entry"]
                raise ValueError(msg)
            
            tool = self.tools[tool_name]
            if "entry_point" not in tool or "cli_command" not in tool:
                msg = f"Tool '{tool_name}' missing entry_point or cli_command in manifest."
                log(msg, "ERROR")
                readiness["runner_readiness_status"] = "blocked"
                readiness["missing_artifacts"][tool_name] = readiness["missing_artifacts"].get(tool_name, []) + ["manifest_fields"]
                raise ValueError(msg)

            cert_path = Path(tool_name) / "validation" / "certification_manifest.json"
            cert_exists = cert_path.exists()
            readiness["certification_manifest_present"][tool_name] = cert_exists
            
            if not cert_exists:
                readiness["missing_artifacts"][tool_name] = readiness["missing_artifacts"].get(tool_name, []) + ["certification_manifest"]
                if governance.get("require_tool_certification", False):
                    msg = f"Certification manifest missing for tool '{tool_name}' at {cert_path}"
                    log(msg, "ERROR")
                    readiness["runner_readiness_status"] = "blocked"
                    raise ValueError(msg)
                else:
                    if readiness["runner_readiness_status"] == "ready":
                        readiness["runner_readiness_status"] = "degraded"

            val_dir = Path(tool_name) / "validation"
            val_dir_exists = val_dir.is_dir()
            readiness["validation_dir_present"][tool_name] = val_dir_exists
            
            if not val_dir_exists:
                readiness["missing_artifacts"][tool_name] = readiness["missing_artifacts"].get(tool_name, []) + ["validation_dir"]
                if governance.get("require_validation_dir", False):
                    msg = f"Validation directory missing for tool '{tool_name}'"
                    log(msg, "ERROR")
                    readiness["runner_readiness_status"] = "blocked"
                    raise ValueError(msg)
                else:
                    if readiness["runner_readiness_status"] == "ready":
                        readiness["runner_readiness_status"] = "degraded"

            job_config = Path(job["config"])
            if not job_config.exists():
                msg = f"Job config file '{job_config}' not found."
                log(msg, "ERROR")
                readiness["runner_readiness_status"] = "blocked"
                raise ValueError(msg)

        with open(self.output_root / "tool_readiness_summary.json", 'w') as f:
            json.dump(readiness, f, indent=2)

    def expand_jobs(self):
        log("Expanding jobs by seed...")
        for job in self.config["jobs"]:
            seeds = job.get("seeds", [None])
            for seed in seeds:
                expanded_job = job.copy()
                expanded_job["seed"] = seed
                self.expanded_jobs.append(expanded_job)

    def generate_dry_run_plan(self):
        log("Generating dry run plan...")
        plan = {
            "run_id": self.config["run_id"],
            "mode": self.config["mode"],
            "expanded_jobs": []
        }
        for job in self.expanded_jobs:
            cmd = self.resolve_command(job)
            plan["expanded_jobs"].append({
                "job_id": job["job_id"],
                "seed": job["seed"],
                "command": cmd,
                "output_dir": str(self.get_job_output_dir(job))
            })
        
        with open(self.output_root / "dry_run_plan.json", 'w') as f:
            json.dump(plan, f, indent=2)

    def resolve_command(self, job):
        tool = self.tools[job["tool"]]
        cmd_template = tool["cli_command"]
        
        job_config = Path(job["config"]).as_posix()
        out_dir = Path(self.get_job_output_dir(job)).as_posix()
        
        # C4 Enhancement: Only inject {config} if present in template
        cmd = cmd_template
        if "{config}" in cmd:
            cmd = cmd.replace("{config}", job_config)
        elif "config" in tool.get("config_params", []):
             # heuristic: if config_params has 'config' but template doesn't have {config}
             # we might need to append it? For now, we trust the template.
             pass
             
        cmd = cmd.replace("{out_dir}", out_dir)
        cmd = cmd.replace("{out}", out_dir) # support both
        
        # Add seed if applicable and requested
        if job["seed"] is not None and "seed_arg" in job.get("args", {}):
            seed_arg = job["args"]["seed_arg"]
            cmd += f" {seed_arg} {job['seed']}"

        # Add other args
        for k, v in job.get("args", {}).items():
            if k == "seed_arg": continue
            cmd += f" --{k} {v}"
            
        return cmd

    def get_job_output_dir(self, job):
        subdir = job.get("output_subdir", f"jobs/{job['job_id']}")
        if job["seed"] is not None:
            return self.output_root / subdir / f"seed_{job['seed']}"
        return self.output_root / subdir

    def run(self):
        mode = self.config["mode"]
        log(f"Starting execution in {mode} mode")
        
        if self.dry_run:
            self.generate_dry_run_plan()
            log("Dry run complete. No commands executed.")
            return

        if mode == "serial":
            self.run_serial()
        elif mode == "parallel":
            self.run_parallel()
        elif mode == "dependency_graph":
            self.run_dependency_graph()
        else:
            raise ValueError(f"Unknown mode: {mode}")

        self.post_run()

    def execute_job(self, job):
        out_dir = self.get_job_output_dir(job)
        out_dir.mkdir(parents=True, exist_ok=True)
        
        job_config = job["config"]
        # C4 Enhancement: Auto-inject seed into config if no CLI seed_arg is specified
        if job["seed"] is not None and "seed_arg" not in job.get("args", {}):
            try:
                with open(job_config, 'r') as f:
                    cdata = json.load(f)
                cdata["seed"] = job["seed"]
                
                new_config_path = out_dir / "config_seeded.json"
                with open(new_config_path, 'w') as f:
                    json.dump(cdata, f, indent=2)
                
                # Use the new config for this job
                job = job.copy()
                job["config"] = str(new_config_path)
                job_config = str(new_config_path)
            except Exception as e:
                log(f"Failed to inject seed into config: {e}", "WARNING")

        cmd = self.resolve_command(job)
        
        job_full_id = f"{job['job_id']}__seed_{job['seed']}" if job['seed'] is not None else job['job_id']
        stdout_log = self.output_root / "logs" / f"{job_full_id}.stdout.log"
        stderr_log = self.output_root / "logs" / f"{job_full_id}.stderr.log"
        
        log(f"Executing job: {job_full_id}")
        log(f"Command: {cmd}")
        
        start_time = time.time()
        env = os.environ.copy()
        env.update(self.config.get("execution", {}).get("env", {}))
        
        try:
            # Use shell=False as recommended unless configured (we stick to False for safety)
            # shlex.split helps converting cmd string to list
            res = subprocess.run(
                shlex.split(cmd),
                capture_output=True,
                text=True,
                env=env,
                timeout=self.config.get("execution", {}).get("timeout_seconds", 3600),
                cwd=os.getcwd()
            )
            exit_code = res.returncode
            stdout = res.stdout
            stderr = res.stderr
        except Exception as e:
            exit_code = -1
            stdout = ""
            stderr = str(e)
            log(f"Job {job_full_id} failed with error: {e}", "ERROR")

        end_time = time.time()
        
        with open(stdout_log, 'w') as f: f.write(stdout)
        with open(stderr_log, 'w') as f: f.write(stderr)
        
        result = {
            "job_id": job["job_id"],
            "seed": job["seed"],
            "command": cmd,
            "exit_code": exit_code,
            "duration": end_time - start_time,
            "stdout_log": str(stdout_log),
            "stderr_log": str(stderr_log),
            "output_dir": str(out_dir),
            "tool": job["tool"],
            "claim_role": job.get("claim_role", "exploratory"),
            "config_path": job_config
        }
        return result

    def run_serial(self):
        for job in self.expanded_jobs:
            res = self.execute_job(job)
            self.results.append(res)
            if res["exit_code"] != 0 and self.stop_on_failure:
                log(f"Stopping on failure as configured. Job {res['job_id']} failed.", "WARNING")
                break

    def run_parallel(self):
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_job = {executor.submit(self.execute_job, job): job for job in self.expanded_jobs}
            for future in as_completed(future_to_job):
                res = future.result()
                self.results.append(res)
                if res["exit_code"] != 0 and self.stop_on_failure:
                    log(f"Job {res['job_id']} failed. stop_on_failure is True, but parallel execution continues for already started jobs.", "WARNING")
                    # Note: We can't easily cancel already running threads with ThreadPoolExecutor without more complexity
                    # But we can avoid starting new ones if we had a queue.

    def run_dependency_graph(self):
        log("Running dependency graph mode (simple implementation)...")
        # Build graph
        job_map = {job["job_id"]: job for job in self.config["jobs"]}
        # Expanded jobs need to be grouped by job_id to handle dependencies between job groups
        # If A depends on B, all seeds of A depend on all seeds of B completing? 
        # Requirement is a bit vague. Let's assume job level dependency.
        
        completed_jobs = set()
        failed_jobs = set()
        
        pending_job_ids = [j["job_id"] for j in self.config["jobs"]]
        
        while pending_job_ids:
            ready_job_ids = []
            for jid in pending_job_ids:
                deps = job_map[jid].get("depends_on", [])
                if all(d in completed_jobs for d in deps):
                    ready_job_ids.append(jid)
            
            if not ready_job_ids:
                if pending_job_ids:
                    log("Circular dependency or missing dependency detected!", "ERROR")
                    break
                break
            
            # Execute all seeds of ready jobs
            for jid in ready_job_ids:
                log(f"Starting job group: {jid}")
                job_seeds = [ej for ej in self.expanded_jobs if ej["job_id"] == jid]
                group_failed = False
                
                # We could run seeds in parallel here too, but let's keep it simple
                for ej in job_seeds:
                    res = self.execute_job(ej)
                    self.results.append(res)
                    if res["exit_code"] != 0:
                        group_failed = True
                
                if group_failed:
                    failed_jobs.add(jid)
                    if self.stop_on_failure:
                        log(f"Job group {jid} failed. Stopping.", "ERROR")
                        return
                else:
                    completed_jobs.add(jid)
                
                pending_job_ids.remove(jid)

    def post_run(self):
        log("Post-run processing...")
        run_manifest = {
            "run_id": self.config["run_id"],
            "timestamp": datetime.datetime.now().isoformat(),
            "source_commit": self.source_commit,
            "config_hash": self.config_hash,
            "results": self.results
        }
        with open(self.output_root / "run_manifest.json", 'w') as f:
            json.dump(run_manifest, f, indent=2)

        failed = [r for r in self.results if r["exit_code"] != 0]
        failed_jobs_file = self.output_root / "failed_jobs.json"
        if failed:
            with open(failed_jobs_file, 'w') as f:
                json.dump(failed, f, indent=2)
            log(f"{len(failed)} jobs failed.", "WARNING")
        elif failed_jobs_file.exists():
            failed_jobs_file.unlink()

        self.generate_claim_gate_input()
        self.generate_certification_evidence_packet()
        self.generate_uncertainty_summary()

    def generate_claim_gate_input(self):
        log("Generating claim gate input packet...")
        tools_used = {}
        for res in self.results:
            tname = res["tool"]
            if tname not in tools_used:
                t = self.tools[tname]
                tools_used[tname] = {
                    "tool_name": tname,
                    "model_class": t.get("model_class", ""),
                    "certification_level": t.get("certification_level", ""),
                    "recoverable_outputs": []
                }
            tools_used[tname]["recoverable_outputs"].append(res["output_dir"])

        claim_gate_input = {
            "run_id": self.config["run_id"],
            "generated_by": "multi_sim_runner.py",
            "source_commit": self.source_commit,
            "config_hash": self.config_hash,
            "claim_interpretation_allowed": False,
            "tools": list(tools_used.values()),
            "evidence": {
                "model_classes_count": len(set(t["model_class"] for t in tools_used.values())),
                "seeds_used": len(set(res["seed"] for res in self.results if res["seed"] is not None)),
                "recoverable_output_paths": [res["output_dir"] for res in self.results],
                "falsification_run": any(res["claim_role"] == "falsification" for res in self.results),
                "observables": [] # To be filled by analysis
            },
            "notes": ["This packet is evidence input only. It does not classify claims."]
        }
        
        with open(self.output_root / "claim_gate_input.json", 'w') as f:
            json.dump(claim_gate_input, f, indent=2)

    def generate_uncertainty_summary(self):
        log("Generating uncertainty summary across seeds...")
        job_groups = {}
        for res in self.results:
            jid = res["job_id"]
            if jid not in job_groups:
                job_groups[jid] = []
            job_groups[jid].append(res)
            
        summary = {
            "run_id": self.config["run_id"],
            "timestamp": datetime.datetime.now().isoformat(),
            "jobs": {}
        }
        
        for jid, group in job_groups.items():
            if len(group) < 2:
                continue
                
            metrics_collection = {}
            for res in group:
                out_dir = Path(res["output_dir"])
                metric_files = ["v2p3_report.json", "summary.json", "v2p3_precision_report.json"]
                data = None
                for mf in metric_files:
                    path = out_dir / mf
                    if path.exists():
                        try:
                            with open(path, 'r') as f:
                                data = json.load(f)
                            break
                        except:
                            continue
                
                if data:
                    self._extract_numerical_metrics(data, metrics_collection)
            
            if metrics_collection:
                job_stats = {}
                for mname, values in metrics_collection.items():
                    if len(values) >= 2:
                        mean = statistics.mean(values)
                        stdev = statistics.stdev(values) if len(values) > 1 else 0.0
                        stderr = stdev / math.sqrt(len(values))
                        ci95 = 1.96 * stderr
                        job_stats[mname] = {
                            "mean": mean,
                            "stdev": stdev,
                            "stderr": stderr,
                            "ci95_low": mean - ci95,
                            "ci95_high": mean + ci95,
                            "sample_size": len(values)
                        }
                if job_stats:
                    summary["jobs"][jid] = job_stats
                    
        with open(self.output_root / "uncertainty_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)

    def _extract_numerical_metrics(self, data, collection, prefix=""):
        if isinstance(data, dict):
            for k, v in data.items():
                new_prefix = f"{prefix}.{k}" if prefix else k
                self._extract_numerical_metrics(v, collection, new_prefix)
        elif isinstance(data, (int, float)) and not isinstance(data, bool):
            if prefix not in collection:
                collection[prefix] = []
            collection[prefix].append(data)

    def generate_certification_evidence_packet(self):
        log("Generating certification evidence packet...")
        tools_used = sorted(list(set(res["tool"] for res in self.results)))
        seeds = sorted(list(set(res["seed"] for res in self.results if res["seed"] is not None)))
        outputs = [res["output_dir"] for res in self.results]
        failures = [res["job_id"] for res in self.results if res["exit_code"] != 0]
        
        found_artifacts = []
        missing_artifacts = []
        
        for tname in tools_used:
            cert_path = Path(tname) / "validation" / "certification_manifest.json"
            if cert_path.exists():
                found_artifacts.append(str(cert_path))
            else:
                missing_artifacts.append(f"{tname}:certification_manifest")
            
            val_dir = Path(tname) / "validation"
            if val_dir.is_dir():
                found_artifacts.append(str(val_dir))
            else:
                missing_artifacts.append(f"{tname}:validation_dir")

        packet = {
            "run_id": self.config["run_id"],
            "tools_used": tools_used,
            "seeds_executed": seeds,
            "outputs_generated": outputs,
            "validation_artifacts_found": found_artifacts,
            "validation_artifacts_missing": missing_artifacts,
            "execution_failures": failures,
            "provenance_ready": len(missing_artifacts) == 0 and len(failures) == 0
        }
        
        with open(self.output_root / "certification_evidence_packet.json", 'w') as f:
            json.dump(packet, f, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Governed Multi-Tool Simulation Runner")
    parser.add_argument("--config", type=str, required=True, help="Path to multi-run config JSON")
    parser.add_argument("--dry-run", action="store_true", help="Do not execute simulation commands")
    parser.add_argument("--max-workers", type=int, help="Override max workers for parallel mode")
    parser.add_argument("--stop-on-failure", action="store_true", default=None, help="Override stop on failure setting")
    args = parser.parse_args()

    runner = MultiSimRunner(args.config, dry_run=args.dry_run, max_workers=args.max_workers, stop_on_failure=args.stop_on_failure)
    try:
        runner.preflight()
        runner.run()
    except Exception as e:
        log(f"Runner failed: {e}", "ERROR")
        sys.exit(1)
