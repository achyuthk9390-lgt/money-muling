from flask import Flask, render_template, request
import pandas as pd
import networkx as nx

app = Flask(__name__)

# Home Page
@app.route("/")
def home():
    return render_template("index.html")


# Upload Route
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    df = pd.read_csv(file)

    # Create Directed Graph
    G = nx.DiGraph()

    for _, row in df.iterrows():
        G.add_edge(row["sender_id"], row["receiver_id"])

    suspicious_accounts = {}
    rings = []

    # Detect Cycles (Fraud Rings)
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

    # Fan-in detection (many incoming transactions)
    for node in G.nodes():
        if G.in_degree(node) >= 5:
            suspicious_accounts[node] = suspicious_accounts.get(node, 0) + 70

    # Cap score at 100
    for node in suspicious_accounts:
        if suspicious_accounts[node] > 100:
            suspicious_accounts[node] = 100

    return render_template("results.html",
                           suspicious=suspicious_accounts,
                           rings=rings)


# Run Server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

