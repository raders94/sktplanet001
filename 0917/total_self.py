import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

PRO01_CSV_PATH = './pro01.csv'

df = pd.read_csv(PRO01_CSV_PATH, encoding='cp949') #utf-8 or cp949

pd.DataFrame({'자료형': df.dtypes.astype('str'),
              '비결측수': df.notna().sum(),
              '결측수': df.isna().sum(),
              '결측률(%)': df.isna().mean()*100,
              '고유값 수': df.nunique(dropna=True)})

col = df.columns.to_list

data_cols = ['월', '수출입구분명','적공구분','컨테이너수(20피트)', '컨테이너수(40피트)'] #원하는 수치만 선택

project = df[data_cols]

project["전체total"] = (
    project["컨테이너수(20피트)"]
    + project["컨테이너수(40피트)"] * 2
)

#project    #특이값(10피트,기타)제외한 합계 

# 2. 월별 전체 물동량
monthly_total = project.groupby("월")["전체total"].sum()

# 3. 월별 적컨 물동량
monthly_loaded = (
    project.loc[project["적공구분"] == "적컨"]
    .groupby("월")["전체total"]
    .sum()
)

# 4. 데이터프레임 생성
result = pd.DataFrame({
    "전체total": monthly_total,
    "적컨total": monthly_loaded
})

# 5. 적컨 비중 계산
result["적컨비중(%)"] = (
    result["적컨total"]
    .div(result["전체total"])
    .mul(100)
    .round(2)
)



# whole = st.checkbox(label='지역', options=['전체','서울','부산','대전'])   




result = result.reset_index()

select_options = ["전체"] + [
    col for col in result.columns
    if col != "월"
]

selected = st.selectbox(
    "항목 선택",
    select_options
)

if selected == "전체":
    st.dataframe(result, hide_index=True)
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # 1. 전체total 막대 (뒤쪽 큰 막대)
    fig.add_trace(
        go.Bar(
            x=result["월"],
            y=result["전체total"],
            name="전체 물동량",
            marker_color="rgba(100, 149, 237, 0.45)",
            width=0.65,
            text=result["전체total"],
            textposition="outside"
        ),
        secondary_y=False
    )

    # 2. 적컨total 막대 (앞쪽 작은 막대, 겹치게)
    fig.add_trace(
        go.Bar(
            x=result["월"],
            y=result["적컨total"],
            name="적컨 물동량",
            marker_color="rgba(25, 25, 112, 0.85)",
            width=0.4,
            text=result["적컨total"],
            textposition="outside"
        ),
        secondary_y=False
    )

    # 3. 적컨비중 선그래프
    fig.add_trace(
        go.Scatter(
            x=result["월"],
            y=result["적컨비중(%)"],
            name="적컨 비중(%)",
            mode="lines+markers+text",
            text=result["적컨비중(%)"].astype(str) + "%",
            textposition="top center",
            line=dict(color="crimson", width=3),
            marker=dict(size=8)
        ),
        secondary_y=True
    )

    # 레이아웃 설정
    fig.update_layout(
        title="월별 전체 물동량 / 적컨 물동량 / 적컨 비중",
        template="plotly_white",
        barmode="overlay",   # 막대 겹치기
        hovermode="x unified",
        height=550,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(t=80, l=50, r=50, b=50)
    )

    # x축
    fig.update_xaxes(title_text="월")

    # 왼쪽 y축 (물동량)
    fig.update_yaxes(
        title_text="물동량",
        secondary_y=False
    )

    # 오른쪽 y축 (비중 %)
    fig.update_yaxes(
        title_text="적컨 비중(%)",
        secondary_y=True,
        range=[0, 100]
    )

    st.plotly_chart(fig, use_container_width=True)


elif selected == "전체total":
    st.dataframe(result[['월',"전체total"]], hide_index=True)
elif selected == "적컨total":
    st.dataframe(result[['월',"적컨total"]], hide_index=True)
elif selected == "적컨비중(%)":
    st.dataframe(result[['월',"적컨비중(%)"]], hide_index=True)


project["total"] = 0

mask = project["적공구분"] == "적컨"

project.loc[mask, "total"] = (
    project.loc[mask, "컨테이너수(20피트)"]
    + project.loc[mask, "컨테이너수(40피트)"] * 2
)


result = []
for i in project["월"].unique().tolist():
    month_sum = project.loc[project['월'] == i ].sum()
    month_sum["월"] = i
    result.append(month_sum)
    
monthly_sum = pd.DataFrame(result)
monthly_sum = monthly_sum.sort_values("월")
result = monthly_sum[['월','total']]

result_month = result.sort_values("월").set_index("월")

result_month["증감률(%)"] = (
    result["total"]
    .pct_change()
    .mul(100)
    .round(2)
)


trans_result = project.pivot_table(
    index="월",
    columns="수출입구분명",
    values="total",
    aggfunc="sum",
    fill_value=0
)

trans_result["환적"] = trans_result["수입환적"] + trans_result["수출환적"]

trans_result = trans_result[["환적", "수입", "수출"]]

trans_result["총합"] = trans_result[["환적", "수입", "수출"]].sum(axis=1)

trans_result["환적비중(%)"] = (
    trans_result["환적"]
    .div(trans_result["총합"])
    .mul(100)
    .round(2)
)
trans_result.columns.name = None

fig = make_subplots(
    specs=[[{"secondary_y": True}]]
)


# =========================
# 누적 막대그래프
# =========================

# 수입
fig.add_trace(
    go.Bar(
        x=trans_result.index,
        y=trans_result["수입"],
        name="수입",
        marker_color="#4C78A8"
    ),
    secondary_y=False
)

# 수출
fig.add_trace(
    go.Bar(
        x=trans_result.index,
        y=trans_result["수출"],
        name="수출",
        marker_color="#F2A541"
    ),
    secondary_y=False
)

# 환적
fig.add_trace(
    go.Bar(
        x=trans_result.index,
        y=trans_result["환적"],
        name="환적",
        marker_color="#59A14F"
    ),
    secondary_y=False
)


# =========================
# 환적 비중 선그래프
# =========================

fig.add_trace(
    go.Scatter(
        x=trans_result.index,
        y=trans_result["환적비중(%)"],

        name="환적 비중",

        mode="lines+markers+text",

        # 그래프 위에 비중 표시
        text=trans_result["환적비중(%)"].astype(str) + "%",

        textposition="top center",

        line=dict(
            color="#E15759",
            width=3
        ),

        marker=dict(
            size=9
        )
    ),
    secondary_y=True
)


# =========================
# 그래프 디자인
# =========================

fig.update_layout(

    title="월별 수입 · 수출 · 환적 물동량 및 환적 비중",

    # 누적 막대
    barmode="stack",

    template="plotly_white",

    height=600,

    hovermode="x unified",

    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),

    margin=dict(
        t=100,
        l=60,
        r=60,
        b=60
    )
)


# X축
fig.update_xaxes(
    title_text="월"
)


# 왼쪽 Y축 → 물동량
fig.update_yaxes(
    title_text="물동량",
    secondary_y=False,
    rangemode="tozero"
)


# 오른쪽 Y축 → 환적비중
fig.update_yaxes(
    title_text="환적 비중 (%)",
    secondary_y=True,
    range=[0, 100],
    ticksuffix="%"
)


# Streamlit 출력
st.plotly_chart(
    fig,
    use_container_width=True
)