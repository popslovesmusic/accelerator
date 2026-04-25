import numpy as np
import networkx as nx

class RuleEngine:
    def __init__(self, config):
        self.config = config
        self.n_states = config['n_states']
        self.forbidden = config['forbidden_node']
        self.res_thresh_node = config['residue_threshold_node']
        self.res_required = config['residue_required']
        
        # Build State Graph G
        # Nodes 0 to N-1
        self.G = nx.fast_gnp_random_graph(self.n_states, config['edge_prob'], directed=True, seed=config['seed'])
        
        # Ensure some reachability from node 1 (starting node)
        if not list(self.G.successors(1)):
            self.G.add_edge(1, 2)
            self.G.add_edge(1, 3)

    def is_admissible(self, target_node, agent_residue):
        # 1. Rule: L0 (Forbidden State)
        if target_node == self.forbidden:
            return False
            
        # 2. Rule: Residue Gating
        # If target node index is above threshold, require residue
        if target_node >= self.res_thresh_node:
            if agent_residue < self.res_required:
                return False
                
        return True

    def get_admissible_continuations(self, current_node, agent_residue):
        candidates = list(self.G.successors(current_node))
        admissible = [c for c in candidates if self.is_admissible(c, agent_residue)]
        return admissible

class FSAAgent:
    def __init__(self, start_node=1):
        self.current_state = start_node
        self.residue = 0
        self.active = True

    def step(self, engine):
        if not self.active:
            return
            
        admissible = engine.get_admissible_continuations(self.current_state, self.residue)
        
        if not admissible:
            self.active = False
            return
            
        # Select one admissible continuation
        next_state = np.random.choice(admissible)
        
        # Update state and residue
        self.current_state = next_state
        self.residue += 1 # Simple increment per continuation
