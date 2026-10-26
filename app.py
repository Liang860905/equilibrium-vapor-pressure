import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 網頁基本設定
st.set_page_config(page_title="飽和蒸氣壓與動態平衡", layout="wide")

st.title("飽和蒸氣壓與動態平衡互動模擬")
st.markdown("定溫下，在密閉容器內放入水，觀察隨時間變化的**蒸發速率**、**凝結速率**與**水蒸氣粒子數（蒸氣壓）**。")

# 1. 設置連續時間滑桿
t_current = st.slider("⬅️ 拖動滑桿改變經過時間 (t)", min_value=0.0, max_value=10.0, value=0.0, step=0.1)

# 2. 數學模型設定
r_evap = 10.0  # 固定蒸發速率 (定溫下為定值)
k = 0.5        # 速率常數
t_eq = 7.0     # 設定在 t = 7.0 時視覺上完全達到平衡

# 計算當前時間點的凝結速率 (達到 t_eq 後鎖定為與蒸發速率相等)
if t_current >= t_eq:
    r_cond_current = r_evap
    status_title = "狀態 ③：r_蒸發 = r_凝結 ≠ 0 ➔ 達動態平衡"
    status_desc = "• 上方蒸氣壓力已達最大值（即為**飽和蒸氣壓**）\n• 氣相粒子數不再改變，宏觀上液面高度不變，但微觀上蒸發與凝結仍在等速進行。"
elif t_current == 0:
    r_cond_current = 0.0
    status_title = "狀態 ①：剛放入水 (t = 0)"
    status_desc = "• 一開始上方無水蒸氣粒子，僅有 **r_蒸發**\n• 單位時間蒸發的粒子數固定，因此 **r_蒸發** 為定值，此時 **r_凝結 = 0**。"
else:
    # 使曲線平滑並在 t_eq 銜接至 r_evap
    norm_factor = 1 - np.exp(-k * t_eq)
    r_cond_current = r_evap * (1 - np.exp(-k * t_current)) / norm_factor
    status_title = "狀態 ②：r_蒸發 > r_凝結 (未飽和階段)"
    status_desc = "• 空間中的水蒸氣粒子逐漸增加，蒸氣壓上升\n• 粒子碰撞液面的頻率增加，促使 **r_凝結** 隨時間變大，但仍小於 **r_蒸發**。"

# 計算當前蒸氣壓佔飽和蒸氣壓的比例 (0.0 ~ 1.0)
vapor_ratio = r_cond_current / r_evap

# 3. 顯示當前狀態資訊面板
col1, col2, col3, col4 = st.columns(4)
col1.metric("蒸發速率 (r_蒸發)", f"{r_evap:.1f}")
col2.metric("凝結速率 (r_凝結)", f"{r_cond_current:.1f}")
col3.metric("當前蒸氣壓狀態", f"{vapor_ratio * 100:.0f}% 飽和蒸氣壓")
with col4:
    st.info(f"**{status_title}**\n\n{status_desc}")

# 4. 建立雙欄互動圖表 (左：速率曲線圖 / 右：微觀密閉容器)
fig = make_subplots(
    rows=1, cols=2,
    column_widths=[0.55, 0.45],
    subplot_titles=("速率對時間關係圖 (r - t 圖)", "密閉容器微觀示意圖")
)

# --- 左圖：速率與時間關係圖 ---
t_array = np.linspace(0, 10, 200)
norm_factor = 1 - np.exp(-k * t_eq)
r_cond_array = np.where(t_array >= t_eq, r_evap, r_evap * (1 - np.exp(-k * t_array)) / norm_factor)
r_evap_array = np.full_like(t_array, r_evap)

# 繪製完整背景虛線 (代表整體趨勢)
fig.add_trace(go.Scatter(x=t_array, y=r_evap_array, mode='lines', line=dict(color='rgba(46, 139, 87, 0.25)', width=2, dash='dot'), showlegend=False), row=1, col=1)
fig.add_trace(go.Scatter(x=t_array, y=r_cond_array, mode='lines', line=dict(color='rgba(210, 105, 30, 0.25)', width=2, dash='dot'), showlegend=False), row=1, col=1)

# 繪製 0 到 t_current 的實線 (已發生的歷程)
t_past = np.linspace(0, t_current, 100)
r_cond_past = np.where(t_past >= t_eq, r_evap, r_evap * (1 - np.exp(-k * t_past)) / norm_factor)
r_evap_past = np.full_like(t_past, r_evap)

fig.add_trace(go.Scatter(x=t_past, y=r_evap_past, mode='lines', name='r_蒸發 (蒸發速率)', line=dict(color='#2E8B57', width=4)), row=1, col=1)
fig.add_trace(go.Scatter(x=t_past, y=r_cond_past, mode='lines', name='r_凝結 (凝結速率)', line=dict(color='#D2691E', width=4)), row=1, col=1)

# 繪製當前時間點的圓點與鉛直時間軸
fig.add_trace(go.Scatter(x=[t_current], y=[r_evap], mode='markers', marker=dict(color='#2E8B57', size=10), showlegend=False), row=1, col=1)
fig.add_trace(go.Scatter(x=[t_current], y=[r_cond_current], mode='markers', marker=dict(color='#D2691E', size=10), showlegend=False), row=1, col=1)
fig.add_vline(x=t_current, line_width=1.5, line_dash="dash", line_color="gray", row=1, col=1)

# 標示 ① ② ③ 階段位置
fig.add_annotation(x=0.2, y=-1.5, text="① 初態", showarrow=False, font=dict(size=13), row=1, col=1)
fig.add_annotation(x=3.5, y=-1.5, text="② 未飽和 (r_蒸發 > r_凝結)", showarrow=False, font=dict(size=13), row=1, col=1)
fig.add_annotation(x=8.5, y=-1.5, text="③ 達平衡 (r_蒸發 = r_凝結)", showarrow=False, font=dict(size=13), row=1, col=1)

# --- 右圖：密閉容器微觀粒子與速率箭頭 ---
# 1. 容器外框與蓋子
fig.add_shape(type="rect", x0=1, y0=1, x1=9, y1=9, line=dict(color="#555555", width=3), fillcolor="rgba(245,245,245,0.2)", row=1, col=2)
fig.add_shape(type="rect", x0=0.7, y0=9, x1=9.3, y1=9.3, line=dict(color="#444444", width=2), fillcolor="#777777", row=1, col=2)

# 2. 液態水 (液面隨蒸發略微下降，達平衡後維持定值)
water_level = 3.5 - 0.35 * vapor_ratio
fig.add_shape(type="rect", x0=1, y0=1, x1=9, y1=water_level, line=dict(width=0), fillcolor="rgba(135, 206, 235, 0.7)", row=1, col=2)

# 3. 氣相水蒸氣粒子 (使用固定亂數種子，使粒子隨時間逐一浮現且不亂跳)
max_particles = 45
num_particles = int( round(max_particles * vapor_ratio) )
np.random.seed(42)
px = np.random.uniform(1.4, 8.6, max_particles)
py = np.random.uniform(3.8, 8.6, max_particles)

if num_particles > 0:
    fig.add_trace(go.Scatter(
        x=px[:num_particles], y=py[:num_particles],
        mode='markers',
        name='水蒸氣粒子 H₂O(g)',
        marker=dict(color='#E69F00', size=11, line=dict(color='#8B4500', width=1))
    ), row=1, col=2)

# 4. 動態速率箭頭 (綠色向上：蒸發速率固定 / 橘色向下：凝結速率隨蒸氣壓變長)
evap_arrow_len = 3.2
# 向上蒸發箭頭 (固定長度)
fig.add_annotation(
    x=3.5, y=water_level + evap_arrow_len,
    ax=3.5, ay=water_level + 0.2,
    xref="x2", yref="y2", axref="x2", ayref="y2",
    showarrow=True, arrowhead=2, arrowsize=1.2, arrowwidth=4, arrowcolor="#2E8B57"
)
fig.add_annotation(x=3.5, y=water_level - 0.5, text="r_蒸發 (固定)", showarrow=False, font=dict(color="#2E8B57", size=13), row=1, col=2)

# 向下凝結箭頭 (長度隨凝結速率成正比)
if vapor_ratio > 0.02:
    cond_arrow_len = evap_arrow_len * vapor_ratio
    arrow_top = water_level + 0.2 + cond_arrow_len
    arrow_bottom = water_level + 0.2
    fig.add_annotation(
        x=6.5, y=arrow_bottom,
        ax=6.5, ay=arrow_top,
        xref="x2", yref="y2", axref="x2", ayref="y2",
        showarrow=True, arrowhead=2, arrowsize=1.2, arrowwidth=4, arrowcolor="#D2691E"
    )
    fig.add_annotation(x=6.5, y=water_level - 0.5, text="r_凝結 (隨蒸氣壓變大)", showarrow=False, font=dict(color="#D2691E", size=13), row=1, col=2)

# 5. 圖表版面與座標軸設定
fig.update_xaxes(title_text="時間 (t)", range=[0, 10.5], row=1, col=1)
fig.update_yaxes(title_text="速率 (r)", range=[-2, 12.5], showticklabels=False, row=1, col=1)

fig.update_xaxes(range=[0, 10], visible=False, row=1, col=2)
fig.update_yaxes(range=[0, 10.5], visible=False, row=1, col=2)

fig.update_layout(
    height=520,
    margin=dict(l=20, r=20, t=50, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)
