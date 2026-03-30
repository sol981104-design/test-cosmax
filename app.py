import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="시제품 데이터 분석 대시보드", layout="wide")
st.title("📊 시제품 데이터 분석 대시보드")

# ── 파일 업로드 ──
uploaded_file = st.file_uploader("엑셀 파일을 업로드하세요 (.xlsx)", type=["xlsx"])

if uploaded_file is None:
    st.info("엑셀 파일을 업로드하면 대시보드가 표시됩니다.")
    st.stop()

xls = pd.ExcelFile(uploaded_file)
df_product = pd.read_excel(xls, sheet_name="시제품정보")
df_product["작성일"] = pd.to_datetime(df_product["작성일"], errors="coerce")

df_stability = pd.read_excel(xls, sheet_name="안정성테스트결과")
df_stability["측정일"] = pd.to_datetime(df_stability["측정일"], errors="coerce")

# ── 사이드바 필터 ──
st.sidebar.header("필터")

제품유형_옵션 = st.sidebar.multiselect("제품유형", df_product["제품유형"].unique(), default=df_product["제품유형"].unique())
개발단계_옵션 = st.sidebar.multiselect("개발단계", df_product["개발단계"].unique(), default=df_product["개발단계"].unique())
피부타입_옵션 = st.sidebar.multiselect("목표피부타입", df_product["목표피부타입"].unique(), default=df_product["목표피부타입"].unique())

filtered = df_product[
    df_product["제품유형"].isin(제품유형_옵션)
    & df_product["개발단계"].isin(개발단계_옵션)
    & df_product["목표피부타입"].isin(피부타입_옵션)
]

# 안정성 데이터도 선택된 시제품코드 기준 필터링
filtered_codes = filtered["시제품코드"].unique()
filtered_stab = df_stability[df_stability["시제품코드"].isin(filtered_codes)]

# ── 탭 구성 ──
tab1, tab2 = st.tabs(["🧴 시제품 정보", "🔬 안정성 테스트"])

# ═══════════════════════════════════════════
# 탭 1: 시제품 정보
# ═══════════════════════════════════════════
with tab1:
    # KPI 카드
    cols = st.columns(4)
    cols[0].metric("총 시제품 수", f"{len(filtered)}건")
    cols[1].metric("제품유형 수", f"{filtered['제품유형'].nunique()}개")
    cols[2].metric("담당팀 수", f"{filtered['담당팀'].nunique()}개")
    cols[3].metric("주요컨셉 수", f"{filtered['주요컨셉'].nunique()}개")

    st.markdown("---")
    row1_left, row1_right = st.columns(2)

    with row1_left:
        st.subheader("제품유형별 시제품 수")
        type_counts = filtered["제품유형"].value_counts().reset_index()
        type_counts.columns = ["제품유형", "건수"]
        fig1 = px.bar(type_counts, x="제품유형", y="건수", color="제품유형", text_auto=True)
        fig1.update_layout(showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)

    with row1_right:
        st.subheader("개발단계 분포")
        stage_counts = filtered["개발단계"].value_counts().reset_index()
        stage_counts.columns = ["개발단계", "건수"]
        fig2 = px.pie(stage_counts, names="개발단계", values="건수", hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)

    row2_left, row2_right = st.columns(2)

    with row2_left:
        st.subheader("목표피부타입별 시제품 수")
        skin_counts = filtered["목표피부타입"].value_counts().reset_index()
        skin_counts.columns = ["목표피부타입", "건수"]
        fig3 = px.bar(skin_counts, x="목표피부타입", y="건수", color="목표피부타입", text_auto=True)
        fig3.update_layout(showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    with row2_right:
        st.subheader("주요컨셉 분포")
        concept_counts = filtered["주요컨셉"].value_counts().reset_index()
        concept_counts.columns = ["주요컨셉", "건수"]
        fig4 = px.pie(concept_counts, names="주요컨셉", values="건수", hole=0.4)
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")
    st.subheader("담당팀별 시제품 현황")
    team_skin = pd.crosstab(filtered["담당팀"], filtered["제품유형"])
    fig5 = px.bar(team_skin, barmode="stack", text_auto=True)
    fig5.update_layout(xaxis_title="담당팀", yaxis_title="건수", legend_title="제품유형")
    st.plotly_chart(fig5, use_container_width=True)

    st.subheader("월별 시제품 작성 추이")
    monthly = filtered.set_index("작성일").resample("M").size().reset_index(name="건수")
    monthly["월"] = monthly["작성일"].dt.strftime("%Y-%m")
    fig6 = px.line(monthly, x="월", y="건수", markers=True)
    st.plotly_chart(fig6, use_container_width=True)

    st.markdown("---")
    st.subheader("원본 데이터")
    st.dataframe(filtered, use_container_width=True)

# ═══════════════════════════════════════════
# 탭 2: 안정성 테스트
# ═══════════════════════════════════════════
with tab2:
    if filtered_stab.empty:
        st.warning("선택된 시제품에 대한 안정성 테스트 데이터가 없습니다.")
        st.stop()

    # KPI 카드
    cols = st.columns(4)
    cols[0].metric("총 테스트 수", f"{len(filtered_stab)}건")
    cols[1].metric("적합 판정", f"{(filtered_stab['판정결과'] == '적합').sum()}건")
    cols[2].metric("부적합 판정", f"{(filtered_stab['판정결과'] == '부적합').sum()}건")
    cols[3].metric("재검토", f"{(filtered_stab['판정결과'] == '재검토').sum()}건")

    st.markdown("---")
    row1_left, row1_right = st.columns(2)

    with row1_left:
        st.subheader("판정결과 분포")
        result_counts = filtered_stab["판정결과"].value_counts().reset_index()
        result_counts.columns = ["판정결과", "건수"]
        color_map = {"적합": "#2ecc71", "부적합": "#e74c3c", "재검토": "#f39c12"}
        fig_r = px.pie(result_counts, names="판정결과", values="건수", hole=0.4,
                       color="판정결과", color_discrete_map=color_map)
        st.plotly_chart(fig_r, use_container_width=True)

    with row1_right:
        st.subheader("테스트조건별 판정결과")
        cond_result = pd.crosstab(filtered_stab["테스트조건"], filtered_stab["판정결과"])
        fig_cr = px.bar(cond_result, barmode="group", text_auto=True,
                        color_discrete_map=color_map)
        fig_cr.update_layout(xaxis_title="테스트조건", yaxis_title="건수", legend_title="판정결과")
        st.plotly_chart(fig_cr, use_container_width=True)

    st.markdown("---")
    row2_left, row2_right = st.columns(2)

    with row2_left:
        st.subheader("보관온도별 점도 분포")
        fig_v = px.box(filtered_stab, x="테스트조건", y="점도_cP", color="테스트조건",
                       points="all")
        fig_v.update_layout(showlegend=False)
        st.plotly_chart(fig_v, use_container_width=True)

    with row2_right:
        st.subheader("보관온도별 pH 분포")
        fig_ph = px.box(filtered_stab, x="테스트조건", y="pH", color="테스트조건",
                        points="all")
        fig_ph.update_layout(showlegend=False)
        st.plotly_chart(fig_ph, use_container_width=True)

    st.markdown("---")
    row3_left, row3_right = st.columns(2)

    with row3_left:
        st.subheader("보관기간(주)에 따른 점도 변화")
        fig_vt = px.scatter(filtered_stab, x="보관기간_주", y="점도_cP",
                            color="테스트조건", trendline="ols",
                            hover_data=["시제품코드", "판정결과"])
        st.plotly_chart(fig_vt, use_container_width=True)

    with row3_right:
        st.subheader("보관기간(주)에 따른 pH 변화")
        fig_pt = px.scatter(filtered_stab, x="보관기간_주", y="pH",
                            color="테스트조건", trendline="ols",
                            hover_data=["시제품코드", "판정결과"])
        st.plotly_chart(fig_pt, use_container_width=True)

    st.markdown("---")
    row4_left, row4_right = st.columns(2)

    with row4_left:
        st.subheader("색상변화등급 분포")
        color_counts = filtered_stab["색상변화등급"].value_counts().sort_index().reset_index()
        color_counts.columns = ["색상변화등급", "건수"]
        fig_clr = px.bar(color_counts, x="색상변화등급", y="건수", text_auto=True)
        st.plotly_chart(fig_clr, use_container_width=True)

    with row4_right:
        st.subheader("향변화 / 분리현상 발생 현황")
        issue_data = pd.DataFrame({
            "항목": ["향변화", "분리현상"],
            "발생(Y)": [
                (filtered_stab["향변화여부"] == "Y").sum(),
                (filtered_stab["분리현상여부"] == "Y").sum(),
            ],
            "미발생(N)": [
                (filtered_stab["향변화여부"] == "N").sum(),
                (filtered_stab["분리현상여부"] == "N").sum(),
            ],
        })
        issue_melted = issue_data.melt(id_vars="항목", var_name="상태", value_name="건수")
        fig_iss = px.bar(issue_melted, x="항목", y="건수", color="상태",
                         barmode="group", text_auto=True,
                         color_discrete_map={"발생(Y)": "#e74c3c", "미발생(N)": "#2ecc71"})
        st.plotly_chart(fig_iss, use_container_width=True)

    st.markdown("---")
    st.subheader("시제품별 판정결과 요약")
    summary = pd.crosstab(filtered_stab["시제품코드"], filtered_stab["판정결과"], margins=True, margins_name="합계")
    st.dataframe(summary, use_container_width=True)

    st.markdown("---")
    st.subheader("안정성 테스트 원본 데이터")
    st.dataframe(filtered_stab, use_container_width=True)
