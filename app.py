import streamlit as st
from datetime import datetime
import uuid

# 页面配置
st.set_page_config(
    page_title="产品可行性分析系统",
    page_icon="📊",
    layout="wide"
)

# 标题
st.title("📊 产品可行性 - AI分析系统")
st.markdown("---")

# 侧边栏 - 关于信息
with st.sidebar:
    st.image("https://via.placeholder.com/300x100?text=Laurence+Ku", width=200)
    st.markdown("## 关于分析系统")
    st.markdown("""
    本系统基于：
    - 25+年研发管理经验
    - AI大模型数据分析
    - 行业数据库与竞品追踪
    - DFSS/六西格玛方法论
    """)
    st.markdown("---")
    
    # 分析人可输入（默认为空）
    analyst_name = st.text_input(
        "分析人姓名",
        value="",
        placeholder="请输入您的姓名或分析师姓名",
        help="请填写分析人姓名"
    )
    analyst_title = st.text_input(
        "分析人头衔（可选）",
        placeholder="例如：研发总监、技术顾问",
        help="可填写职位或公司信息"
    )
    
    # 显示用户填写的分析人信息（仅当有输入时）
    if analyst_name:
        st.markdown(f"**分析人：{analyst_name}**")
        if analyst_title:
            st.markdown(f"_{analyst_title}_")
    else:
        st.caption("请填写分析人姓名")

# 主界面 - 输入表单
st.markdown("### 📝 产品信息输入")

# 两列布局
col1, col2 = st.columns(2)

with col1:
    # 产品基本信息
    st.markdown("#### 基本信息")
    product_name = st.text_input(
        "产品名称", 
        placeholder="例如：宠物智能饮水机",
        help="请输入产品名称"
    )
    product_description = st.text_area(
        "产品简要描述",
        placeholder="例如：一款支持APP控制、可记录饮水量的智能宠物饮水机",
        height=100
    )
    
    target_markets = st.multiselect(
        "目标市场",
        options=["中国大陆", "美国", "欧洲", "东南亚", "日本", "其他"],
        default=["中国大陆"]
    )
    
    target_users = st.text_input(
        "目标用户群体",
        placeholder="例如：25-40岁城市中产、养猫人群",
        help="描述目标用户的年龄、收入、生活方式等特征"
    )

with col2:
    # 市场与渠道信息
    st.markdown("#### 市场与渠道")
    
    channel_status = st.selectbox(
        "现有渠道情况",
        options=["有成熟渠道", "有部分渠道", "渠道较弱", "无渠道/从零开始"]
    )
    
    channel_detail = st.text_area(
        "渠道详情",
        placeholder="例如：天猫旗舰店、京东自营、部分线下宠物店",
        height=80
    )
    
    brand_status = st.selectbox(
        "品牌认知度",
        options=["高（知名品牌）", "中（行业内有认知）", "低（需要建立品牌）"]
    )

# 技术信息
st.markdown("#### 技术能力")
col3, col4 = st.columns(2)

with col3:
    tech_experience = st.multiselect(
        "相关技术经验",
        options=[
            "智能硬件/物联网", "APP开发", "机械结构设计",
            "光学设计", "电子电路", "供应链管理",
            "海外认证（UL/CE/FCC）", "DFSS/六西格玛"
        ],
        default=[]
    )

with col4:
    dev_stage = st.selectbox(
        "产品开发阶段",
        options=["概念/想法", "调研中", "已立项", "开发中", "已有样机"]
    )

# 预算与目标
st.markdown("#### 商业目标")
col5, col6 = st.columns(2)

with col5:
    estimated_budget = st.selectbox(
        "预估研发预算",
        options=["50万以下", "50-100万", "100-200万", "200-500万", "500万以上"]
    )

with col6:
    sales_target = st.text_input(
        "首年销售目标",
        placeholder="例如：1000万人民币 / 200万美元"
    )

# 额外信息
st.markdown("#### 其他信息")
additional_info = st.text_area(
    "补充说明（可选）",
    placeholder="任何你认为重要的信息，如：已有技术储备、合作伙伴、特殊要求等",
    height=80
)

# 提交按钮
st.markdown("---")
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    submitted = st.button("🚀 开始分析", type="primary", use_container_width=True)

# 处理提交
if submitted:
    if not product_name:
        st.error("请填写产品名称")
    else:
        # 清空原有内容，显示手工处理提示
        st.empty()
        
        # 显示一个大的提示卡片
        st.markdown("---")
        st.markdown("## 📢 温馨提示")
        st.markdown("""
        ### 分析工具还在与大模型对接中，当前需要手工输入。
        
        您的需求我们已经收到，请直接联系我获取专业的可行性分析报告。
        """)
        
        # 联系方式（可加上分析人信息）
        contact_info = """
        📧 **联系方式**：
        - 联系人：古生
        - 邮箱：nc.ku@hotmail.com
        - 电话：+86-13823760640
        """
        if analyst_name:
            contact_info += f"\n- 分析人：{analyst_name}" + (f" ({analyst_title})" if analyst_title else "")
        st.info(contact_info)
        
        # 可选：显示用户输入摘要（方便用户自己核对，也可不显示）
        with st.expander("📋 您刚才输入的信息（点击展开）"):
            st.markdown(f"""
            | 项目 | 内容 |
            |-----|-----|
            | 产品名称 | {product_name} |
            | 产品描述 | {product_description or '未填写'} |
            | 目标市场 | {', '.join(target_markets)} |
            | 目标用户 | {target_users or '未填写'} |
            | 渠道情况 | {channel_status} - {channel_detail or '未填写'} |
            | 品牌认知度 | {brand_status} |
            | 相关技术经验 | {', '.join(tech_experience) if tech_experience else '未填写'} |
            | 开发阶段 | {dev_stage} |
            | 预估预算 | {estimated_budget} |
            | 销售目标 | {sales_target or '未填写'} |
            | 分析人 | {analyst_name or '未填写'} {('(' + analyst_title + ')') if analyst_title else ''} |
            """)
        
        # 生成一个唯一请求编号（供用户跟踪）
        request_id = str(uuid.uuid4())[:8]
        st.caption(f"您的请求编号：{request_id}（联系时可提供此编号）")
        
        # 添加返回顶部的按钮（可选，让用户可以重新填写）
        if st.button("← 返回重新填写"):
            st.rerun()
else:
    # 未提交时显示页脚
    st.markdown("---")
    st.caption("© 2026 Laurence Ku | AI产品可行性分析系统 | 基于25年研发管理经验")
