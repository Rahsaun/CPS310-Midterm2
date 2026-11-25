"""Execute generated scenarios against the existing game and observe invariants."""
import math
import random

import numpy as np

from Zombie_Game import ArmedHuman, Human, SimulationPlayground, Zombie


def observe(sim, capacity):
    agents = sim.humans + sim.zombies
    assert len({id(agent) for agent in agents}) == len(agents), "duplicate live agent"
    assert len(agents) <= capacity, "population exceeds initial capacity"
    assert all(isinstance(agent, Human) for agent in sim.humans), "human type violation"
    assert all(isinstance(agent, Zombie) for agent in sim.zombies), "zombie type violation"
    for agent in agents:
        assert agent.alive and 0 < agent.health <= agent.max_health, "invalid live health"
        assert all(math.isfinite(value) for value in (agent.x, agent.y, agent.health)), "non-finite state"
        assert 0 <= agent.x <= sim.width and 0 <= agent.y <= sim.height, "agent outside arena"


def run_scenario(width, height, num_regular, num_armed, num_zombies, ticks, seed, strategy_mode):
    random.seed(seed)
    np.random.seed(seed)
    sim = SimulationPlayground(width=width, height=height, use_multiprocessing=False, workers=1)
    sim.strategy_mode = strategy_mode
    capacity = num_regular + num_armed + num_zombies
    history = []
    try:
        sim.populate(num_regular, num_armed, num_zombies)
        assert sum(type(agent) is Human for agent in sim.humans) == num_regular, "regular count mismatch"
        assert sum(isinstance(agent, ArmedHuman) for agent in sim.humans) == num_armed, "armed count mismatch"
        assert len(sim.zombies) == num_zombies, "zombie count mismatch"
        for tick in range(ticks + 1):
            observe(sim, capacity)
            assert sim.tick_count == tick, "tick sequence mismatch"
            history.append({"tick": tick, "humans": len(sim.humans), "zombies": len(sim.zombies)})
            if tick == ticks or not sim.humans or not sim.zombies:
                break
            sim.step()
    finally:
        sim.close()
    return {"initial_population": capacity, "ticks_completed": len(history) - 1,
            "history": history, "strategy": strategy_mode}
