import networkx as nx
import matplotlib.pyplot as plt

def compute_critical_path(tasks):
    graph = nx.DiGraph()

    # Każde zadanie to krawędź z wagą duration
    for task in tasks:
        graph.add_edge(task.start_event, task.end_event, weight=task.duration, name=task.name)

    # Szukamy ścieżki o największej sumie wag (czyli najdłuższy czas trwania) między dowolnym źródłem a ujściem
    longest_path = nx.dag_longest_path(graph, weight="weight")

    # Teraz znajdź nazwy zadań (czyli krawędzi) pomiędzy tymi zdarzeniami
    critical_tasks = []
    for i in range(len(longest_path) - 1):
        u = longest_path[i]
        v = longest_path[i+1]
        critical_tasks.append(graph[u][v]["name"])

    return critical_tasks


def draw_gantt_chart(tasks):
    fig, ax = plt.subplots(figsize=(10, 5))

    y_labels = []
    start_times = []
    durations = []

    for i, task in enumerate(tasks):
        y_labels.append(task.name)
        start_times.append(i * 2)  # Przykładowe starty zadań
        durations.append(task.duration)

    ax.barh(y_labels, durations, left=start_times, color='skyblue')
    ax.set_xlabel("Czas")
    ax.set_title("Wykres Gantta")

    plt.savefig("gantt_chart.png")