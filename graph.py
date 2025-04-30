import requests
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest

# Fetch Bitcoin transactions
def get_transactions(bitcoin_address):
    url = f"https://blockchain.info/rawaddr/{bitcoin_address}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("txs", [])
    else:
        print(f"Error fetching data: {response.text}")
        return []

# Extract features
def extract_features(transactions):
    features = []
    txn_refs = []
    for txn in transactions:
        total_value = sum(out["value"] for out in txn["out"]) / 1e8  # satoshis to BTC
        num_inputs = len(txn["inputs"])
        num_outputs = len(txn["out"])
        features.append([total_value, num_inputs, num_outputs])
        txn_refs.append(txn["hash"])
    return np.array(features), txn_refs

# Detect anomalies
def detect_anomalies(features):
    model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
    model.fit(features)
    predictions = model.predict(features)
    return [i for i, p in enumerate(predictions) if p == -1]

# Display suspicious transactions
def print_suspicious_transactions(anomaly_indices, features, txn_refs):
    print("\n🚨 Suspicious Transactions Detected:\n")
    for idx in anomaly_indices:
        txid = txn_refs[idx]
        value, inputs, outputs = features[idx]
        link = f"https://www.blockchain.com/explorer/transactions/btc/{txid}"
        print(f"🔗 {link}")
        print(f"   ↳ Value: {value:.8f} BTC | Inputs: {int(inputs)} | Outputs: {int(outputs)}\n")

# Build and visualize graph
def visualize_graph(transactions, features, txn_refs, anomaly_indices):
    G = nx.DiGraph()
    labels = {}

    for idx in anomaly_indices:
        txn = transactions[idx]
        txid = txn_refs[idx]
        value = features[idx][0]
        tx_label = f"Tx: {txid[:6]}... | {value:.2f} BTC"
        
        # Add transaction node
        G.add_node(txid, label=tx_label, color='red')
        labels[txid] = tx_label

        # Add input nodes
        for i, inp in enumerate(txn["inputs"][:2]):
            addr = inp.get("prev_out", {}).get("addr", f"input_{i}")
            G.add_node(addr, label=addr, color='blue')
            G.add_edge(addr, txid)

        if len(txn["inputs"]) > 2:
            G.add_node(f"{txid}_in_others", label="Other Inputs", color='lightblue')
            G.add_edge(f"{txid}_in_others", txid)

        # Add output nodes
        for i, out in enumerate(txn["out"][:2]):
            addr = out.get("addr", f"output_{i}")
            G.add_node(addr, label=addr, color='green')
            G.add_edge(txid, addr)

        if len(txn["out"]) > 2:
            G.add_node(f"{txid}_out_others", label="Other Outputs", color='lightgreen')
            G.add_edge(txid, f"{txid}_out_others")

    # Draw graph
    colors = [G.nodes[n].get('color', 'gray') for n in G.nodes()]
    pos = nx.spring_layout(G, k=0.5)
    nx.draw(G, pos, with_labels=False, node_color=colors, node_size=800, arrows=True)
    nx.draw_networkx_labels(G, pos, labels={n: G.nodes[n]['label'] for n in G.nodes() if 'label' in G.nodes[n]}, font_size=8)

    # Add legend
    import matplotlib.patches as mpatches
    legend_elements = [
        mpatches.Patch(color='red', label='Suspicious Transaction'),
        mpatches.Patch(color='blue', label='Input Address'),
        mpatches.Patch(color='green', label='Output Address'),
        mpatches.Patch(color='lightblue', label='Other Inputs'),
        mpatches.Patch(color='lightgreen', label='Other Outputs')
    ]
    plt.legend(handles=legend_elements, loc='upper left', fontsize='small')
    
    plt.title("Suspicious Bitcoin Transaction Network")
    plt.show()

# ---- Run everything ----
if __name__ == "__main__":
    bitcoin_address = input("Enter a Bitcoin address: ")
    transactions = get_transactions(bitcoin_address)
    
    if transactions:
        features, txn_refs = extract_features(transactions)
        anomaly_indices = detect_anomalies(features)

        print_suspicious_transactions(anomaly_indices, features, txn_refs)
        visualize_graph(transactions, features, txn_refs, anomaly_indices)
    else:
        print("No transactions found or error in fetching.")
