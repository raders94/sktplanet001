from pathlib import Path
import pandas as pd
import streamlit as st


st.set_page_config(page_title='판매 대시보드', page_icon='😶‍🌫️',layout='wide')

Target_dir='data'
Target_csv='data.csv'
DIR = Path(__file__).resolve().parent
data_path= DIR.parent/ Target_dir / Target_csv

df= pd.read_csv(data_path)

st.dataframe(df)

st.title('판매 대시보드')

with st.sidebar:
    st.header('조회조건')
    region=st.selectbox(
        label='지역',
        options=[
            #'전체', '서울', '부산', '대전'
            '전체',
            *(df['region'].unique().tolist())
            ],
    )

    minimum_sales= st.slider(
        label='최소 매출', min_value=0,
        max_value=int(df['sales'].max()),value=0,step=50_0000,
    )
    filtered = df[df['sales']>= minimum_sales].copy()
    if region != '전체':
        filtered = filtered[filtered['region']==region]

    
    ## KPI 총매출, 총판매량, 조회건수
    total_sales = filtered['sales'].sum()

    total_amount = filtered['quantity'].sum()

    total_rows = len(filtered)

    if total_rows>0:
        avg_sales=filtered['sales'].mean()
    else:
        avg_sales = 0


col1, col2, col3, col4 = st.columns(4)

with col1: st.metric(label='총 매출', value=f'{total_sales:,}원',border=True)
with col2: st.metric(label='총 판매량', value=f'{total_amount:,}개',border=True)
with col4: st.metric(label='총 조회량', value=f'{total_rows:,}',border=True)
with col3: st.metric(label='평균매출', value=f'{avg_sales:,.0f}원',border=True)

st.divider()
if filtered.empty:
    st.warning('조건에 맞는 데이터가 없습니다')
else:
    monthly_sales= filtered.groupby('month', as_index=False)['sales'].sum() #month가 인덱스로 들어감

    left, right = st.columns([3,2])

    with left: 
        st.subheader('월별매출')
        st.line_chart(monthly_sales, x='month',y='sales')
    with right:
        st.subheader('조회 데이터')
        st.dataframe(filtered,hide_index=True,column_config={'quantity':st.column_config.NumberColumn(
            '판매량',
            format='%,d개'
        ),
        'sales': st.column_config.NumberColumn(
            label='매출',format='%,d원'
        )})