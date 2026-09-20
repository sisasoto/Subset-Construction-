"""
models.py - Data models for NFA and DFA.
"""
from typing import Set, Dict, List, FrozenSet

class NFA:
    def __init__(self, num_states: int, initial_states: Set[int], alphabet: List[str], final_states: Set[int], delta: Dict[int, Dict[str, Set[int]]]):
        self.num_states = num_states
        self.initial_states = initial_states
        self.alphabet = alphabet
        self.final_states = final_states
        self.delta = delta  # state -> {symbol: set_of_next_states}

    def get_transition(self, state: int, symbol: str) -> Set[int]:
        return self.delta.get(state, {}).get(symbol, set())


class DFA:
    def __init__(self, alphabet: List[str]):
        self.alphabet = alphabet
        self.states: List[FrozenSet[int]] = []
        self.state_to_id: Dict[FrozenSet[int], int] = {}
        self.start_state_id: int = 1
        self.final_state_ids: List[int] = []
        self.delta: Dict[int, Dict[str, int]] = {}

    def add_state(self, state_set: FrozenSet[int]) -> int:
        if state_set not in self.state_to_id:
            new_id = len(self.states) + 1
            self.state_to_id[state_set] = new_id
            self.states.append(state_set)
            self.delta[new_id] = {}
            return new_id
        return self.state_to_id[state_set]

    def set_transition(self, src_id: int, symbol: str, dest_id: int):
        if src_id not in self.delta:
            self.delta[src_id] = {}
        self.delta[src_id][symbol] = dest_id
