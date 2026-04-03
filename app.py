import streamlit as st
import openai
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
        "api_key_label": "DeepSeek API Key",
        "api_key_help": "请输入你的 DeepSeek API Key，用于自动生成报告",
        "input_title": "📝 产品信息输入",
        "basic_info": "基本信息",
        "product_name": "产品名称",
        "product_name_ph": "例如：宠物智能饮水机",
        "product_desc": "产品简要描述",
        "product_desc_ph": "例如：一款支持APP控制、可记录饮水量的智能宠物饮水机",
        "target_markets": "目标市场",
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
        "generating": "AI 正在生成报告，请稍候...（可能需要30-60秒）",
        "api_key_missing": "请先在侧边栏输入你的 DeepSeek API Key",
        "product_name_missing": "请填写产品名称",
        "error_prefix": "报告生成失败：",
        "report_title": "📄 生成的可行性分析报告",
        "download_btn": "📥 下载报告 (Markdown)",
        "back_btn": "← 返回重新填写",
        "footer": "© 2026 Laurence Ku | AI产品可行性分析系统 | 基于25年研发管理经验",
        "report_prompt": """
你是一位资深产品分析师和研发顾问，拥有25年消费电子及智能硬件行业经验。请根据以下产品信息，生成一份专业的《产品可行性分析报告》。

报告必须严格按照以下Markdown结构输出，内容要具体、有洞察，数据基于行业常识合理推断。

# 《产品可行性分析报告》
## {product_name}

## 报告基本信息

| 项目 | 内容 |
|------|------|
| 产品名称 | {product_name} |
| 产品描述 | {product_description} |
| 目标市场 | {target_markets} |
| 目标用户 | {target_users} |
| 报告日期 | 自动生成 |
| 分析人 | AI 分析师（基于行业数据库） |

---

## 第一部分：市场需求分析

### 1.1 市场规模与趋势

（请根据目标市场分别列出主要市场的规模、增长率、驱动因素和瓶颈，用表格形式）

### 1.2 用户画像

（用表格描述核心用户特征）

### 1.3 用户痛点分析

（列出3-5个核心痛点，用表格说明提及频率和描述）

### 1.4 关键功能需求排序

（用表格列出功能、重要性评分和说明）

---

## 第二部分：竞品分析

### 2.1 主要竞争对手

（根据产品品类，列出至少3个主要竞品，用表格说明品牌、产品、优势、劣势、定价区间）

### 2.2 竞品功能对比

（选择5-6个关键功能进行对比，用表格展示）

### 2.3 市场空白点分析

（列出至少3个市场空白机会）

---

## 第三部分：渠道适配性分析

### 3.1 目标市场渠道结构

（用表格描述主要渠道类型、占比、特点、适合度）

### 3.2 客户现有渠道现状

（基于用户输入：渠道情况={channel_status}，渠道详情={channel_detail}，品牌认知度={brand_status}，进行分析）

### 3.3 渠道策略建议

（按年份给出渠道拓展建议，用表格）

---

## 第四部分：技术可行性评估

### 4.1 关键技术要求

（用表格列出关键技术项、要求、客户现有能力、风险评估）

### 4.2 开发周期估算

（用表格列出阶段、时间、关键任务）

### 4.3 关键风险点

（用表格列出风险、可能性、影响、应对措施）

---

## 第五部分：销售预测

### 5.1 预测模型假设

（列出定价、目标市场、份额等假设）

### 5.2 销售额预测

（3年预测，用表格）

### 5.3 投资回报估算

（用表格列出研发投入、市场推广、首批生产成本、总启动资金、毛利率、盈亏平衡点）

---

## 第六部分：结论与建议

### 6.1 综合评估

（用表格打分：市场吸引力、技术可行性、渠道匹配度、竞争格局、投资回报，各1-10分，并说明）

### 6.2 差异化定位建议

（给出2-3个定位选项，用表格分析优势和风险）

### 6.3 最终建议

（给出综合评分和建议的下一步行动，5点以内）

---

请直接输出报告内容，不要添加额外解释。对于用户未提供的信息，基于行业标准进行合理推断，并注明“基于行业分析”。
"""
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
        "api_key_label": "DeepSeek API Key",
        "api_key_help": "Enter your DeepSeek API Key to auto-generate report",
        "input_title": "📝 Product Information Input",
        "basic_info": "Basic Information",
        "product_name": "Product Name",
        "product_name_ph": "e.g., Smart Pet Water Fountain",
        "product_desc": "Brief Description",
        "product_desc_ph": "e.g., A smart pet fountain with APP control and water intake logging",
        "target_markets": "Target Markets",
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
        "generating": "AI is generating report, please wait... (may take 30-60 seconds)",
        "api_key_missing": "Please enter your DeepSeek API Key in the sidebar",
        "product_name_missing": "Please enter the product name",
        "error_prefix": "Report generation failed: ",
        "report_title": "📄 Generated Feasibility Analysis Report",
        "download_btn": "📥 Download Report (Markdown)",
        "back_btn": "← Back to re-enter",
        "footer": "© 2026 Laurence Ku | AI Product Feasibility System | Based on 25+ years R&D experience",
        "report_prompt": """
You are a senior product analyst and R&D consultant with 25 years of experience in consumer electronics and smart hardware. Based on the following product information, generate a professional "Product Feasibility Analysis Report".

The report must strictly follow the Markdown structure below. The content should be specific, insightful, and based on industry common sense.

# Product Feasibility Analysis Report
## {product_name}

## Report Basic Information

| Item | Content |
|------|---------|
| Product Name | {product_name} |
| Product Description | {product_description} |
| Target Markets | {target_markets} |
| Target Users | {target_users} |
| Report Date | Auto-generated |
| Analyst | AI Analyst (based on industry database) |

---

## Part 1: Market Demand Analysis

### 1.1 Market Size & Trends

(For each target market, list market size, growth rate, key drivers and barriers in a table)

### 1.2 User Persona

(Describe core user characteristics in a table)

### 1.3 User Pain Points

(List 3-5 core pain points in a table with frequency and description)

### 1.4 Key Feature Priority

(List features, importance score, and explanation in a table)

---

## Part 2: Competitive Analysis

### 2.1 Main Competitors

(List at least 3 main competitors with brand, product, strengths, weaknesses, price range in a table)

### 2.2 Feature Comparison

(Compare 5-6 key features in a table)

### 2.3 Market Gap Summary

(List at least 3 market gap opportunities)

---

## Part 3: Channel Suitability Analysis

### 3.1 Target Market Channel Structure

(Describe main channel types, share, characteristics, suitability in a table)

### 3.2 Client's Current Channel Status

(Based on user input: channel status={channel_status}, channel details={channel_detail}, brand awareness={brand_status})

### 3.3 Channel Strategy Recommendations

(Provide channel expansion recommendations by year in a table)

---

## Part 4: Technical Feasibility Assessment

### 4.1 Key Technical Requirements

(List technology, requirement, client capability, risk level in a table)

### 4.2 Development Timeline Estimate

(List phase, duration, key tasks in a table)

### 4.3 Key Risk Points

(List risk, probability, impact, mitigation in a table)

---

## Part 5: Sales Forecast

### 5.1 Forecast Assumptions

(List pricing, target market, share assumptions)

### 5.2 Sales Forecast

(3-year forecast in a table)

### 5.3 ROI Estimate

(List R&D investment, marketing, first production cost, total capital, gross margin, breakeven point in a table)

---

## Part 6: Conclusion & Recommendations

### 6.1 Comprehensive Evaluation

(Score each dimension: Market Attractiveness, Technical Feasibility, Channel Fit, Competitive Landscape, ROI Potential out of 10, with explanation in a table)

### 6.2 Differentiation Positioning Recommendations

(Provide 2-3 positioning options with advantages and risks in a table)

### 6.3 Final Recommendation

(Provide overall score and 5 specific next steps)

---

Output the report directly without additional explanation. For information not provided by the user, make reasonable inferences based on industry standards and note "based on industry analysis".
"""
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
    deepseek_api_key = st.text_input(
        t["api_key_label"],
        type="password",
        help=t["api_key_help"]
    )

# ================== 主表单 ==================
st.markdown(f"### {t['input_title']}")
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"#### {t['basic_info']}")
    product_name = st.text_input(t["product_name"], placeholder=t["product_name_ph"])
    product_description = st.text_area(t["product_desc"], placeholder=t["product_desc_ph"], height=100)
    target_markets = st.multiselect(t["target_markets"], options=["中国大陆", "美国", "欧洲", "东南亚", "日本", "其他"], default=["中国大陆"])
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

# ================== 生成报告 ==================
if submitted:
    if not product_name:
        st.error(t["product_name_missing"])
    elif not deepseek_api_key:
        st.error(t["api_key_missing"])
    else:
        with st.spinner(t["generating"]):
            try:
                # 配置 openai
                openai.api_key = deepseek_api_key
                openai.base_url = "https://api.deepseek.com"
                
                # 获取语言对应的 prompt 模板并填充
                prompt_template = t["report_prompt"]
                # 格式化目标市场列表
                target_markets_str = ", ".join(target_markets)
                # 填充产品信息
                prompt = prompt_template.format(
                    product_name=product_name,
                    product_description=product_description or "未提供",
                    target_markets=target_markets_str,
                    target_users=target_users or "未提供",
                    channel_status=channel_status,
                    channel_detail=channel_detail or "未提供",
                    brand_status=brand_status
                )
                
                # 调用 DeepSeek API
                response = openai.ChatCompletion.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    stream=False,
                    temperature=0.7,
                )
                report_content = response.choices[0].message.content
                
                # 清空原有内容，显示报告
                st.empty()
                st.markdown(f"## {t['report_title']}")
                st.markdown(report_content)
                
                # 提供下载按钮
                st.download_button(
                    label=t["download_btn"],
                    data=report_content,
                    file_name=f"{product_name}_Feasibility_Report.md",
                    mime="text/markdown"
                )
                
                # 返回按钮
                if st.button(t["back_btn"]):
                    st.rerun()
                    
            except Exception as e:
                st.error(f"{t['error_prefix']}{e}")
                st.info("请检查 API Key 是否正确，或稍后重试。")

# ================== 页脚 ==================
else:
    st.markdown("---")
    st.caption(t["footer"])
