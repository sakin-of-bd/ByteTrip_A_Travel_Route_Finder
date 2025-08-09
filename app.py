from flask import Flask, render_template, request
import pandas as pd
import heapq
from collections import deque, defaultdict

app = Flask(__name__)

df = pd.read_csv("route_infos.csv")
graph = defaultdict(list)
for _, row in df.iterrows():
    frm, to = row['from'], row['to']
    graph[frm].append((to, row['cost'], row['distance_km'], row['time_minutes']))
    graph[to].append((frm, row['cost'], row['distance_km'], row['time_minutes']))  # bidirectional

def dijkstra(graph, start, end, weight_index):
    heap = [(0, start, [])]
    visited = set()
    while heap:
        cost, node, path = heapq.heappop(heap)
        if node in visited:
            continue
        path = path + [node]
        visited.add(node)
        if node == end:
            return cost, path
        for neighbor in graph[node]:
            if neighbor[0] not in visited:
                heapq.heappush(heap, (cost + neighbor[weight_index], neighbor[0], path))
    return float('inf'), []

def bfs_shortest_path(graph, start, end):
    queue = deque([(start, [start], 0)])
    visited = set()
    while queue:
        node, path, total_dist = queue.popleft()
        if node == end:
            return total_dist, path
        if node in visited:
            continue
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor[0] not in visited:
                queue.append((neighbor[0], path + [neighbor[0]], total_dist + neighbor[2]))
    return float('inf'), []

@app.route("/", methods=["GET", "POST"])
def index():
    districts = sorted(set(df['from']).union(df['to']))
    if request.method == "POST":
        start = request.form["start"]
        end = request.form["end"]
        choice = request.form["choice"]

        if choice == '1':
            result, path = dijkstra(graph, start, end, 1)
            output = f"Cheapest path cost: {result} Tk"
        elif choice == '2':
            result, path = bfs_shortest_path(graph, start, end)
            output = f"Shortest distance: {result} km"
        elif choice == '3':
            result, path = dijkstra(graph, start, end, 3)
            output = f"Shortest time: {result} minutes"
        else:
            output = "Invalid option."
            path = []

        return render_template("result.html", output=output, path=path)

    return render_template("index.html", districts=districts)

if __name__ == "__main__":
    app.run(debug=True)
