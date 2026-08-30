import streamlit as st
import streamlit.components.v1 as components

# 1. 網頁基本設定
st.set_page_config(layout="wide", page_title="高客製化流程圖生成器")
st.title("🛩️ 高客製化互動式流程圖網頁應用")

# 2. 初始化 Session State (確保重新整理時資料不遺失)
if "nodes" not in st.session_state:
    st.session_state.nodes = [
        {"title": "窗口送件", "desc": "單位彙整文件，送\n交通通行證辦理櫃檯", "icon": "bi-box-seam-fill", "tip": ""},
        {"title": "航警局背景審查", "desc": "國安與治安\n背景查核", "icon": "bi-search", "tip": "需時約 N 個工作天"},
        {"title": "飛安測驗", "desc": "針對初次申辦者", "icon": "bi-card-checklist", "tip": ""},
        {"title": "製證與領取", "desc": "審核通過，發放\n通行證", "icon": "bi-vcard-fill", "tip": ""}
    ]

# 3. 側邊欄：全域視覺樣式控制
st.sidebar.header("🎨 1. 全域視覺樣式調整")
circle_size = st.sidebar.slider("圓圈大小 (px)", min_value=50, max_value=120, value=75, step=5)
main_color = st.sidebar.color_picker("主線條與圓圈顏色", value="#1a65a3")
tip_color = st.sidebar.color_picker("提示氣泡顏色", value="#ffd100")

# 4. 側邊欄：動態新增與刪除節點
st.sidebar.header("➕ 2. 節點管理")
col_add, col_del = st.sidebar.columns(2)

if col_add.button("新增節點", use_container_width=True):
    st.session_state.nodes.append({"title": "新步驟", "desc": "請輸入描述內容", "icon": "bi-gear-fill", "tip": ""})
    st.rerun()

if col_del.button("刪除末端節點", use_container_width=True):
    if len(st.session_state.nodes) > 1:
        st.session_state.nodes.pop()
        st.rerun()
    else:
        st.sidebar.warning("至少需保留一個節點！")

# 5. 側邊欄：逐個節點內容與圖示編輯
st.sidebar.header("📝 3. 編輯各步驟內容")
updated_nodes = []
for i, node in enumerate(st.session_state.nodes):
    with st.sidebar.expander(f"📌 步驟 {i+1}: {node['title']}", expanded=(i==0)):
        t = st.text_input(f"標題", value=node['title'], key=f"t_{i}")
        d = st.text_area(f"描述 (可換行)", value=node['desc'], key=f"d_{i}")
        
        # 提供常用的 Bootstrap 圖示供使用者選擇
        icon_options = {
            "包裹箱 (送件)": "bi-box-seam-fill",
            "放大鏡 (審查)": "bi-search",
            "打勾清單 (測驗)": "bi-card-checklist",
            "識別證 (領取)": "bi-vcard-fill",
            "齒輪 (設定)": "bi-gear-fill",
            "使用者 (人物)": "bi-person-fill",
            "飛機 (交通)": "bi-airplane-fill",
            "文件 (檔案)": "bi-file-earmark-text-fill"
        }
        # 尋找當前圖示的中文標籤，若找不到則預設第一個
        current_label = list(icon_options.keys())[0]
        for k, v in icon_options.items():
            if v == node['icon']:
                current_label = k
        
        selected_icon_label = st.selectbox(f"選擇圓圈圖示", options=list(icon_options.keys()), index=list(icon_options.keys()).index(current_label), key=f"i_{i}")
        ico = icon_options[selected_icon_label]
        
        tp = st.text_input(f"上方提示文字 (留空則隱藏)", value=node['tip'], key=f"tp_{i}")
        updated_nodes.append({"title": t, "desc": d, "icon": ico, "tip": tp})

st.session_state.nodes = updated_nodes

# 6. 動態生成 HTML 節點字串
nodes_html = ""
num_nodes = len(st.session_state.nodes)

# 計算動態定位箭頭的 CSS 比例
arrow_css = ""

for i, node in enumerate(st.session_state.nodes):
    s_d = node['desc'].replace("\n", "<br>")
    
    # 判斷是否顯示提示氣泡
    tip_html = f'<div class="tip-bubble">{node["tip"]}</div>' if node['tip'] else ''
    
    # 生成節點
    nodes_html += f"""
    <div class="flow-node">
        {tip_html}
        <div class="node-title">{node['title']}</div>
        <div class="circle-icon"><i class="bi {node['icon']}"></i></div>
        <div class="node-desc">{s_d}</div>
    </div>
    """
    
    # 如果不是最後一個節點，生成右側箭頭
    if i < num_nodes - 1:
        # 計算箭頭應該放置的百分比位置
        left_percent = ((i + 0.65) / (num_nodes - 0.3)) * 100
        arrow_css += f"""
        .arrow-{i} {{ left: {left_percent}%; }}
        """
        nodes_html += f"""
        <div class="flow-arrow arrow-{i}"><i class="bi bi-chevron-right"></i></div>
        """

# 7. 封裝完整 HTML 範本 (包含 html2canvas 下載功能)
html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://jsdelivr.net">
    <!-- 引入 html2canvas 用於將網頁區塊轉為圖片 -->
    <script src="https://cloudflare.com"></script>
    <style>
        body {{
            font-family: "Microsoft JhengHei", sans-serif;
            background-color: #f8f9fa;
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        /* 下載按鈕設計 */
        .download-btn {{
            background-color: #28a745;
            color: white;
            font-size: 16px;
            font-weight: bold;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: 0.2s;
        }}
        .download-btn:hover {{
            background-color: #218838;
        }}
        /* 整個要被打包下載的畫布區塊 */
        .capture-area {{
            background-color: #f8f9fa;
            padding: 40px 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
        }}
        .title-board {{
            background-color: #222;
            color: white;
            font-size: 28px;
            font-weight: bold;
            padding: 12px 40px;
            border-radius: 6px;
            border: 3px solid white;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            margin-bottom: 80px;
            letter-spacing: 2px;
        }}
        .flow-container {{
            position: relative;
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            width: 95%;
            padding-top: 40px;
        }}
        .main-line {{
            position: absolute;
            top: calc({circle_size}px / 2 + 55px);
            left: 0;
            right: 0;
            height: 12px;
            background-color: {main_color};
            z-index: 1;
        }}
        .flow-node {{
            position: relative;
            display: flex;
            flex-direction: column;
            align-items: center;
            width: calc(100% / {num_nodes});
            z-index: 2;
        }}
        .node-title {{
            font-size: 18px;
            font-weight: bold;
            color: #111;
            margin-bottom: 15px;
            text-align: center;
            height: 25px;
        }}
        /* 動態圓圈大小與全域顏色設定 */
        .circle-icon {{
            width: {circle_size}px;
            height: {circle_size}px;
            background-color: {main_color};
            border: 4px solid #fff;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            box-shadow: 0 0 0 4px {main_color};
            color: white;
            font-size: calc({circle_size}px * 0.42);
            margin-bottom: 25px;
        }}
        .node-desc {{
            font-size: 14px;
            color: #333;
            text-align: center;
            line-height: 1.5;
            font-weight: 500;
        }}
        .flow-arrow {{
            position: absolute;
            top: calc({circle_size}px / 2 + 37px);
            font-size: 32px;
            color: {main_color};
            z-index: 3;
        }}
        {arrow_css}

        /* 提示氣泡與顏色設定 */
        .tip-bubble {{
            position: absolute;
            top: -45px;
            background-color: {tip_color};
            color: black;
            font-size: 13px;
            font-weight: bold;
            padding: 6px 14px;
            border-radius: 20px;
            white-space: nowrap;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .tip-bubble::after {{
            content: "";
            position: absolute;
            bottom: -6px;
            left: 50%;
            transform: translateX(-50%);
            border-width: 6px 6px 0;
            border-style: solid;
            border-color: {tip_color} transparent;
            display: block;
            width: 0;
        }}
    </style>
</head>
<body>

    <!-- 下載按鈕 (點擊觸發 html2canvas 截圖並下載) -->
    <button class="download-btn" onclick="downloadFlowchart()">💾 匯出流程圖為圖片 (PNG)</button>

    <div class="capture-area" id="flowchart-zone">
        <div class="title-board">申辦航線圖：從送件到領證</div>
        
        <div class="flow-container">
            <div class="main-line"></div>
            {nodes_html}
        </div>
    </div>

    <script>
        function downloadFlowchart() {{
            const element = document.getElementById('flowchart-zone');
            // 使用 html2canvas 捕捉區塊，提高 scale 可增加圖片解析度
            html2canvas(element, {{ scale: 2, useCORS: true }}).then(canvas => {{
                const link = document.createElement('a');
                link.download = 'flowchart.png';
                link.href = canvas.toDataURL('image/png');
                link.click();
            }});
        }}
    </script>

</body>
</html>
"""

# 8. 將最終成品渲染至 Streamlit 畫面中 (動態調整高度防止邊界被切到)
components.html(html_template, height=600, scrolling=True)

st.success("💡 操作指南：可在左側隨時調色、控大控制大小、新增節點；滿意後點擊上方的綠色按鈕即可將成品存為 PNG 檔案！")
