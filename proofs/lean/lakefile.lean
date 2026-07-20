import Lake
open Lake DSL

package «mpf_closure_pilot» where
  -- Package configuration options
  leanOptions := #[
    ⟨`pp.unicode.fun, true⟩ -- pretty-prints 'fun a => b' as 'λ a => b'
  ]

@[default_target]
lean_lib «MpfClosurePilot» where
  -- Module target configuration
