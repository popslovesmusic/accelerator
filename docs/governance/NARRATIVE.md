# Welcome to the One Process: An Onboarding Narrative

Welcome, Researcher. You have just stepped into the **Acellorator Research Ecosystem**. 

This is not merely a repository of simulation scripts; it is a governed engine for exploring **"THE LAW OF THE ONE PROCESS."** Our mission is to move beyond "object-oriented" physics\_app and into a world where everything—from particle\_analog swarms to the vacuum\_analog itself—is understood as a series of irreducible processes\_proc.

Here is your guide to surviving and contributing to this high-rigor environment.

---

### 1. The Core Philosophy
In this repo, we do not believe in "things" that interact. We believe in **processes** that constrain one another. All our work is mapped to five core primitives:
*   **$\epsilon$ (Epsilon):** Mismatch or signal pressure.
*   **$R$ (Residue):** The memory or trace left by a process.
*   **$\rho$ (Rho):** The capacity for a process to continue.
*   **$K$ (CSI):** The coupling reach or interaction domain.
*   **$-(i)$:** Admissibility orientation.

If you can’t describe your simulation results using these terms, you aren't doing "One Process" science yet.

### 1.1 The Math Core (Interpretation, Not Proof)
The repository includes a stabilized **math core** (`docs/math/` and `registry/math/`) that defines operators, law families, failure families, gaps, and proof obligations. It functions as an **interpretive and governance layer**:
- it constrains what simulation outputs are allowed to mean,
- it labels formal status (e.g., NOT_PROVEN / restricted-domain),
- and it blocks claim inflation (no theorem elevation, no ontology closure, no physics escalation).

All writing that uses simulation evidence must use claim-humble language, beginning with: **"Within these models..."**.

### 2. The Two Worlds: Python and C++
Our ecosystem is built on a **Requirement of Equivalence**. 
*   **The Python World:** This is where we think. We have 15+ prototypes (NumPy-based) that define the logical baseline. They are readable, flexible, and serve as the "Source of Truth" for how a model *should* behave.
*   **The C++ World:** This is where we work. We have 23 high-performance engines (AVX2 and SYCL/GPU optimized) that can process millions of agents or grid cells. 

**Your Mandate:** A C++ engine is not "Verified" until it passes a regression test against its Python counterpart. Performance must never come at the cost of logic.

### 3. C4 Status: The Standard of Rigor
You will notice the term **"C4 Status"** everywhere. In most labs, "it runs" is enough. Here, it is just the beginning. To reach C4, a tool must prove its worth through:
1.  **Multi-Seed Stability:** We don't trust single runs. We run 5–10 seeds and calculate the variance.
2.  **Uncertainty Quantification (UQ):** We report 95% Confidence Intervals. If the error bars are too wide, the tool is "Blocked."
3.  **Falsification:** We run "Negative Controls." We try to make the simulation fail by removing energy preservation or breaking symmetry. If it *doesn't* fail when it should, the engine is lying to us.
4.  **Provenance:** Every data point is tagged with the Git commit, the config hash, and the hardware backend (CPU vs GPU drift).

### 4. The Orchestrator: `multi_sim_runner.py`
You will rarely run a single `.py` or `.exe` file manually. Instead, you will use the **Governed Multi-Sim Runner**. 
You provide a JSON config, and the runner handles:
*   **Serial/Parallel Execution.**
*   **Seed Injection.**
*   **Statistical Analysis.**
*   **Governance Packet Emission:** It generates a `claim_gate_input.json`. This is the only document the "Unified Claim Gate" accepts for peer review.

### 5. Claim Humility
The most important rule in this ecosystem is **Humility**. 
We do not claim to find "Universal Truth." All your papers, reports, and READMEs must begin with the phrase: **“Within these models…”** 

We are simulators of process, not masters of reality.

---

### Where to Start?
1.  **Read `registry/tool_manifest.json`:** See the 38 tools available to you.
2.  **Check `docs/reports/TOOL_SCIENTIFIC_RIGOR_REPORT_2026-04-30.md`:** See which tools are C4-ready and which are blocked.
3.  **Run a Smoke Test:** Try `python scripts/multi_sim_runner.py --config configs/multi_runs/example_multi_sim_run.json`.
4.  **Consult the Lexicon:** Check `docs/theory/foundational/` to understand the mathematical grounding of your specific simulator.

Welcome to the process. **Stay rigorous. Stay humble.**
