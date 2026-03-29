import json
import sys
import os
import glob
import matplotlib.pyplot as plt

GRAPH_DIR = os.path.join(os.path.dirname(__file__), "..", "report-images")
os.makedirs(GRAPH_DIR, exist_ok=True)


def load_log(path):
    with open(path) as f:
        return json.load(f)


def label_from_meta(meta):
    return f"{meta['algorithm']} d{meta['depth']} ({meta['move_ordering']})"


# Single-game graph 
def plot_single(path):
    data = load_log(path)
    meta = data["metadata"]
    moves_data = data["moves"]

    moves = [m["move_number"] for m in moves_data]
    nodes = [m["nodes"] for m in moves_data]
    times = [m["time"] for m in moves_data]

    fig, ax1 = plt.subplots(figsize=(12, 6))

    color_nodes = "#2196F3"
    color_time = "#FF5722"

    ax1.bar(moves, nodes, color=color_nodes, alpha=0.7, label="Nodes Evaluated")
    ax1.set_xlabel("AI Move Number", fontsize=12)
    ax1.set_ylabel("Nodes Evaluated", fontsize=12, color=color_nodes)
    ax1.tick_params(axis='y', labelcolor=color_nodes)
    step = max(1, len(moves) // 20)
    ax1.set_xticks(moves[::step])

    ax2 = ax1.twinx()
    ax2.plot(moves, times, color=color_time, marker='o', linewidth=2, label="Time (s)")
    ax2.set_ylabel("Time (seconds)", fontsize=12, color=color_time)
    ax2.tick_params(axis='y', labelcolor=color_time)

    title = f"{meta['algorithm']} | Depth {meta['depth']} | {meta['move_ordering']} | {meta['outcome']}"
    fig.suptitle(title, fontsize=14, fontweight='bold')
    fig.legend(loc="upper left", bbox_to_anchor=(0.1, 0.92))
    fig.tight_layout()

    basename = os.path.splitext(os.path.basename(path))[0]
    out = os.path.join(GRAPH_DIR, f"{basename}.png")
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out}")


# Comparison graph
def plot_comparison(paths):
    fig, (ax_nodes, ax_time) = plt.subplots(1, 2, figsize=(16, 6))
    colors = ["#2196F3", "#FF5722", "#4CAF50", "#9C27B0", "#FF9800", "#00BCD4"]

    labels = []
    for i, path in enumerate(paths):
        data = load_log(path)
        meta = data["metadata"]
        moves_data = data["moves"]
        label = label_from_meta(meta)
        labels.append(label)
        c = colors[i % len(colors)]

        move_nums = [m["move_number"] for m in moves_data]
        nodes = [m["nodes"] for m in moves_data]
        times = [m["time"] for m in moves_data]

        ax_nodes.plot(move_nums, nodes, marker='o', color=c, linewidth=2, label=label)
        ax_time.plot(move_nums, times, marker='s', color=c, linewidth=2, label=label)

    ax_nodes.set_title("Nodes Evaluated per Move", fontweight='bold')
    ax_nodes.set_xlabel("AI Move Number")
    ax_nodes.set_ylabel("Nodes")
    ax_nodes.legend()

    ax_time.set_title("Time per Move", fontweight='bold')
    ax_time.set_xlabel("AI Move Number")
    ax_time.set_ylabel("Time (seconds)")
    ax_time.legend()

    fig.suptitle("Algorithm Comparison", fontsize=14, fontweight='bold')
    fig.tight_layout()

    out = os.path.join(GRAPH_DIR, "comparison.png")
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out}")

    # If 2 logs try pruning rate graph
    if len(paths) == 2:
        plot_pruning_rate(paths)


# Pruning rate graph (unpruned vs pruned) 
def plot_pruning_rate(paths):
    logs = [load_log(p) for p in paths]

    # Determine which has more total nodes
    totals = [l["metadata"]["total_nodes"] for l in logs]
    if totals[0] >= totals[1]:
        base_log, pruned_log = logs[0], logs[1]
    else:
        base_log, pruned_log = logs[1], logs[0]

    base_moves = base_log["moves"]
    pruned_moves = pruned_log["moves"]
    n = min(len(base_moves), len(pruned_moves))

    if n == 0:
        return

    move_nums = list(range(1, n + 1))
    rates = []
    for i in range(n):
        bn = base_moves[i]["nodes"]
        pn = pruned_moves[i]["nodes"]
        rate = (1 - pn / bn) * 100 if bn > 0 else 0
        rates.append(rate)

    avg_rate = sum(rates) / len(rates)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(move_nums, rates, color="#4CAF50", alpha=0.7)
    ax.axhline(y=avg_rate, color="#FF5722", linestyle='--', linewidth=2,
               label=f"Average: {avg_rate:.1f}%")
    ax.set_xlabel("Move Number", fontsize=12)
    ax.set_ylabel("Pruning Rate (%)", fontsize=12)
    ax.set_title(
        f"Pruning Rate: {label_from_meta(base_log['metadata'])} vs {label_from_meta(pruned_log['metadata'])}",
        fontsize=13, fontweight='bold')
    ax.legend(fontsize=12)
    step = max(1, len(move_nums) // 20)
    ax.set_xticks(move_nums[::step])
    fig.tight_layout()

    out = os.path.join(GRAPH_DIR, "pruning_rate.png")
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out}")


# Summary of all logs in a directory 
def plot_summary(log_dir):
    files = glob.glob(os.path.join(log_dir, "*.json"))
    if not files:
        print(f"No JSON logs found in {log_dir}")
        return

    rows = []
    for f in sorted(files):
        data = load_log(f)
        m = data["metadata"]
        rows.append(m)

    # Group by algorithm, depth, ordering
    groups = {}
    for r in rows:
        key = (r["algorithm"], r["depth"], r["move_ordering"])
        groups.setdefault(key, []).append(r)

    labels = []
    avg_nodes = []
    avg_times = []
    wins = []
    losses = []
    draws = []

    for key, items in sorted(groups.items()):
        algo, depth, ordering = key
        labels.append(f"{algo}\nd{depth} {ordering}")
        avg_nodes.append(sum(i["total_nodes"] for i in items) / len(items))
        avg_times.append(sum(i["total_time"] for i in items) / len(items))
        w = sum(1 for i in items if i["outcome"] in ("white_wins", "black_wins"))
        d = sum(1 for i in items if i["outcome"] == "draw")
        l = sum(1 for i in items if i["outcome"] not in ("white_wins", "black_wins", "draw"))
        wins.append(w)
        draws.append(d)
        losses.append(l)

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # Avg total nodes
    axes[0].barh(labels, avg_nodes, color="#2196F3")
    axes[0].set_title("Avg Total Nodes", fontweight='bold')
    axes[0].set_xlabel("Nodes")

    # Avg total time
    axes[1].barh(labels, avg_times, color="#FF5722")
    axes[1].set_title("Avg Total Time (s)", fontweight='bold')
    axes[1].set_xlabel("Seconds")

    # Win/Draw/Loss
    x = range(len(labels))
    axes[2].bar(x, wins, label="Win", color="#4CAF50")
    axes[2].bar(x, draws, bottom=wins, label="Draw", color="#FFC107")
    axes[2].bar(x, losses, bottom=[w + d for w, d in zip(wins, draws)], label="Other", color="#F44336")
    axes[2].set_xticks(list(x))
    axes[2].set_xticklabels(labels, fontsize=8)
    axes[2].set_title("Outcomes", fontweight='bold')
    axes[2].legend()

    fig.suptitle("Experiment Summary", fontsize=14, fontweight='bold')
    fig.tight_layout()

    out = os.path.join(GRAPH_DIR, "summary.png")
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out}")

    # Print table
    print(f"\n{'Config':<35} {'Games':>5} {'Avg Nodes':>12} {'Avg Time':>10} {'W/D/L':>10}")
    print("-" * 75)
    for i, key in enumerate(sorted(groups.keys())):
        algo, depth, ordering = key
        items = groups[key]
        n = len(items)
        an = sum(it["total_nodes"] for it in items) / n
        at = sum(it["total_time"] for it in items) / n
        print(f"{algo} d{depth} {ordering:<15} {n:>5} {an:>12.0f} {at:>9.1f}s {wins[i]}/{draws[i]}/{losses[i]:>8}")


# CLI Entry Point 
if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        print(__doc__)
        sys.exit(0)

    if args[0] == "--summary":
        log_dir = args[1] if len(args) > 1 else os.path.join(os.path.dirname(__file__), "logs")
        plot_summary(log_dir)
    elif len(args) == 1:
        plot_single(args[0])
    else:
        plot_comparison(args)
