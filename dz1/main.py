import random
import matplotlib.pyplot as plt

adj_matrix = [
    [0.3, 0.3, 0.4],
    [0, 0.2, 0.8],
    [0, 0, 1]
]

def imitate(graph, init_state=0, final_state=2, max_iter=1000):
    steps = 0
    state = init_state
    for _ in range(max_iter):
        if state == final_state:
            break
        state = random.choices(range(init_state, final_state+1), weights=graph[state], k=1)[0]
        steps += 1
    return steps

def plot(students_cnt=1000):
    plt.plot(range(students_cnt), [imitate(adj_matrix) for _ in range(students_cnt)])