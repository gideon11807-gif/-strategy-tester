# # # # # from typing import List, Dict, Any
# # # # # import math

# # # # # def _batches(trades: List[Dict], size: int = 20) -> List[List[Dict]]:
# # # # #     return [trades[i : i + size] for i in range(0, len(trades), size)]

# # # # # # ── existing helpers (win_rate, profit_factor, expectancy, avg_rr, max_drawdown, equity_curve, consecutive_stats) stay exactly the same ──
# # # # # # (I kept them untouched for brevity – just copy them from your original file)

# # # # # def median(values: list) -> float:
# # # # #     if not values:
# # # # #         return 0.0
# # # # #     sorted_vals = sorted(float(v) for v in values)
# # # # #     n = len(sorted_vals)
# # # # #     return round(sorted_vals[n // 2], 2)

# # # # # def median_win_rr(trades: List[Dict]) -> float:
# # # # #     wins = [t["rr"] for t in trades if t["outcome"] == "win"]
# # # # #     return median(wins)

# # # # # def median_loss_rr(trades: List[Dict]) -> float:
# # # # #     losses = [t["rr"] for t in trades if t["outcome"] == "loss"]
# # # # #     return median(losses)

# # # # # def wilson_confidence_interval(wins: int, n: int, z: float = 1.96) -> tuple:
# # # # #     if n == 0:
# # # # #         return 0.0, 0.0
# # # # #     p = wins / n
# # # # #     denom = 1 + z**2 / n
# # # # #     center = (p + z**2 / (2 * n)) / denom
# # # # #     margin = z * math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denom
# # # # #     lower = max(0.0, center - margin)
# # # # #     upper = min(1.0, center + margin)
# # # # #     return round(lower * 100, 1), round(upper * 100, 1)

# # # # # def current_loss_streak(trades: List[Dict]) -> int:
# # # # #     if not trades:
# # # # #         return 0
# # # # #     count = 0
# # # # #     for t in reversed(trades):
# # # # #         if t["outcome"] == "loss":
# # # # #             count += 1
# # # # #         else:
# # # # #             break
# # # # #     return count

# # # # # # ── FULL ANALYSIS (updated) ─────────────────────────────────────────────────
# # # # # def analyze(trades: List[Dict]) -> Dict[str, Any]:
# # # # #     if not trades:
# # # # #         return {"overall": {}, "batches": [], "equity_curve": []}

# # # # #     # Sort chronologically (important for streaks + equity curve)
# # # # #     trades = sorted(trades, key=lambda t: t.get("date", ""))

# # # # #     overall = {
# # # # #         "total_trades": len(trades),
# # # # #         "win_rate": win_rate(trades),
# # # # #         "profit_factor": profit_factor(trades),
# # # # #         "expectancy": expectancy(trades),
# # # # #         "avg_rr": avg_rr(trades),
# # # # #         "max_drawdown": max_drawdown(trades),
# # # # #         "streaks": consecutive_stats(trades),
# # # # #         "total_r": round(sum(t["pnl_r"] for t in trades), 3),
# # # # #         # NEW FEATURES
# # # # #         "median_win_rr": median_win_rr(trades),
# # # # #         "median_loss_rr": median_loss_rr(trades),
# # # # #         "win_rate_ci": f"{wilson_confidence_interval(sum(1 for t in trades if t['outcome'] == 'win'), len(trades))[0]}–"
# # # # #                        f"{wilson_confidence_interval(sum(1 for t in trades if t['outcome'] == 'win'), len(trades))[1]}%",
# # # # #         "current_loss_streak": current_loss_streak(trades),
# # # # #     }

# # # # #     batch_list = _batches(trades)
# # # # #     batches = []
# # # # #     for i, batch in enumerate(batch_list):
# # # # #         w = sum(1 for t in batch if t["outcome"] == "win")
# # # # #         lower, upper = wilson_confidence_interval(w, len(batch))
# # # # #         batches.append({
# # # # #             "batch_number": i + 1,
# # # # #             "trade_range": f"{i*20 + 1}–{i*20 + len(batch)}",
# # # # #             "total_trades": len(batch),
# # # # #             "win_rate": win_rate(batch),
# # # # #             "profit_factor": profit_factor(batch),
# # # # #             "expectancy": expectancy(batch),
# # # # #             "avg_rr": avg_rr(batch),
# # # # #             "max_drawdown": max_drawdown(batch),
# # # # #             "total_r": round(sum(t["pnl_r"] for t in batch), 3),
# # # # #             # NEW
# # # # #             "median_win_rr": median_win_rr(batch),
# # # # #             "median_loss_rr": median_loss_rr(batch),
# # # # #             "win_rate_ci": f"{lower}–{upper}%",
# # # # #         })

# # # # #     return {
# # # # #         "overall": overall,
# # # # #         "batches": batches,
# # # # #         "equity_curve": equity_curve(trades),
# # # # #     }

# # # # """
# # # # analyzer.py — Core statistics engine for the strategy tester.
# # # # All calculations operate on a list of trade dicts:
# # # #   { "id", "pair", "direction", "outcome", "rr", "pnl_r", "date", "notes" }
# # # # """

# # # # from typing import List, Dict, Any
# # # # import math


# # # # def _batches(trades: List[Dict], size: int = 20) -> List[List[Dict]]:
# # # #     """Split trades into fixed non-overlapping batches of `size`."""
# # # #     return [trades[i : i + size] for i in range(0, len(trades), size)]


# # # # # ── per-batch metrics ────────────────────────────────────────────────────────

# # # # def win_rate(trades: List[Dict]) -> float:
# # # #     if not trades:
# # # #         return 0.0
# # # #     wins = sum(1 for t in trades if t["outcome"] == "win")
# # # #     return round(wins / len(trades) * 100, 2)


# # # # def profit_factor(trades: List[Dict]) -> float:
# # # #     gross_profit = sum(t["pnl_r"] for t in trades if t["pnl_r"] > 0)
# # # #     gross_loss   = abs(sum(t["pnl_r"] for t in trades if t["pnl_r"] < 0))
# # # #     if gross_loss == 0:
# # # #         return round(gross_profit, 2) if gross_profit else 0.0
# # # #     return round(gross_profit / gross_loss, 2)


# # # # def expectancy(trades: List[Dict]) -> float:
# # # #     """Average R gained per trade (positive = edge exists)."""
# # # #     if not trades:
# # # #         return 0.0
# # # #     return round(sum(t["pnl_r"] for t in trades) / len(trades), 3)


# # # # def avg_rr(trades: List[Dict]) -> float:
# # # #     winning = [t["rr"] for t in trades if t["outcome"] == "win" and t["rr"]]
# # # #     if not winning:
# # # #         return 0.0
# # # #     return round(sum(winning) / len(winning), 2)


# # # # def max_drawdown(trades: List[Dict]) -> Dict[str, Any]:
# # # #     """
# # # #     Returns max drawdown as R and as percentage of peak equity.
# # # #     Equity curve starts at 0, each trade adds pnl_r.
# # # #     """
# # # #     if not trades:
# # # #         return {"r": 0.0, "pct": 0.0}

# # # #     equity = 0.0
# # # #     peak   = 0.0
# # # #     max_dd = 0.0

# # # #     for t in trades:
# # # #         equity += t["pnl_r"]
# # # #         if equity > peak:
# # # #             peak = equity
# # # #         dd = peak - equity
# # # #         if dd > max_dd:
# # # #             max_dd = dd

# # # #     pct = round(max_dd / peak * 100, 2) if peak > 0 else 0.0
# # # #     return {"r": round(max_dd, 3), "pct": pct}


# # # # def equity_curve(trades: List[Dict]) -> List[float]:
# # # #     """Running cumulative P&L in R units."""
# # # #     curve, running = [], 0.0
# # # #     for t in trades:
# # # #         running += t["pnl_r"]
# # # #         curve.append(round(running, 3))
# # # #     return curve


# # # # def consecutive_stats(trades: List[Dict]) -> Dict[str, int]:
# # # #     """Longest consecutive win / loss streaks."""
# # # #     max_wins = max_losses = cur_wins = cur_losses = 0
# # # #     for t in trades:
# # # #         if t["outcome"] == "win":
# # # #             cur_wins  += 1
# # # #             cur_losses = 0
# # # #         else:
# # # #             cur_losses += 1
# # # #             cur_wins   = 0
# # # #         max_wins   = max(max_wins,   cur_wins)
# # # #         max_losses = max(max_losses, cur_losses)
# # # #     return {"max_consecutive_wins": max_wins, "max_consecutive_losses": max_losses}


# # # # # ── NEW: advanced metrics ────────────────────────────────────────────────────

# # # # def median(values: list) -> float:
# # # #     if not values:
# # # #         return 0.0
# # # #     sorted_vals = sorted(float(v) for v in values)
# # # #     n = len(sorted_vals)
# # # #     return round(sorted_vals[n // 2], 2)


# # # # def median_win_rr(trades: List[Dict]) -> float:
# # # #     wins = [t["rr"] for t in trades if t["outcome"] == "win"]
# # # #     return median(wins)


# # # # def median_loss_rr(trades: List[Dict]) -> float:
# # # #     losses = [t["rr"] for t in trades if t["outcome"] == "loss"]
# # # #     return median(losses)


# # # # def wilson_confidence_interval(wins: int, n: int, z: float = 1.96) -> tuple:
# # # #     if n == 0:
# # # #         return 0.0, 0.0
# # # #     p = wins / n
# # # #     denom = 1 + z**2 / n
# # # #     center = (p + z**2 / (2 * n)) / denom
# # # #     margin = z * math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denom
# # # #     lower = max(0.0, center - margin)
# # # #     upper = min(1.0, center + margin)
# # # #     return round(lower * 100, 1), round(upper * 100, 1)


# # # # def current_loss_streak(trades: List[Dict]) -> int:
# # # #     if not trades:
# # # #         return 0
# # # #     count = 0
# # # #     for t in reversed(trades):
# # # #         if t["outcome"] == "loss":
# # # #             count += 1
# # # #         else:
# # # #             break
# # # #     return count


# # # # # ── full analysis ────────────────────────────────────────────────────────────

# # # # def analyze(trades: List[Dict]) -> Dict[str, Any]:
# # # #     """
# # # #     Run full analysis across all trades AND per batch of 20.
# # # #     Returns a structured dict ready to serialize as JSON.
# # # #     """
# # # #     if not trades:
# # # #         return {"overall": {}, "batches": [], "equity_curve": []}

# # # #     # Sort chronologically (important for streaks + equity curve)
# # # #     trades = sorted(trades, key=lambda t: t.get("date", ""))

# # # #     wins_total = sum(1 for t in trades if t["outcome"] == "win")
# # # #     ci_lower, ci_upper = wilson_confidence_interval(wins_total, len(trades))

# # # #     overall = {
# # # #         "total_trades":        len(trades),
# # # #         "win_rate":            win_rate(trades),
# # # #         "profit_factor":       profit_factor(trades),
# # # #         "expectancy":          expectancy(trades),
# # # #         "avg_rr":              avg_rr(trades),
# # # #         "max_drawdown":        max_drawdown(trades),
# # # #         "streaks":             consecutive_stats(trades),
# # # #         "total_r":             round(sum(t["pnl_r"] for t in trades), 3),
# # # #         # NEW
# # # #         "median_win_rr":       median_win_rr(trades),
# # # #         "median_loss_rr":      median_loss_rr(trades),
# # # #         "win_rate_ci":         f"{ci_lower}–{ci_upper}%",
# # # #         "current_loss_streak": current_loss_streak(trades),
# # # #     }

# # # #     batch_list = _batches(trades)
# # # #     batches = []
# # # #     for i, batch in enumerate(batch_list):
# # # #         w = sum(1 for t in batch if t["outcome"] == "win")
# # # #         lower, upper = wilson_confidence_interval(w, len(batch))
# # # #         batches.append({
# # # #             "batch_number":   i + 1,
# # # #             "trade_range":    f"{i*20 + 1}–{i*20 + len(batch)}",
# # # #             "total_trades":   len(batch),
# # # #             "win_rate":       win_rate(batch),
# # # #             "profit_factor":  profit_factor(batch),
# # # #             "expectancy":     expectancy(batch),
# # # #             "avg_rr":         avg_rr(batch),
# # # #             "max_drawdown":   max_drawdown(batch),
# # # #             "total_r":        round(sum(t["pnl_r"] for t in batch), 3),
# # # #             # NEW
# # # #             "median_win_rr":  median_win_rr(batch),
# # # #             "median_loss_rr": median_loss_rr(batch),
# # # #             "win_rate_ci":    f"{lower}–{upper}%",
# # # #         })

# # # #     return {
# # # #         "overall":      overall,
# # # #         "batches":      batches,
# # # #         "equity_curve": equity_curve(trades),
# # # #     }



# # # """
# # # analyzer.py — Core statistics engine for the strategy tester.
# # # All calculations operate on a list of trade dicts:
# # #   { "id", "pair", "direction", "outcome", "rr", "pnl_r", "date", "session", "mood", "journal", "notes" }
# # # """

# # # from typing import List, Dict, Any
# # # import math


# # # def _batches(trades: List[Dict], size: int = 20) -> List[List[Dict]]:
# # #     return [trades[i : i + size] for i in range(0, len(trades), size)]


# # # def win_rate(trades: List[Dict]) -> float:
# # #     if not trades:
# # #         return 0.0
# # #     wins = sum(1 for t in trades if t["outcome"] == "win")
# # #     return round(wins / len(trades) * 100, 2)


# # # def profit_factor(trades: List[Dict]) -> float:
# # #     gross_profit = sum(t["pnl_r"] for t in trades if t["pnl_r"] > 0)
# # #     gross_loss   = abs(sum(t["pnl_r"] for t in trades if t["pnl_r"] < 0))
# # #     if gross_loss == 0:
# # #         return round(gross_profit, 2) if gross_profit else 0.0
# # #     return round(gross_profit / gross_loss, 2)


# # # def expectancy(trades: List[Dict]) -> float:
# # #     if not trades:
# # #         return 0.0
# # #     return round(sum(t["pnl_r"] for t in trades) / len(trades), 3)


# # # def avg_rr(trades: List[Dict]) -> float:
# # #     winning = [t["rr"] for t in trades if t["outcome"] == "win" and t["rr"]]
# # #     if not winning:
# # #         return 0.0
# # #     return round(sum(winning) / len(winning), 2)


# # # def max_drawdown(trades: List[Dict]) -> Dict[str, Any]:
# # #     if not trades:
# # #         return {"r": 0.0, "pct": 0.0}
# # #     equity = 0.0
# # #     peak   = 0.0
# # #     max_dd = 0.0
# # #     for t in trades:
# # #         equity += t["pnl_r"]
# # #         if equity > peak:
# # #             peak = equity
# # #         dd = peak - equity
# # #         if dd > max_dd:
# # #             max_dd = dd
# # #     pct = round(max_dd / peak * 100, 2) if peak > 0 else 0.0
# # #     return {"r": round(max_dd, 3), "pct": pct}


# # # def equity_curve(trades: List[Dict]) -> List[float]:
# # #     curve, running = [], 0.0
# # #     for t in trades:
# # #         running += t["pnl_r"]
# # #         curve.append(round(running, 3))
# # #     return curve


# # # def consecutive_stats(trades: List[Dict]) -> Dict[str, int]:
# # #     max_wins = max_losses = cur_wins = cur_losses = 0
# # #     for t in trades:
# # #         if t["outcome"] == "win":
# # #             cur_wins  += 1
# # #             cur_losses = 0
# # #         else:
# # #             cur_losses += 1
# # #             cur_wins   = 0
# # #         max_wins   = max(max_wins,   cur_wins)
# # #         max_losses = max(max_losses, cur_losses)
# # #     return {"max_consecutive_wins": max_wins, "max_consecutive_losses": max_losses}


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
# # #     denom  = 1 + z**2 / n
# # #     center = (p + z**2 / (2 * n)) / denom
# # #     margin = z * math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denom
# # #     lower  = max(0.0, center - margin)
# # #     upper  = min(1.0, center + margin)
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


# # # # ── NEW: session breakdown ────────────────────────────────────────────────────

# # # SESSIONS = ["asian", "london", "new_york", "overlap"]

# # # def session_breakdown(trades: List[Dict]) -> Dict[str, Any]:
# # #     """Win rate, total R and trade count broken down by session."""
# # #     result = {}
# # #     for session in SESSIONS:
# # #         session_trades = [t for t in trades if t.get("session", "").lower() == session]
# # #         if not session_trades:
# # #             result[session] = {"trades": 0, "win_rate": 0.0, "total_r": 0.0, "expectancy": 0.0}
# # #             continue
# # #         result[session] = {
# # #             "trades":     len(session_trades),
# # #             "win_rate":   win_rate(session_trades),
# # #             "total_r":    round(sum(t["pnl_r"] for t in session_trades), 3),
# # #             "expectancy": expectancy(session_trades),
# # #         }
# # #     return result


# # # # ── NEW: mood breakdown ───────────────────────────────────────────────────────

# # # def mood_breakdown(trades: List[Dict]) -> Dict[str, Any]:
# # #     """Win rate and total R broken down by mood tag."""
# # #     moods = {}
# # #     for t in trades:
# # #         mood = t.get("mood", "").strip().lower()
# # #         if not mood:
# # #             continue
# # #         if mood not in moods:
# # #             moods[mood] = []
# # #         moods[mood].append(t)
# # #     result = {}
# # #     for mood, mtrades in moods.items():
# # #         result[mood] = {
# # #             "trades":   len(mtrades),
# # #             "win_rate": win_rate(mtrades),
# # #             "total_r":  round(sum(t["pnl_r"] for t in mtrades), 3),
# # #         }
# # #     return result


# # # # ── full analysis ─────────────────────────────────────────────────────────────

# # # def analyze(trades: List[Dict]) -> Dict[str, Any]:
# # #     if not trades:
# # #         return {"overall": {}, "batches": [], "equity_curve": [], "session_breakdown": {}, "mood_breakdown": {}}

# # #     trades = sorted(trades, key=lambda t: t.get("date", ""))

# # #     wins_total = sum(1 for t in trades if t["outcome"] == "win")
# # #     ci_lower, ci_upper = wilson_confidence_interval(wins_total, len(trades))

# # #     overall = {
# # #         "total_trades":        len(trades),
# # #         "win_rate":            win_rate(trades),
# # #         "profit_factor":       profit_factor(trades),
# # #         "expectancy":          expectancy(trades),
# # #         "avg_rr":              avg_rr(trades),
# # #         "max_drawdown":        max_drawdown(trades),
# # #         "streaks":             consecutive_stats(trades),
# # #         "total_r":             round(sum(t["pnl_r"] for t in trades), 3),
# # #         "median_win_rr":       median_win_rr(trades),
# # #         "median_loss_rr":      median_loss_rr(trades),
# # #         "win_rate_ci":         f"{ci_lower}–{ci_upper}%",
# # #         "current_loss_streak": current_loss_streak(trades),
# # #     }

# # #     batch_list = _batches(trades)
# # #     batches = []
# # #     for i, batch in enumerate(batch_list):
# # #         w = sum(1 for t in batch if t["outcome"] == "win")
# # #         lower, upper = wilson_confidence_interval(w, len(batch))
# # #         batches.append({
# # #             "batch_number":   i + 1,
# # #             "trade_range":    f"{i*20 + 1}–{i*20 + len(batch)}",
# # #             "total_trades":   len(batch),
# # #             "win_rate":       win_rate(batch),
# # #             "profit_factor":  profit_factor(batch),
# # #             "expectancy":     expectancy(batch),
# # #             "avg_rr":         avg_rr(batch),
# # #             "max_drawdown":   max_drawdown(batch),
# # #             "total_r":        round(sum(t["pnl_r"] for t in batch), 3),
# # #             "median_win_rr":  median_win_rr(batch),
# # #             "median_loss_rr": median_loss_rr(batch),
# # #             "win_rate_ci":    f"{lower}–{upper}%",
# # #         })

# # #     return {
# # #         "overall":           overall,
# # #         "batches":           batches,
# # #         "equity_curve":      equity_curve(trades),
# # #         "session_breakdown": session_breakdown(trades),
# # #         "mood_breakdown":    mood_breakdown(trades),
# # #     }


# # """
# # analyzer.py — Core statistics engine for the strategy tester.
# # Trade dict fields:
# #   id, pair, direction, outcome, rr, pnl_r, date,
# #   session, mood, journal, notes, positions
# # """

# # from typing import List, Dict, Any
# # import math


# # def _batches(trades: List[Dict], size: int = 20) -> List[List[Dict]]:
# #     return [trades[i : i + size] for i in range(0, len(trades), size)]


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
# #     if not trades:
# #         return 0.0
# #     return round(sum(t["pnl_r"] for t in trades) / len(trades), 3)


# # def avg_rr(trades: List[Dict]) -> float:
# #     winning = [t["rr"] for t in trades if t["outcome"] == "win" and t["rr"]]
# #     if not winning:
# #         return 0.0
# #     return round(sum(winning) / len(winning), 2)


# # def max_drawdown(trades: List[Dict]) -> Dict[str, Any]:
# #     if not trades:
# #         return {"r": 0.0, "pct": 0.0}
# #     equity = peak = max_dd = 0.0
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
# #     curve, running = [], 0.0
# #     for t in trades:
# #         running += t["pnl_r"]
# #         curve.append(round(running, 3))
# #     return curve


# # def consecutive_stats(trades: List[Dict]) -> Dict[str, int]:
# #     max_wins = max_losses = cur_wins = cur_losses = 0
# #     for t in trades:
# #         if t["outcome"] == "win":
# #             cur_wins += 1; cur_losses = 0
# #         else:
# #             cur_losses += 1; cur_wins = 0
# #         max_wins   = max(max_wins,   cur_wins)
# #         max_losses = max(max_losses, cur_losses)
# #     return {"max_consecutive_wins": max_wins, "max_consecutive_losses": max_losses}


# # def median(values: list) -> float:
# #     if not values:
# #         return 0.0
# #     sv = sorted(float(v) for v in values)
# #     return round(sv[len(sv) // 2], 2)


# # def median_win_rr(trades):  return median([t["rr"] for t in trades if t["outcome"] == "win"])
# # def median_loss_rr(trades): return median([t["rr"] for t in trades if t["outcome"] == "loss"])


# # def wilson_confidence_interval(wins: int, n: int, z: float = 1.96) -> tuple:
# #     if n == 0:
# #         return 0.0, 0.0
# #     p      = wins / n
# #     denom  = 1 + z**2 / n
# #     center = (p + z**2 / (2 * n)) / denom
# #     margin = z * math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denom
# #     return round(max(0.0, center - margin) * 100, 1), round(min(1.0, center + margin) * 100, 1)


# # def current_loss_streak(trades: List[Dict]) -> int:
# #     count = 0
# #     for t in reversed(trades):
# #         if t["outcome"] == "loss": count += 1
# #         else: break
# #     return count


# # def session_breakdown(trades: List[Dict]) -> Dict[str, Any]:
# #     result = {}
# #     for session in ["asian", "london", "new_york", "overlap"]:
# #         st = [t for t in trades if t.get("session", "").lower() == session]
# #         result[session] = {
# #             "trades": len(st),
# #             "win_rate": win_rate(st),
# #             "total_r": round(sum(t["pnl_r"] for t in st), 3),
# #             "expectancy": expectancy(st),
# #         } if st else {"trades": 0, "win_rate": 0.0, "total_r": 0.0, "expectancy": 0.0}
# #     return result


# # def mood_breakdown(trades: List[Dict]) -> Dict[str, Any]:
# #     moods = {}
# #     for t in trades:
# #         mood = t.get("mood", "").strip().lower()
# #         if mood:
# #             moods.setdefault(mood, []).append(t)
# #     return {
# #         mood: {"trades": len(mt), "win_rate": win_rate(mt), "total_r": round(sum(t["pnl_r"] for t in mt), 3)}
# #         for mood, mt in moods.items()
# #     }


# # def positions_breakdown(trades: List[Dict]) -> Dict[str, Any]:
# #     """Average positions per trade, and win rate grouped by position count."""
# #     pos_vals = [t.get("positions", 1) for t in trades if t.get("positions")]
# #     avg_pos  = round(sum(pos_vals) / len(pos_vals), 2) if pos_vals else 0.0
# #     groups   = {}
# #     for t in trades:
# #         p = str(t.get("positions", 1))
# #         groups.setdefault(p, []).append(t)
# #     return {
# #         "avg_positions": avg_pos,
# #         "by_positions": {
# #             p: {"trades": len(gt), "win_rate": win_rate(gt), "total_r": round(sum(t["pnl_r"] for t in gt), 3)}
# #             for p, gt in sorted(groups.items(), key=lambda x: int(x[0]))
# #         }
# #     }


# # def analyze(trades: List[Dict]) -> Dict[str, Any]:
# #     if not trades:
# #         return {"overall": {}, "batches": [], "equity_curve": [],
# #                 "session_breakdown": {}, "mood_breakdown": {}, "positions_breakdown": {}}

# #     trades = sorted(trades, key=lambda t: t.get("date", ""))
# #     wins   = sum(1 for t in trades if t["outcome"] == "win")
# #     ci_lo, ci_hi = wilson_confidence_interval(wins, len(trades))

# #     overall = {
# #         "total_trades":        len(trades),
# #         "win_rate":            win_rate(trades),
# #         "profit_factor":       profit_factor(trades),
# #         "expectancy":          expectancy(trades),
# #         "avg_rr":              avg_rr(trades),
# #         "max_drawdown":        max_drawdown(trades),
# #         "streaks":             consecutive_stats(trades),
# #         "total_r":             round(sum(t["pnl_r"] for t in trades), 3),
# #         "median_win_rr":       median_win_rr(trades),
# #         "median_loss_rr":      median_loss_rr(trades),
# #         "win_rate_ci":         f"{ci_lo}–{ci_hi}%",
# #         "current_loss_streak": current_loss_streak(trades),
# #     }

# #     batches = []
# #     for i, batch in enumerate(_batches(trades)):
# #         w = sum(1 for t in batch if t["outcome"] == "win")
# #         lo, hi = wilson_confidence_interval(w, len(batch))
# #         batches.append({
# #             "batch_number":   i + 1,
# #             "trade_range":    f"{i*20+1}–{i*20+len(batch)}",
# #             "total_trades":   len(batch),
# #             "win_rate":       win_rate(batch),
# #             "profit_factor":  profit_factor(batch),
# #             "expectancy":     expectancy(batch),
# #             "avg_rr":         avg_rr(batch),
# #             "max_drawdown":   max_drawdown(batch),
# #             "total_r":        round(sum(t["pnl_r"] for t in batch), 3),
# #             "median_win_rr":  median_win_rr(batch),
# #             "median_loss_rr": median_loss_rr(batch),
# #             "win_rate_ci":    f"{lo}–{hi}%",
# #         })

# #     return {
# #         "overall":              overall,
# #         "batches":              batches,
# #         "equity_curve":         equity_curve(trades),
# #         "session_breakdown":    session_breakdown(trades),
# #         "mood_breakdown":       mood_breakdown(trades),
# #         "positions_breakdown":  positions_breakdown(trades),
# #     }


# """
# analyzer.py — Core statistics engine for the strategy tester.
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
#     equity = peak = max_dd = 0.0
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
#             cur_wins += 1; cur_losses = 0
#         else:
#             cur_losses += 1; cur_wins = 0
#         max_wins   = max(max_wins,   cur_wins)
#         max_losses = max(max_losses, cur_losses)
#     return {"max_consecutive_wins": max_wins, "max_consecutive_losses": max_losses}


# def median(values: list) -> float:
#     if not values:
#         return 0.0
#     sv = sorted(float(v) for v in values)
#     return round(sv[len(sv) // 2], 2)


# def median_win_rr(trades):  return median([t["rr"] for t in trades if t["outcome"] == "win"])
# def median_loss_rr(trades): return median([t["rr"] for t in trades if t["outcome"] == "loss"])


# def wilson_confidence_interval(wins: int, n: int, z: float = 1.96) -> tuple:
#     if n == 0:
#         return 0.0, 0.0
#     p      = wins / n
#     denom  = 1 + z**2 / n
#     center = (p + z**2 / (2 * n)) / denom
#     margin = z * math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denom
#     return round(max(0.0, center - margin) * 100, 1), round(min(1.0, center + margin) * 100, 1)


# def current_loss_streak(trades: List[Dict]) -> int:
#     count = 0
#     for t in reversed(trades):
#         if t["outcome"] == "loss": count += 1
#         else: break
#     return count


# def session_breakdown(trades: List[Dict]) -> Dict[str, Any]:
#     result = {}
#     for session in ["asian", "london", "new_york", "overlap"]:
#         st = [t for t in trades if t.get("session", "").lower() == session]
#         total_profit = round(sum(t.get("raw_profit", 0) for t in st), 2)
#         result[session] = {
#             "trades":       len(st),
#             "win_rate":     win_rate(st),
#             "total_r":      round(sum(t["pnl_r"] for t in st), 3),
#             "expectancy":   expectancy(st),
#             "total_profit": total_profit,
#         } if st else {"trades": 0, "win_rate": 0.0, "total_r": 0.0, "expectancy": 0.0, "total_profit": 0.0}
#     return result


# def mood_breakdown(trades: List[Dict]) -> Dict[str, Any]:
#     moods = {}
#     for t in trades:
#         mood = t.get("mood", "").strip().lower()
#         if mood:
#             moods.setdefault(mood, []).append(t)
#     return {
#         mood: {"trades": len(mt), "win_rate": win_rate(mt), "total_r": round(sum(t["pnl_r"] for t in mt), 3)}
#         for mood, mt in moods.items()
#     }


# def positions_breakdown(trades: List[Dict]) -> Dict[str, Any]:
#     pos_vals = [t.get("positions", 1) for t in trades if t.get("positions")]
#     avg_pos  = round(sum(pos_vals) / len(pos_vals), 2) if pos_vals else 0.0
#     groups   = {}
#     for t in trades:
#         p = str(t.get("positions", 1))
#         groups.setdefault(p, []).append(t)
#     return {
#         "avg_positions": avg_pos,
#         "by_positions": {
#             p: {"trades": len(gt), "win_rate": win_rate(gt), "total_r": round(sum(t["pnl_r"] for t in gt), 3)}
#             for p, gt in sorted(groups.items(), key=lambda x: int(x[0]))
#         }
#     }


# # ── NEW: enhanced analytics ───────────────────────────────────────────────────

# def winners_losers(trades: List[Dict]) -> Dict[str, Any]:
#     """Detailed breakdown of winning and losing trades."""
#     wins   = [t for t in trades if t["outcome"] == "win"]
#     losses = [t for t in trades if t["outcome"] == "loss"]

#     best_win_r   = max((t["pnl_r"] for t in wins),   default=0.0)
#     worst_loss_r = min((t["pnl_r"] for t in losses), default=0.0)
#     avg_win_r    = round(sum(t["pnl_r"] for t in wins)   / len(wins),   3) if wins   else 0.0
#     avg_loss_r   = round(sum(t["pnl_r"] for t in losses) / len(losses), 3) if losses else 0.0

#     best_win_profit   = max((t.get("raw_profit", 0) for t in wins),   default=0.0)
#     worst_loss_profit = min((t.get("raw_profit", 0) for t in losses), default=0.0)
#     avg_win_profit    = round(sum(t.get("raw_profit", 0) for t in wins)   / len(wins),   2) if wins   else 0.0
#     avg_loss_profit   = round(sum(t.get("raw_profit", 0) for t in losses) / len(losses), 2) if losses else 0.0

#     streaks = consecutive_stats(trades)

#     return {
#         "winners": {
#             "count":          len(wins),
#             "best_r":         round(best_win_r, 3),
#             "avg_r":          avg_win_r,
#             "best_profit":    round(best_win_profit, 2),
#             "avg_profit":     avg_win_profit,
#             "max_streak":     streaks["max_consecutive_wins"],
#         },
#         "losers": {
#             "count":          len(losses),
#             "worst_r":        round(worst_loss_r, 3),
#             "avg_r":          avg_loss_r,
#             "worst_profit":   round(worst_loss_profit, 2),
#             "avg_profit":     avg_loss_profit,
#             "max_streak":     streaks["max_consecutive_losses"],
#         },
#     }


# def side_breakdown(trades: List[Dict]) -> Dict[str, Any]:
#     """Performance split by trade direction (long/short = buy/sell)."""
#     longs  = [t for t in trades if t.get("direction") == "long"]
#     shorts = [t for t in trades if t.get("direction") == "short"]

#     def side_stats(side_trades):
#         if not side_trades:
#             return {"trades": 0, "win_rate": 0.0, "total_r": 0.0, "total_profit": 0.0}
#         return {
#             "trades":       len(side_trades),
#             "win_rate":     win_rate(side_trades),
#             "total_r":      round(sum(t["pnl_r"] for t in side_trades), 3),
#             "total_profit": round(sum(t.get("raw_profit", 0) for t in side_trades), 2),
#         }

#     return {
#         "long":  side_stats(longs),
#         "short": side_stats(shorts),
#     }


# def expectancy_bar(trades: List[Dict]) -> Dict[str, Any]:
#     """Data for the expectancy vs profit factor visual bar."""
#     wins   = [t for t in trades if t["outcome"] == "win"]
#     losses = [t for t in trades if t["outcome"] == "loss"]

#     avg_win_r    = round(sum(t["pnl_r"] for t in wins)   / len(wins),   3) if wins   else 0.0
#     avg_loss_r   = round(sum(t["pnl_r"] for t in losses) / len(losses), 3) if losses else 0.0
#     avg_win_usd  = round(sum(t.get("raw_profit", 0) for t in wins)   / len(wins),   2) if wins   else 0.0
#     avg_loss_usd = round(sum(t.get("raw_profit", 0) for t in losses) / len(losses), 2) if losses else 0.0

#     exp_r   = expectancy(trades)
#     exp_usd = round(sum(t.get("raw_profit", 0) for t in trades) / len(trades), 2) if trades else 0.0
#     pf      = profit_factor(trades)

#     # Bar widths as percentages (relative to each other)
#     total = abs(avg_win_r) + abs(avg_loss_r)
#     win_pct  = round(abs(avg_win_r)  / total * 100, 1) if total else 50.0
#     loss_pct = round(abs(avg_loss_r) / total * 100, 1) if total else 50.0

#     return {
#         "expectancy_r":   exp_r,
#         "expectancy_usd": exp_usd,
#         "profit_factor":  pf,
#         "avg_win_r":      avg_win_r,
#         "avg_loss_r":     avg_loss_r,
#         "avg_win_usd":    avg_win_usd,
#         "avg_loss_usd":   avg_loss_usd,
#         "win_bar_pct":    win_pct,
#         "loss_bar_pct":   loss_pct,
#     }


# def analyze(trades: List[Dict]) -> Dict[str, Any]:
#     if not trades:
#         return {
#             "overall": {}, "batches": [], "equity_curve": [],
#             "session_breakdown": {}, "mood_breakdown": {},
#             "positions_breakdown": {}, "winners_losers": {},
#             "side_breakdown": {}, "expectancy_bar": {},
#         }

#     trades = sorted(trades, key=lambda t: t.get("date", ""))
#     wins   = sum(1 for t in trades if t["outcome"] == "win")
#     ci_lo, ci_hi = wilson_confidence_interval(wins, len(trades))

#     overall = {
#         "total_trades":        len(trades),
#         "win_rate":            win_rate(trades),
#         "profit_factor":       profit_factor(trades),
#         "expectancy":          expectancy(trades),
#         "avg_rr":              avg_rr(trades),
#         "max_drawdown":        max_drawdown(trades),
#         "streaks":             consecutive_stats(trades),
#         "total_r":             round(sum(t["pnl_r"] for t in trades), 3),
#         "total_profit":        round(sum(t.get("raw_profit", 0) for t in trades), 2),
#         "median_win_rr":       median_win_rr(trades),
#         "median_loss_rr":      median_loss_rr(trades),
#         "win_rate_ci":         f"{ci_lo}–{ci_hi}%",
#         "current_loss_streak": current_loss_streak(trades),
#     }

#     batches = []
#     for i, batch in enumerate(_batches(trades)):
#         w = sum(1 for t in batch if t["outcome"] == "win")
#         lo, hi = wilson_confidence_interval(w, len(batch))
#         batches.append({
#             "batch_number":   i + 1,
#             "trade_range":    f"{i*20+1}–{i*20+len(batch)}",
#             "total_trades":   len(batch),
#             "win_rate":       win_rate(batch),
#             "profit_factor":  profit_factor(batch),
#             "expectancy":     expectancy(batch),
#             "avg_rr":         avg_rr(batch),
#             "max_drawdown":   max_drawdown(batch),
#             "total_r":        round(sum(t["pnl_r"] for t in batch), 3),
#             "median_win_rr":  median_win_rr(batch),
#             "median_loss_rr": median_loss_rr(batch),
#             "win_rate_ci":    f"{lo}–{hi}%",
#         })

#     return {
#         "overall":             overall,
#         "batches":             batches,
#         "equity_curve":        equity_curve(trades),
#         "session_breakdown":   session_breakdown(trades),
#         "mood_breakdown":      mood_breakdown(trades),
#         "positions_breakdown": positions_breakdown(trades),
#         "winners_losers":      winners_losers(trades),
#         "side_breakdown":      side_breakdown(trades),
#         "expectancy_bar":      expectancy_bar(trades),
#     }

"""
analyzer.py — Core statistics engine for the strategy tester.
"""

from typing import List, Dict, Any
import math


def _batches(trades: List[Dict], size: int = 20) -> List[List[Dict]]:
    return [trades[i : i + size] for i in range(0, len(trades), size)]


def win_rate(trades: List[Dict]) -> float:
    if not trades: return 0.0
    return round(sum(1 for t in trades if t["outcome"] == "win") / len(trades) * 100, 2)


def profit_factor(trades: List[Dict]) -> float:
    gp = sum(t["pnl_r"] for t in trades if t["pnl_r"] > 0)
    gl = abs(sum(t["pnl_r"] for t in trades if t["pnl_r"] < 0))
    if gl == 0: return round(gp, 2) if gp else 0.0
    return round(gp / gl, 2)


def expectancy(trades: List[Dict]) -> float:
    if not trades: return 0.0
    return round(sum(t["pnl_r"] for t in trades) / len(trades), 3)


def avg_rr(trades: List[Dict]) -> float:
    winning = [t["rr"] for t in trades if t["outcome"] == "win" and t["rr"]]
    if not winning: return 0.0
    return round(sum(winning) / len(winning), 2)


def max_drawdown(trades: List[Dict]) -> Dict[str, Any]:
    if not trades: return {"r": 0.0, "pct": 0.0}
    equity = peak = max_dd = 0.0
    for t in trades:
        equity += t["pnl_r"]
        if equity > peak: peak = equity
        dd = peak - equity
        if dd > max_dd: max_dd = dd
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
    if not values: return 0.0
    sv = sorted(float(v) for v in values)
    return round(sv[len(sv) // 2], 2)


def median_win_rr(trades):  return median([t["rr"] for t in trades if t["outcome"] == "win"])
def median_loss_rr(trades): return median([t["rr"] for t in trades if t["outcome"] == "loss"])


def wilson_confidence_interval(wins: int, n: int, z: float = 1.96) -> tuple:
    if n == 0: return 0.0, 0.0
    p = wins / n
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
        profit_vals = [t.get("raw_profit", 0) for t in st if t.get("raw_profit") is not None]
        result[session] = {
            "trades": len(st), "win_rate": win_rate(st),
            "total_r": round(sum(t["pnl_r"] for t in st), 3),
            "expectancy": expectancy(st),
            "total_profit": round(sum(profit_vals), 2),
            "avg_rr": avg_rr(st),
        } if st else {"trades": 0, "win_rate": 0.0, "total_r": 0.0, "expectancy": 0.0, "total_profit": 0.0, "avg_rr": 0.0}
    return result


def mood_breakdown(trades: List[Dict]) -> Dict[str, Any]:
    moods = {}
    for t in trades:
        mood = t.get("mood", "").strip().lower()
        if mood: moods.setdefault(mood, []).append(t)
    return {
        mood: {"trades": len(mt), "win_rate": win_rate(mt), "total_r": round(sum(t["pnl_r"] for t in mt), 3)}
        for mood, mt in moods.items()
    }


def winners_losers_breakdown(trades: List[Dict]) -> Dict[str, Any]:
    wins   = [t for t in trades if t["outcome"] == "win"]
    losses = [t for t in trades if t["outcome"] == "loss"]
    win_rs   = [t["pnl_r"] for t in wins]
    loss_rs  = [abs(t["pnl_r"]) for t in losses]
    win_pnls  = [t.get("raw_profit", 0) for t in wins  if t.get("raw_profit") is not None]
    loss_pnls = [abs(t.get("raw_profit", 0)) for t in losses if t.get("raw_profit") is not None]
    return {
        "winners": {
            "count": len(wins),
            "best_r": round(max(win_rs), 3) if win_rs else 0.0,
            "avg_r":  round(sum(win_rs) / len(win_rs), 3) if win_rs else 0.0,
            "best_profit": round(max(win_pnls), 2) if win_pnls else None,
            "avg_profit":  round(sum(win_pnls) / len(win_pnls), 2) if win_pnls else None,
            "max_streak": consecutive_stats(trades)["max_consecutive_wins"],
        },
        "losers": {
            "count": len(losses),
            "worst_r": round(max(loss_rs), 3) if loss_rs else 0.0,
            "avg_r":   round(sum(loss_rs) / len(loss_rs), 3) if loss_rs else 0.0,
            "worst_profit": round(max(loss_pnls), 2) if loss_pnls else None,
            "avg_profit":   round(sum(loss_pnls) / len(loss_pnls), 2) if loss_pnls else None,
            "max_streak": consecutive_stats(trades)["max_consecutive_losses"],
        }
    }


def side_breakdown(trades: List[Dict]) -> Dict[str, Any]:
    def _stats(st):
        pv = [t.get("raw_profit", 0) for t in st if t.get("raw_profit") is not None]
        return {"trades": len(st), "win_rate": win_rate(st),
                "total_r": round(sum(t["pnl_r"] for t in st), 3),
                "expectancy": expectancy(st), "total_profit": round(sum(pv), 2), "avg_rr": avg_rr(st)}
    return {
        "long":  _stats([t for t in trades if t.get("direction") == "long"]),
        "short": _stats([t for t in trades if t.get("direction") == "short"]),
    }


def expectancy_bar(trades: List[Dict]) -> Dict[str, Any]:
    wins   = [t for t in trades if t["outcome"] == "win"]
    losses = [t for t in trades if t["outcome"] == "loss"]
    avg_win_r  = round(sum(t["pnl_r"] for t in wins)   / len(wins),   3) if wins   else 0.0
    avg_loss_r = round(sum(t["pnl_r"] for t in losses) / len(losses), 3) if losses else 0.0
    wp = [t.get("raw_profit", 0) for t in wins   if t.get("raw_profit") is not None]
    lp = [t.get("raw_profit", 0) for t in losses if t.get("raw_profit") is not None]
    wr = win_rate(trades) / 100
    return {
        "avg_win_r": avg_win_r, "avg_loss_r": avg_loss_r,
        "avg_win_profit":  round(sum(wp) / len(wp), 2) if wp else None,
        "avg_loss_profit": round(sum(lp) / len(lp), 2) if lp else None,
        "expectancy_r": round(wr * avg_win_r + (1 - wr) * avg_loss_r, 3),
        "win_rate": win_rate(trades),
    }


# ── NEW: pair performance ─────────────────────────────────────────────────────

def pair_performance(trades: List[Dict]) -> List[Dict]:
    pairs = {}
    for t in trades:
        p = t.get("pair", "OTHER")
        pairs.setdefault(p, []).append(t)
    result = []
    for pair, pt in sorted(pairs.items(), key=lambda x: -len(x[1])):
        pv = [t.get("raw_profit", 0) for t in pt if t.get("raw_profit") is not None]
        result.append({
            "pair":          pair,
            "trades":        len(pt),
            "win_rate":      win_rate(pt),
            "total_r":       round(sum(t["pnl_r"] for t in pt), 3),
            "avg_rr":        avg_rr(pt),
            "expectancy":    expectancy(pt),
            "profit_factor": profit_factor(pt),
            "total_profit":  round(sum(pv), 2) if pv else None,
        })
    return result


# ── NEW: time of day breakdown ────────────────────────────────────────────────

def time_of_day_breakdown(trades: List[Dict]) -> Dict[str, Any]:
    """Group trades by hour (0-23) and return win rate + total R per hour."""
    hours = {}
    for t in trades:
        time_str = t.get("time", "")
        if not time_str: continue
        try:
            hour = int(time_str.split(":")[0])
            hours.setdefault(hour, []).append(t)
        except (ValueError, IndexError):
            continue
    result = {}
    for hour, ht in hours.items():
        result[str(hour)] = {
            "hour":    hour,
            "trades":  len(ht),
            "win_rate": win_rate(ht),
            "total_r": round(sum(t["pnl_r"] for t in ht), 3),
            "expectancy": expectancy(ht),
        }
    return result


# ── NEW: day of week breakdown ────────────────────────────────────────────────

def day_of_week_breakdown(trades: List[Dict]) -> Dict[str, Any]:
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    groups = {d: [] for d in days}
    import datetime
    for t in trades:
        try:
            dt = datetime.date.fromisoformat(t.get("date", ""))
            day_name = days[dt.weekday()]
            groups[day_name].append(t)
        except (ValueError, TypeError):
            continue
    return {
        day: {
            "trades":    len(dt),
            "win_rate":  win_rate(dt),
            "total_r":   round(sum(t["pnl_r"] for t in dt), 3),
            "expectancy": expectancy(dt),
        }
        for day, dt in groups.items() if dt
    }


# ── full analysis ─────────────────────────────────────────────────────────────

def analyze(trades: List[Dict]) -> Dict[str, Any]:
    if not trades:
        return {
            "overall": {}, "batches": [], "equity_curve": [],
            "session_breakdown": {}, "mood_breakdown": {},
            "winners_losers": {}, "side_breakdown": {}, "expectancy_bar": {},
            "pair_performance": [], "time_of_day": {}, "day_of_week": {},
        }

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
        "total_profit":        round(sum(t.get("raw_profit", 0) for t in trades if t.get("raw_profit") is not None), 2),
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
        "overall":           overall,
        "batches":           batches,
        "equity_curve":      equity_curve(trades),
        "session_breakdown": session_breakdown(trades),
        "mood_breakdown":    mood_breakdown(trades),
        "winners_losers":    winners_losers_breakdown(trades),
        "side_breakdown":    side_breakdown(trades),
        "expectancy_bar":    expectancy_bar(trades),
        "pair_performance":  pair_performance(trades),
        "time_of_day":       time_of_day_breakdown(trades),
        "day_of_week":       day_of_week_breakdown(trades),
    }
    