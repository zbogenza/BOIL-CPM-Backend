import matplotlib.pyplot as plt
import networkx as nx
from io import BytesIO
import base64
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Task
from .serializers import TaskSerializer
from .cpm import compute_critical_path


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

@api_view(['POST'])
def bulk_create_tasks(request):
    Task.objects.all().delete()
    serializer = TaskSerializer(data=request.data, many=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Zadania dodane poprawnie"}, status=201)
    return Response(serializer.errors, status=400)


@api_view(['GET'])
def critical_path_view(request):
    tasks = Task.objects.all()
    critical_path = compute_critical_path(tasks)
    gantt_chart_url = generate_gantt_chart(tasks)
    return Response({"critical_path": critical_path, "gantt_chart_url": gantt_chart_url})


def generate_gantt_chart(tasks):
    G = nx.DiGraph()

    # 1. Budowanie grafu
    for task in tasks:
        G.add_edge(
            task.start_event,
            task.end_event,
            label=f"{task.name} ({task.duration} dni)",
            weight=task.duration
        )

    # 2. Obliczanie EET (early event time) - forward pass
    EET = {node: 0 for node in G.nodes()}
    topo_order = list(nx.topological_sort(G))
    for node in topo_order:
        for succ in G.successors(node):
            duration = G[node][succ]['weight']
            EET[succ] = max(EET[succ], EET[node] + duration)

    # 3. Obliczanie LET (late event time) - backward pass
    project_duration = max(EET.values())
    LET = {node: project_duration for node in G.nodes()}
    for node in reversed(topo_order):
        for pred in G.predecessors(node):
            duration = G[pred][node]['weight']
            LET[pred] = min(LET[pred], LET[node] - duration)

    # 4. Zapas czasu dla zdarzeń
    FLOAT = {node: LET[node] - EET[node] for node in G.nodes()}

    # 5. Rysowanie wykresu
    pos = nx.spring_layout(G)
    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=False, node_color="lightblue", edge_color="black", node_size=1000)

    # Etykiety krawędzi (zadania)
    edge_labels = {(u, v): d["label"] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

    # Etykiety węzłów (zdarzenia z danymi CPM)
    for node in G.nodes():
        x, y = pos[node]
        label = (
            f"  [{node}]\n"
            f"{EET[node]}     {LET[node]}\n"
            f"    {FLOAT[node]}"
        )
        plt.text(x, y, label, ha="center", va="center", fontsize=8,
                 bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.4'))

    # Eksport do base64
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    plt.close()

    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()

