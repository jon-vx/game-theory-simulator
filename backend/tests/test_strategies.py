import random
from unittest.mock import Mock

import pytest

from app.simulation.models import HistoryEntry, MatchHistory, Move, PayoffMatrix
from app.simulation.strategies import create_strategy


C = Move.COOPERATE
D = Move.DEFECT


def play(key, opponents, rng=None):
    """Play a strategy against a scripted opponent and return its moves as C/D."""
    strategy = create_strategy(key)
    rng = rng if rng is not None else random.Random(42)
    payoffs = PayoffMatrix()
    entries = []
    moves = []
    for opponent in opponents:
        move = strategy.choose_move(MatchHistory(entries), rng)
        moves.append("C" if move is C else "D")
        opponent_move = C if opponent == "C" else D
        entries.append(HistoryEntry(move, opponent_move, *payoffs.score(move, opponent_move)))
    return "".join(moves)


@pytest.mark.parametrize("key,opponents,expected", [
    ("tit_for_tat", "CDCC", "CCDC"),
    ("pavlov", "CDDC", "CCDC"),
    ("grim_trigger", "CDCCCC", "CCDDDD"),
    ("tit_for_two_tats", "CDDCCC", "CCCDCC"),
    ("two_tits_for_tat", "CDCCCC", "CCDDCC"),
    ("hard_tit_for_tat", "CDCCCC", "CCDDDC"),
    ("suspicious_tit_for_tat", "CDCC", "DCDC"),
    ("gradual", "DDDDDDDDDD", "CDCCDDDDCC"),
    ("soft_majority", "DCCC", "CDCC"),
    ("hard_majority", "DCCC", "DDDC"),
    ("alternate", "CCCCCC", "CDCDCD"),
    ("detective", "CCCCCCC", "CDCCDDD"),
    ("detective", "CDCDCCC", "CDCCDCC"),
    ("handshake", "CDCCCC", "CDCCCC"),
    ("handshake", "CCCCCC", "CDDDDD"),
    ("contrite_tit_for_tat", "CDCC", "CCDC"),
    ("adaptive", "CCCCCCCCCCCCCC", "CCCCCCDDDDDDDD"),
])
def test_scripted_behavior(key, opponents, expected):
    assert play(key, opponents) == expected


@pytest.mark.parametrize("key,draw,expected", [
    ("generous_tit_for_tat", 0.09, "CCC"),
    ("generous_tit_for_tat", 0.1, "CDD"),
    ("naive_prober", 0.09, "DDD"),
    ("naive_prober", 0.1, "CCC"),
    ("random_cooperate_bias", 0.69, "CCC"),
    ("random_cooperate_bias", 0.7, "DDD"),
    ("random_defect_bias", 0.29, "CCC"),
    ("random_defect_bias", 0.3, "DDD"),
])
def test_probability_boundaries(key, draw, expected):
    rng = Mock(spec=random.Random)
    rng.random.return_value = draw
    opponents = "DDD" if key == "generous_tit_for_tat" else "CCC"
    assert play(key, opponents, rng=rng) == expected
