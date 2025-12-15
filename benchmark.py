# benchmark.py
import argparse
import csv
import random
from statistics import mean

from config.settings import DIFFICULTY_LEVELS, ALPHABETA_MAX_STICKS
from game.game_controller import GameController


def random_state_from_template(template_piles, total_sticks, rng: random.Random):
    """
    Buat state acak dengan jumlah pile = len(template_piles) dan total = total_sticks.
    Distribusi mengikuti 'shape' template_piles, tapi tetap bervariasi.
    """
    n = len(template_piles)
    if n <= 0:
        raise ValueError("template_piles kosong")

    # weight mengikuti template + noise random
    weights = []
    for p in template_piles:
        base = max(1, int(p))
        noise_factor = 0.5 + rng.random()  # 0.5 .. 1.5
        weights.append(base * noise_factor)

    s = sum(weights)
    raw = [int(w / s * total_sticks) for w in weights]
    rem = total_sticks - sum(raw)

    # distribusikan sisa
    while rem > 0:
        raw[rng.randrange(n)] += 1
        rem -= 1

    # pastikan tidak semuanya nol
    if sum(raw) == 0 and total_sticks > 0:
        raw[rng.randrange(n)] = total_sticks

    return raw


def run_trials(difficulty_name, trials, p1_algo, p2_algo, seed, write_csv=None, force_alpha_beta=False):
    cfg = DIFFICULTY_LEVELS[difficulty_name]
    template = cfg["piles"]
    total = cfg.get("total_sticks", sum(template))
    allow_ab = cfg.get("allow_alphabeta", total <= ALPHABETA_MAX_STICKS)

    # rule sesuai project kamu: AB dibatasi supaya tidak freeze
    need_ab = ("Alpha-Beta" in (p1_algo, p2_algo))
    if need_ab and (not force_alpha_beta) and ((not allow_ab) or total > ALPHABETA_MAX_STICKS):
        print(f"[SKIP] {difficulty_name}: total_sticks={total} melebihi batas Alpha-Beta ({ALPHABETA_MAX_STICKS}).")
        print("       Jalankan dengan --force-alpha-beta jika benar-benar mau (berisiko hang).")
        return None

    rng = random.Random(seed)

    wins = {"Reflex": 0, "Alpha-Beta": 0}
    winners_by_player = {1: 0, 2: 0}
    moves_list = []
    duration_list = []
    p1_avg_ms = []
    p2_avg_ms = []
    p1_nodes = []
    p2_nodes = []

    rows = []
    for t in range(1, trials + 1):
        state = random_state_from_template(template, total, rng)

        controller = GameController(state, p1_algo, p2_algo)
        summary = controller.run_to_end()

        winner_player = summary.get("winner")
        winners_by_player[winner_player] = winners_by_player.get(winner_player, 0) + 1

        if winner_player == 1:
            winner_algo = p1_algo
        elif winner_player == 2:
            winner_algo = p2_algo
        else:
            winner_algo = None

        if winner_algo in wins:
            wins[winner_algo] += 1

        moves_list.append(summary.get("total_moves", 0))
        duration_list.append(summary.get("match_duration_sec", 0.0))

        p1 = summary.get("player1", {})
        p2 = summary.get("player2", {})
        p1_avg_ms.append(float(p1.get("avg_time_ms", 0.0)))
        p2_avg_ms.append(float(p2.get("avg_time_ms", 0.0)))
        p1_nodes.append(int(p1.get("total_nodes", 0)))
        p2_nodes.append(int(p2.get("total_nodes", 0)))

        rows.append({
            "trial": t,
            "difficulty": difficulty_name,
            "initial_state": str(state),
            "p1_algo": p1_algo,
            "p2_algo": p2_algo,
            "winner_player": winner_player,
            "winner_algo": winner_algo,
            "total_moves": summary.get("total_moves", 0),
            "match_duration_sec": summary.get("match_duration_sec", 0.0),
            "p1_avg_time_ms": p1.get("avg_time_ms", 0.0),
            "p2_avg_time_ms": p2.get("avg_time_ms", 0.0),
            "p1_total_nodes": p1.get("total_nodes", 0),
            "p2_total_nodes": p2.get("total_nodes", 0),
        })

    # print ringkasan
    print(f"\n=== RESULT: {difficulty_name} | trials={trials} | P1={p1_algo} vs P2={p2_algo} ===")
    print(f"Total sticks target: {total} | piles: {len(template)}")
    print(f"Wins: Reflex={wins['Reflex']} | Alpha-Beta={wins['Alpha-Beta']}")
    print(f"Avg total moves: {mean(moves_list):.2f}")
    print(f"Avg match duration (sec): {mean(duration_list):.4f}")
    print(f"P1 avg time per move (ms): {mean(p1_avg_ms):.4f} | total nodes avg: {mean(p1_nodes):.2f}")
    print(f"P2 avg time per move (ms): {mean(p2_avg_ms):.4f} | total nodes avg: {mean(p2_nodes):.2f}")

    # CSV output (opsional)
    if write_csv:
        with open(write_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        print(f"[OK] CSV saved: {write_csv}")

    return {
        "difficulty": difficulty_name,
        "trials": trials,
        "wins": wins,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--difficulty", default="Easy", choices=list(DIFFICULTY_LEVELS.keys()) + ["ALL"])
    parser.add_argument("--trials", type=int, default=25)
    parser.add_argument("--p1", default="Alpha-Beta", choices=["Reflex", "Alpha-Beta"])
    parser.add_argument("--p2", default="Reflex", choices=["Reflex", "Alpha-Beta"])
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--csv", default=None)
    parser.add_argument("--force-alpha-beta", action="store_true")
    args = parser.parse_args()

    if args.difficulty == "ALL":
        for name in DIFFICULTY_LEVELS.keys():
            out_csv = None
            if args.csv:
                out_csv = args.csv.replace(".csv", f"_{name}.csv")
            run_trials(name, args.trials, args.p1, args.p2, args.seed, out_csv, args.force_alpha_beta)
    else:
        run_trials(args.difficulty, args.trials, args.p1, args.p2, args.seed, args.csv, args.force_alpha_beta)


if __name__ == "__main__":
    main()
