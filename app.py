from flask import Flask, render_template, jsonify
import pandas as pd

app = Flask(__name__)

@app.route("/")
def dashboard():
    df = pd.read_csv("data/chat_metrics.csv")

    # KPIs
    total_chats = df["total_chats"].sum()
    avg_response = f"{df['avg_response_time'].mean():.1f} sec"
    avg_csat = f"{df['csat'].mean() * 100:.1f}%"
    avg_agents = int(df["active_agents"].mean())

    # Chart data
    chats_trend = df[["day", "total_chats"]].to_dict(orient="records")
    response_trend = df[["day", "avg_response_time"]].to_dict(orient="records")
    category_mix = {
        "Support": df["support"].mean(),
        "Sales": df["sales"].mean(),
        "Tech": df["tech"].mean(),
    }
    agents_csat = df[["day", "active_agents", "csat"]].to_dict(orient="records")

    return render_template(
        "dashboard.html",
        total_chats=total_chats,
        avg_response=avg_response,
        avg_csat=avg_csat,
        avg_agents=avg_agents,
        chats_trend=chats_trend,
        response_trend=response_trend,
        category_mix=category_mix,
        agents_csat=agents_csat,
    )

@app.route("/api/data")
def api_data():
    df = pd.read_csv("data/chat_metrics.csv")
    return jsonify(df.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

