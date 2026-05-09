import json
import requests
import streamlit as st
import textwrap

# 初始化会话
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "is_loading" not in st.session_state:
    st.session_state.is_loading = False
if "input_value" not in st.session_state:
    st.session_state.input_value = ""

MODEL_URL = "https://api.deepseek.com/chat/completions"

# 烟品研发数据（真实数据）
PRODUCT_DATA = {
    "烟品特征表": [
        {
            "烟品ID": "A01",
            "品牌": "中华（硬）",
            "香型": "烤烟",
            "烟支规格": "常规（84mm）",
            "焦油量": "10mg",
            "爆珠": "无",
            "滤嘴": "普通",
            "包装": "硬盒"
        },
        {
            "烟品ID": "A02",
            "品牌": "玉溪（软）",
            "香型": "烤烟",
            "烟支规格": "常规",
            "焦油量": "8mg",
            "爆珠": "无",
            "滤嘴": "普通",
            "包装": "软包"
        },
        {
            "烟品ID": "A03",
            "品牌": "南京（十二钗）",
            "香型": "烤烟 + 薄荷",
            "烟支规格": "细支",
            "焦油量": "6mg",
            "爆珠": "薄荷爆珠",
            "滤嘴": "复合",
            "包装": "硬盒"
        },
        {
            "烟品ID": "A04",
            "品牌": "芙蓉王（硬）",
            "香型": "烤烟",
            "烟支规格": "常规",
            "焦油量": "11mg",
            "爆珠": "无",
            "滤嘴": "普通",
            "包装": "硬盒"
        },
        {
            "烟品ID": "A05",
            "品牌": "利群（新版）",
            "香型": "烤烟",
            "烟支规格": "常规",
            "焦油量": "10mg",
            "爆珠": "无",
            "滤嘴": "普通",
            "包装": "硬盒"
        },
        {
            "烟品ID": "A06",
            "品牌": "云烟（细支珍品）",
            "香型": "烤烟 + 清甜",
            "烟支规格": "细支",
            "焦油量": "6mg",
            "爆珠": "无",
            "滤嘴": "甜感滤嘴",
            "包装": "硬盒"
        },
        {
            "烟品ID": "A07",
            "品牌": "娇子（宽窄好运）",
            "香型": "烤烟 + 果味",
            "烟支规格": "细支",
            "焦油量": "5mg",
            "爆珠": "川贝枇杷爆珠",
            "滤嘴": "复合",
            "包装": "镭射硬盒"
        },
        {
            "烟品ID": "A08",
            "品牌": "红塔山（经典1956）",
            "香型": "烤烟",
            "烟支规格": "常规",
            "焦油量": "10mg",
            "爆珠": "无",
            "滤嘴": "普通",
            "包装": "软包"
        }
    ],
    "分城市定价表": [
        {
            "烟品ID": "A01",
            "城市": "北京 / 上海",
            "零售价(元/包)": 45,
            "价格档位": "高端（30+）"
        },
        {
            "烟品ID": "A01",
            "城市": "成都 / 武汉",
            "零售价(元/包)": 42,
            "价格档位": "中高端"
        },
        {
            "烟品ID": "A02",
            "城市": "全国均价",
            "零售价(元/包)": 23,
            "价格档位": "中端（20–30）"
        },
        {
            "烟品ID": "A03",
            "城市": "南京 / 上海",
            "零售价(元/包)": 26,
            "价格档位": "中端"
        },
        {
            "烟品ID": "A04",
            "城市": "广州 / 深圳",
            "零售价(元/包)": 25,
            "价格档位": "中端"
        },
        {
            "烟品ID": "A05",
            "城市": "杭州 / 宁波",
            "零售价(元/包)": 19,
            "价格档位": "普一类（10–20）"
        },
        {
            "烟品ID": "A06",
            "城市": "全国均价",
            "零售价(元/包)": 26,
            "价格档位": "中端"
        },
        {
            "烟品ID": "A07",
            "城市": "成都 / 重庆",
            "零售价(元/包)": 26,
            "价格档位": "中端"
        },
        {
            "烟品ID": "A08",
            "城市": "县城 / 乡镇",
            "零售价(元/包)": 7,
            "价格档位": "低端（<10）"
        }
    ],
    "分城市销量表": [
        {
            "烟品ID": "A01",
            "城市": "上海",
            "月销量(万包)": 120,
            "同比增速": "-5%",
            "渗透率": "18%"
        },
        {
            "烟品ID": "A02",
            "城市": "昆明",
            "月销量(万包)": 95,
            "同比增速": "+8%",
            "渗透率": "25%"
        },
        {
            "烟品ID": "A03",
            "城市": "南京",
            "月销量(万包)": 80,
            "同比增速": "+22%",
            "渗透率": "30%"
        },
        {
            "烟品ID": "A04",
            "城市": "长沙",
            "月销量(万包)": 85,
            "同比增速": "+5%",
            "渗透率": "22%"
        },
        {
            "烟品ID": "A05",
            "城市": "杭州",
            "月销量(万包)": 110,
            "同比增速": "+12%",
            "渗透率": "28%"
        },
        {
            "烟品ID": "A06",
            "城市": "广州",
            "月销量(万包)": 75,
            "同比增速": "+18%",
            "渗透率": "20%"
        },
        {
            "烟品ID": "A07",
            "城市": "成都",
            "月销量(万包)": 65,
            "同比增速": "+25%",
            "渗透率": "24%"
        },
        {
            "烟品ID": "A08",
            "城市": "河南县城",
            "月销量(万包)": 200,
            "同比增速": "+16%",
            "渗透率": "45%"
        }
    ],
    "分渠道销量表": [
        {
            "渠道类型": "便利店",
            "主要烟品": "A01, A05, A08",
            "月销量占比": "35%",
            "同比增速": "+5%",
            "用户特征": "年轻白领、学生，注重便利性"
        },
        {
            "渠道类型": "烟酒店",
            "主要烟品": "A02, A03, A06",
            "月销量占比": "40%",
            "同比增速": "+8%",
            "用户特征": "中年男性，注重品质和口感"
        },
        {
            "渠道类型": "超市",
            "主要烟品": "A04, A05, A07",
            "月销量占比": "15%",
            "同比增速": "+10%",
            "用户特征": "家庭主妇、中老年人，注重性价比"
        },
        {
            "渠道类型": "线上平台",
            "主要烟品": "A03, A06, A07",
            "月销量占比": "10%",
            "同比增速": "+25%",
            "用户特征": "年轻群体，注重创新和体验"
        }
    ],
    "用户画像表": [
        {
            "年龄段": "18–25",
            "性别": "男",
            "城市层级": "新一线 / 二线",
            "消费档位": "普一类",
            "偏好香型": "薄荷 / 果味爆珠",
            "偏好规格": "细支 > 中支",
            "可接受价格(元)": "10–25"
        },
        {
            "年龄段": "18–25",
            "性别": "女",
            "城市层级": "一线 / 新一线",
            "消费档位": "中端",
            "偏好香型": "清甜 / 水果爆珠",
            "偏好规格": "细支（必选）",
            "可接受价格(元)": "18–30"
        },
        {
            "年龄段": "26–35",
            "性别": "男",
            "城市层级": "一线 / 新一线",
            "消费档位": "中端",
            "偏好香型": "本香烤烟",
            "偏好规格": "中支 > 常规",
            "可接受价格(元)": "20–35"
        },
        {
            "年龄段": "26–35",
            "性别": "女",
            "城市层级": "二线 / 省会",
            "消费档位": "普一类",
            "偏好香型": "薄荷爆珠",
            "偏好规格": "细支",
            "可接受价格(元)": "15–25"
        },
        {
            "年龄段": "36–50",
            "性别": "男",
            "城市层级": "全层级",
            "消费档位": "普一类 / 低端",
            "偏好香型": "浓香型烤烟",
            "偏好规格": "常规",
            "可接受价格(元)": "7–20"
        },
        {
            "年龄段": "50+",
            "性别": "男",
            "城市层级": "三四线 / 县城",
            "消费档位": "低端",
            "偏好香型": "传统烤烟",
            "偏好规格": "常规",
            "可接受价格(元)": "5–12"
        }
    ]
}

def get_ai_answer(question, api_key):
    # 使用 dedent 去除多余缩进
    prompt = textwrap.dedent(f"""
        你是一个专业的烟品研发分析师。请针对用户的具体问题进行精准分析，禁止输出无关内容。
        
        【核心要求】
        1. 只分析用户问题中提到的具体人群、烟品特征和销量数据
        2. 禁止输出其他无关数据
        3. 严格按照六大模块格式输出
        4. 禁止在分析中直接引用具体的用户ID（如"用户001"、"用户002"）或烟品ID（如"A01"、"A02"）
        5. 使用百分比、占比、趋势等宏观描述来呈现分析结果，而不是列举具体案例
        6. 基于数据整体趋势和规律进行分析，而不是基于个别案例
        7. 在分析中引用数据时，使用品牌名称（如"中华（硬）"、"玉溪（软）"）而非烟品ID
        
        【格式约束】
        1. 必须使用 Markdown 粗体格式作为标题（例如：**一、目标人群/市场特征分析**）。
        2. 标题后必须紧跟一个空行。
        3. 内容输出从标题后的第一行开始，段落间无多余空行。
        4. 模块间保持一个空行。
        
        【输出模板】
        **一、目标人群/市场/渠道特征分析**

        [分析用户问题中提到的人群、市场或渠道特征，使用宏观描述而非具体案例]

        **二、烟品特征偏好分析**

        [分析用户问题中提到的烟品特征偏好，使用百分比、占比等宏观描述]

        **三、销量表现分析**

        [分析用户问题中提到的销量数据，使用趋势、对比等宏观描述]

        **四、市场机会与竞争分析**

        [分析用户问题中提到的市场机会与竞争，使用宏观描述]

        **五、新品特征/渠道策略建议**

        [基于数据提出新品特征或渠道策略建议，使用宏观描述]

        **六、研发/营销风险与应对**

        [分析研发或营销风险与应对策略，使用宏观描述]

        用户提问：{question}
        烟品研发数据：{json.dumps(PRODUCT_DATA, ensure_ascii=False, indent=2)}
        """)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0
    }
    try:
        res = requests.post(MODEL_URL, headers=headers, json=payload, timeout=30)
        return res.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"接口请求失败：{str(e)}"

def main():
    st.set_page_config(
        page_title="烟品新品研发智能分析系统",
        page_icon="🚬",
        layout="wide"
    )

    # 侧边栏配置密钥 + 示例问题
    with st.sidebar:
        st.markdown("### 🔑 接口密钥配置")
        input_key = st.text_input("Deepseek API_KEY", value=st.session_state.api_key, type="password")
        if st.button("保存密钥", type="primary", use_container_width=True):
            st.session_state.api_key = input_key
            st.success("密钥已保存")

        st.divider()
        st.markdown("### 💡 示例提问")
        example_qs = [
            "在全国哪些渠道销售最好，进行原因分析",
            "广州最畅销的烟品是什么，分析下原因",
            "江浙现在做什么烟最有机会？",
            "20–30元中端市场，用户最喜欢什么特征？",
            "针对18–25岁女性，新品该怎么做？"
            
        ]
        for i, q in enumerate(example_qs):
            if st.button(q, key=f"eq_{i}", use_container_width=True):
                st.session_state.input_value = q
                st.rerun()

    # 全局样式
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;600&display=swap');
    * {font-family: 'Noto Sans SC', sans-serif !important;font-size:14px !important;box-sizing:border-box;}
    #MainMenu, footer, header {visibility:hidden;}
    .block-container {padding:0 !important;max-width:100% !important;}
    .title-text {font-size:16px !important;font-weight:600;}
    .u-bub {background:#e5392e;color:#fff;border-radius:14px 14px 3px 14px;padding:12px 16px;max-width:70%;line-height:1.6;}
    .a-bub {background:#f3f4f8;border-radius:3px 14px 14px 14px;padding:12px 16px;max-width:85%;line-height:1.8;color:#1e293b;white-space:pre-wrap;}
    .u-msg {display:flex;justify-content:flex-end;margin:12px 0;}
    .a-msg {display:flex;gap:10px;margin:12px 0;}
    .a-av {width:32px;height:32px;border-radius:50%;flex-shrink:0;background:linear-gradient(135deg,#667eea,#764ba2);display:flex;align-items:center;justify-content:center;}
    .chat-container {background:#fff;border:1.5px solid #e8eaf0;border-radius:12px;padding:20px;height:450px;overflow-y:auto;display:flex;flex-direction:column;gap:8px;}
    .chat-empty {display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;color:#94a3b8;}
    .flow-bar {display:flex;align-items:center;justify-content:center;flex-wrap:wrap;gap:8px;background:#f8faff;border:1px solid #dde5ff;border-radius:8px;padding:12px;margin-bottom:14px;}
    .fn {background:#fff;border:1px solid #c7d2fe;border-radius:6px;padding:6px 12px;color:#4338ca;font-weight:500;}
    .fa {color:#a5b4fc;}
    ::-webkit-scrollbar {width:6px;}
    ::-webkit-scrollbar-thumb {background:#cbd5e1;border-radius:3px;}

    /* 针对 text_area 设置边框和阴影 */
    div[data-baseweb="textarea"] {
        border: 2px solid #dde5ff !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05) !important;
        border-radius: 8px !important;
        background-color: #ffffff !important;
    }

    /* 当鼠标点击输入框时，给边框一个高亮颜色，阴影加深一点 */
    div[data-baseweb="textarea"]:focus-within {
        border: 2px solid #4f46e5 !important;
        box-shadow: 0 4px 8px rgba(79, 70, 229, 0.15) !important;
    }

    /* 确保内部文字区域背景透明 */
    textarea {
        background-color: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # 顶部标题栏
    st.markdown('<div style="display:flex;align-items:center;gap:10px;padding:0 24px;height:52px;background:#fff;border-bottom:1.5px solid #e8eaf0;position:sticky;top:0;z-index:200;">'
    '<span style="font-size:18px;">🚬</span>'
    '<span class="title-text">烟品新品研发智能分析系统</span>'
    '<div style="flex:1;"></div>'
    '<span style="width:7px;height:7px;border-radius:50%;background:#22c55e;display:inline-block;"></span>'
    '<span>系统运行正常</span>'
    '</div>', unsafe_allow_html=True)

    # 顶部说明栏
    st.markdown('<div class="flow-bar"><span class="fn">多维数据支撑</span><span class="fa">→</span><span class="fn">烟品特征+销量表现+用户画像</span><span class="fa">→</span><span class="fn">自动生成研发建议报告</span></div>', unsafe_allow_html=True)

    # 唯一对话框
    chat_container = st.empty()

    def draw_chat(loading=False):
        html = '<div class="chat-container">'
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                html += f'<div class="u-msg"><div class="u-bub">{msg["content"]}</div></div>'
            else:
                # 处理 Markdown 格式
                content = msg["content"]
                # 确保 Markdown 标题格式正确
                content = content.replace('**一、', '\n\n**一、')
                content = content.replace('**二、', '\n\n**二、')
                content = content.replace('**三、', '\n\n**三、')
                content = content.replace('**四、', '\n\n**四、')
                content = content.replace('**五、', '\n\n**五、')
                content = content.replace('**六、', '\n\n**六、')
                html += f'<div class="a-msg"><div class="a-av">🚬</div><div class="a-bub">{content}</div></div>'
        if loading:
            html += '<div class="a-msg"><div class="a-av">🚬</div><div class="a-bub">正在分析数据，请稍候……</div></div>'
        html += '</div>'
        chat_container.markdown(html, unsafe_allow_html=True)

    # 初始空状态
    if not st.session_state.chat_history:
        chat_container.markdown('''
        <div class="chat-container">
            <div class="chat-empty">
                <div style="font-size:40px;margin-bottom:12px;">🚬</div>
                <div class="title-text" style="margin-bottom:8px;">烟品新品研发智能分析系统</div>
                <div>基于烟品特征、销量表现和用户画像数据，自动生成研发决策建议</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    else:
        draw_chat(loading=st.session_state.is_loading)

    # 清空输入函数
    def clear_input():
        st.session_state.input_value = ""
        st.session_state.chat_history = []
        st.session_state.is_loading = False

    # 输入框
    user_in = st.text_area(
        label="输入问题",
        placeholder="请输入烟品研发相关问题，如：在全国哪些渠道销售最好，进行原因分析",
        value=st.session_state.input_value,
        label_visibility="collapsed",
        height=80
    )

    col1, col2, col3 = st.columns([6,1,1])
    with col2:
        send_btn = st.button("发送 →", type="primary", use_container_width=True)
    with col3:
        clear_btn = st.button("清空", use_container_width=True, on_click=clear_input)

    # 发送按钮逻辑
    if send_btn and user_in.strip() and not st.session_state.is_loading:
        if not st.session_state.api_key:
            st.warning("请先在左侧侧边栏输入并保存 Deepseek API_KEY")
        else:
            question = user_in.strip()
            st.session_state.chat_history.append({"role": "user", "content": question})
            st.session_state.is_loading = True
            st.session_state.input_value = ""  # 清空输入框
            draw_chat(loading=True)
            st.rerun()

    # 获取答案逻辑
    if st.session_state.is_loading and len(st.session_state.chat_history) > 0 and st.session_state.chat_history[-1]["role"] == "user":
        ans = get_ai_answer(st.session_state.chat_history[-1]["content"], st.session_state.api_key)
        st.session_state.chat_history.append({"role": "assistant", "content": ans})
        st.session_state.is_loading = False
        draw_chat(loading=False)

if __name__ == "__main__":
    main()
