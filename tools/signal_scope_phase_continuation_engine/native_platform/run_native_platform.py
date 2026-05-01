import os
import json
import numpy as np
from datetime import datetime

from .engine_bridge import EngineBridge
from .signalscope_core import SignalScope
from .hex_state import make_full_hex
from .wheel12_projection import project_to_12, apply_operator_pressure
from .v14_bridge import V14Bridge
from .residue_imprinter import qualify_and_commit
from .feedback_adapter import FeedbackAdapter
from .residue_feedback import residue_bias
from .phase_space import compute_phase_vector, phase_mismatch
from .residue_phase_continuation import ResiduePhaseContinuation
from .phase_operator_map import operator_pressure
from .operator_selection import select_operator, apply_operator
from .groove_router import GrooveRouter
from .signal_layer import compute_x_channel, get_consistency_level
from .inductive_transformer import InductiveTransformerLayer

from core.memory_layer import load_memory_state, save_memory_state

def run_platform(num_frames=100, num_nodes=100, engine_steps_per_frame=None, feedback_enabled=None, run_id=None, input_signals=None, memory_path="sessions/native_memory.json", connected=True, connected_state="train", ablation_cfg=None, thresholds=None):
    print(f"🚀 Initializing Native Wave-Residue Platform (Mode: {connected_state.upper()})...")
    
    if ablation_cfg is None:
        ablation_cfg = {}

    # Load Feedback Config
    fb_config_path = "native_platform/feedback_config.json"
    if os.path.exists(fb_config_path):
        with open(fb_config_path, 'r') as f:
            fb_config = json.load(f)
    else:
        fb_config = {"feedback": {"enabled": False}}
    
    # Apply CLI/Interface Overrides
    if engine_steps_per_frame is not None:
        fb_config.setdefault("feedback", {})["engine_steps_per_frame"] = engine_steps_per_frame
    if feedback_enabled is not None:
        fb_config.setdefault("feedback", {})["enabled"] = feedback_enabled
    
    # Merge passed thresholds
    if thresholds:
        fb_config.setdefault("thresholds", {}).update(thresholds)

    # Check input signal length
    if input_signals is not None:
        num_frames = len(input_signals)

    # 1. Initialize Components
    engine = EngineBridge(num_nodes=num_nodes)
    scope = SignalScope()
    v14 = V14Bridge()
    
    memory = load_memory_state(memory_path)
    
    # Patch 17/20/23: Phase Continuation with survivability gating
    phase_continuation = ResiduePhaseContinuation(
        history_size=64, 
        trace_size=128, 
        successful_traversals=memory.successful_traversals,
        thresholds=fb_config.get("thresholds")
    )
    
    # Patch 22: Initialize GrooveRouter from memory
    router = GrooveRouter.from_dict(memory.groove_data)
    
    # Patch 24: Inductive Transformer Layer
    transformer = InductiveTransformerLayer(channels=8)
    
    feedback = FeedbackAdapter(fb_config)
    
    # Initial states for feedback
    last_state = type('obj', (object,), {'caution_scalar': 0.0, 'recovery_scalar': 0.0, 'hold_state': False, 'components': []})
    last_residue = None
    
    # Track metrics for engine injection and transition
    last_flow_bias = 0.0
    last_continuation_mismatch = 0.0
    
    # Prior states for selections
    prev_phi = None
    pending_phi_continued = None
    prev_phi_oriented = None
    mismatch_series = []
    
    # Patch 24: Track frequency drift
    last_omega = np.zeros(8)

    # Optimization Phase 4: Integrated C++ Core Toggle
    use_integrated_cpp_core = ablation_cfg.get("use_integrated_cpp", True)
    
    if run_id is None:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    os.makedirs('logs', exist_ok=True)
    os.makedirs('sessions', exist_ok=True)
    feedback_trace_path = f"logs/feedback_trace_{run_id}.jsonl"
    
    print(f"Starting loop for {num_frames} frames (Run ID: {run_id})...")
    
    # Pre-process signals if using integrated core
    integrated_phases = None
    integrated_mismatches = None
    if use_integrated_cpp_core and engine.engine is not None:
        print("⚡ Using Integrated C++ Core for Physics & Phase Space...")
        if input_signals is not None:
            sig_batch = np.asarray(input_signals, dtype=np.float32)
            is_eeg = sig_batch.ndim == 2
        else:
            t_vals = np.arange(num_frames, dtype=np.float32)
            sig_batch = np.sin(t_vals * 0.1)
            is_eeg = False
            
        steps_per_frame = int(fb_config.get('feedback', {}).get('engine_steps_per_frame', 20))
        integrated_phases, integrated_mismatches = engine.engine.run_phase_continuation_mission_avx2(
            sig_batch, steps_per_frame, is_eeg
        )

    # Open log file once for buffered writing
    with open(feedback_trace_path, "a", encoding="utf-8") as f_log:
        # FV-1: Shuffle input signals if requested
        if ablation_cfg.get("shuffle_input") and input_signals is None:
            # Generate synthetic sine and shuffle it
            t_vals = np.arange(num_frames)
            input_signals = np.sin(t_vals * 0.1)
            np.random.shuffle(input_signals)

        for t in range(num_frames):
            # A. Signal Generation
            if input_signals is not None:
                raw_input = input_signals[t]
                if isinstance(raw_input, (np.ndarray, list)):
                    input_signal_actual = float(np.mean(raw_input))
                    scope_input_actual = np.asarray(raw_input)
                else:
                    input_signal_actual = float(raw_input)
                    scope_input_actual = input_signal_actual
            else:
                input_signal_actual = np.sin(t * 0.1)
                scope_input_actual = input_signal_actual

            # B/C. Step Engine & Phase Computation (Integrated or Legacy)
            if integrated_phases is not None:
                phi_actual = integrated_phases[t]
                raw_mismatch = float(integrated_mismatches[t])
                # Mock internal scope data from phi
                scope_data_actual = {
                    'W_local': phi_actual[0:3],
                    'W_global': phi_actual[0:3], # simplified
                    'W_meta': phi_actual[0:3],
                    'C': phi_actual[3],
                    'E': phi_actual[4],
                    'V': phi_actual[5:8]
                }
                scope_data_internal = scope_data_actual
                signal_x = 0.95 
            else:
                # Legacy Frame-by-Frame Path
                input_signal = input_signal_actual if connected else 0.0
                scope_input = scope_input_actual if connected else np.zeros_like(scope_input_actual)
                base_bias = feedback.update(last_state, last_residue) if fb_config["feedback"]["enabled"] else 1.0
                r_bias = 1.0 if ablation_cfg.get("disable_residue") else residue_bias(last_residue)
                control_pattern = base_bias * r_bias
                flow_feedback_gain = float(fb_config.get('feedback', {}).get('flow_feedback_gain', 0.2))
                control_pattern = control_pattern * (1.0 + flow_feedback_gain * last_flow_bias)
                smooth_mismatch = np.mean(mismatch_series[-5:]) if len(mismatch_series) > 0 else 0.0
                control_pattern *= (1.0 - 0.02 * smooth_mismatch)
                min_b = float(fb_config.get('feedback', {}).get('min_bias', 0.5))
                max_b = float(fb_config.get('feedback', {}).get('max_bias', 2.0))
                control_pattern = float(np.clip(control_pattern, min_b, max_b))

                engine_steps = int(fb_config.get('feedback', {}).get('engine_steps_per_frame', 20))
                engine_mean = engine.evolve(input_signal, control_pattern, steps=engine_steps)
                node_outputs = engine.get_node_outputs()
                
                if isinstance(scope_input_actual, np.ndarray):
                    scope_data_actual = scope.update(scope_input_actual)
                else:
                    scope_data_actual = scope.update(node_outputs)
                
                if not connected:
                    scope_data_internal = scope.update(np.zeros_like(node_outputs))
                else:
                    scope_data_internal = scope_data_actual

                signal_x = compute_x_channel(scope_data_internal['W_local'], scope_data_internal['W_global'])
                phi_actual = compute_phase_vector(
                    scope_data_actual['W_local'],
                    scope_data_actual['C'],
                    scope_data_actual['E'],
                    scope_data_actual['V']
                )
                raw_mismatch = float(phase_mismatch(pending_phi_continued, phi_actual)) if pending_phi_continued is not None else 0.0

            # D. Remaining Logic (Operator Selection, Reasoning, Imprinting)
            if ablation_cfg.get("force_operator"):
                op_star, op_cost = "++", 0.0
            else:
                op_star, op_cost = select_operator(phi_actual, prev_phi)
            
            phi_oriented_actual = apply_operator(phi_actual, op_star)

            # Leakage Control: Internal model sees its own PREVIOUS PREDICTION if disconnected
            phi_for_internal = phi_oriented_actual if connected else (pending_phi_continued if pending_phi_continued is not None else phi_oriented_actual)

            # Patch 23: Survivability Gating (uses internal perception)
            if connected:
                eff_signal_x = 1.0 if ablation_cfg.get("disable_signal_x") else signal_x
                decision, failed_tests = phase_continuation.evaluate_survivability(
                    phi_for_internal, 
                    raw_mismatch, 
                    op_star, 
                    eff_signal_x
                )
                if ablation_cfg.get("disable_survivability_gate"):
                    decision = "reinforce"
            else:
                decision, failed_tests = "hold", ["disconnected_protocol"]
            
            continuation_mismatch = raw_mismatch if connected else last_continuation_mismatch

            # Patch 24: Inductive Transformer Layer Update
            if ablation_cfg.get("disable_inductive_layer"):
                phi_inductive = np.zeros(8)
            else:
                phi_inductive = transformer.update(phi_for_internal, scope_data_internal['C'], signal_x, connected=connected)
            
            phase_error = float(phase_mismatch(phi_oriented_actual, phi_inductive))
            freq_drift = float(np.linalg.norm(transformer.omega - last_omega))
            last_omega = transformer.omega.copy()

            if connected and not ablation_cfg.get("disable_groove_memory"):
                active_groove, route_score = router.route(prev_phi_oriented, phi_oriented_actual, op_star)
            else:
                active_groove, route_score = None, 0.0
            
            groove_feedback_vec = router.active_feedback_vector()

            phi_continued = phase_continuation.continue_next(
                phi_for_internal, 
                decision,
                external_feedback_vec=groove_feedback_vec,
                inductive_feedback_vec=phi_inductive
            )
            
            mismatch_series.append(continuation_mismatch)

            if connected:
                if not ablation_cfg.get("disable_residue"):
                    phase_continuation.store_trace_segment(prev_phi_oriented, phi_oriented_actual, continuation_mismatch, decision)
                    phase_continuation.reinforce_trace(phi_oriented_actual, continuation_mismatch, threshold=0.02)
                
                if not ablation_cfg.get("disable_groove_memory"):
                    router.reinforce_active(prev_phi_oriented, phi_oriented_actual, op_star, decision, threshold=0.020)
            
            prev_phi_oriented = phi_oriented_actual.copy()
            op_pressure = operator_pressure(continuation_mismatch, last_continuation_mismatch, scope_data_actual['C'], scope_data_actual['E'], scope_data_actual['V'])

            last_flow_bias = float(np.tanh(np.mean(scope_data_actual['V'])))
            last_continuation_mismatch = continuation_mismatch
            pending_phi_continued = phi_continued.copy()
            
            full_hex = make_full_hex(scope_data_actual["W_local"], scope_data_actual["W_global"], scope_data_actual["W_meta"])
            signature_12, orientation_bias = project_to_12(
                scope_data_actual["W_local"], 
                scope_data_actual["C"], 
                scope_data_actual["E"], 
                scope_data_actual["V"]
            )
            signature_12 = apply_operator_pressure(signature_12, op_pressure)
            
            trace, state = v14.run_turn(signature_12, orientation_bias)
            
            meta_dict = {
                "phi": phi_actual.tolist(),
                "hex": full_hex,
                "continuation_mismatch": continuation_mismatch,
                "op_pressure": op_pressure
            }
            memory, residue = qualify_and_commit(trace, state, memory, t, fb_config, metadata=meta_dict)
            
            status = "IMPRINTED" if residue.is_committed else "SKIPPED"
            geom = transformer.get_raw_geometry()
            
            log_entry = {
                "t": t,
                "input_signal": float(input_signal_actual),
                "control_pattern": float(control_pattern) if integrated_phases is None else 1.0,
                "caution": float(state.caution_scalar),
                "recovery": float(state.recovery_scalar),
                "residue_committed": bool(residue.is_committed),
                "residue_reject_reasons": getattr(residue, 'reject_reasons', []),
                "residue_score": float(getattr(residue, 'stability_score', 0.0)),
                "bias": float(residue_bias(last_residue)) if not ablation_cfg.get("disable_residue") else 1.0,
                "hex": full_hex,
                "C": float(scope_data_actual['C']),
                "E": float(scope_data_actual['E']),
                "V": scope_data_actual['V'].tolist(),
                "phi_current": phi_actual.tolist(),
                "phi_continued": phi_continued.tolist(),
                "continuation_mismatch": continuation_mismatch,
                "continuation_mismatch_next": continuation_mismatch,
                "trace_groove_size": len(phase_continuation.trace_buffer),
                "trace_segment_count": len(phase_continuation.trace_segments),
                "trace_feedback_gain": float(phase_continuation.groove_gain()),
                "successful_traversals": int(phase_continuation.successful_traversals),
                "traversal_count": phase_continuation.traversal_count,
                "op_pressure": op_pressure,
                "active_groove_id": router.active_groove_id,
                "groove_count": len(router.grooves),
                "groove_score": float(route_score),
                "operator_star": op_star,
                "survivability_decision": decision,
                "failed_tests": failed_tests,
                "signal_x": signal_x,
                "consistency_level": get_consistency_level(signal_x),
                "phase_error": phase_error,
                "frequency_drift": freq_drift,
                "inductive_L": transformer.L.tolist(),
                "teacher_theta": geom["teacher_theta"],
                "student_theta": geom["student_theta"],
                "teacher_amp": geom["teacher_amp"],
                "student_amp": geom["student_amp"],
                "teacher_omega": geom["teacher_omega"],
                "student_omega": geom["student_omega"],
                "connected": connected,
                "connected_state": connected_state
            }
            f_log.write(json.dumps(log_entry) + "\n")

            if t % 10 == 0:
                gid = router.active_groove_id or "none"
                print(f"Frame {t}: [{full_hex}] C={scope_data_actual['C']:.2f} X={signal_x:.2f} Err={phase_error:.4f} G={gid} ({decision}) -> {status}")

            last_state = state
            last_residue = residue
            prev_phi = phi_actual.copy()

    # 2. Finalize
    if connected and len(mismatch_series) > 0:
        q = len(mismatch_series) // 4
        if q > 0:
            first_mean = np.mean(mismatch_series[:q])
            last_mean = np.mean(mismatch_series[-q:])
            if last_mean <= first_mean:
                phase_continuation.mark_successful_traversal()
            else:
                phase_continuation.mark_failed_traversal()
        else:
            phase_continuation.mark_successful_traversal()

    phase_continuation.mark_traversal_complete()
    memory.successful_traversals = int(phase_continuation.successful_traversals)
    memory.groove_data = router.to_dict()
    
    save_memory_state(memory_path, memory)
    print(f"✅ Run Complete. Trace: logs/feedback_trace_{run_id}.jsonl")
    
    return {
        "run_id": run_id,
        "frames": num_frames,
        "memory_path": memory_path,
        "feedback_trace_path": feedback_trace_path,
        "groove_summary": router.summary()
    }

if __name__ == "__main__":
    run_platform()
