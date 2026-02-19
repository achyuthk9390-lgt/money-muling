suspicious_accounts = {}

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

# Fan-in detection
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

