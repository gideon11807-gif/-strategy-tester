# # # # # from flask import Flask, jsonify, request, abort
# # # # # from flask_cors import CORS
# # # # # import json, os, uuid
# # # # # from datetime import datetime
# # # # # from analyzer import analyze

# # # # # app = Flask(__name__)
# # # # # CORS(app)

# # # # # DATA_FILE = os.path.join(os.path.dirname(__file__), "trades.json")

# # # # # # ── persistence helpers ──────────────────────────────────────────────────────
# # # # # def _load() -> list:
# # # # #     if not os.path.exists(DATA_FILE):
# # # # #         return []
# # # # #     with open(DATA_FILE, "r") as f:
# # # # #         return json.load(f)

# # # # # def _save(trades: list):
# # # # #     with open(DATA_FILE, "w") as f:
# # # # #         json.dump(trades, f, indent=2)

# # # # # def _pnl(outcome: str, rr: float) -> float:
# # # # #     if outcome == "win":
# # # # #         return round(rr, 3)
# # # # #     elif outcome == "loss":
# # # # #         return -1.0
# # # # #     else:  # breakeven
# # # # #         return 0.0

# # # # # # ── validation ───────────────────────────────────────────────────────────────
# # # # # VALID_OUTCOMES = {"win", "loss", "breakeven"}
# # # # # VALID_DIRECTIONS = {"long", "short"}
# # # # # VALID_PAIRS = {
# # # # #     "EURUSD", "GBPUSD", "USDJPY", "USDCHF",
# # # # #     "XAUUSD", "XAGUSD", "AUDUSD", "NZDUSD",
# # # # #     "USDCAD", "GBPJPY", "US30", "NAS100", "OTHER",
# # # # # }

# # # # # def _validate_trade(data: dict) -> dict:
# # # # #     errors = []
# # # # #     pair = str(data.get("pair", "")).upper().strip()
# # # # #     direction = str(data.get("direction", "")).lower().strip()
# # # # #     outcome = str(data.get("outcome", "")).lower().strip()
# # # # #     rr_raw = data.get("rr")
# # # # #     date = data.get("date", datetime.today().strftime("%Y-%m-%d"))
# # # # #     notes = str(data.get("notes", "")).strip()[:300]

# # # # #     if pair not in VALID_PAIRS:
# # # # #         errors.append(f"pair must be one of {sorted(VALID_PAIRS)}")
# # # # #     if direction not in VALID_DIRECTIONS:
# # # # #         errors.append("direction must be 'long' or 'short'")
# # # # #     if outcome not in VALID_OUTCOMES:
# # # # #         errors.append("outcome must be 'win', 'loss', or 'breakeven'")
# # # # #     try:
# # # # #         rr = float(rr_raw)
# # # # #         if rr <= 0 or rr > 100:
# # # # #             errors.append("rr must be a positive number ≤ 100")
# # # # #     except (TypeError, ValueError):
# # # # #         rr = 1.0
# # # # #         errors.append("rr must be a valid number")

# # # # #     if errors:
# # # # #         abort(400, description="; ".join(errors))

# # # # #     return {
# # # # #         "id": str(uuid.uuid4())[:8],
# # # # #         "pair": pair,
# # # # #         "direction": direction,
# # # # #         "outcome": outcome,
# # # # #         "rr": round(float(rr_raw), 2),
# # # # #         "pnl_r": _pnl(outcome, float(rr_raw)),
# # # # #         "date": date,
# # # # #         "notes": notes,
# # # # #     }

# # # # # # ── routes ───────────────────────────────────────────────────────────────────
# # # # # @app.route("/api/trades", methods=["GET"])
# # # # # def get_trades():
# # # # #     return jsonify(_load())

# # # # # @app.route("/api/trades", methods=["POST"])
# # # # # def add_trade():
# # # # #     trade = _validate_trade(request.get_json(force=True) or {})
# # # # #     trades = _load()
# # # # #     trades.append(trade)
# # # # #     _save(trades)
# # # # #     return jsonify(trade), 201

# # # # # @app.route("/api/trades/<trade_id>", methods=["DELETE"])
# # # # # def delete_trade(trade_id):
# # # # #     trades = _load()
# # # # #     new = [t for t in trades if t["id"] != trade_id]
# # # # #     if len(new) == len(trades):
# # # # #         abort(404, description="Trade not found")
# # # # #     _save(new)
# # # # #     return jsonify({"deleted": trade_id})

# # # # # @app.route("/api/trades", methods=["DELETE"])
# # # # # def clear_trades():
# # # # #     _save([])
# # # # #     return jsonify({"message": "All trades cleared"})

# # # # # @app.route("/api/trades/bulk", methods=["POST"])
# # # # # def bulk_import():
# # # # #     items = request.get_json(force=True) or []
# # # # #     if not isinstance(items, list):
# # # # #         abort(400, description="Expected a JSON array of trades")
# # # # #     trades = _load()
# # # # #     imported = []
# # # # #     for item in items:
# # # # #         t = _validate_trade(item)
# # # # #         trades.append(t)
# # # # #         imported.append(t)
# # # # #     _save(trades)
# # # # #     return jsonify({"imported": len(imported), "trades": imported}), 201

# # # # # @app.route("/api/analyze", methods=["GET"])
# # # # # def analyze_trades():
# # # # #     trades = _load()
# # # # #     return jsonify(analyze(trades))

# # # # # # ── error handlers ───────────────────────────────────────────────────────────
# # # # # @app.errorhandler(400)
# # # # # def bad_request(e):
# # # # #     return jsonify({"error": str(e.description)}), 400

# # # # # @app.errorhandler(404)
# # # # # def not_found(e):
# # # # #     return jsonify({"error": str(e.description)}), 404

# # # # # if __name__ == "__main__":
# # # # #     app.run(debug=True, port=5000)

# # # # """
# # # # app.py — Flask REST API for the Strategy Tester.

# # # # Endpoints:
# # # #   GET    /api/trades          → list all trades
# # # #   POST   /api/trades          → add a trade
# # # #   DELETE /api/trades/<id>     → remove a trade
# # # #   GET    /api/analyze         → full analysis (overall + batches)
# # # #   POST   /api/trades/bulk     → import list of trades at once
# # # #   DELETE /api/trades          → clear all trades
# # # # """

# # # # from flask import Flask, jsonify, request, abort
# # # # from flask_cors import CORS
# # # # import json, os, uuid
# # # # from datetime import datetime
# # # # from analyzer import analyze

# # # # app = Flask(__name__)

# # # # # ── CORS fix: allow all origins on every /api/ route ────────────────────────
# # # # CORS(app, resources={r"/api/*": {"origins": "*"}})

# # # # DATA_FILE = os.path.join(os.path.dirname(__file__), "trades.json")


# # # # # ── persistence helpers ──────────────────────────────────────────────────────

# # # # def _load() -> list:
# # # #     if not os.path.exists(DATA_FILE):
# # # #         return []
# # # #     with open(DATA_FILE, "r") as f:
# # # #         return json.load(f)


# # # # def _save(trades: list):
# # # #     with open(DATA_FILE, "w") as f:
# # # #         json.dump(trades, f, indent=2)


# # # # def _pnl(outcome: str, rr: float) -> float:
# # # #     """Convert outcome + R:R into a signed P&L in R units."""
# # # #     if outcome == "win":
# # # #         return round(rr, 3)
# # # #     elif outcome == "loss":
# # # #         return -1.0
# # # #     else:   # breakeven
# # # #         return 0.0


# # # # # ── validation ───────────────────────────────────────────────────────────────

# # # # VALID_OUTCOMES   = {"win", "loss", "breakeven"}
# # # # VALID_DIRECTIONS = {"long", "short"}
# # # # VALID_PAIRS = {
# # # #     "EURUSD", "GBPUSD", "USDJPY", "USDCHF",
# # # #     "XAUUSD", "XAGUSD", "AUDUSD", "NZDUSD",
# # # #     "USDCAD", "GBPJPY", "US30", "NAS100", "OTHER",
# # # # }


# # # # def _validate_trade(data: dict) -> dict:
# # # #     errors = []
# # # #     pair      = str(data.get("pair", "")).upper().strip()
# # # #     direction = str(data.get("direction", "")).lower().strip()
# # # #     outcome   = str(data.get("outcome", "")).lower().strip()
# # # #     rr_raw    = data.get("rr")
# # # #     date      = data.get("date", datetime.today().strftime("%Y-%m-%d"))
# # # #     notes     = str(data.get("notes", "")).strip()[:300]

# # # #     if pair not in VALID_PAIRS:
# # # #         errors.append(f"pair must be one of {sorted(VALID_PAIRS)}")
# # # #     if direction not in VALID_DIRECTIONS:
# # # #         errors.append("direction must be 'long' or 'short'")
# # # #     if outcome not in VALID_OUTCOMES:
# # # #         errors.append("outcome must be 'win', 'loss', or 'breakeven'")
# # # #     try:
# # # #         rr = float(rr_raw)
# # # #         if rr <= 0 or rr > 100:
# # # #             errors.append("rr must be a positive number ≤ 100")
# # # #     except (TypeError, ValueError):
# # # #         rr = 1.0
# # # #         errors.append("rr must be a valid number")

# # # #     if errors:
# # # #         abort(400, description="; ".join(errors))

# # # #     return {
# # # #         "id":        str(uuid.uuid4())[:8],
# # # #         "pair":      pair,
# # # #         "direction": direction,
# # # #         "outcome":   outcome,
# # # #         "rr":        round(float(rr_raw), 2),
# # # #         "pnl_r":     _pnl(outcome, float(rr_raw)),
# # # #         "date":      date,
# # # #         "notes":     notes,
# # # #     }


# # # # # ── routes ───────────────────────────────────────────────────────────────────

# # # # @app.route("/api/trades", methods=["GET"])
# # # # def get_trades():
# # # #     return jsonify(_load())


# # # # @app.route("/api/trades", methods=["POST"])
# # # # def add_trade():
# # # #     trade = _validate_trade(request.get_json(force=True) or {})
# # # #     trades = _load()
# # # #     trades.append(trade)
# # # #     _save(trades)
# # # #     return jsonify(trade), 201


# # # # @app.route("/api/trades/<trade_id>", methods=["DELETE"])
# # # # def delete_trade(trade_id):
# # # #     trades = _load()
# # # #     new = [t for t in trades if t["id"] != trade_id]
# # # #     if len(new) == len(trades):
# # # #         abort(404, description="Trade not found")
# # # #     _save(new)
# # # #     return jsonify({"deleted": trade_id})


# # # # @app.route("/api/trades", methods=["DELETE"])
# # # # def clear_trades():
# # # #     _save([])
# # # #     return jsonify({"message": "All trades cleared"})


# # # # @app.route("/api/trades/bulk", methods=["POST"])
# # # # def bulk_import():
# # # #     items = request.get_json(force=True) or []
# # # #     if not isinstance(items, list):
# # # #         abort(400, description="Expected a JSON array of trades")
# # # #     trades = _load()
# # # #     imported = []
# # # #     for item in items:
# # # #         t = _validate_trade(item)
# # # #         trades.append(t)
# # # #         imported.append(t)
# # # #     _save(trades)
# # # #     return jsonify({"imported": len(imported), "trades": imported}), 201


# # # # @app.route("/api/analyze", methods=["GET"])
# # # # def analyze_trades():
# # # #     trades = _load()
# # # #     return jsonify(analyze(trades))


# # # # # ── error handlers ───────────────────────────────────────────────────────────

# # # # @app.errorhandler(400)
# # # # def bad_request(e):
# # # #     return jsonify({"error": str(e.description)}), 400


# # # # @app.errorhandler(404)
# # # # def not_found(e):
# # # #     return jsonify({"error": str(e.description)}), 404


# # # # if __name__ == "__main__":
# # # #     app.run(debug=True, port=5000)

# # # """
# # # app.py — Flask REST API for the Strategy Tester.

# # # Endpoints:
# # #   GET    /api/trades          → list all trades
# # #   POST   /api/trades          → add a trade
# # #   DELETE /api/trades/<id>     → remove a trade
# # #   GET    /api/analyze         → full analysis (overall + batches)
# # #   POST   /api/trades/bulk     → import list of trades at once
# # #   DELETE /api/trades          → clear all trades
# # # """

# # # from flask import Flask, jsonify, request, abort
# # # from flask_cors import CORS
# # # import json, os, uuid
# # # from datetime import datetime
# # # from analyzer import analyze

# # # app = Flask(__name__)

# # # # ── CORS fix ─────────────────────────────────────────────────────────────────
# # # CORS(app, resources={r"/api/*": {"origins": "*"}})

# # # DATA_FILE = os.path.join(os.path.dirname(__file__), "trades.json")


# # # # ── persistence helpers ──────────────────────────────────────────────────────

# # # def _load() -> list:
# # #     if not os.path.exists(DATA_FILE):
# # #         with open(DATA_FILE, "w") as f:
# # #             json.dump([], f)
# # #         return []
# # #     with open(DATA_FILE, "r") as f:
# # #         content = f.read().strip()
# # #         if not content:
# # #             with open(DATA_FILE, "w") as fw:
# # #                 json.dump([], fw)
# # #             return []
# # #         return json.loads(content)


# # # def _save(trades: list):
# # #     with open(DATA_FILE, "w") as f:
# # #         json.dump(trades, f, indent=2)


# # # def _pnl(outcome: str, rr: float) -> float:
# # #     """Convert outcome + R:R into a signed P&L in R units."""
# # #     if outcome == "win":
# # #         return round(rr, 3)
# # #     elif outcome == "loss":
# # #         return -1.0
# # #     else:   # breakeven
# # #         return 0.0


# # # # ── validation ───────────────────────────────────────────────────────────────

# # # VALID_OUTCOMES   = {"win", "loss", "breakeven"}
# # # VALID_DIRECTIONS = {"long", "short"}
# # # VALID_PAIRS = {
# # #     "EURUSD", "GBPUSD", "USDJPY", "USDCHF",
# # #     "XAUUSD", "XAGUSD", "AUDUSD", "NZDUSD",
# # #     "USDCAD", "GBPJPY", "US30", "NAS100", "OTHER",
# # # }


# # # def _validate_trade(data: dict) -> dict:
# # #     errors = []
# # #     pair      = str(data.get("pair", "")).upper().strip()
# # #     direction = str(data.get("direction", "")).lower().strip()
# # #     outcome   = str(data.get("outcome", "")).lower().strip()
# # #     rr_raw    = data.get("rr")
# # #     date      = data.get("date", datetime.today().strftime("%Y-%m-%d"))
# # #     notes     = str(data.get("notes", "")).strip()[:300]

# # #     if pair not in VALID_PAIRS:
# # #         errors.append(f"pair must be one of {sorted(VALID_PAIRS)}")
# # #     if direction not in VALID_DIRECTIONS:
# # #         errors.append("direction must be 'long' or 'short'")
# # #     if outcome not in VALID_OUTCOMES:
# # #         errors.append("outcome must be 'win', 'loss', or 'breakeven'")
# # #     try:
# # #         rr = float(rr_raw)
# # #         if rr <= 0 or rr > 100:
# # #             errors.append("rr must be a positive number ≤ 100")
# # #     except (TypeError, ValueError):
# # #         rr = 1.0
# # #         errors.append("rr must be a valid number")

# # #     if errors:
# # #         abort(400, description="; ".join(errors))

# # #     return {
# # #         "id":        str(uuid.uuid4())[:8],
# # #         "pair":      pair,
# # #         "direction": direction,
# # #         "outcome":   outcome,
# # #         "rr":        round(float(rr_raw), 2),
# # #         "pnl_r":     _pnl(outcome, float(rr_raw)),
# # #         "date":      date,
# # #         "notes":     notes,
# # #     }


# # # # ── routes ───────────────────────────────────────────────────────────────────

# # # @app.route("/api/trades", methods=["GET"])
# # # def get_trades():
# # #     return jsonify(_load())


# # # @app.route("/api/trades", methods=["POST"])
# # # def add_trade():
# # #     trade = _validate_trade(request.get_json(force=True) or {})
# # #     trades = _load()
# # #     trades.append(trade)
# # #     _save(trades)
# # #     return jsonify(trade), 201


# # # @app.route("/api/trades/<trade_id>", methods=["DELETE"])
# # # def delete_trade(trade_id):
# # #     trades = _load()
# # #     new = [t for t in trades if t["id"] != trade_id]
# # #     if len(new) == len(trades):
# # #         abort(404, description="Trade not found")
# # #     _save(new)
# # #     return jsonify({"deleted": trade_id})


# # # @app.route("/api/trades", methods=["DELETE"])
# # # def clear_trades():
# # #     _save([])
# # #     return jsonify({"message": "All trades cleared"})


# # # @app.route("/api/trades/bulk", methods=["POST"])
# # # def bulk_import():
# # #     items = request.get_json(force=True) or []
# # #     if not isinstance(items, list):
# # #         abort(400, description="Expected a JSON array of trades")
# # #     trades = _load()
# # #     imported = []
# # #     for item in items:
# # #         t = _validate_trade(item)
# # #         trades.append(t)
# # #         imported.append(t)
# # #     _save(trades)
# # #     return jsonify({"imported": len(imported), "trades": imported}), 201


# # # @app.route("/api/analyze", methods=["GET"])
# # # def analyze_trades():
# # #     trades = _load()
# # #     return jsonify(analyze(trades))


# # # # ── error handlers ───────────────────────────────────────────────────────────

# # # @app.errorhandler(400)
# # # def bad_request(e):
# # #     return jsonify({"error": str(e.description)}), 400


# # # @app.errorhandler(404)
# # # def not_found(e):
# # #     return jsonify({"error": str(e.description)}), 404


# # # if __name__ == "__main__":
# # #     app.run(debug=True, port=5000)

# # """
# # app.py — Flask REST API for the Strategy Tester.

# # Endpoints:
# #   GET    /api/trades              → list all trades
# #   POST   /api/trades              → add a trade
# #   DELETE /api/trades/<id>         → remove a trade
# #   GET    /api/analyze             → full analysis (overall + batches)
# #   POST   /api/trades/bulk         → import list of trades at once
# #   DELETE /api/trades              → clear all trades

# #   GET    /api/checklist/config    → get saved checklist config (custom items)
# #   POST   /api/checklist/config    → save checklist config (custom items)
# #   POST   /api/checklist/log       → log a checklist snapshot + trade together
# #   GET    /api/checklist/history   → get all checklist snapshots
# # """

# # from flask import Flask, jsonify, request, abort
# # from flask_cors import CORS
# # import json, os, uuid
# # from datetime import datetime
# # from analyzer import analyze

# # app = Flask(__name__)

# # # ── CORS fix ──────────────────────────────────────────────────────────────────
# # CORS(app, resources={r"/api/*": {"origins": "*"}})

# # DATA_FILE      = os.path.join(os.path.dirname(__file__), "trades.json")
# # CHECKLIST_FILE = os.path.join(os.path.dirname(__file__), "checklist.json")


# # # ── persistence helpers ───────────────────────────────────────────────────────

# # def _load() -> list:
# #     if not os.path.exists(DATA_FILE):
# #         with open(DATA_FILE, "w") as f:
# #             json.dump([], f)
# #         return []
# #     with open(DATA_FILE, "r") as f:
# #         content = f.read().strip()
# #         if not content:
# #             with open(DATA_FILE, "w") as fw:
# #                 json.dump([], fw)
# #             return []
# #         return json.loads(content)


# # def _save(trades: list):
# #     with open(DATA_FILE, "w") as f:
# #         json.dump(trades, f, indent=2)


# # def _load_checklist() -> dict:
# #     default = {"custom_items": [], "history": []}
# #     if not os.path.exists(CHECKLIST_FILE):
# #         with open(CHECKLIST_FILE, "w") as f:
# #             json.dump(default, f, indent=2)
# #         return default
# #     with open(CHECKLIST_FILE, "r") as f:
# #         content = f.read().strip()
# #         if not content:
# #             with open(CHECKLIST_FILE, "w") as fw:
# #                 json.dump(default, fw, indent=2)
# #             return default
# #         return json.loads(content)


# # def _save_checklist(data: dict):
# #     with open(CHECKLIST_FILE, "w") as f:
# #         json.dump(data, f, indent=2)


# # def _pnl(outcome: str, rr: float) -> float:
# #     if outcome == "win":
# #         return round(rr, 3)
# #     elif outcome == "loss":
# #         return -1.0
# #     else:
# #         return 0.0


# # # ── validation ────────────────────────────────────────────────────────────────

# # VALID_OUTCOMES   = {"win", "loss", "breakeven"}
# # VALID_DIRECTIONS = {"long", "short"}
# # VALID_PAIRS = {
# #     "EURUSD", "GBPUSD", "USDJPY", "USDCHF",
# #     "XAUUSD", "XAGUSD", "AUDUSD", "NZDUSD",
# #     "USDCAD", "GBPJPY", "US30", "NAS100", "OTHER",
# # }


# # def _validate_trade(data: dict) -> dict:
# #     errors = []
# #     pair      = str(data.get("pair", "")).upper().strip()
# #     direction = str(data.get("direction", "")).lower().strip()
# #     outcome   = str(data.get("outcome", "")).lower().strip()
# #     rr_raw    = data.get("rr")
# #     date      = data.get("date", datetime.today().strftime("%Y-%m-%d"))
# #     notes     = str(data.get("notes", "")).strip()[:300]

# #     if pair not in VALID_PAIRS:
# #         errors.append(f"pair must be one of {sorted(VALID_PAIRS)}")
# #     if direction not in VALID_DIRECTIONS:
# #         errors.append("direction must be 'long' or 'short'")
# #     if outcome not in VALID_OUTCOMES:
# #         errors.append("outcome must be 'win', 'loss', or 'breakeven'")
# #     try:
# #         rr = float(rr_raw)
# #         if rr <= 0 or rr > 100:
# #             errors.append("rr must be a positive number ≤ 100")
# #     except (TypeError, ValueError):
# #         errors.append("rr must be a valid number")

# #     if errors:
# #         abort(400, description="; ".join(errors))

# #     return {
# #         "id":        str(uuid.uuid4())[:8],
# #         "pair":      pair,
# #         "direction": direction,
# #         "outcome":   outcome,
# #         "rr":        round(float(rr_raw), 2),
# #         "pnl_r":     _pnl(outcome, float(rr_raw)),
# #         "date":      date,
# #         "notes":     notes,
# #     }


# # # ── trade routes ──────────────────────────────────────────────────────────────

# # @app.route("/api/trades", methods=["GET"])
# # def get_trades():
# #     return jsonify(_load())


# # @app.route("/api/trades", methods=["POST"])
# # def add_trade():
# #     trade = _validate_trade(request.get_json(force=True) or {})
# #     trades = _load()
# #     trades.append(trade)
# #     _save(trades)
# #     return jsonify(trade), 201


# # @app.route("/api/trades/<trade_id>", methods=["DELETE"])
# # def delete_trade(trade_id):
# #     trades = _load()
# #     new = [t for t in trades if t["id"] != trade_id]
# #     if len(new) == len(trades):
# #         abort(404, description="Trade not found")
# #     _save(new)
# #     return jsonify({"deleted": trade_id})


# # @app.route("/api/trades", methods=["DELETE"])
# # def clear_trades():
# #     _save([])
# #     return jsonify({"message": "All trades cleared"})


# # @app.route("/api/trades/bulk", methods=["POST"])
# # def bulk_import():
# #     items = request.get_json(force=True) or []
# #     if not isinstance(items, list):
# #         abort(400, description="Expected a JSON array of trades")
# #     trades = _load()
# #     imported = []
# #     for item in items:
# #         t = _validate_trade(item)
# #         trades.append(t)
# #         imported.append(t)
# #     _save(trades)
# #     return jsonify({"imported": len(imported), "trades": imported}), 201


# # @app.route("/api/analyze", methods=["GET"])
# # def analyze_trades():
# #     trades = _load()
# #     return jsonify(analyze(trades))


# # # ── checklist routes ──────────────────────────────────────────────────────────

# # @app.route("/api/checklist/config", methods=["GET"])
# # def get_checklist_config():
# #     data = _load_checklist()
# #     return jsonify({"custom_items": data.get("custom_items", [])})


# # @app.route("/api/checklist/config", methods=["POST"])
# # def save_checklist_config():
# #     body = request.get_json(force=True) or {}
# #     custom_items = body.get("custom_items", [])
# #     if not isinstance(custom_items, list):
# #         abort(400, description="custom_items must be a list")
# #     custom_items = [str(i).strip()[:200] for i in custom_items if str(i).strip()]
# #     data = _load_checklist()
# #     data["custom_items"] = custom_items
# #     _save_checklist(data)
# #     return jsonify({"custom_items": custom_items})


# # @app.route("/api/checklist/log", methods=["POST"])
# # def log_checklist():
# #     """Save a checklist snapshot and log the associated trade together."""
# #     body = request.get_json(force=True) or {}

# #     # Validate and save the trade
# #     trade = _validate_trade(body.get("trade", {}))
# #     trades = _load()
# #     trades.append(trade)
# #     _save(trades)

# #     # Save checklist snapshot linked to this trade
# #     snapshot = {
# #         "id":          str(uuid.uuid4())[:8],
# #         "trade_id":    trade["id"],
# #         "date":        trade["date"],
# #         "timeframe":   str(body.get("timeframe", "")).strip(),
# #         "sections":    body.get("sections", {}),
# #         "custom":      body.get("custom", {}),
# #         "dollar_risk": body.get("dollar_risk", 0),
# #         "logged_at":   datetime.now().isoformat(),
# #     }

# #     data = _load_checklist()
# #     data.setdefault("history", []).append(snapshot)
# #     _save_checklist(data)

# #     return jsonify({"trade": trade, "snapshot": snapshot}), 201


# # @app.route("/api/checklist/history", methods=["GET"])
# # def get_checklist_history():
# #     data = _load_checklist()
# #     return jsonify(data.get("history", []))


# # # ── error handlers ────────────────────────────────────────────────────────────

# # @app.errorhandler(400)
# # def bad_request(e):
# #     return jsonify({"error": str(e.description)}), 400


# # @app.errorhandler(404)
# # def not_found(e):
# #     return jsonify({"error": str(e.description)}), 404


# # if __name__ == "__main__":
# #     app.run(debug=True, port=5000)

# """
# app.py — Flask REST API for the Strategy Tester.

# Endpoints:
#   GET    /api/trades              → list all trades
#   POST   /api/trades              → add a trade
#   DELETE /api/trades/<id>         → remove a trade
#   GET    /api/analyze             → full analysis (overall + batches + session + mood)
#   POST   /api/trades/bulk         → import list of trades at once
#   DELETE /api/trades              → clear all trades

#   GET    /api/checklist/config    → get saved checklist config
#   POST   /api/checklist/config    → save checklist config
#   POST   /api/checklist/log       → log checklist snapshot + trade together
#   GET    /api/checklist/history   → get all checklist snapshots
# """

# from flask import Flask, jsonify, request, abort
# from flask_cors import CORS
# import json, os, uuid
# from datetime import datetime
# from analyzer import analyze

# app = Flask(__name__)
# CORS(app, resources={r"/api/*": {"origins": "*"}})

# DATA_FILE      = os.path.join(os.path.dirname(__file__), "trades.json")
# CHECKLIST_FILE = os.path.join(os.path.dirname(__file__), "checklist.json")


# # ── persistence helpers ───────────────────────────────────────────────────────

# def _load() -> list:
#     if not os.path.exists(DATA_FILE):
#         with open(DATA_FILE, "w") as f:
#             json.dump([], f)
#         return []
#     with open(DATA_FILE, "r") as f:
#         content = f.read().strip()
#         if not content:
#             with open(DATA_FILE, "w") as fw:
#                 json.dump([], fw)
#             return []
#         return json.loads(content)


# def _save(trades: list):
#     with open(DATA_FILE, "w") as f:
#         json.dump(trades, f, indent=2)


# def _load_checklist() -> dict:
#     default = {"custom_items": [], "history": []}
#     if not os.path.exists(CHECKLIST_FILE):
#         with open(CHECKLIST_FILE, "w") as f:
#             json.dump(default, f, indent=2)
#         return default
#     with open(CHECKLIST_FILE, "r") as f:
#         content = f.read().strip()
#         if not content:
#             with open(CHECKLIST_FILE, "w") as fw:
#                 json.dump(default, fw, indent=2)
#             return default
#         return json.loads(content)


# def _save_checklist(data: dict):
#     with open(CHECKLIST_FILE, "w") as f:
#         json.dump(data, f, indent=2)


# def _pnl(outcome: str, rr: float) -> float:
#     if outcome == "win":
#         return round(rr, 3)
#     elif outcome == "loss":
#         return -1.0
#     else:
#         return 0.0


# # ── validation ────────────────────────────────────────────────────────────────

# VALID_OUTCOMES   = {"win", "loss", "breakeven"}
# VALID_DIRECTIONS = {"long", "short"}
# VALID_SESSIONS   = {"asian", "london", "new_york", "overlap", ""}
# VALID_MOODS      = {"calm", "confident", "anxious", "revenge", "fomo", "bored", ""}
# VALID_PAIRS = {
#     "EURUSD", "GBPUSD", "USDJPY", "USDCHF",
#     "XAUUSD", "XAGUSD", "AUDUSD", "NZDUSD",
#     "USDCAD", "GBPJPY", "US30", "NAS100", "OTHER",
# }


# def _validate_trade(data: dict) -> dict:
#     errors  = []
#     pair      = str(data.get("pair",      "")).upper().strip()
#     direction = str(data.get("direction", "")).lower().strip()
#     outcome   = str(data.get("outcome",   "")).lower().strip()
#     session   = str(data.get("session",   "")).lower().strip()
#     mood      = str(data.get("mood",      "")).lower().strip()
#     rr_raw    = data.get("rr")
#     date      = data.get("date", datetime.today().strftime("%Y-%m-%d"))
#     notes     = str(data.get("notes",   "")).strip()[:300]
#     journal   = str(data.get("journal", "")).strip()[:1000]

#     if pair not in VALID_PAIRS:
#         errors.append(f"pair must be one of {sorted(VALID_PAIRS)}")
#     if direction not in VALID_DIRECTIONS:
#         errors.append("direction must be 'long' or 'short'")
#     if outcome not in VALID_OUTCOMES:
#         errors.append("outcome must be 'win', 'loss', or 'breakeven'")
#     if session not in VALID_SESSIONS:
#         errors.append("session must be asian, london, new_york, or overlap")
#     if mood not in VALID_MOODS:
#         errors.append("mood must be calm, confident, anxious, revenge, fomo, or bored")
#     try:
#         rr = float(rr_raw)
#         if rr <= 0 or rr > 100:
#             errors.append("rr must be a positive number ≤ 100")
#     except (TypeError, ValueError):
#         errors.append("rr must be a valid number")

#     if errors:
#         abort(400, description="; ".join(errors))

#     return {
#         "id":        str(uuid.uuid4())[:8],
#         "pair":      pair,
#         "direction": direction,
#         "outcome":   outcome,
#         "rr":        round(float(rr_raw), 2),
#         "pnl_r":     _pnl(outcome, float(rr_raw)),
#         "date":      date,
#         "session":   session,
#         "mood":      mood,
#         "notes":     notes,
#         "journal":   journal,
#     }


# # ── trade routes ──────────────────────────────────────────────────────────────

# @app.route("/api/trades", methods=["GET"])
# def get_trades():
#     return jsonify(_load())


# @app.route("/api/trades", methods=["POST"])
# def add_trade():
#     trade  = _validate_trade(request.get_json(force=True) or {})
#     trades = _load()
#     trades.append(trade)
#     _save(trades)
#     return jsonify(trade), 201


# @app.route("/api/trades/<trade_id>", methods=["DELETE"])
# def delete_trade(trade_id):
#     trades = _load()
#     new    = [t for t in trades if t["id"] != trade_id]
#     if len(new) == len(trades):
#         abort(404, description="Trade not found")
#     _save(new)
#     return jsonify({"deleted": trade_id})


# @app.route("/api/trades", methods=["DELETE"])
# def clear_trades():
#     _save([])
#     return jsonify({"message": "All trades cleared"})


# @app.route("/api/trades/bulk", methods=["POST"])
# def bulk_import():
#     items = request.get_json(force=True) or []
#     if not isinstance(items, list):
#         abort(400, description="Expected a JSON array of trades")
#     trades   = _load()
#     imported = []
#     for item in items:
#         t = _validate_trade(item)
#         trades.append(t)
#         imported.append(t)
#     _save(trades)
#     return jsonify({"imported": len(imported), "trades": imported}), 201


# @app.route("/api/analyze", methods=["GET"])
# def analyze_trades():
#     trades = _load()
#     return jsonify(analyze(trades))


# # ── checklist routes ──────────────────────────────────────────────────────────

# @app.route("/api/checklist/config", methods=["GET"])
# def get_checklist_config():
#     data = _load_checklist()
#     return jsonify({"custom_items": data.get("custom_items", [])})


# @app.route("/api/checklist/config", methods=["POST"])
# def save_checklist_config():
#     body         = request.get_json(force=True) or {}
#     custom_items = body.get("custom_items", [])
#     if not isinstance(custom_items, list):
#         abort(400, description="custom_items must be a list")
#     custom_items = [str(i).strip()[:200] for i in custom_items if str(i).strip()]
#     data = _load_checklist()
#     data["custom_items"] = custom_items
#     _save_checklist(data)
#     return jsonify({"custom_items": custom_items})


# @app.route("/api/checklist/log", methods=["POST"])
# def log_checklist():
#     body  = request.get_json(force=True) or {}
#     trade = _validate_trade(body.get("trade", {}))
#     trades = _load()
#     trades.append(trade)
#     _save(trades)

#     snapshot = {
#         "id":          str(uuid.uuid4())[:8],
#         "trade_id":    trade["id"],
#         "date":        trade["date"],
#         "timeframe":   str(body.get("timeframe", "")).strip(),
#         "sections":    body.get("sections", {}),
#         "custom":      body.get("custom", {}),
#         "dollar_risk": body.get("dollar_risk", 0),
#         "logged_at":   datetime.now().isoformat(),
#     }

#     data = _load_checklist()
#     data.setdefault("history", []).append(snapshot)
#     _save_checklist(data)

#     return jsonify({"trade": trade, "snapshot": snapshot}), 201


# @app.route("/api/checklist/history", methods=["GET"])
# def get_checklist_history():
#     data = _load_checklist()
#     return jsonify(data.get("history", []))


# # ── error handlers ────────────────────────────────────────────────────────────

# @app.errorhandler(400)
# def bad_request(e):
#     return jsonify({"error": str(e.description)}), 400


# @app.errorhandler(404)
# def not_found(e):
#     return jsonify({"error": str(e.description)}), 404


# if __name__ == "__main__":
#     app.run(debug=True, port=5000)

"""
app.py — Flask REST API for the Strategy Tester.

Endpoints:
  GET    /api/trades              → list all trades
  POST   /api/trades              → add a trade
  DELETE /api/trades/<id>         → remove one trade
  DELETE /api/trades              → clear all trades
  GET    /api/analyze             → full analysis
  POST   /api/trades/bulk         → bulk import (JSON array)
  POST   /api/trades/import_csv   → import broker CSV text

  GET    /api/checklist/config    → get checklist config
  POST   /api/checklist/config    → save checklist config
  POST   /api/checklist/log       → log checklist + trade together
  GET    /api/checklist/history   → all checklist snapshots
"""

from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import json, os, uuid, csv, io
from datetime import datetime
from analyzer import analyze

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

DATA_FILE      = os.path.join(os.path.dirname(__file__), "trades.json")
CHECKLIST_FILE = os.path.join(os.path.dirname(__file__), "checklist.json")

# ── Valid pairs (with common broker suffix variants) ──────────────────────────
VALID_PAIRS = {
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF",
    "XAUUSD", "XAGUSD", "AUDUSD", "NZDUSD",
    "USDCAD", "GBPJPY", "US30", "NAS100",
    "BTCUSD", "ETHUSD", "OTHER",
}

VALID_OUTCOMES   = {"win", "loss", "breakeven"}
VALID_DIRECTIONS = {"long", "short"}
VALID_SESSIONS   = {"asian", "london", "new_york", "overlap", ""}
VALID_MOODS      = {"calm", "confident", "anxious", "revenge", "fomo", "bored", ""}


# ── Symbol cleaner ─────────────────────────────────────────────────────────────
def _clean_symbol(raw: str) -> str:
    """
    Convert broker symbol names to standard pairs.
    e.g. BTCUSDs → BTCUSD, XAUUSDs → XAUUSD, EURUSDs → EURUSD
    """
    s = raw.upper().strip()
    # Strip trailing 's', 'm', 'pro', '+' broker suffixes
    for suffix in ["PRO", "ECN", "SB"]:
        if s.endswith(suffix):
            s = s[:-len(suffix)]
    if s.endswith("S") and s[:-1] in VALID_PAIRS:
        s = s[:-1]
    return s if s in VALID_PAIRS else "OTHER"


# ── R estimator from broker profit data ───────────────────────────────────────
def _estimate_r(profit: float, lot: float, open_price: float, close_price: float, direction: str) -> tuple:
    """
    Estimate R value from broker data.
    Strategy: use pip/point movement relative to lot size.
    Returns (outcome, rr, pnl_r)
    """
    if profit == 0:
        return "breakeven", 0.0, 0.0

    # Price movement in absolute terms
    if direction == "long":
        move = close_price - open_price
    else:
        move = open_price - close_price

    # Normalize profit by lot to get per-unit profit
    per_unit = abs(profit / lot) if lot else abs(profit)

    # Use profit sign to determine outcome
    if profit > 0:
        outcome = "win"
        # R = ratio of per-unit profit to a baseline (assume 1R = losing 1 unit)
        rr = round(min(per_unit / max(per_unit * 0.5, 0.01), 20.0), 2)
        # Simple approach: normalize so losses = -1R, wins = proportional
        rr = round(abs(profit) / (abs(profit) * 0.5 + 0.001) * 1.0, 2)
        rr = max(0.1, min(rr, 20.0))
        pnl_r = round(rr, 3)
    else:
        outcome = "loss"
        rr = 1.0
        pnl_r = -1.0

    return outcome, rr, pnl_r


# ── Persistence helpers ───────────────────────────────────────────────────────

def _load() -> list:
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump([], f)
        return []
    with open(DATA_FILE, "r") as f:
        content = f.read().strip()
        if not content:
            with open(DATA_FILE, "w") as fw:
                json.dump([], fw)
            return []
        return json.loads(content)


def _save(trades: list):
    with open(DATA_FILE, "w") as f:
        json.dump(trades, f, indent=2)


def _load_checklist() -> dict:
    default = {"custom_items": [], "history": []}
    if not os.path.exists(CHECKLIST_FILE):
        with open(CHECKLIST_FILE, "w") as f:
            json.dump(default, f, indent=2)
        return default
    with open(CHECKLIST_FILE, "r") as f:
        content = f.read().strip()
        if not content:
            with open(CHECKLIST_FILE, "w") as fw:
                json.dump(default, fw, indent=2)
            return default
        return json.loads(content)


def _save_checklist(data: dict):
    with open(CHECKLIST_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _pnl(outcome: str, rr: float) -> float:
    if outcome == "win":   return round(rr, 3)
    if outcome == "loss":  return -1.0
    return 0.0


# ── Trade validation ──────────────────────────────────────────────────────────

def _validate_trade(data: dict) -> dict:
    errors    = []
    pair      = str(data.get("pair",      "")).upper().strip()
    direction = str(data.get("direction", "")).lower().strip()
    outcome   = str(data.get("outcome",   "")).lower().strip()
    session   = str(data.get("session",   "")).lower().strip()
    mood      = str(data.get("mood",      "")).lower().strip()
    rr_raw    = data.get("rr")
    date      = data.get("date", datetime.today().strftime("%Y-%m-%d"))
    notes     = str(data.get("notes",     "")).strip()[:300]
    journal   = str(data.get("journal",   "")).strip()[:1000]
    positions = data.get("positions", 1)

    if pair not in VALID_PAIRS:
        errors.append(f"pair must be one of {sorted(VALID_PAIRS)}")
    if direction not in VALID_DIRECTIONS:
        errors.append("direction must be 'long' or 'short'")
    if outcome not in VALID_OUTCOMES:
        errors.append("outcome must be 'win', 'loss', or 'breakeven'")
    if session not in VALID_SESSIONS:
        errors.append("invalid session value")
    if mood not in VALID_MOODS:
        errors.append("invalid mood value")
    try:
        rr = float(rr_raw)
        if rr <= 0 or rr > 100:
            errors.append("rr must be a positive number ≤ 100")
    except (TypeError, ValueError):
        errors.append("rr must be a valid number")

    try:
        positions = int(positions)
        if positions < 1:
            positions = 1
    except (TypeError, ValueError):
        positions = 1

    if errors:
        abort(400, description="; ".join(errors))

    return {
        "id":        str(uuid.uuid4())[:8],
        "pair":      pair,
        "direction": direction,
        "outcome":   outcome,
        "rr":        round(float(rr_raw), 2),
        "pnl_r":     _pnl(outcome, float(rr_raw)),
        "date":      date,
        "session":   session,
        "mood":      mood,
        "notes":     notes,
        "journal":   journal,
        "positions": positions,
    }


# ── Trade routes ──────────────────────────────────────────────────────────────

@app.route("/api/trades", methods=["GET"])
def get_trades():
    return jsonify(_load())


@app.route("/api/trades", methods=["POST"])
def add_trade():
    trade  = _validate_trade(request.get_json(force=True) or {})
    trades = _load()
    trades.append(trade)
    _save(trades)
    return jsonify(trade), 201


@app.route("/api/trades/<trade_id>", methods=["DELETE"])
def delete_trade(trade_id):
    trades = _load()
    new    = [t for t in trades if t["id"] != trade_id]
    if len(new) == len(trades):
        abort(404, description="Trade not found")
    _save(new)
    return jsonify({"deleted": trade_id})


@app.route("/api/trades", methods=["DELETE"])
def clear_trades():
    _save([])
    return jsonify({"message": "All trades cleared"})


@app.route("/api/trades/bulk", methods=["POST"])
def bulk_import():
    items    = request.get_json(force=True) or []
    if not isinstance(items, list):
        abort(400, description="Expected a JSON array of trades")
    trades   = _load()
    imported = []
    for item in items:
        t = _validate_trade(item)
        trades.append(t)
        imported.append(t)
    _save(trades)
    return jsonify({"imported": len(imported), "trades": imported}), 201


@app.route("/api/trades/import_csv", methods=["POST"])
def import_csv():
    """
    Accept broker CSV text in body:
      symbol,type,lot,open_price,close_price,profit,date
    Parse, clean, estimate R, and import all rows.
    """
    body = request.get_json(force=True) or {}
    csv_text = body.get("csv_text", "").strip()
    if not csv_text:
        abort(400, description="csv_text is required")

    reader   = csv.DictReader(io.StringIO(csv_text))
    trades   = _load()
    imported = []
    errors   = []

    for i, row in enumerate(reader, start=1):
        try:
            raw_symbol  = row.get("symbol", "").strip()
            trade_type  = row.get("type",   "").strip().lower()
            lot         = float(row.get("lot",         0) or 0)
            open_price  = float(row.get("open_price",  0) or 0)
            close_price = float(row.get("close_price", 0) or 0)
            profit      = float(row.get("profit",      0) or 0)
            date        = row.get("date", datetime.today().strftime("%Y-%m-%d")).strip()

            pair      = _clean_symbol(raw_symbol)
            direction = "long" if trade_type == "buy" else "short"
            outcome, rr, pnl_r = _estimate_r(profit, lot, open_price, close_price, direction)

            trade = {
                "id":         str(uuid.uuid4())[:8],
                "pair":       pair,
                "direction":  direction,
                "outcome":    outcome,
                "rr":         rr,
                "pnl_r":      pnl_r,
                "date":       date,
                "session":    "",
                "mood":       "",
                "notes":      f"lot:{lot} open:{open_price} close:{close_price} profit:{profit}",
                "journal":    "",
                "positions":  1,
                "imported":   True,
                "raw_profit": profit,
                "lot":        lot,
            }
            trades.append(trade)
            imported.append(trade)
        except Exception as e:
            errors.append(f"Row {i}: {str(e)}")

    _save(trades)
    return jsonify({
        "imported": len(imported),
        "errors":   errors,
        "trades":   imported
    }), 201


@app.route("/api/analyze", methods=["GET"])
def analyze_trades():
    return jsonify(analyze(_load()))


# ── Checklist routes ──────────────────────────────────────────────────────────

@app.route("/api/checklist/config", methods=["GET"])
def get_checklist_config():
    data = _load_checklist()
    return jsonify({"custom_items": data.get("custom_items", [])})


@app.route("/api/checklist/config", methods=["POST"])
def save_checklist_config():
    body         = request.get_json(force=True) or {}
    custom_items = body.get("custom_items", [])
    if not isinstance(custom_items, list):
        abort(400, description="custom_items must be a list")
    custom_items = [str(i).strip()[:200] for i in custom_items if str(i).strip()]
    data = _load_checklist()
    data["custom_items"] = custom_items
    _save_checklist(data)
    return jsonify({"custom_items": custom_items})


@app.route("/api/checklist/log", methods=["POST"])
def log_checklist():
    body  = request.get_json(force=True) or {}
    trade = _validate_trade(body.get("trade", {}))
    trades = _load()
    trades.append(trade)
    _save(trades)
    snapshot = {
        "id":          str(uuid.uuid4())[:8],
        "trade_id":    trade["id"],
        "date":        trade["date"],
        "timeframe":   str(body.get("timeframe", "")).strip(),
        "sections":    body.get("sections", {}),
        "custom":      body.get("custom", {}),
        "dollar_risk": body.get("dollar_risk", 0),
        "logged_at":   datetime.now().isoformat(),
    }
    data = _load_checklist()
    data.setdefault("history", []).append(snapshot)
    _save_checklist(data)
    return jsonify({"trade": trade, "snapshot": snapshot}), 201


@app.route("/api/checklist/history", methods=["GET"])
def get_checklist_history():
    return jsonify(_load_checklist().get("history", []))


# ── Error handlers ────────────────────────────────────────────────────────────

@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": str(e.description)}), 400

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": str(e.description)}), 404


if __name__ == "__main__":
    app.run(debug=True, port=5000)