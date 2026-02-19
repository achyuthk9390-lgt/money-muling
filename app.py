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

    suspicious = []
    rings = []

    cycles = list(nx.simple_cycles(G))
    ring_count = 1

    for cycle in cycles:
        if 3 <= len(cycle) <= 5:
            rings.append({
                "ring_id": f"RING_{ring_count}",
                "members": cycle
            })
            suspicious.extend(cycle)
            ring_count += 1

    for node in G.nodes():
        if G.in_degree(node) >= 10:
            suspicious.append(node)
        if G.out_degree(node) >= 10:
            suspicious.append(node)

    suspicious = list(set(suspicious))

    # Create graph visualization
    net = Network(height="500px", width="100%", directed=True)

    for node in G.nodes():
        if node in suspicious:
            net.add_node(node, color="red")
        else:
            net.add_node(node, color="blue")

    for edge in G.edges():
        net.add_edge(edge[0], edge[1])

    if not os.path.exists("static"):
        os.makedirs("static")

    net.save_graph("static/graph.html")

    return render_template("results.html",
                           suspicious=suspicious,
                           rings=rings)

if __name__ == "__main__":
    app.run(debug=True)
