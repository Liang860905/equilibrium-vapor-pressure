import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="飽和蒸氣壓與動態平衡", layout="wide")

st.title("飽和蒸氣壓：蒸發與凝結粒子動態模擬")
st.markdown("透過拖動下方滑桿或點擊自動播放，觀察**水蒸氣粒子飛出液面（蒸發）**與**撞擊液面返回水中（凝結）**的實體動態過程。")

html_code = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        margin: 0;
        padding: 12px;
        background-color: #ffffff;
        color: #1f2937;
    }
    .control-panel {
        background: #f8fafc;
        padding: 16px 20px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 16px;
        flex-wrap: wrap;
    }
    .btn {
        background: #2563eb;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 600;
        cursor: pointer;
        font-size: 14px;
        transition: background 0.15s;
    }
    .btn:hover { background: #1d4ed8; }
    .btn-reset { background: #64748b; }
    .btn-reset:hover { background: #475569; }
    .slider-wrap {
        flex-grow: 1;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    input[type=range] {
        flex-grow: 1;
        height: 6px;
        cursor: pointer;
        accent-color: #2563eb;
    }
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-bottom: 16px;
    }
    .metric-card {
        background: #ffffff;
        padding: 12px 16px;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .metric-title { font-size: 13px; color: #64748b; margin-bottom: 4px; font-weight: 600; }
    .metric-value { font-size: 22px; font-weight: 700; }
    .status-banner {
        grid-column: span 4;
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 14px;
        line-height: 1.5;
        background: #eff6ff;
        border-left: 5px solid #2563eb;
    }
    .canvas-grid {
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
    }
    .canvas-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .box-title {
        font-size: 15px;
        font-weight: 700;
        color: #334155;
        margin-bottom: 8px;
    }
    .legend-bar {
        display: flex;
        gap: 18px;
        font-size: 13px;
        color: #475569;
        margin-top: 8px;
    }
    .dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 5px; }
</style>
</head>
<body>

<div class="control-panel">
    <button id="playBtn" class="btn">⏸ 暫停時間推進</button>
    <button id="resetBtn" class="btn btn-reset">🔄 重置 (t = 0)</button>
    <div class="slider-wrap">
        <span style="font-weight: 600; font-size: 14px;">拉動時間軸 (t)：</span>
        <input type="range" id="timeSlider" min="0" max="10" step="0.05" value="0">
        <span id="timeLabel" style="font-weight: 700; min-width: 55px; color: #2563eb;">0.0 s</span>
    </div>
</div>

<div class="metrics-grid">
    <div class="metric-card">
        <div class="metric-title">蒸發速率 (r_蒸發)</div>
        <div class="metric-value" style="color: #16a34a;">10.0 <span style="font-size:13px;font-weight:normal;">(定溫固定)</span></div>
    </div>
    <div class="metric-card">
        <div class="metric-title">凝結速率 (r_凝結)</div>
        <div class="metric-value" id="rCondVal" style="color: #ea580c;">0.0</div>
    </div>
    <div class="metric-card">
        <div class="metric-title">氣相水蒸氣粒子數</div>
        <div class="metric-value" id="pCountVal" style="color: #d97706;">0 / 45</div>
    </div>
    <div class="metric-card">
        <div class="metric-title">蒸氣壓狀態</div>
        <div class="metric-value" id="pressureVal" style="color: #2563eb;">0% 飽和</div>
    </div>
    <div class="status-banner" id="statusBanner"></div>
</div>

<div class="canvas-grid">
    <div class="canvas-box" style="flex: 1.15; min-width: 420px;">
        <div class="box-title">速率對時間關係圖 (r - t 圖)</div>
        <canvas id="graphCanvas" width="480" height="360"></canvas>
    </div>
    <div class="canvas-box" style="flex: 1; min-width: 380px;">
        <div class="box-title">密閉容器微觀粒子動態 (60 FPS 實體碰撞)</div>
        <canvas id="beakerCanvas" width="400" height="360"></canvas>
        <div class="legend-bar">
            <span><span class="dot" style="background:#f59e0b; border:1px solid #b45309;"></span>氣相水蒸氣 H₂O(g)</span>
            <span><span class="dot" style="background:#16a34a;"></span>正從液面蒸發 (向上跳出)</span>
            <span><span class="dot" style="background:#ea580c;"></span>碰撞液面凝結 (沒入水中)</span>
        </div>
    </div>
</div>

<script>
const slider = document.getElementById('timeSlider');
const timeLabel = document.getElementById('timeLabel');
const playBtn = document.getElementById('playBtn');
const resetBtn = document.getElementById('resetBtn');
const rCondVal = document.getElementById('rCondVal');
const pCountVal = document.getElementById('pCountVal');
const pressureVal = document.getElementById('pressureVal');
const statusBanner = document.getElementById('statusBanner');

const gCanvas = document.getElementById('graphCanvas');
const gCtx = gCanvas.getContext('2d');
const bCanvas = document.getElementById('beakerCanvas');
const bCtx = bCanvas.getContext('2d');

let t = 0.0;
let isPlaying = true; // 預設自動開始推進，立刻看到蒸發與粒子運動
const r_evap = 10.0;
const t_eq = 7.0;
const k = 0.45;
const norm = 1 - Math.exp(-k * t_eq);
const maxGasParticles = 45;

// 容器幾何座標
const B_LEFT = 60, B_RIGHT = 340, B_TOP = 35, B_BOTTOM = 330;

// 計算特定時間的凝結速率
function getRCond(time) {
    if (time <= 0) return 0;
    if (time >= t_eq) return r_evap;
    return r_evap * (1 - Math.exp(-k * time)) / norm;
}

// 液態水背景粒子 (在水面下緩慢游動)
let liquidParticles = [];
for (let i = 0; i < 65; i++) {
    liquidParticles.push({
        x: B_LEFT + 10 + Math.random() * (B_RIGHT - B_LEFT - 20),
        y: 235 + Math.random() * (B_BOTTOM - 245),
        vx: (Math.random() - 0.5) * 0.8,
        vy: (Math.random() - 0.5) * 0.8
    });
}

// 氣相水蒸氣粒子與視覺特效陣列
let gasParticles = [];
let effects = []; // 儲存蒸發跳出與凝結落入的動態漣漪與箭頭

function spawnGasParticle(fromSurface = true, waterY = 230) {
    const x = B_LEFT + 20 + Math.random() * (B_RIGHT - B_LEFT - 40);
    const y = fromSurface ? waterY - 4 : B_TOP + 20 + Math.random() * (waterY - B_TOP - 40);
    const angle = -Math.PI / 4 - Math.random() * (Math.PI / 2); // 向上扇形角度飛出
    const speed = 2.2 + Math.random() * 1.3;
    gasParticles.push({
        x: x,
        y: y,
        vx: fromSurface ? Math.cos(angle) * speed : (Math.random() - 0.5) * 3.5,
        vy: fromSurface ? Math.sin(angle) * speed : (Math.random() - 0.5) * 3.5,
        highlightGreen: fromSurface ? 28 : 0 // 剛蒸發時呈現綠色高亮
    });
    if (fromSurface) {
        effects.push({ x: x, y: waterY, type: 'evap', age: 0, maxAge: 28 });
    }
}

function triggerCondensation(waterY) {
    if (gasParticles.length === 0) return;
    // 尋找最接近水面的氣體粒子讓它凝結沒入水中
    let bestIdx = 0;
    let maxY = -1;
    for (let i = 0; i < gasParticles.length; i++) {
        if (gasParticles[i].y > maxY) {
            maxY = gasParticles[i].y;
            bestIdx = i;
        }
    }
    const p = gasParticles[bestIdx];
    effects.push({ x: p.x, y: waterY, type: 'cond', age: 0, maxAge: 28 });
    gasParticles.splice(bestIdx, 1);
}

// 事件綁定
slider.addEventListener('input', (e) => {
    t = parseFloat(e.target.value);
    isPlaying = false;
    playBtn.textContent = "▶ 繼續時間推進";
});

playBtn.addEventListener('click', () => {
    isPlaying = !isPlaying;
    if (isPlaying && t >= 10) t = 0;
    playBtn.textContent = isPlaying ? "⏸ 暫停時間推進" : "▶ 繼續時間推進";
});

resetBtn.addEventListener('click', () => {
    t = 0;
    slider.value = 0;
    gasParticles = [];
    effects = [];
    isPlaying = false;
    playBtn.textContent = "▶ 開始時間推進";
});

// 更新上方數據與狀態說明
function updateMetrics(r_cond, ratio, waterY) {
    timeLabel.textContent = t.toFixed(1) + " s";
    rCondVal.textContent = r_cond.toFixed(1);
    const targetCount = Math.round(maxGasParticles * ratio);
    pCountVal.textContent = `${targetCount} / ${maxGasParticles}`;
    pressureVal.textContent = `${Math.round(ratio * 100)}% 飽和`;

    if (t === 0) {
        statusBanner.style.borderLeftColor = "#16a34a";
        statusBanner.style.background = "#f0fdf4";
        statusBanner.innerHTML = "<b>狀態 ①：初始狀態 (t = 0)</b> — 上方空間尚無水蒸氣粒子（蒸氣壓 = 0），此時僅有水分子從液面飛出（<b>r_蒸發 > 0，r_凝結 = 0</b>）。";
    } else if (t < t_eq) {
        statusBanner.style.borderLeftColor = "#d97706";
        statusBanner.style.background = "#fffbeb";
        statusBanner.innerHTML = "<b>狀態 ②：未飽和階段 (r_蒸發 > r_凝結)</b> — 氣相粒子數逐漸變多（蒸氣壓變大），粒子撞回液面凝結的頻率隨之上升，但蒸發仍快於凝結。";
    } else {
        statusBanner.style.borderLeftColor = "#2563eb";
        statusBanner.style.background = "#eff6ff";
        statusBanner.innerHTML = "<b>狀態 ③：達動態平衡 (r_蒸發 = r_凝結 ≠ 0)</b> — <b>每當有 1 顆水分子蒸發飛出，同時就有 1 顆水蒸氣撞擊液面凝結！</b>氣相粒子總數維持 45 顆不變，此時壓力即為<b>飽和蒸氣壓</b>。";
    }
}

// 繪製左側速率曲線圖
function drawGraph(r_cond) {
    gCtx.clearRect(0, 0, gCanvas.width, gCanvas.height);
    const ox = 55, oy = 305, w = 390, h = 250;

    // 座標軸
    gCtx.strokeStyle = "#334155";
    gCtx.lineWidth = 2;
    gCtx.beginPath();
    gCtx.moveTo(ox, oy - h - 15);
    gCtx.lineTo(ox, oy);
    gCtx.lineTo(ox + w + 15, oy);
    gCtx.stroke();

    gCtx.fillStyle = "#334155";
    gCtx.font = "bold 13px sans-serif";
    gCtx.fillText("速率 (r)", 12, 35);
    gCtx.fillText("時間 (t)", ox + w - 25, oy + 32);

    // 階段分界虛線
    const eqX = ox + (t_eq / 10) * w;
    gCtx.setLineDash([4, 4]);
    gCtx.strokeStyle = "#cbd5e1";
    gCtx.beginPath();
    gCtx.moveTo(eqX, oy - h);
    gCtx.lineTo(eqX, oy);
    gCtx.stroke();
    gCtx.setLineDash([]);

    gCtx.fillStyle = "#64748b";
    gCtx.font = "12px sans-serif";
    gCtx.fillText("① t=0", ox - 10, oy + 20);
    gCtx.fillText("② r_蒸發 > r_凝結", ox + 95, oy + 20);
    gCtx.fillText("③ 達動態平衡", eqX + 18, oy + 20);

    // 背景完整趨勢淡線
    const evapY = oy - (r_evap / 12) * h;
    gCtx.strokeStyle = "rgba(22, 163, 74, 0.2)";
    gCtx.lineWidth = 3;
    gCtx.beginPath();
    gCtx.moveTo(ox, evapY);
    gCtx.lineTo(ox + w, evapY);
    gCtx.stroke();

    gCtx.strokeStyle = "rgba(234, 88, 12, 0.2)";
    gCtx.beginPath();
    for (let i = 0; i <= 100; i++) {
        let ti = (i / 100) * 10;
        let rc = getRCond(ti);
        let px = ox + (ti / 10) * w;
        let py = oy - (rc / 12) * h;
        if (i === 0) gCtx.moveTo(px, py);
        else gCtx.lineTo(px, py);
    }
    gCtx.stroke();

    // 繪製 0 ~ t 的實線軌跡
    const curX = ox + (t / 10) * w;
    gCtx.strokeStyle = "#16a34a";
    gCtx.lineWidth = 3.5;
    gCtx.beginPath();
    gCtx.moveTo(ox, evapY);
    gCtx.lineTo(curX, evapY);
    gCtx.stroke();

    gCtx.strokeStyle = "#ea580c";
    gCtx.lineWidth = 3.5;
    gCtx.beginPath();
    const steps = Math.max(2, Math.floor(t * 15));
    for (let i = 0; i <= steps; i++) {
        let ti = (i / steps) * t;
        let rc = getRCond(ti);
        let px = ox + (ti / 10) * w;
        let py = oy - (rc / 12) * h;
        if (i === 0) gCtx.moveTo(px, py);
        else gCtx.lineTo(px, py);
    }
    gCtx.stroke();

    // 當前時間鉛直線與端點
    const condY = oy - (r_cond / 12) * h;
    gCtx.setLineDash([3, 3]);
    gCtx.strokeStyle = "#94a3b8";
    gCtx.lineWidth = 1.5;
    gCtx.beginPath();
    gCtx.moveTo(curX, oy - h);
    gCtx.lineTo(curX, oy);
    gCtx.stroke();
    gCtx.setLineDash([]);

    gCtx.fillStyle = "#16a34a";
    gCtx.beginPath(); gCtx.arc(curX, evapY, 6, 0, Math.PI * 2); gCtx.fill();
    gCtx.fillText("r_蒸發", ox + w - 42, evapY - 10);

    gCtx.fillStyle = "#ea580c";
    gCtx.beginPath(); gCtx.arc(curX, condY, 6, 0, Math.PI * 2); gCtx.fill();
    gCtx.fillText("r_凝結", ox + w - 42, evapY + 20);
}

// 繪製箭頭輔助函式
function drawVectorArrow(ctx, x1, y1, x2, y2, color, label) {
    const headlen = 10;
    const angle = Math.atan2(y2 - y1, x2 - x1);
    ctx.strokeStyle = color;
    ctx.fillStyle = color;
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(x2, y2);
    ctx.lineTo(x2 - headlen * Math.cos(angle - Math.PI / 6), y2 - headlen * Math.sin(angle - Math.PI / 6));
    ctx.lineTo(x2 - headlen * Math.cos(angle + Math.PI / 6), y2 - headlen * Math.sin(angle + Math.PI / 6));
    ctx.closePath();
    ctx.fill();

    ctx.font = "bold 12px sans-serif";
    ctx.fillText(label, x1 - 22, Math.max(y1, y2) + 18);
}

// 繪製右側密閉容器與動態粒子
function drawBeaker(r_cond, ratio) {
    bCtx.clearRect(0, 0, bCanvas.width, bCanvas.height);

    // 液面高度隨蒸發略微下降，達平衡後維持不變
    const waterY = 225 + ratio * 14;

    // 1. 調整氣體粒子數量以符合當前時間點
    const targetGasCount = Math.round(maxGasParticles * ratio);
    while (gasParticles.length < targetGasCount) {
        spawnGasParticle(true, waterY);
    }
    while (gasParticles.length > targetGasCount) {
        gasParticles.pop();
    }

    // 2. 定期觸發「蒸發飛出 + 凝結落入」的實體交換動畫 (即使達平衡後仍持續發生！)
    if (Math.random() < 0.085) {
        const condProb = ratio; // 凝結發生機率與當前蒸氣壓成正比
        if (Math.random() < condProb && gasParticles.length > 0) {
            // 發生一顆凝結，同時補一顆蒸發，完美呈現動態平衡 r_蒸發 = r_凝結
            triggerCondensation(waterY);
            spawnGasParticle(true, waterY);
        } else if (t > 0) {
            // 未飽和時，單純展示水分子從液面跳出並落回的微觀交換
            effects.push({
                x: B_LEFT + 25 + Math.random() * (B_RIGHT - B_LEFT - 50),
                y: waterY,
                type: 'evap',
                age: 0,
                maxAge: 25
            });
        }
    }

    // 3. 繪製液態水區域
    bCtx.fillStyle = "rgba(56, 189, 248, 0.35)";
    bCtx.fillRect(B_LEFT, waterY, B_RIGHT - B_LEFT, B_BOTTOM - waterY);

    // 液面波紋線
    bCtx.strokeStyle = "#0284c7";
    bCtx.lineWidth = 2.5;
    bCtx.beginPath();
    bCtx.moveTo(B_LEFT, waterY);
    bCtx.lineTo(B_RIGHT, waterY);
    bCtx.stroke();

    // 4. 更新並繪製水中水分子 (藍色微粒緩慢熱運動)
    bCtx.fillStyle = "rgba(2, 132, 199, 0.45)";
    for (let lp of liquidParticles) {
        lp.x += lp.vx;
        lp.y += lp.vy;
        if (lp.x < B_LEFT + 8 || lp.x > B_RIGHT - 8) lp.vx *= -1;
        if (lp.y < waterY + 8) { lp.y = waterY + 8; lp.vy = Math.abs(lp.vy); }
        if (lp.y > B_BOTTOM - 8) { lp.y = B_BOTTOM - 8; lp.vy = -Math.abs(lp.vy); }
        bCtx.beginPath();
        bCtx.arc(lp.x, lp.y, 4, 0, Math.PI * 2);
        bCtx.fill();
    }

    // 5. 繪製宏觀速率對比箭頭 (半透明背景參考)
    const arrowLen = 75;
    drawVectorArrow(bCtx, 135, waterY - 8, 135, waterY - 8 - arrowLen, "rgba(22, 163, 74, 0.75)", "r_蒸發");
    if (ratio > 0.02) {
        const cLen = arrowLen * ratio;
        drawVectorArrow(bCtx, 265, waterY - 8 - cLen, 265, waterY - 8, "rgba(234, 88, 12, 0.75)", "r_凝結");
    }

    // 6. 更新並繪製氣相水蒸氣粒子 (60 FPS 碰撞器壁與液面)
    for (let p of gasParticles) {
        p.x += p.vx;
        p.y += p.vy;

        // 碰撞左右器壁反彈
        if (p.x < B_LEFT + 7) { p.x = B_LEFT + 7; p.vx *= -1; }
        if (p.x > B_RIGHT - 7) { p.x = B_RIGHT - 7; p.vx *= -1; }
        // 碰撞頂部密封蓋反彈 (產生蒸氣壓！)
        if (p.y < B_TOP + 7) { p.y = B_TOP + 7; p.vy *= -1; }

        // 碰撞底部水面：有機率觸發「凝結沒入水中，同時另一處蒸發飛出」
        if (p.y > waterY - 7) {
            if (Math.random() < 0.35 * ratio) {
                // 粒子撞進水面凝結
                effects.push({ x: p.x, y: waterY, type: 'cond', age: 0, maxAge: 28 });
                // 同時從水面另一處蒸發出一顆新粒子 (維持動態平衡數目)
                p.x = B_LEFT + 20 + Math.random() * (B_RIGHT - B_LEFT - 40);
                p.y = waterY - 6;
                p.vx = (Math.random() - 0.5) * 3.5;
                p.vy = -(2.0 + Math.random() * 1.5);
                p.highlightGreen = 26;
                effects.push({ x: p.x, y: waterY, type: 'evap', age: 0, maxAge: 28 });
            } else {
                p.y = waterY - 7;
                p.vy = -Math.abs(p.vy);
            }
        }

        // 繪製氣體粒子 (剛蒸發時外圍發綠光，平時為橘黃色小球)
        bCtx.beginPath();
        bCtx.arc(p.x, p.y, 6, 0, Math.PI * 2);
        if (p.highlightGreen > 0) {
            bCtx.fillStyle = "#22c55e";
            bCtx.strokeStyle = "#15803d";
            p.highlightGreen--;
        } else {
            bCtx.fillStyle = "#f59e0b";
            bCtx.strokeStyle = "#b45309";
        }
        bCtx.lineWidth = 1.5;
        bCtx.fill();
        bCtx.stroke();
    }

    // 7. 繪製水面上的「蒸發躍出」與「凝結沒入」瞬時漣漪與小箭頭特效
    for (let i = effects.length - 1; i >= 0; i--) {
        let ef = effects[i];
        ef.age++;
        let alpha = 1 - ef.age / ef.maxAge;
        if (ef.type === 'evap') {
            // 綠色向上小箭頭與水面漣漪
            bCtx.strokeStyle = `rgba(22, 163, 74, ${alpha})`;
            bCtx.fillStyle = `rgba(22, 163, 74, ${alpha})`;
            bCtx.lineWidth = 2;
            bCtx.beginPath();
            bCtx.ellipse(ef.x, ef.y, ef.age * 0.6, ef.age * 0.2, 0, 0, Math.PI * 2);
            bCtx.stroke();
            bCtx.font = "bold 11px sans-serif";
            bCtx.fillText("↑蒸發", ef.x - 14, ef.y - ef.age * 0.9);
        } else {
            // 橘紅色向下沒入水中的粒子與漣漪
            bCtx.strokeStyle = `rgba(234, 88, 12, ${alpha})`;
            bCtx.fillStyle = `rgba(234, 88, 12, ${alpha})`;
            bCtx.lineWidth = 2;
            bCtx.beginPath();
            bCtx.ellipse(ef.x, ef.y, ef.age * 0.6, ef.age * 0.2, 0, 0, Math.PI * 2);
            bCtx.stroke();
            bCtx.beginPath();
            bCtx.arc(ef.x, ef.y + ef.age * 0.7, 5, 0, Math.PI * 2);
            bCtx.fill();
            bCtx.font = "bold 11px sans-serif";
            bCtx.fillText("↓凝結", ef.x - 14, ef.y + ef.age * 0.7 + 14);
        }
        if (ef.age >= ef.maxAge) effects.splice(i, 1);
    }

    // 8. 繪製密閉容器厚玻璃外框與頂部密封蓋
    bCtx.strokeStyle = "#475569";
    bCtx.lineWidth = 4;
    bCtx.strokeRect(B_LEFT, B_TOP, B_RIGHT - B_LEFT, B_BOTTOM - B_TOP);

    // 密封蓋
    bCtx.fillStyle = "#64748b";
    bCtx.fillRect(B_LEFT - 12, B_TOP - 10, (B_RIGHT - B_LEFT) + 24, 10);
}

// 主動畫迴圈 (60 FPS)
function animate() {
    if (isPlaying) {
        t += 0.015;
        if (t > 10) {
            t = 10;
            isPlaying = false;
            playBtn.textContent = "▶ 重新播放時間推進";
        }
        slider.value = t;
    }

    const r_cond = getRCond(t);
    const ratio = r_cond / r_evap;

    updateMetrics(r_cond, ratio);
    drawGraph(r_cond);
    drawBeaker(r_cond, ratio);

    requestAnimationFrame(animate);
}

animate();
</script>
</body>
</html>
"""

# 將 HTML5 Canvas 物理引擎嵌入 Streamlit
components.html(html_code, height=620, scrolling=False)
