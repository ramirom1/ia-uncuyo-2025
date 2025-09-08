import gymnasium as gym
from gymnasium import wrappers 
from gymnasium.envs.toy_text.frozen_lake import generate_random_map
from randomCustom import *

limit = 1000

env = gym.make('FrozenLake-v1', render_mode='human', desc = generate_random_map_custom(8, 0.3), is_slippery = False).env
env = wrappers.TimeLimit(env, limit)


print("Numero de estados:", env.observation_space.n)
print("Numero de acciones:", env.action_space.n)

state = env.reset()
print("Posicion inicial del agente:", state[0])

done = truncated = False
i=0
while not (done or truncated):
    action = env.action_space.sample()
    i+=1
    # Accion aleatoria
    next_state, reward, done, truncated, _ = env.step(action)
    print(f"Accion: {action}, Nuevo estado: {next_state}, Recompensa: {reward}")
    if not reward == 1.0:
        print(f"Gano? (encontro el objetivo): False")
        print(f"Perdio? (se cayo): {done}")
        print(f"Freno? (alcanzo el maximo de pasos posible): {truncated}\n")
    else:
        print(f"Gano? (encontro el objetivo): {done}")

    state = next_state




    