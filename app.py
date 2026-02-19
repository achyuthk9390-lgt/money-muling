@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    df = pd.read_csv(file)

    G = nx.DiGraph()

    for _, row in df.iterrows():
        G.add_edge(row["sender_id"], row["receiver_id"])

    suspicious_accounts = {}
    rings = []

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

    return render_template("results.html",
                           suspicious=suspicious_accounts,
                           rings=rings)

