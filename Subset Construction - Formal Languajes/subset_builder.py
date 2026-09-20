"""
subset_builder.py - Subset Construction Algorithm implementation (Kozen Lecture 6).
"""
from typing import Set, FrozenSet
from models import NFA, DFA

class SubsetConstructionBuilder:
    @staticmethod
    def build_dfa(nfa: NFA) -> DFA:
        dfa = DFA(nfa.alphabet)
        
        start_set = frozenset(nfa.initial_states)
        start_id = dfa.add_state(start_set)
        dfa.start_state_id = start_id
        
        unmarked = [start_set]
        
        while unmarked:
            current_set = unmarked.pop(0)
            current_id = dfa.state_to_id[current_set]
            
            for sym in nfa.alphabet:
                next_set_mutable: Set[int] = set()
                for q in current_set:
                    next_set_mutable.update(nfa.get_transition(q, sym))
                
                next_frozenset = frozenset(next_set_mutable)
                
                if next_frozenset not in dfa.state_to_id:
                    next_id = dfa.add_state(next_frozenset)
                    unmarked.append(next_frozenset)
                else:
                    next_id = dfa.state_to_id[next_frozenset]
                    
                dfa.set_transition(current_id, sym, next_id)
                
        # Identify accepting/final states for DFA
        final_ids = []
        for st_set, st_id in dfa.state_to_id.items():
            if any(q in nfa.final_states for q in st_set):
                final_ids.append(st_id)
        final_ids.sort()
        dfa.final_state_ids = final_ids
        
        return dfa
