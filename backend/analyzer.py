# # # from typing import List, Dict, Any
# # # import math

# # # def _batches(trades: List[Dict], size: int = 20) -> List[List[Dict]]:
# # #     return [trades[i : i + size] for i in range(0, len(trades), size)]

# # # # ── existing helpers (win_rate, profit_factor, expectancy, avg_rr, max_drawdown, equity_curve, consecutive_stats) stay exactly the same ──
# # # # (I kept them untouched for brevity – just copy them from your original file)

# # # def median(values: list) -> float:
# # #     if not values:
# # #         return 0.0
# # #     sorted_vals = sorted(float(v) for v in values)
# # #     n = len(sorted_vals)
# # #     return round(sorted_vals[n // 2], 2)

# # # def median_win_rr(trades: List[Dict]) -> float:
# # #     wins = [t["rr"] for t in trades if t["outcome"] == "win"]
# # #     return median(wins)

# # # def median_loss_rr(trades: List[Dict]) -> float:
# # #     losses = [t["rr"] for t in trades if t["outcome"] == "loss"]
# # #     return median(losses)

# # # def wilson_confidence_interval(wins: int, n: int, z: float = 1.96) -> tuple:
# # #     if n == 0:
# # #         return 0.0, 0.0
# # #     p = wins / n
# # #     denom = 1 + z**2 / n
# # #     center = (p + z**2 / (2 * n)) / denom
# # #     margin = z * math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denom
# # #     lower = max(0.0, center - margin)
# # #     upper = min(1.0, center + margin)
# # #     return round(lower * 100, 1), round(upper * 100, 1)

# # # def current_loss_streak(trades: List[Dict]) -> int:
# # #     if not trades:
# # #         return 0
# # #     count = 0
# # #     for t in reversed(trades):
# # #         if t["outcome"] == "loss":
# # #             count += 1
# # #         else:
# # #             break
# # #     return count

# # # # ── FULL ANALYSIS (updated) ─────────────────────────────────────────────────
# # # def analyze(trades: List[Dict]) -> Dict[str, Any]:
# # #     if not trades:
# # #         return {"overall": {}, "batches": [], "equity_curve": []}

# # #     # Sort chronologically (important for streaks + equity curve)
# # #     trades = sorted(trades, key=lambda t: t.get("date", ""))

# # #     overall = {
# # #         "total_trades": len(trades),
# # #         "win_rate": win_rate(trades),
# # #         "profit_factor": profit_factor(trades),
# # #         "expectancy": expectancy(trades),
# # #         "avg_rr": avg_rr(trades),
# # #         "max_drawdown": max_drawdown(trades),
# # #         "streaks": consecutive_stats(trades),
# # #         "total_r": round(sum(t["pnl_r"] for t in trades), 3),
# # #         # NEW FEATURES
# # #         "median_win_rr": median_win_rr(trades),
# # #         "median_loss_rr": median_loss_rr(trades),
# # #         "win_rate_ci": f"{wilson_confidence_interval(sum(1 for t in trades if t['outcome'] == 'win'), len(trades))[0]}–"
# # #                        f"{wilson_confidence_interval(sum(1 for t in trades if t['outcome'] == 'win'), len(trades))[1]}%",
# # #         "current_loss_streak": current_loss_streak(trades),
# # #     }

# # #     batch_list = _batches(trades)
# # #     batches = []
# # #     for i, batch in enumerate(batch_list):
# # #         w = sum(1 for t in batch if t["outcome"] == "win")
# # #         lower, upper = wilson_confidence_interval(w, len(batch))
# # #         batches.append({
# # #             "batch_number": i + 1,
# # #             "trade_range": f"{i*20 + 1}–{i*20 + len(batch)}",
# # #             "total_trades": len(batch),
# # #             "win_rate": win_rate(batch),
# # #             "profit_factor": profit_factor(batch),
# # #             "expectancy": expectancy(batch),
# # #             "avg_rr": avg_rr(batch),
# # #             "max_drawdown": max_drawdown(batch),
# # #             "total_r": round(sum(t["pnl_r"] for t in batch), 3),
# # #             # NEW
# # #             "median_win_rr": median_win_rr(batch),
# # #             "median_loss_rr": median_loss_rr(batch),
# # #             "win_rate_ci": f"{lower}–{upper}%",
# # #         })

# # #     return {
# # #         "overall": overall,
# # #         "batches": batches,
# # #         "equity_curve": equity_curve(trades),
# # #     }

# # """
# # analyzer.py — Core statistics engine for the strategy tester.
# # All calculations operate on a list of trade dicts:
# #   { "id", "pair", "direction", "outcome", "rr", "pnl_r", "date", "notes" }
# # """

# # from typing import List, Dict, Any
# # import math


# # def _batches(trades: List[Dict], size: int = 20) -> List[List[Dict]]:
# #     """Split trades into fixed non-overlapping batches of `size`."""
# #     return [trades[i : i + size] for i in range(0, len(trades), size)]


# # # ── per-batch metrics ────────────────────────────────────────────────────────

# # def win_rate(trades: List[Dict]) -> float:
# #     if not trades:
# #         return 0.0
# #     wins = sum(1 for t in trades if t["outcome"] == "win")
# #     return round(wins / len(trades) * 100, 2)


# # def profit_factor(trades: List[Dict]) -> float:
# #     gross_profit = sum(t["pnl_r"] for t in trades if t["pnl_r"] > 0)
# #     gross_loss   = abs(sum(t["pnl_r"] for t in trades if t["pnl_r"] < 0))
# #     if gross_loss == 0:
# #         return round(gross_profit, 2) if gross_profit else 0.0
# #     return round(gross_profit / gross_loss, 2)


# # def expectancy(trades: List[Dict]) -> float:
# #     """Average R gained per trade (positive = edge exists)."""
# #     if not trades:
# #         return 0.0
# #     return round(sum(t["pnl_r"] for t in trades) / len(trades), 3)


# # def avg_rr(trades: List[Dict]) -> float:
# #     winning = [t["rr"] for t in trades if t["outcome"] == "win" and t["rr"]]
# #     if not winning:
# #         return 0.0
# #     return round(sum(winning) / len(winning), 2)


# # def max_drawdown(trades: List[Dict]) -> Dict[str, Any]:
# #     """
# #     Returns max drawdown as R and as percentage of peak equity.
# #     Equity curve starts at 0, each trade adds pnl_r.
# #     """
# #     if not trades:
# #         return {"r": 0.0, "pct": 0.0}

# #     equity = 0.0
# #     peak   = 0.0
# #     max_dd = 0.0

# #     for t in trades:
# #         equity += t["pnl_r"]
# #         if equity > peak:
# #             peak = equity
# #         dd = peak - equity
# #         if dd > max_dd:
# #             max_dd = dd

# #     pct = round(max_dd / peak * 100, 2) if peak > 0 else 0.0
# #     return {"r": round(max_dd, 3), "pct": pct}


# # def equity_curve(trades: List[Dict]) -> List[float]:
# #     """Running cumulative P&L in R units."""
# #     curve, running = [], 0.0
# #     for t in trades:
# #         running += t["pnl_r"]
# #         curve.append(round(running, 3))
# #     return curve


# # def consecutive_stats(trades: List[Dict]) -> Dict[str, int]:
# #     """Longest consecutive win / loss streaks."""
# #     max_wins = max_losses = cur_wins = cur_losses = 0
# #     for t in trades:
# #         if t["outcome"] == "win":
# #             cur_wins  += 1
# #             cur_losses = 0
# #         else:
# #             cur_losses += 1
# #             cur_wins   = 0
# #         max_wins   = max(max_wins,   cur_wins)
# #         max_losses = max(max_losses, cur_losses)
# #     return {"max_consecutive_wins": max_wins, "max_consecutive_losses": max_losses}


# # # ── NEW: advanced metrics ────────────────────────────────────────────────────

# # def median(values: list) -> float:
# #     if not values:
# #         return 0.0
# #     sorted_vals = sorted(float(v) for v in values)
# #     n = len(sorted_vals)
# #     return round(sorted_vals[n // 2], 2)


# # def median_win_rr(trades: List[Dict]) -> float:
# #     wins = [t["rr"] for t in trades if t["outcome"] == "win"]
# #     return median(wins)


# # def median_loss_rr(trades: List[Dict]) -> float:
# #     losses = [t["rr"] for t in trades if t["outcome"] == "loss"]
# #     return median(losses)


# # def wilson_confidence_interval(wins: int, n: int, z: float = 1.96) -> tuple:
# #     if n == 0:
# #         return 0.0, 0.0
# #     p = wins / n
# #     denom = 1 + z**2 / n
# #     center = (p + z**2 / (2 * n)) / denom
# #     margin = z * math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denom
# #     lower = max(0.0, center - margin)
# #     upper = min(1.0, center + margin)
# #     return round(lower * 100, 1), round(upper * 100, 1)


# # def current_loss_streak(trades: List[Dict]) -> int:
# #     if not trades:
# #         return 0
# #     count = 0
# #     for t in reversed(trades):
# #         if t["outcome"] == "loss":
# #             count += 1
# #         else:
# #             break
# #     return count


# # # ── full analysis ────────────────────────────────────────────────────────────

# # def analyze(trades: List[Dict]) -> Dict[str, Any]:
# #     """
# #     Run full analysis across all trades AND per batch of 20.
# #     Returns a structured dict ready to serialize as JSON.
# #     """
# #     if not trades:
# #         return {"overall": {}, "batches": [], "equity_curve": []}

# #     # Sort chronologically (important for streaks + equity curve)
# #     trades = sorted(trades, key=lambda t: t.get("date", ""))

# #     wins_total = sum(1 for t in trades if t["outcome"] == "win")
# #     ci_lower, ci_upper = wilson_confidence_interval(wins_total, len(trades))

# #     overall = {
# #         "total_trades":        len(trades),
# #         "win_rate":            win_rate(trades),
# #         "profit_factor":       profit_factor(trades),
# #         "expectancy":          expectancy(trades),
# #         "avg_rr":              avg_rr(trades),
# #         "max_drawdown":        max_drawdown(trades),
# #         "streaks":             consecutive_stats(trades),
# #         "total_r":             round(sum(t["pnl_r"] for t in trades), 3),
# #         # NEW
# #         "median_win_rr":       median_win_rr(trades),
# #         "median_loss_rr":      median_loss_rr(trades),
# #         "win_rate_ci":         f"{ci_lower}–{ci_upper}%",
# #         "current_loss_streak": current_loss_streak(trades),
# #     }

# #     batch_list = _batches(trades)
# #     batches = []
# #     for i, batch in enumerate(batch_list):
# #         w = sum(1 for t in batch if t["outcome"] == "win")
# #         lower, upper = wilson_confidence_interval(w, len(batch))
# #         batches.append({
# #             "batch_number":   i + 1,
# #             "trade_range":    f"{i*20 + 1}–{i*20 + len(batch)}",
# #             "total_trades":   len(batch),
# #             "win_rate":       win_rate(batch),
# #             "profit_factor":  profit_factor(batch),
# #             "expectancy":     expectancy(batch),
# #             "avg_rr":         avg_rr(batch),
# #             "max_drawdown":   max_drawdown(batch),
# #             "total_r":        round(sum(t["pnl_r"] for t in batch), 3),
# #             # NEW
# #             "median_win_rr":  median_win_rr(batch),
# #             "median_loss_rr": median_loss_rr(batch),
# #             "win_rate_ci":    f"{lower}–{upper}%",
# #         })

# #     return {
# #         "overall":      overall,
# #         "batches":      batches,
# #         "equity_curve": equity_curve(trades),
# #     }



# """
# analyzer.py — Core statistics engine for the strategy tester.
# All calculations operate on a list of trade dicts:
#   { "id", "pair", "direction", "outcome", "rr", "pnl_r", "date", "session", "mood", "journal", "notes" }
# """

# from typing import List, Dict, Any
# import math


# def _batches(trades: List[Dict], size: int = 20) -> List[List[Dict]]:
#     return [trades[i : i + size] for i in range(0, len(trades), size)]


# def win_rate(trades: List[Dict]) -> float:
#     if not trades:
#         return 0.0
#     wins = sum(1 for t in trades if t["outcome"] == "win")
#     return round(wins / len(trades) * 100, 2)


# def profit_factor(trades: List[Dict]) -> float:
#     gross_profit = sum(t["pnl_r"] for t in trades if t["pnl_r"] > 0)
#     gross_loss   = abs(sum(t["pnl_r"] for t in trades if t["pnl_r"] < 0))
#     if gross_loss == 0:
#         return round(gross_profit, 2) if gross_profit else 0.0
#     return round(gross_profit / gross_loss, 2)


# def expectancy(trades: List[Dict]) -> float:
#     if not trades:
#         return 0.0
#     return round(sum(t["pnl_r"] for t in trades) / len(trades), 3)


# def avg_rr(trades: List[Dict]) -> float:
#     winning = [t["rr"] for t in trades if t["outcome"] == "win" and t["rr"]]
#     if not winning:
#         return 0.0
#     return round(sum(winning) / len(winning), 2)


# def max_drawdown(trades: List[Dict]) -> Dict[str, Any]:
#     if not trades:
#         return {"r": 0.0, "pct": 0.0}
#     equity = 0.0
#     peak   = 0.0
#     max_dd = 0.0
#     for t in trades:
#         equity += t["pnl_r"]
#         if equity > peak:
#             peak = equity
#         dd = peak - equity
#         if dd > max_dd:
#             max_dd = dd
#     pct = round(max_dd / peak * 100, 2) if peak > 0 else 0.0
#     return {"r": round(max_dd, 3), "pct": pct}


# def equity_curve(trades: List[Dict]) -> List[float]:
#     curve, running = [], 0.0
#     for t in trades:
#         running += t["pnl_r"]
#         curve.append(round(running, 3))
#     return curve


# def consecutive_stats(trades: List[Dict]) -> Dict[str, int]:
#     max_wins = max_losses = cur_wins = cur_losses = 0
#     for t in trades:
#         if t["outcome"] == "win":
#             cur_wins  += 1
#             cur_losses = 0
#         else:
#             cur_losses += 1
#             cur_wins   = 0
#         max_wins   = max(max_wins,   cur_wins)
#         max_losses = max(max_losses, cur_losses)
#     return {"max_consecutive_wins": max_wins, "max_consecutive_losses": max_losses}


# def median(values: list) -> float:
#     if not values:
#         return 0.0
#     sorted_vals = sorted(float(v) for v in values)
#     n = len(sorted_vals)
#     return round(sorted_vals[n // 2], 2)


# def median_win_rr(trades: List[Dict]) -> float:
#     wins = [t["rr"] for t in trades if t["outcome"] == "win"]
#     return median(wins)


# def median_loss_rr(trades: List[Dict]) -> float:
#     losses = [t["rr"] for t in trades if t["outcome"] == "loss"]
#     return median(losses)


# def wilson_confidence_interval(wins: int, n: int, z: float = 1.96) -> tuple:
#     if n == 0:
#         return 0.0, 0.0
#     p = wins / n
#     denom  = 1 + z**2 / n
#     center = (p + z**2 / (2 * n)) / denom
#     margin = z * math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denom
#     lower  = max(0.0, center - margin)
#     upper  = min(1.0, center + margin)
#     return round(lower * 100, 1), round(upper * 100, 1)


# def current_loss_streak(trades: List[Dict]) -> int:
#     if not trades:
#         return 0
#     count = 0
#     for t in reversed(trades):
#         if t["outcome"] == "loss":
#             count += 1
#         else:
#             break
#     return count


# # ── NEW: session breakdown ────────────────────────────────────────────────────

# SESSIONS = ["asian", "london", "new_york", "overlap"]

# def session_breakdown(trades: List[Dict]) -> Dict[str, Any]:
#     """Win rate, total R and trade count broken down by session."""
#     result = {}
#     for session in SESSIONS:
#         session_trades = [t for t in trades if t.get("session", "").lower() == session]
#         if not session_trades:
#             result[session] = {"trades": 0, "win_rate": 0.0, "total_r": 0.0, "expectancy": 0.0}
#             continue
#         result[session] = {
#             "trades":     len(session_trades),
#             "win_rate":   win_rate(session_trades),
#             "total_r":    round(sum(t["pnl_r"] for t in session_trades), 3),
#             "expectancy": expectancy(session_trades),
#         }
#     return result


# # ── NEW: mood breakdown ───────────────────────────────────────────────────────

# def mood_breakdown(trades: List[Dict]) -> Dict[str, Any]:
#     """Win rate and total R broken down by mood tag."""
#     moods = {}
#     for t in trades:
#         mood = t.get("mood", "").strip().lower()
#         if not mood:
#             continue
#         if mood not in moods:
#             moods[mood] = []
#         moods[mood].append(t)
#     result = {}
#     for mood, mtrades in moods.items():
#         result[mood] = {
#             "trades":   len(mtrades),
#             "win_rate": win_rate(mtrades),
#             "total_r":  round(sum(t["pnl_r"] for t in mtrades), 3),
#         }
#     return result


# # ── full analysis ─────────────────────────────────────────────────────────────

# def analyze(trades: List[Dict]) -> Dict[str, Any]:
#     if not trades:
#         return {"overall": {}, "batches": [], "equity_curve": [], "session_breakdown": {}, "mood_breakdown": {}}

#     trades = sorted(trades, key=lambda t: t.get("date", ""))

#     wins_total = sum(1 for t in trades if t["outcome"] == "win")
#     ci_lower, ci_upper = wilson_confidence_interval(wins_total, len(trades))

#     overall = {
#         "total_trades":        len(trades),
#         "win_rate":            win_rate(trades),
#         "profit_factor":       profit_factor(trades),
#         "expectancy":          expectancy(trades),
#         "avg_rr":              avg_rr(trades),
#         "max_drawdown":        max_drawdown(trades),
#         "streaks":             consecutive_stats(trades),
#         "total_r":             round(sum(t["pnl_r"] for t in trades), 3),
#         "median_win_rr":       median_win_rr(trades),
#         "median_loss_rr":      median_loss_rr(trades),
#         "win_rate_ci":         f"{ci_lower}–{ci_upper}%",
#         "current_loss_streak": current_loss_streak(trades),
#     }

#     batch_list = _batches(trades)
#     batches = []
#     for i, batch in enumerate(batch_list):
#         w = sum(1 for t in batch if t["outcome"] == "win")
#         lower, upper = wilson_confidence_interval(w, len(batch))
#         batches.append({
#             "batch_number":   i + 1,
#             "trade_range":    f"{i*20 + 1}–{i*20 + len(batch)}",
#             "total_trades":   len(batch),
#             "win_rate":       win_rate(batch),
#             "profit_factor":  profit_factor(batch),
#             "expectancy":     expectancy(batch),
#             "avg_rr":         avg_rr(batch),
#             "max_drawdown":   max_drawdown(batch),
#             "total_r":        round(sum(t["pnl_r"] for t in batch), 3),
#             "median_win_rr":  median_win_rr(batch),
#             "median_loss_rr": median_loss_rr(batch),
#             "win_rate_ci":    f"{lower}–{upper}%",
#         })

#     return {
#         "overall":           overall,
#         "batches":           batches,
#         "equity_curve":      equity_curve(trades),
#         "session_breakdown": session_breakdown(trades),
#         "mood_breakdown":    mood_breakdown(trades),
#     }


"""
analyzer.py — Core statistics engine for the strategy tester.
Trade dict fields:
  id, pair, direction, outcome, rr, pnl_r, date,
  session, mood, journal, notes, positions
"""

from typing import List, Dict, Any
import math


def _batches(trades: List[Dict], size: int = 20) -> List[List[Dict]]:
    return [trades[i : i + size] for i in range(0, len(trades), size)]


def win_rate(trades: List[Dict]) -> float:
    if not trades:
        return 0.0
    wins = sum(1 for t in trades if t["outcome"] == "win")
    return round(wins / len(trades) * 100, 2)


def profit_factor(trades: List[Dict]) -> float:
    gross_profit = sum(t["pnl_r"] for t in trades if t["pnl_r"] > 0)
    gross_loss   = abs(sum(t["pnl_r"] for t in trades if t["pnl_r"] < 0))
    if gross_loss == 0:
        return round(gross_profit, 2) if gross_profit else 0.0
    return round(gross_profit / gross_loss, 2)


def expectancy(trades: List[Dict]) -> float:
    if not trades:
        return 0.0
    return round(sum(t["pnl_r"] for t in trades) / len(trades), 3)


def avg_rr(trades: List[Dict]) -> float:
    winning = [t["rr"] for t in trades if t["outcome"] == "win" and t["rr"]]
    if not winning:
        return 0.0
    return round(sum(winning) / len(winning), 2)


def max_drawdown(trades: List[Dict]) -> Dict[str, Any]:
    if not trades:
        return {"r": 0.0, "pct": 0.0}
    equity = peak = max_dd = 0.0
    for t in trades:
        equity += t["pnl_r"]
        if equity > peak:
            peak = equity
        dd = peak - equity
        if dd > max_dd:
            max_dd = dd
    pct = round(max_dd / peak * 100, 2) if peak > 0 else 0.0
    return {"r": round(max_dd, 3), "pct": pct}


def equity_curve(trades: List[Dict]) -> List[float]:
    curve, running = [], 0.0
    for t in trades:
        running += t["pnl_r"]
        curve.append(round(running, 3))
    return curve


def consecutive_stats(trades: List[Dict]) -> Dict[str, int]:
    max_wins = max_losses = cur_wins = cur_losses = 0
    for t in trades:
        if t["outcome"] == "win":
            cur_wins += 1; cur_losses = 0
        else:
            cur_losses += 1; cur_wins = 0
        max_wins   = max(max_wins,   cur_wins)
        max_losses = max(max_losses, cur_losses)
    return {"max_consecutive_wins": max_wins, "max_consecutive_losses": max_losses}


def median(values: list) -> float:
    if not values:
        return 0.0
    sv = sorted(float(v) for v in values)
    return round(sv[len(sv) // 2], 2)


def median_win_rr(trades):  return median([t["rr"] for t in trades if t["outcome"] == "win"])
def median_loss_rr(trades): return median([t["rr"] for t in trades if t["outcome"] == "loss"])


def wilson_confidence_interval(wins: int, n: int, z: float = 1.96) -> tuple:
    if n == 0:
        return 0.0, 0.0
    p      = wins / n
    denom  = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    margin = z * math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denom
    return round(max(0.0, center - margin) * 100, 1), round(min(1.0, center + margin) * 100, 1)


def current_loss_streak(trades: List[Dict]) -> int:
    count = 0
    for t in reversed(trades):
        if t["outcome"] == "loss": count += 1
        else: break
    return count


def session_breakdown(trades: List[Dict]) -> Dict[str, Any]:
    result = {}
    for session in ["asian", "london", "new_york", "overlap"]:
        st = [t for t in trades if t.get("session", "").lower() == session]
        result[session] = {
            "trades": len(st),
            "win_rate": win_rate(st),
            "total_r": round(sum(t["pnl_r"] for t in st), 3),
            "expectancy": expectancy(st),
        } if st else {"trades": 0, "win_rate": 0.0, "total_r": 0.0, "expectancy": 0.0}
    return result


def mood_breakdown(trades: List[Dict]) -> Dict[str, Any]:
    moods = {}
    for t in trades:
        mood = t.get("mood", "").strip().lower()
        if mood:
            moods.setdefault(mood, []).append(t)
    return {
        mood: {"trades": len(mt), "win_rate": win_rate(mt), "total_r": round(sum(t["pnl_r"] for t in mt), 3)}
        for mood, mt in moods.items()
    }


def positions_breakdown(trades: List[Dict]) -> Dict[str, Any]:
    """Average positions per trade, and win rate grouped by position count."""
    pos_vals = [t.get("positions", 1) for t in trades if t.get("positions")]
    avg_pos  = round(sum(pos_vals) / len(pos_vals), 2) if pos_vals else 0.0
    groups   = {}
    for t in trades:
        p = str(t.get("positions", 1))
        groups.setdefault(p, []).append(t)
    return {
        "avg_positions": avg_pos,
        "by_positions": {
            p: {"trades": len(gt), "win_rate": win_rate(gt), "total_r": round(sum(t["pnl_r"] for t in gt), 3)}
            for p, gt in sorted(groups.items(), key=lambda x: int(x[0]))
        }
    }


def analyze(trades: List[Dict]) -> Dict[str, Any]:
    if not trades:
        return {"overall": {}, "batches": [], "equity_curve": [],
                "session_breakdown": {}, "mood_breakdown": {}, "positions_breakdown": {}}

    trades = sorted(trades, key=lambda t: t.get("date", ""))
    wins   = sum(1 for t in trades if t["outcome"] == "win")
    ci_lo, ci_hi = wilson_confidence_interval(wins, len(trades))

    overall = {
        "total_trades":        len(trades),
        "win_rate":            win_rate(trades),
        "profit_factor":       profit_factor(trades),
        "expectancy":          expectancy(trades),
        "avg_rr":              avg_rr(trades),
        "max_drawdown":        max_drawdown(trades),
        "streaks":             consecutive_stats(trades),
        "total_r":             round(sum(t["pnl_r"] for t in trades), 3),
        "median_win_rr":       median_win_rr(trades),
        "median_loss_rr":      median_loss_rr(trades),
        "win_rate_ci":         f"{ci_lo}–{ci_hi}%",
        "current_loss_streak": current_loss_streak(trades),
    }

    batches = []
    for i, batch in enumerate(_batches(trades)):
        w = sum(1 for t in batch if t["outcome"] == "win")
        lo, hi = wilson_confidence_interval(w, len(batch))
        batches.append({
            "batch_number":   i + 1,
            "trade_range":    f"{i*20+1}–{i*20+len(batch)}",
            "total_trades":   len(batch),
            "win_rate":       win_rate(batch),
            "profit_factor":  profit_factor(batch),
            "expectancy":     expectancy(batch),
            "avg_rr":         avg_rr(batch),
            "max_drawdown":   max_drawdown(batch),
            "total_r":        round(sum(t["pnl_r"] for t in batch), 3),
            "median_win_rr":  median_win_rr(batch),
            "median_loss_rr": median_loss_rr(batch),
            "win_rate_ci":    f"{lo}–{hi}%",
        })

    return {
        "overall":              overall,
        "batches":              batches,
        "equity_curve":         equity_curve(trades),
        "session_breakdown":    session_breakdown(trades),
        "mood_breakdown":       mood_breakdown(trades),
        "positions_breakdown":  positions_breakdown(trades),
    }