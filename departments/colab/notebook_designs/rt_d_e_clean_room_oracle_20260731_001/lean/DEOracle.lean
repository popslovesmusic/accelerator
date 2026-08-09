namespace RTDECleanRoom

abbrev ContextId := String
abbrev ProfileId := String
abbrev Payload := List Int
abbrev State := String
/- The Lean scaffold uses Int as an exact bounded numeric instantiation. The
   Python reference evaluator covers finite real-valued computational inputs. -/
abbrev DistinctionValue := Int
abbrev ThresholdEnvironment := ProfileId → Option DistinctionValue

structure Witness where
  token : Payload

structure HistoryStep where
  step : Nat
  state : State

abbrev History := List HistoryStep

structure DRecord where
  relationType : String
  context : ContextId
  targetContext : ContextId
  sourcePayload : Payload
  witness : Option Witness
  history : Option History
  target : State
  profile : ProfileId
  distinction : DistinctionValue

def exactBind (w : Witness) (p : Payload) : Prop := w.token = p
def sameContext (c₁ c₂ : ContextId) : Prop := c₁ = c₂
def knownProfile (p : ProfileId) (env : ThresholdEnvironment) : Prop := ∃ threshold, env p = some threshold ∧ 0 < threshold
def orderedHistory : History → Prop
  | [] => False
  | [_] => True
  | a :: b :: rest => a.step < b.step ∧ orderedHistory (b :: rest)
def terminatesAt (h : History) (target : State) : Prop := ∃ last, h.getLast? = some last ∧ last.state = target
def positiveDistinction (d : DistinctionValue) : Prop := 0 < d
def aboveThreshold (d : DistinctionValue) (p : ProfileId) (env : ThresholdEnvironment) : Prop := ∃ threshold, env p = some threshold ∧ d > threshold

def representableD (r : DRecord) (env : ThresholdEnvironment) : Prop :=
  r.relationType = "SourceRelation" ∧
  sameContext r.context r.targetContext ∧
  knownProfile r.profile env ∧
  (∃ w, r.witness = some w ∧ exactBind w r.sourcePayload) ∧
  (∃ h, r.history = some h ∧ orderedHistory h ∧ terminatesAt h r.target)

def nonCollapsedE (r : DRecord) (env : ThresholdEnvironment) : Prop :=
  knownProfile r.profile env ∧ positiveDistinction r.distinction ∧ aboveThreshold r.distinction r.profile env

def admissibleDE (r : DRecord) (env : ThresholdEnvironment) : Prop := representableD r env ∧ nonCollapsedE r env

theorem admissibleDE_is_conjunction (r : DRecord) (env : ThresholdEnvironment) :
    admissibleDE r env ↔ representableD r env ∧ nonCollapsedE r env := Iff.rfl

end RTDECleanRoom
