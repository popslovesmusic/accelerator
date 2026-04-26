# `run_many.ps1`

Batch runner for the Acellorator tool ecosystem.

## Examples

Run a tool by name (resolved via `tool_manifest.json`):

```powershell
pwsh -File utilities/run_many.ps1 `
  -Tool ca_admissibility_sim_v1 `
  -Configs "ca_admissibility_sim_v1/configs/*.json" `
  -OutRoot "outputs/batch_ca"
```

Override seeds without touching the original configs:

```powershell
pwsh -File utilities/run_many.ps1 `
  -Tool structural_box_sim_v2 `
  -Configs "structural_box_sim_v2/configs/default.json" `
  -Seeds 1001,1002,1003 `
  -OutRoot "outputs/batch_box"
```

Run an explicit script path instead of a tool name:

```powershell
pwsh -File utilities/run_many.ps1 `
  -Script "ca_admissibility_sim_v1/sim.py" `
  -Configs "outputs/ca_seeded_demo_config.json" `
  -Seeds 123,124 `
  -OutRoot "outputs/batch_ca_demo"
```

## Outputs

- Runs: `<OutRoot>/runs/<run_name>/`
- Generated configs (when `-Seeds` used): `<OutRoot>/configs_generated/`
- Index: `<OutRoot>/analysis/index.csv`

