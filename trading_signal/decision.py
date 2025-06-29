def generate_signal(metrics: dict) -> dict:
    """
    Takes a dictionary of key metrics and returns:
    - score (0–100)
    - decision ("BUY" or "WAIT")
    - all flags + rationale
    """

    score = 0
    rationale = []

    # --- EMA50 ---
    if metrics["price"] > metrics["ema50"]:
        score += 10
        rationale.append("🟢 Price > EMA50")
        ema50_flag = "🟢"
    else:
        ema50_flag = "🟡"

    # --- EMA20 proximity ---
    proximity = abs(metrics["price"] - metrics["ema20"]) / metrics["ema20"] * 100
    if proximity <= 5:
        score += max(0, 15 - proximity * 3)
        rationale.append("🟢 Close to EMA20")
        ema20_flag = "🟢"
    else:
        ema20_flag = "🟡"

    # --- Fibonacci zone (use 2-month) ---
    if metrics["fib2m_618"] <= metrics["price"] <= metrics["fib2m_382"]:
        score += 30
        rationale.append("🟢 Within 2M Fibonacci zone")
        fib_flag = "🟢"
    else:
        fib_flag = "🟡"

    # --- Volume ---
    if metrics["volume"] >= metrics["avg_volume"]:
        score += min((metrics["volume"] / metrics["avg_volume"]) * 20, 20)
        rationale.append("🟢 Volume above average")
        volume_flag = "🟢"
    else:
        volume_flag = "🟡"

    # --- RSI ---
    rsi = metrics["rsi"]
    if 50 <= rsi <= 70:
        score += 25
        rationale.append("🟢 RSI in healthy range")
        rsi_flag = "🟢"
    elif 40 <= rsi < 50 or 70 < rsi <= 80:
        score += 12
        rsi_flag = "🟡"
    else:
        rsi_flag = "🟡"

    # --- Final decision ---
    decision = "BUY" if score >= 70 else "WAIT"

    return {
        "Score %": round(score, 1),
        "Decision": decision,
        "Flag EMA20": ema20_flag,
        "Flag EMA50": ema50_flag,
        "Flag Fib": fib_flag,
        "Flag Volume": volume_flag,
        "Flag RSI": rsi_flag,
        "Rationale": rationale
    }
