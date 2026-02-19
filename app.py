from flask import Flask, render_template, request
import pandas as pd
import networkx as nx
from pyvis.network import Network
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    df = pd.read_csv(file)

    G = nx.DiGraph()

    for _, row in df.iterrows():
        G.add_edge(row["sender_id"], row["receiver_id"])

    suspicious_accounts = {}
    rings = []

    # Graph Theory 1: Cycle Detection
    cycles = list(nx.simple_cycles(G))
    ring_count = 1
    for cycle in cycles:
        if 3 <= len(cycle) <= 5:
            rings.append({
                "ring_id": f"RING_{ring_count}",
                "members": cycle
            })
            for node in cycle:
                suspicious_accounts[node] = suspicious_accounts.get(node, 0) + 90
            ring_count += 1

    # Graph Theory 2: Degree Centrality
    centrality = nx.degree_centrality(G)

    for node, value in centrality.items():
        if value > 0.3:
            suspicious_accounts[node] = suspicious_accounts.get(node, 0) + 50

    # Cap score
    for node in suspicious_accounts:
        suspicious_accounts[node] = min(suspicious_accounts[node], 100)

    # Create interactive graph
    net = Network(height="500px", width="100%", directed=True)

    for node in G.nodes():
        score = suspicious_accounts.get(node, 0)

        if score >= 80:
            color = "red"
        elif score >= 50:
            color = "orange"
        else:
            color = "blue"

        net.add_node(node, label=node, color=color)

    for edge in G.edges():
        net.add_edge(edge[0], edge[1])

    net.save_graph("templates/graph.html")

    return render_template("results.html",
                           suspicious=suspicious_accounts,
                           rings=rings)
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

