import pytest

from app.simulation.match import run_match
from app.simulation.models import Move, PayoffMatrix
from app.simulation.tournament import run_tournament


STRATEGIES = ("tit_for_tat", "pavlov", "random", "always_defect")


def test_match_scores_moves_and_history() -> None:
    result = run_match("tit_for_tat", "always_defect", rounds=3, seed=42)

    assert [(row.move_a, row.move_b) for row in result.history] == [
        (Move.COOPERATE, Move.DEFECT),
        (Move.DEFECT, Move.DEFECT),
        (Move.DEFECT, Move.DEFECT),
    ]
    assert (result.score_a, result.score_b) == (2, 7)
    assert result.winner == "b"
    assert result.cooperation_rate_a == pytest.approx(1 / 3)
    assert result.history[-1].cumulative_score_b == result.score_b


@pytest.mark.parametrize("values", [(3, 3, 1, 0), (5, 3, 3, 0), (5, 3, 1, 1), (6, 3, 1, 0)])
def test_invalid_payoff_matrix_is_rejected(values) -> None:
    with pytest.raises(ValueError):
        PayoffMatrix(*values)


@pytest.mark.parametrize("self_play", [False, True])
def test_round_robin_pairings_are_complete_and_reproducible(self_play) -> None:
    result = run_tournament(
        STRATEGIES, rounds=20, seed=42, include_self_play=self_play, matches_per_pair=3
    )

    n = len(STRATEGIES)
    pairs = n * (n + 1) // 2 if self_play else n * (n - 1) // 2
    assert len(result.matches) == pairs * 3
    assert len({m.seed for m in result.matches}) == len(result.matches)
    assert result == run_tournament(
        STRATEGIES, rounds=20, seed=42, include_self_play=self_play, matches_per_pair=3
    )


def test_leaderboard_aggregates_repeated_matches() -> None:
    result = run_tournament(
        ("tit_for_tat", "always_defect"), rounds=3, seed=42, matches_per_pair=5
    )

    # Every repeat starts from fresh strategy state.
    assert all((m.score_a, m.score_b) == (2, 7) for m in result.matches)
    defector, tit_for_tat = result.leaderboard
    assert (defector.strategy_key, defector.rank) == ("always_defect", 1)
    assert defector.total_score == 35
    assert defector.wins == defector.matches_played == 5
    assert tit_for_tat.total_score == 10
    assert tit_for_tat.losses == 5
    assert tit_for_tat.cooperation_rate == pytest.approx(1 / 3)
