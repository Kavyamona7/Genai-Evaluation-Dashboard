import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from services.evaluation_service import run_single_evaluation
from services.evaluator import update_result_quality_scores
from services.ranker import add_overall_score
from services.recommender import get_recommendations

# ---------------------------
# Page config
# ---------------------------
st.set_page_config(
    page_title="LLM Evaluation Dashboard",
    page_icon="🤖",
    layout="wide"
)

# ---------------------------
# Styling
# ---------------------------
st.markdown("""
<style>
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}
.main-title {
    font-size: 2.4rem;
    font-weight: 700;
    margin-bottom: 0.2rem;
}
.subtitle {
    color: #9ca3af;
    margin-bottom: 1.2rem;
}
.metric-box {
    background: #111827;
    padding: 16px;
    border-radius: 14px;
    border: 1px solid #2d3748;
}
.card-box {
    background: #0f172a;
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #263041;
    margin-bottom: 14px;
}
.small-label {
    color: #9ca3af;
    font-size: 0.9rem;
}
.highlight {
    font-weight: 600;
    font-size: 1.05rem;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Session state
# ---------------------------
if "results" not in st.session_state:
    st.session_state.results = []

def add_result(result: dict) -> None:
    st.session_state.results.append(result)


# ---------------------------
# Header
# ---------------------------
st.markdown('<div class="main-title">🤖 LLM Evaluation Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Compare language models by latency, estimated cost, response length, and quality score.</div>',
    unsafe_allow_html=True
)

# ---------------------------
# Sidebar
# ---------------------------
with st.sidebar:
    st.header("⚙️ Settings")

    model_options = ["gpt-4o-mini", "gpt-4.1-mini"]

    selected_models = st.multiselect(
        "Select models",
        options=model_options,
        default=["gpt-4o-mini", "gpt-4.1-mini"]
    )

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.1
    )

    prompt_preset = st.selectbox(
        "Prompt preset",
        [
            "Custom",
            "Explain what a data pipeline is in simple terms.",
            "Summarize how LLMs can be evaluated for business use.",
            "Write a short risk-aware explanation of generative AI for an insurance company.",
            "Explain prompt engineering in simple language."
        ]
    )

    st.markdown("---")
    st.caption("Tip: Use business-focused prompts for stronger screenshots and demos.")

# ---------------------------
# Prompt input
# ---------------------------
default_prompt = "" if prompt_preset == "Custom" else prompt_preset

prompt = st.text_area(
    "Enter your prompt",
    value=default_prompt,
    height=160,
    placeholder="Type your evaluation prompt here..."
)

col1, col2 = st.columns([1, 1])

with col1:
    run_clicked = st.button("🚀 Run Evaluation", use_container_width=True)

with col2:
    clear_clicked = st.button("🗑️ Clear Results", use_container_width=True)

if clear_clicked:
    st.session_state.results = []
    st.rerun()

# ---------------------------
# Run evaluation
# ---------------------------
if run_clicked:
    if not prompt.strip():
        st.warning("Please enter a prompt.")
    elif not selected_models:
        st.warning("Please select at least one model.")
    else:
        progress = st.progress(0)
        status = st.empty()

        for idx, model in enumerate(selected_models):
            try:
                status.info(f"Running {model}...")

                result = run_single_evaluation(
                    model=model,
                    prompt=prompt,
                    temperature=temperature
                )

                add_result(result)

                progress.progress((idx + 1) / len(selected_models))

            except Exception as e:
                st.error(f"Error with model {model}: {e}")

        status.success("Evaluation complete.")

# ---------------------------
# Results
# ---------------------------
if st.session_state.results:
    df = pd.DataFrame(st.session_state.results)
    for i in range(len(st.session_state.results)):
        st.session_state.results[i] = update_result_quality_scores(
            st.session_state.results[i]
        )

    df = pd.DataFrame(st.session_state.results)
    df = add_overall_score(df)
    recommendations = get_recommendations(df)

    total_models = len(df)
    avg_latency = round(df["latency_seconds"].mean(), 2)
    avg_quality = round(df["quality_score"].mean(), 2)
    total_cost = round(df["estimated_cost_usd"].sum(), 4)

    st.markdown("## 📊 Overview")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Models Tested", total_models)
    m2.metric("Avg Latency (s)", avg_latency)
    m3.metric("Avg Quality", avg_quality)
    m4.metric("Total Est. Cost ($)", total_cost)

    st.markdown("## 🏆 Recommendations")
    r1, r2, r3, r4 = st.columns(4)
    r1.success(f"Fastest: {recommendations['fastest']}")
    r2.success(f"Cheapest: {recommendations['cheapest']}")
    r3.success(f"Best Quality: {recommendations['best_quality']}")
    r4.success(f"Best Overall: {recommendations['best_overall']}")
    st.info(
        "Best Overall model balances quality, latency, and cost based on weighted scoring. "
        "Use Fastest for real-time apps, Cheapest for scale, and Best Quality for critical outputs."
    )

    st.markdown("## 🧾 Model Cards")
    card_cols = st.columns(min(3, len(df)))

    for idx, row in df.iterrows():
        with card_cols[idx % len(card_cols)]:
            st.markdown(
                f"""
                <div class="card-box">
                    <div class="highlight">{row['model']}</div>
                    <div class="small-label">Latency</div>
                    <div>{row['latency_seconds']} s</div>
                    <div class="small-label">Estimated Cost</div>
                    <div>${row['estimated_cost_usd']}</div>
                    <div class="small-label">Response Length</div>
                    <div>{row['response_length_words']} words</div>
                    <div class="small-label">Quality Score</div>
                    <div>{row['quality_score']} / 5</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("## 📈 Visual Comparison")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        fig_latency = px.bar(
            df,
            x="model",
            y="latency_seconds",
            title="Latency by Model",
            text="latency_seconds"
        )
        fig_latency.update_layout(
            xaxis_title="Model",
            yaxis_title="Latency (seconds)"
        )
        st.plotly_chart(fig_latency, use_container_width=True)

    with chart_col2:
        fig_quality = px.bar(
            df,
            x="model",
            y="quality_score",
            title="Quality Score by Model",
            text="quality_score"
        )
        fig_quality.update_layout(
            xaxis_title="Model",
            yaxis_title="Quality Score"
        )
        st.plotly_chart(fig_quality, use_container_width=True)

    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:
        fig_cost = px.scatter(
            df,
            x="latency_seconds",
            y="estimated_cost_usd",
            color="model",
            size="response_length_words",
            title="Cost vs Latency",
            hover_data=["quality_score", "response_length_words"]
        )
        fig_cost.update_layout(
            xaxis_title="Latency (seconds)",
            yaxis_title="Estimated Cost (USD)"
        )
        st.plotly_chart(fig_cost, use_container_width=True)

    with chart_col4:
        fig_words = px.bar(
            df,
            x="model",
            y="response_length_words",
            title="Response Length by Model",
            text="response_length_words"
        )
        fig_words.update_layout(
            xaxis_title="Model",
            yaxis_title="Word Count"
        )
        st.plotly_chart(fig_words, use_container_width=True)

    st.markdown("## 📊 Normalized Comparison")

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df["model"],
        y=df["normalized_quality"],
        name="Quality",
    ))

    fig.add_trace(go.Bar(
        x=df["model"],
        y=df["normalized_latency"],
        name="Speed",
    ))

    fig.add_trace(go.Bar(
        x=df["model"],
        y=df["normalized_cost"],
        name="Cost Efficiency",
    ))

    fig.update_layout(
        barmode="group",
        title="Normalized Model Comparison",
        yaxis_title="Score (0-1)",
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("## ⚖️ Trade-off Analysis")

    fig_tradeoff = px.scatter(
        df,
        x="latency_seconds",
        y="quality_score",
        size="estimated_cost_usd",
        color="model",
        title="Latency vs Quality (Bubble size = Cost)",
        hover_data=["overall_score"]
    )

    st.plotly_chart(fig_tradeoff, use_container_width=True)

    st.markdown("## 🧠 Detailed Responses")

    tabs = st.tabs(df["model"].tolist())

    for i, tab in enumerate(tabs):
        with tab:
            row = st.session_state.results[i]

            st.subheader(row["model"])
            st.write(row["response"])

            c1, c2, c3 = st.columns(3)

            with c1:
                relevance = st.slider(
                    f"Relevance - {row['model']}",
                    min_value=1,
                    max_value=5,
                    value=int(row.get("relevance_score", 3)),
                    key=f"relevance_{i}"
                )
                st.session_state.results[i]["relevance_score"] = relevance

            with c2:
                clarity = st.slider(
                    f"Clarity - {row['model']}",
                    min_value=1,
                    max_value=5,
                    value=int(row.get("clarity_score", 3)),
                    key=f"clarity_{i}"
                )
                st.session_state.results[i]["clarity_score"] = clarity

            with c3:
                completeness = st.slider(
                    f"Completeness - {row['model']}",
                    min_value=1,
                    max_value=5,
                    value=int(row.get("completeness_score", 3)),
                    key=f"completeness_{i}"
                )
                st.session_state.results[i]["completeness_score"] = completeness

            st.session_state.results[i] = update_result_quality_scores(
                st.session_state.results[i]
            )

            avg_score = st.session_state.results[i]["quality_score"]
            st.info(f"Average quality score for {row['model']}: {avg_score} / 5")

    # refresh dataframe after scoring
    df = pd.DataFrame(st.session_state.results)
    for i in range(len(st.session_state.results)):
        st.session_state.results[i] = update_result_quality_scores(
            st.session_state.results[i]
        )
    df = pd.DataFrame(st.session_state.results)
    df = add_overall_score(df)
    recommendations = get_recommendations(df)

    fig_overall = px.bar(
        df,
        x="model",
        y="overall_score",
        title="Overall Score by Model",
        text="overall_score",
    )
    fig_overall.update_layout(
        xaxis_title="Model",
        yaxis_title="Overall Score",
    )
    st.plotly_chart(fig_overall, use_container_width=True)

    st.markdown("## 📋 Results Table")
    st.dataframe(
        df[[
            "model",
            "latency_seconds",
            "response_length_words",
            "estimated_cost_usd",
            "relevance_score",
            "clarity_score",
            "completeness_score",
            "quality_score",
            "overall_score",
        ]],
        use_container_width=True
    )

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download Results as CSV",
        data=csv,
        file_name="llm_evaluation_results.csv",
        mime="text/csv"
    )

else:
    st.info("Run an evaluation to see metrics, charts, rankings, and detailed responses.")
