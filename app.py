import streamlit as st
import uuid

# ================== 页面配置 ==================
st.set_page_config(
    page_title="Product Feasibility Analysis System",
    page_icon="📊",
    layout="wide"
)

# ================== 语言字典 ==================
TEXTS = {
    "zh": {
        "title": "📊 产品可行性 - AI分析系统",
        "sidebar_title": "关于分析系统",
        "sidebar_basis": "本系统基于：",
        "basis_items": ["25+年研发管理经验", "AI大模型数据分析", "行业数据库与竞品追踪", "DFSS/六西格玛方法论"],
        "analyst_name_label": "分析人姓名",
        "analyst_name_ph": "请输入您的姓名或分析师姓名",
        "analyst_title_label": "分析人头衔（可选）",
        "analyst_title_ph": "例如：研发总监、技术顾问",
        "api_key_label": "AI API Key (暂未启用)",
        "api_key_help": "预留字段，当前无需填写",
        "input_title": "📝 产品信息输入",
        "basic_info": "基本信息",
        "product_name": "产品名称",
        "product_name_ph": "例如：宠物智能饮水机",
        "product_desc": "产品简要描述",
        "product_desc_ph": "例如：一款支持APP控制、可记录饮水量的智能宠物饮水机",
        "target_markets": "目标市场",
        "market_options": ["中国大陆", "美国", "欧洲", "东南亚", "日本", "其他"],
        "target_users": "目标用户群体",
        "target_users_ph": "例如：25-40岁城市中产、养猫人群",
        "market_channel": "市场与渠道",
        "channel_status": "现有渠道情况",
        "channel_options": ["有成熟渠道", "有部分渠道", "渠道较弱", "无渠道/从零开始"],
        "channel_detail": "渠道详情",
        "channel_detail_ph": "例如：天猫旗舰店、京东自营、部分线下宠物店",
        "brand_status": "品牌认知度",
        "brand_options": ["高（知名品牌）", "中（行业内有认知）", "低（需要建立品牌）"],
        "tech_capability": "技术能力",
        "tech_experience": "相关技术经验",
        "tech_options": ["智能硬件/物联网", "APP开发", "机械结构设计", "光学设计", "电子电路", "供应链管理", "海外认证（UL/CE/FCC）", "DFSS/六西格玛"],
        "dev_stage": "产品开发阶段",
        "stage_options": ["概念/想法", "调研中", "已立项", "开发中", "已有样机"],
        "business_goals": "商业目标",
        "estimated_budget": "预估研发预算",
        "budget_options": ["50万以下", "50-100万", "100-200万", "200-500万", "500万以上"],
        "sales_target": "首年销售目标",
        "sales_target_ph": "例如：1000万人民币 / 200万美元",
        "other_info": "其他信息",
        "other_ph": "任何你认为重要的信息，如：已有技术储备、合作伙伴、特殊要求等",
        "submit_btn": "🚀 开始分析",
        "product_name_missing": "请填写产品名称",
        "manual_title": "📢 温馨提示",
        "manual_message": "### 分析工具还在与大模型对接中，当前需要手工输入。\n\n您的需求我们已经收到，请直接联系我获取专业的可行性分析报告。",
        "contact_info": """
        📧 **联系方式**：
        - 联系人：古生
        - 邮箱：nc.ku@hotmail.com
        - 电话：+86-13823760640
        """,
        "input_summary": "📋 您刚才输入的信息（点击展开）",
        "request_id": "您的请求编号：{}（联系时可提供此编号）",
        "back_btn": "← 返回重新填写",
        "footer": "© 2026 Laurence Ku | AI产品可行性分析系统 | 基于25年研发管理经验"
    },
    "en": {
        "title": "📊 Product Feasibility - AI Analysis System",
        "sidebar_title": "About the System",
        "sidebar_basis": "This system is based on:",
        "basis_items": ["25+ years R&D management", "AI big data analysis", "Industry database & competitor tracking", "DFSS/Six Sigma methodology"],
        "analyst_name_label": "Analyst Name",
        "analyst_name_ph": "Enter your name or analyst name",
        "analyst_title_label": "Analyst Title (Optional)",
        "analyst_title_ph": "e.g., R&D Director, Technical Consultant",
        "api_key_label": "AI API Key (not yet active)",
        "api_key_help": "Reserved field, no need to fill for now",
        "input_title": "📝 Product Information Input",
        "basic_info": "Basic Information",
        "product_name": "Product Name",
        "product_name_ph": "e.g., Smart Pet Water Fountain",
        "product_desc": "Brief Description",
        "product_desc_ph": "e.g., A smart pet fountain with APP control and water intake logging",
        "target_markets": "Target Markets",
        "market_options": ["Mainland China", "United States", "Europe", "Southeast Asia", "Japan", "Others"],
        "target_users": "Target User Group",
        "target_users_ph": "e.g., Urban middle-class cat owners aged 25-40",
        "market_channel": "Market & Channel",
        "channel_status": "Current Channel Status",
        "channel_options": ["Mature channels", "Partial channels", "Weak channels", "No channels / start from scratch"],
        "channel_detail": "Channel Details",
        "channel_detail_ph": "e.g., Tmall flagship store, JD self-operated, some offline pet stores",
        "brand_status": "Brand Awareness",
        "brand_options": ["High (well-known)", "Medium (recognized in industry)", "Low (need to build brand)"],
        "tech_capability": "Technical Capability",
        "tech_experience": "Relevant Tech Experience",
        "tech_options": ["Smart Hardware/IoT", "App Development", "Mechanical Design", "Optical Design", "Electronic Circuits", "Supply Chain Management", "Overseas Certification (UL/CE/FCC)", "DFSS/Six Sigma"],
        "dev_stage": "Development Stage",
        "stage_options": ["Idea/Concept", "Researching", "Project approved", "Developing", "Prototype ready"],
        "business_goals": "Business Goals",
        "estimated_budget": "Estimated R&D Budget",
        "budget_options": ["Under 500k", "500k-1M", "1M-2M", "2M-5M", "Above 5M"],
        "sales_target": "First Year Sales Target",
        "sales_target_ph": "e.g., 10M RMB / 2M USD",
        "other_info": "Other Information",
        "other_ph": "Any important info, e.g., existing tech stack, partners, special requirements",
        "submit_btn": "🚀 Start Analysis",
        "product_name_missing": "Please enter the product name",
        "manual_title": "📢 Notice",
        "manual_message": "### The analysis tool is still being connected to the AI model. Manual input is currently required.\n\nYour request has been received. Please contact me directly for a professional feasibility analysis report.",
        "contact_info": """
        📧 **Contact**:
        - Contact: Mr. Gu
        - Email: nc.ku@hotmail.com
        - Phone: +86-13823760640
        """,
        "input_summary": "📋 Information you just entered (click to expand)",
        "request_id": "Your request ID: {} (please provide this ID when contacting)",
        "back_btn": "← Back to re-enter",
        "footer": "© 2026 Laurence Ku | AI Product Feasibility System | Based on 25+ years R&D experience"
    }
}

# ================== 初始化语言 ==================
if "lang" not in st.session_state:
    st.session_state.lang = "zh"

# ================== 右上角按钮 ==================
col1, col2, col3 = st.columns([8, 1, 1])
with col2:
    if st.button("中文", key="zh_btn"):
        st.session_state.lang = "zh"
        st.rerun()
with col3:
    if st.button("English", key="en_btn"):
        st.session_state.lang = "en"
        st.rerun()

lang = st.session_state.lang
t = TEXTS[lang]

# ================== 标题 ==================
st.title(t["title"])
st.markdown("---")

# ================== 侧边栏 ==================
with st.sidebar:
    st.image("https://via.placeholder.com/300x100?text=Laurence+Ku", width=200)
    st.markdown(f"## {t['sidebar_title']}")
    st.markdown(t["sidebar_basis"])
    for item in t["basis_items"]:
        st.markdown(f"- {item}")
    st.markdown("---")
    
    # 分析人输入
    analyst_name = st.text_input(
        t["analyst_name_label"],
        value="",
        placeholder=t["analyst_name_ph"],
        help=t["analyst_name_ph"]
    )
    analyst_title = st.text_input(
        t["analyst_title_label"],
        placeholder=t["analyst_title_ph"],
        help=t["analyst_title_ph"]
    )
    if analyst_name:
        st.markdown(f"**{t['analyst_name_label']}: {analyst_name}**")
        if analyst_title:
            st.markdown(f"_{analyst_title}_")
    else:
        st.caption(t["analyst_name_ph"])
    
    st.markdown("---")
    # 仅显示占位，不实际使用
    st.text_input(t["api_key_label"], type="password", disabled=True, help=t["api_key_help"])

# ================== 主表单 ==================
st.markdown(f"### {t['input_title']}")
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"#### {t['basic_info']}")
    product_name = st.text_input(t["product_name"], placeholder=t["product_name_ph"])
    product_description = st.text_area(t["product_desc"], placeholder=t["product_desc_ph"], height=100)
    target_markets = st.multiselect(t["target_markets"], options=t["market_options"], default=[t["market_options"][0]])
    target_users = st.text_input(t["target_users"], placeholder=t["target_users_ph"])

with col2:
    st.markdown(f"#### {t['market_channel']}")
    channel_status = st.selectbox(t["channel_status"], options=t["channel_options"])
    channel_detail = st.text_area(t["channel_detail"], placeholder=t["channel_detail_ph"], height=80)
    brand_status = st.selectbox(t["brand_status"], options=t["brand_options"])

st.markdown(f"#### {t['tech_capability']}")
col3, col4 = st.columns(2)
with col3:
    tech_experience = st.multiselect(t["tech_experience"], options=t["tech_options"], default=[])
with col4:
    dev_stage = st.selectbox(t["dev_stage"], options=t["stage_options"])

st.markdown(f"#### {t['business_goals']}")
col5, col6 = st.columns(2)
with col5:
    estimated_budget = st.selectbox(t["estimated_budget"], options=t["budget_options"])
with col6:
    sales_target = st.text_input(t["sales_target"], placeholder=t["sales_target_ph"])

st.markdown(f"#### {t['other_info']}")
additional_info = st.text_area("", placeholder=t["other_ph"], height=80)

# ================== 提交按钮 ==================
st.markdown("---")
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    submitted = st.button(t["submit_btn"], type="primary", use_container_width=True)

# ================== 处理提交（手工提示） ==================
if submitted:
    if not product_name:
        st.error(t["product_name_missing"])
    else:
        # 清空原有内容，显示手工处理提示
        st.empty()
        
        st.markdown("---")
        st.markdown(f"## {t['manual_title']}")
        st.markdown(t["manual_message"])
        st.info(t["contact_info"])
        
        # 显示输入摘要
        with st.expander(t["input_summary"]):
            st.markdown(f"""
            | 项目 | 内容 |
            |------|------|
            | {t['product_name']} | {product_name} |
            | {t['product_desc']} | {product_description or '未填写'} |
            | {t['target_markets']} | {', '.join(target_markets)} |
            | {t['target_users']} | {target_users or '未填写'} |
            | {t['channel_status']} | {channel_status} - {channel_detail or '未填写'} |
            | {t['brand_status']} | {brand_status} |
            | {t['tech_experience']} | {', '.join(tech_experience) if tech_experience else '未填写'} |
            | {t['dev_stage']} | {dev_stage} |
            | {t['estimated_budget']} | {estimated_budget} |
            | {t['sales_target']} | {sales_target or '未填写'} |
            """)
        
        # 生成请求编号
        request_id = str(uuid.uuid4())[:8]
        st.caption(t["request_id"].format(request_id))
        
        # 返回按钮
        if st.button(t["back_btn"]):
            st.rerun()

# ================== 页脚 ==================
else:
    st.markdown("---")
    st.caption(t["footer"])
