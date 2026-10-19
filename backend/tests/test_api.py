from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.services.storage import MemoryTournamentStore
from app.simulation.strategies import STRATEGY_REGISTRY


@pytest.fixture
def client():
    with TestClient(create_app(store=MemoryTournamentStore())) as client:
        yield client


@pytest.fixture
def configuration():
    return {
        "strategies": ["always_cooperate", "always_defect", "tit_for_tat"],
        "rounds": 3,
        "matches_per_pair": 1,
        "seed": 42,
        "include_self_play": False,
        "payoffs": {"temptation": 7, "reward": 4, "punishment": 2, "sucker": 0},
    }


def test_health_and_strategies(client) -> None:
    assert client.get("/api/v1/health").json() == {
        "status": "ok",
        "database": "not_configured",
    }
    strategies = client.get("/api/v1/strategies").json()
    assert {s["key"] for s in strategies} == set(STRATEGY_REGISTRY)
    assert all(s["name"] and s["description"] for s in strategies)


def test_create_and_retrieve_tournament_and_match(client, configuration):
    response = client.post("/api/v1/tournaments", json=configuration)
    assert response.status_code == 201
    tournament = response.json()
    assert tournament["configuration"] == configuration
    assert len(tournament["matches"]) == 3
    assert client.get(response.headers["Location"]).json() == tournament

    match = tournament["matches"][0]
    detail = client.get(f"/api/v1/matches/{match['id']}").json()
    assert {k: v for k, v in detail.items() if k != "history"} == match
    assert [row["round_number"] for row in detail["history"]] == [1, 2, 3]
    assert (detail["score_a"], detail["score_b"]) == (0, 21)
    standings = {row["strategy_key"]: row for row in tournament["leaderboard"]}
    assert standings["always_defect"]["total_score"] == 32
    assert standings["always_defect"]["wins"] == 2


def test_every_strategy_runs_in_one_tournament(client):
    response = client.post("/api/v1/tournaments", json={
        "strategies": list(STRATEGY_REGISTRY),
        "rounds": 12,
        "seed": 42,
        "include_self_play": True,
    })
    assert response.status_code == 201
    assert len(response.json()["leaderboard"]) == len(STRATEGY_REGISTRY)


def test_list_is_paginated_and_newest_first(client, configuration):
    first = client.post("/api/v1/tournaments", json=configuration).json()
    second = client.post("/api/v1/tournaments", json=configuration).json()

    page = client.get("/api/v1/tournaments?limit=1&offset=0").json()
    assert page == {"items": [second], "total": 2, "limit": 1, "offset": 0}
    assert client.get("/api/v1/tournaments?limit=1&offset=1").json()["items"] == [first]


@pytest.mark.parametrize("updates", [
    {"strategies": ["always_cooperate"]},
    {"strategies": ["always_cooperate", "always_cooperate"]},
    {"strategies": ["always_cooperate", "unknown"]},
    {"rounds": 0},
    {"matches_per_pair": "5"},
    {"rounds": 10_000, "matches_per_pair": 4},
    {"payoffs": {"temptation": 3}},
])
def test_invalid_configuration_is_rejected_without_saving(client, configuration, updates):
    response = client.post("/api/v1/tournaments", json=configuration | updates)
    assert response.status_code == 422
    assert client.get("/api/v1/tournaments").json()["total"] == 0


@pytest.mark.parametrize("path", ["tournaments", "matches"])
def test_unknown_ids_return_404(client, path):
    assert client.get(f"/api/v1/{path}/{uuid4()}").status_code == 404
