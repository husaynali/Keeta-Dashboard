from flask import Flask, render_template, request
import pandas as pd
import numpy as np

app = Flask(__name__)

# Load data once at start
data = pd.read_csv("data/data.csv")

@app.route("/overall")
def overall_dashboard():
    df = data.copy()

    # Get filters from query string
    agent = request.args.get("agent")
    leader = request.args.get("team_leader")
    supervisor = request.args.get("supervisor")
    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")

    # Apply filters
    if agent:
        df = df[df["agent"] == agent]
    if leader:
        df = df[df["team_leader"] == leader]
    if supervisor:
        df = df[df["supervisor"] == supervisor]
    if from_date and to_date:
        df["day"] = pd.to_datetime(df["day"])
        df = df[(df["day"] >= from_date) & (df["day"] <= to_date)]

    # Compute overall KPIs safely
    overall_kpis = [
        {"label": "Total Chats", "value": int(df["total_chats"].sum()) if "total_chats" in df and not df.empty else 0},
        {"label": "Avg Response Time", "value": f"{df['avg_response_time'].mean():.1f} sec" if "avg_response_time" in df and not df.empty else "N/A"},
        {"label": "Avg CSAT", "value": f"{df['csat'].mean() * 100:.1f}%" if "csat" in df and not df.empty else "N/A"},
        {"label": "Active Agents", "value": int(df["active_agents"].mean()) if "active_agents" in df and not df["active_agents"].isna().all() else 0},
        {"label": "Escalations", "value": int(df["escalations"].sum()) if "escalations" in df and not df.empty else 0},
        {"label": "Resolved Tickets", "value": f"{df['resolved'].mean() * 100:.1f}%" if "resolved" in df and not df.empty else "N/A"},
        {"label": "Pending Tickets", "value": int(df["pending"].sum()) if "pending" in df and not df.empty else 0},
        {"label": "Avg Chat Duration", "value": f"{df['avg_chat_duration'].mean():.1f} min" if "avg_chat_duration" in df and not df.empty else "N/A"},
        {"label": "Sales Conversions", "value": f"{df['sales_conversion'].mean() * 100:.1f}%" if "sales_conversion" in df and not df.empty else "N/A"},
        {"label": "Avg Queue Time", "value": f"{df['avg_queue_time'].mean():.1f} sec" if "avg_queue_time" in df and not df.empty else "N/A"},
    ]

    # Build KPI trends for sparkline charts
    kpi_trends = {}
    trend_cols = [
        "total_chats", "avg_response_time", "csat", "active_agents",
        "escalations", "resolved", "pending", "avg_chat_duration",
        "sales_conversion", "avg_queue_time"
    ]

    for col, kpi in zip(trend_cols, overall_kpis):
        if col in df and not df.empty:
            # Group by day if day exists, else use rolling window
            if "day" in df:
                trend = df.groupby("day")[col].sum().tolist() if df[col].dtype != "float64" else df.groupby("day")[col].mean().tolist()
            else:
                trend = df[col].tolist()
            # Fallback to empty list
            kpi_trends[kpi["label"]] = trend if trend else [0]
        else:
            kpi_trends[kpi["label"]] = [0]

    # Populate filter dropdowns dynamically
    agents = sorted(data["agent"].dropna().unique()) if "agent" in data else []
    leaders = sorted(data["team_leader"].dropna().unique()) if "team_leader" in data else []
    supervisors = sorted(data["supervisor"].dropna().unique()) if "supervisor" in data else []

    return render_template(
        "overall.html",
        kpis=overall_kpis,
        kpi_trends=kpi_trends,
        agents=agents,
        leaders=leaders,
        supervisors=supervisors
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)

