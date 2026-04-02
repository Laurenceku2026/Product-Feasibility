import streamlit as st
import openai
import json
import os
import re
import secrets
import string
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from io import BytesIO
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from datetime import datetime, timedelta

# ================== 页面配置 ==================
st.set_page_config(
    page_title="Product Feasibility Analysis System",
    page_icon="📊",
    layout="wide"
)

# ================== 管理员凭证 ==================
ADMIN_USERNAME = "Laurence_ku"
ADMIN_PASSWORD = "Ku_product$2026"

# ================== 从 secrets 读取永久 API 配置 ==================
try:
    PERSISTENT_API_KEY = st.secrets["AI_API_KEY"]
except:
    PERSISTENT_API_KEY = ""
try:
    PERSISTENT_BASE_URL = st.secrets["AI_BASE_URL"]
except:
    PERSISTENT_BASE_URL = "https://api.deepseek.com"
try:
    PERSISTENT_MODEL_NAME = st.secrets["AI_MODEL_NAME"]
except:
    PERSISTENT_MODEL_NAME = "deepseek-chat"

# ================== 从 secrets 读取 SMTP 邮件配置 ==================
try:
    SMTP_SERVER = st.secrets["SMTP_SERVER"]
    SMTP_PORT = st.secrets["SMTP_PORT"]
    SMTP_USER = st.secrets["SMTP_USER"]
    SMTP_PASSWORD = st.secrets["SMTP_PASSWORD"]
except:
    SMTP_SERVER = ""
    SMTP_PORT = 587
    SMTP_USER = ""
    SMTP_PASSWORD = ""

def send_license_email(to_email, license_key, plan_name, uses, expiry, lang="zh"):
    """发送授权码邮件，支持中英文（静默失败）"""
    if not SMTP_USER or not SMTP_PASSWORD:
        return False
    if lang == "zh":
        subject = f"您的产品可行性分析系统授权码 - {plan_name}"
        body = f"""
亲爱的用户：

感谢您对 Techlife 产品的信任！

您的产品分析报告通行证已生成，详情如下：

- 授权码：{license_key}
- 套餐：{plan_name}
- 可用次数：{uses}
- 有效期至：{expiry}

请在系统左侧边栏的“授权码 (Report Key)”输入框中输入此授权码，即可解锁高级功能（无水印、可下载 Word 报告）。

请妥善保管此授权码，如有疑问请联系：nc.ku@hotmail.com

祝您使用愉快！

Techlife 产品可行性分析系统
"""
    else:
        subject = f"Your License Key for Product Feasibility Analysis System - {plan_name}"
        body = f"""
Dear Customer,

Thank you for trusting Techlife products!

Your product analysis report pass has been generated. Details are as follows:

- License Key: {license_key}
- Plan: {plan_name}
- Available uses: {uses}
- Valid until: {expiry}

Please enter this license key in the "Report Key" input box on the left sidebar to unlock advanced features (no watermark, Word report download available).

Please keep this license key safe. If you have any questions, please contact: nc.ku@hotmail.com

Best regards,

Techlife Product Feasibility Analysis System
"""
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = to_email
    msg['Subject'] = Header(subject, 'utf-8')
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, [to_email], msg.as_string())
        server.quit()
        return True
    except Exception:
        return False

# ================== 授权类型定义 ==================
LICENSE_TYPES = {
    "trial": {"name": "试用版", "max_uses": 60, "max_months": 3, "en_name": "Trial"},
    "level1": {"name": "一级用户", "max_uses": 100, "max_months": 12, "en_name": "Level 1"},
    "level2": {"name": "二级用户", "max_uses": 300, "max_months": 24, "en_name": "Level 2"},
    "level3": {"name": "三级用户", "max_uses": 500, "max_months": 36, "en_name": "Level 3"},
    "level4": {"name": "四级用户", "max_uses": 1000, "max_months": 60, "en_name": "Level 4"},
}

USAGE_FILE = "usage_data.json"

def load_usage_data():
    if os.path.exists(USAGE_FILE):
        try:
            with open(USAGE_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_usage_data(data):
    with open(USAGE_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ================== 初始化 session state ==================
if "lang" not in st.session_state:
    st.session_state.lang = "zh"
if "pulse_active" not in st.session_state:
    st.session_state.pulse_active = False
if "report_content_zh" not in st.session_state:
    st.session_state.report_content_zh = None
if "report_content_en" not in st.session_state:
    st.session_state.report_content_en = None
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "ai_api_key" not in st.session_state:
    st.session_state.ai_api_key = PERSISTENT_API_KEY
if "ai_base_url" not in st.session_state:
    st.session_state.ai_base_url = PERSISTENT_BASE_URL
if "ai_model_name" not in st.session_state:
    st.session_state.ai_model_name = PERSISTENT_MODEL_NAME
if "usage_db" not in st.session_state:
    st.session_state.usage_db = load_usage_data()
if "current_report_key" not in st.session_state:
    st.session_state.current_report_key = ""
if "current_license_type" not in st.session_state:
    st.session_state.current_license_type = None

def activate_license(report_key):
    if report_key in st.session_state.usage_db:
        record = st.session_state.usage_db[report_key]
        remaining = record["remaining"]
        expiry_str = record["expiry"]
        expiry = datetime.fromisoformat(expiry_str)
        if remaining > 0 and datetime.now() <= expiry:
            lic_type = record.get("type", "unknown")
            st.session_state.current_license_type = lic_type
            return True, remaining, expiry_str, lic_type
        else:
            st.session_state.current_license_type = None
            return False, 0, None, None
    else:
        st.session_state.current_license_type = None
        return False, 0, None, None

def consume_usage(report_key):
    if st.session_state.admin_logged_in:
        return True
    if not report_key:
        return False
    valid, remaining, expiry_str, _ = activate_license(report_key)
    if not valid:
        return False
    record = st.session_state.usage_db[report_key]
    record["remaining"] -= 1
    record["total_uses"] = record.get("total_uses", 0) + 1
    save_usage_data(st.session_state.usage_db)
    return True

def get_remaining_info(report_key):
    if st.session_state.admin_logged_in:
        return "无限", "永久"
    valid, remaining, expiry_str, _ = activate_license(report_key)
    if not valid:
        return "未授权", "无"
    expiry = datetime.fromisoformat(expiry_str)
    return str(remaining), expiry.strftime("%Y-%m-%d")

def is_premium_user(report_key):
    if st.session_state.admin_logged_in:
        return True
    if report_key:
        valid, _, _, _ = activate_license(report_key)
        return valid
    return False

def generate_report_key(license_type, custom_uses=None, custom_months=None):
    random_str = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    new_key = f"{license_type.upper()}_{random_str}"
    if license_type == "custom":
        max_uses = custom_uses
        max_months = custom_months
        type_name = "自定义"
    else:
        lic_info = LICENSE_TYPES[license_type]
        max_uses = lic_info["max_uses"]
        max_months = lic_info["max_months"]
        type_name = lic_info["name"]
    expiry = datetime.now() + timedelta(days=max_months*30)
    expiry_str = expiry.isoformat()
    st.session_state.usage_db[new_key] = {
        "type": license_type,
        "remaining": max_uses,
        "expiry": expiry_str,
        "total_uses": 0,
        "generated_at": datetime.now().isoformat()
    }
    save_usage_data(st.session_state.usage_db)
    return new_key, max_uses, expiry_str, type_name

# ================== 防复制/截屏 CSS + 动态水印 ==================
def add_security_css(disable=False):
    if disable:
        return
    st.markdown("""
    <style>
        body, .stApp, .markdown-text-container, .report-container {
            user-select: none;
            -webkit-user-select: none;
            -moz-user-select: none;
            -ms-user-select: none;
        }
        body {
            -webkit-touch-callout: none;
            pointer-events: auto;
        }
        .bg-watermark {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            opacity: 0.05;
            pointer-events: none;
            z-index: 999;
            background-image: repeating-linear-gradient(45deg, 
                #000 0px, #000 2px, 
                transparent 2px, transparent 40px,
                #000 40px, #000 42px,
                transparent 42px, transparent 80px);
            background-size: 80px 80px;
        }
    </style>
    <div class="bg-watermark"></div>
    <script>
        document.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            return false;
        });
        document.addEventListener('keydown', function(e) {
            if (e.ctrlKey && (e.key === 'c' || e.key === 'C' || e.key === 'v' || e.key === 'V' || e.key === 'x' || e.key === 'X' || e.key === 's' || e.key === 'S')) {
                e.preventDefault();
                return false;
            }
            if (e.key === 'F12' || e.key === 'PrintScreen') {
                e.preventDefault();
                alert('截图功能已被禁用，请遵守保密协议。');
                return false;
            }
        });
        document.addEventListener('keyup', function(e) {
            if (e.key === 'PrintScreen') {
                alert('截图行为已被记录，请勿传播保密内容。');
            }
        });
    </script>
    """, unsafe_allow_html=True)

def add_dynamic_watermark(lang, hide):
    if hide:
        return
    if lang == "zh":
        watermark_text = "机密，样板报告，请联系 nc.ku@hotmail.com"
    else:
        watermark_text = "Confidential, Sample Report, Pls contact nc.ku@hotmail.com"
    st.markdown(f"""
    <div style="position: fixed; bottom: 20px; right: 20px; opacity: 0.4; font-size: 14px; color: #666; pointer-events: none; z-index: 1000; font-family: sans-serif; background: rgba(255,255,255,0.5); padding: 4px 8px; border-radius: 4px;">
        {watermark_text}
    </div>
    """, unsafe_allow_html=True)

# ================== Word 表格生成（自动列宽，浅灰边框） ==================
def set_cell_border(cell, border_color=RGBColor(0xCC, 0xCC, 0xCC)):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    for edge in ['top', 'left', 'bottom', 'right']:
        tag = f'w:{edge}'
        border = OxmlElement(tag)
        border.set(qn('w:val'), 'single')
        border.set(qn('w:sz'), '4')
        border.set(qn('w:space'), '0')
        border.set(qn('w:color'), f'{border_color}')
        tcPr.append(border)

def markdown_to_docx(md_text, doc):
    lines = md_text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('# '):
            doc.add_heading(line[2:], level=1)
            i += 1
            continue
        if line.startswith('## '):
            doc.add_heading(line[3:], level=2)
            i += 1
            continue
        if line.startswith('### '):
            doc.add_heading(line[4:], level=3)
            i += 1
            continue
        if line.startswith('|') and i+1 < len(lines):
            table_lines = []
            while i < len(lines) and lines[i].startswith('|'):
                table_lines.append(lines[i].strip())
                i += 1
            if len(table_lines) >= 2:
                def parse_row(row):
                    cells = [cell.strip() for cell in row.split('|')]
                    if cells and cells[0] == '':
                        cells = cells[1:]
                    if cells and cells[-1] == '':
                        cells = cells[:-1]
                    return cells
                headers = parse_row(table_lines[0])
                if len(table_lines) > 1 and '---' in table_lines[1]:
                    data_lines = table_lines[2:] if len(table_lines) > 2 else []
                else:
                    data_lines = table_lines[1:]
                num_cols = len(headers)
                if num_cols > 0:
                    table = doc.add_table(rows=1+len(data_lines), cols=num_cols)
                    table.style = 'Table Grid'
                    table.autofit = True
                    table.width = Inches(6.5)
                    for row in table.rows:
                        for cell in row.cells:
                            set_cell_border(cell, RGBColor(0xCC, 0xCC, 0xCC))
                    for col_idx, cell_text in enumerate(headers):
                        cell = table.cell(0, col_idx)
                        cell.text = cell_text
                        for paragraph in cell.paragraphs:
                            for run in paragraph.runs:
                                run.font.bold = True
                                run.font.name = 'Arial' if lang == 'en' else '宋体'
                    for row_idx, data_line in enumerate(data_lines):
                        cells = parse_row(data_line)
                        for col_idx, cell_text in enumerate(cells):
                            if col_idx < num_cols:
                                cell = table.cell(row_idx+1, col_idx)
                                cell.text = cell_text
                                for paragraph in cell.paragraphs:
                                    for run in paragraph.runs:
                                        run.font.name = 'Arial' if lang == 'en' else '宋体'
                    doc.add_paragraph()
            continue
        if line.strip():
            p = doc.add_paragraph(line)
            for run in p.runs:
                run.font.name = 'Arial' if lang == 'en' else '宋体'
        else:
            doc.add_paragraph()
        i += 1

# ================== 管理员对话框 ==================
@st.dialog("管理员登录")
def admin_login_dialog():
    username = st.text_input("用户名")
    password = st.text_input("密码", type="password")
    if st.button("登录"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.admin_logged_in = True
            st.success("登录成功！")
            st.rerun()
        else:
            st.error("用户名或密码错误")

@st.dialog("管理员设置")
def admin_settings_dialog():
    st.subheader("AI API 配置（临时覆盖）")
    new_key = st.text_input("API Key", value=st.session_state.ai_api_key, type="password")
    new_url = st.text_input("Base URL", value=st.session_state.ai_base_url)
    new_model = st.text_input("模型名称", value=st.session_state.ai_model_name)
    if st.button("应用临时配置"):
        st.session_state.ai_api_key = new_key
        st.session_state.ai_base_url = new_url
        st.session_state.ai_model_name = new_model
        st.success("当前会话已使用新配置（刷新页面后恢复为永久配置）")
        st.rerun()
    st.markdown("---")
    
    st.subheader("Report Key 生成器")
    key_type = st.selectbox("选择授权类型", ["试用版", "一级用户", "二级用户", "三级用户", "四级用户", "自定义"])
    custom_uses = None
    custom_months = None
    if key_type == "自定义":
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            custom_uses = st.number_input("使用次数", min_value=1, step=1, value=100)
        with col_c2:
            custom_months = st.number_input("有效期（月）", min_value=1, step=1, value=12)
    if st.button("生成 Report Key"):
        if key_type == "试用版":
            license_type = "trial"
        elif key_type == "一级用户":
            license_type = "level1"
        elif key_type == "二级用户":
            license_type = "level2"
        elif key_type == "三级用户":
            license_type = "level3"
        elif key_type == "四级用户":
            license_type = "level4"
        else:
            license_type = "custom"
        new_key, max_uses, expiry_str, type_name = generate_report_key(license_type, custom_uses, custom_months)
        st.success(f"已生成 {type_name} Report Key：")
        st.code(new_key, language="text")
        st.write(f"可使用次数：{max_uses} 次，有效期至：{expiry_str[:10]}")
    
    st.markdown("---")
    st.subheader("生成付费套餐授权码")

    col_price1, col_price2, col_price3 = st.columns(3)
    with col_price1:
        st.markdown("**单次通行**")
        st.markdown("18元 / 3美元")
        st.markdown("1次 · 无有效期")
        if st.button("生成单次通行码"):
            new_key, max_uses, expiry_str, _ = generate_report_key("custom", custom_uses=1, custom_months=9999)
            st.success(f"单次通行授权码：")
            st.code(new_key, language="text")
            st.write(f"次数：{max_uses}，有效期：无限制（至 {expiry_str[:10]}）")
    
    with col_price2:
        st.markdown("**100次套餐**")
        st.markdown("180元 / 30美元")
        st.markdown("100次 · 1个月")
        if st.button("生成100次套餐码"):
            new_key, max_uses, expiry_str, _ = generate_report_key("custom", custom_uses=100, custom_months=1)
            st.success(f"100次套餐授权码：")
            st.code(new_key, language="text")
            st.write(f"次数：{max_uses}，有效期：1个月（至 {expiry_str[:10]}）")
    
    with col_price3:
        st.markdown("**1200次套餐**")
        st.markdown("1200元 / 200美元")
        st.markdown("1200次 · 12个月")
        if st.button("生成1200次套餐码"):
            new_key, max_uses, expiry_str, _ = generate_report_key("custom", custom_uses=1200, custom_months=12)
            st.success(f"1200次套餐授权码：")
            st.code(new_key, language="text")
            st.write(f"次数：{max_uses}，有效期：12个月（至 {expiry_str[:10]}）")
    
    st.markdown("---")
    st.subheader("已生成的所有 Report Key")
    for key, data in st.session_state.usage_db.items():
        expiry = datetime.fromisoformat(data["expiry"]).strftime("%Y-%m-%d")
        st.write(f"- {key}: {data['remaining']} 次剩余, 有效期至 {expiry}")
    
    st.markdown("---")
    st.subheader("永久修改 API Key")
    st.markdown("请前往 [Streamlit Cloud Secrets](https://share.streamlit.io/) 修改 `AI_API_KEY`、`AI_BASE_URL` 和 `AI_MODEL_NAME`，然后重启应用。")

# ================== 右上角按钮 ==================
col1, col2, col3, col4 = st.columns([8, 1, 1, 1])
with col2:
    if st.button("中文", key="zh_btn"):
        st.session_state.lang = "zh"
        st.rerun()
with col3:
    if st.button("English", key="en_btn"):
        st.session_state.lang = "en"
        st.rerun()
with col4:
    if st.button("⚙️", key="settings_btn"):
        if st.session_state.admin_logged_in:
            admin_settings_dialog()
        else:
            admin_login_dialog()

# ================== 语言文本（包含完整 report_prompt，内容与原文件一致，此处省略以节省篇幅） ==================
# 注意：由于长度限制，此处省略 TEXTS 字典。请从您提供的 app with payment_test.py 中复制完整的 TEXTS 内容到此处。
# 实际使用时必须包含完整的 TEXTS，否则应用会出错。
TEXTS = {
    "zh": {
        # 请复制原文件中的完整中文内容
    },
    "en": {
        # 请复制原文件中的完整英文内容
    }
}
# 警告：上述 TEXTS 不完整！请务必从原附件中复制完整的 TEXTS 字典替换此处。

# ================== 获取当前语言 ==================
lang = st.session_state.lang
t = TEXTS[lang]

st.title(t["title"])

# ================== 支付回调处理（修复复制按钮和手动返回） ==================
params = st.query_params
if "order_success" in params and "plan" in params:
    plan = params["plan"]
    customer_email = params.get("email", None)
    current_lang = st.session_state.lang
    
    if current_lang == "zh":
        if plan == "single":
            uses = 1
            months = 9999
            plan_name = "单次通行"
        elif plan == "100":
            uses = 100
            months = 1
            plan_name = "100次套餐"
        elif plan == "1200":
            uses = 1200
            months = 12
            plan_name = "1200次套餐"
        else:
            uses = 0
            months = 0
            plan_name = "未知"
    else:
        if plan == "single":
            uses = 1
            months = 9999
            plan_name = "Single Pass"
        elif plan == "100":
            uses = 100
            months = 1
            plan_name = "100 Credits"
        elif plan == "1200":
            uses = 1200
            months = 12
            plan_name = "1200 Credits"
        else:
            uses = 0
            months = 0
            plan_name = "Unknown"
    
    if uses > 0:
        new_key, max_uses, expiry_str, _ = generate_report_key("custom", custom_uses=uses, custom_months=months)
        st.session_state.current_report_key = new_key
        
        # 发送邮件（静默）
        if customer_email:
            send_license_email(customer_email, new_key, plan_name, max_uses, expiry_str[:10], lang=current_lang)
        
        # 显示成功消息和复制按钮（增强复制功能）
        st.success(f"✅ 支付成功！您的授权码已生成并自动填入下方输入框。")
        
        # 使用自定义 HTML + JavaScript 确保复制功能正常
        copy_js = f"""
        <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-top: 10px;">
            <code id="license-key" style="font-size: 16px;">{new_key}</code>
            <button id="copy-btn" style="margin-left: 10px;">📋 复制授权码</button>
        </div>
        <p style="margin-top: 10px;">⚠️ 请务必保存好此授权码，下次使用时可复制粘贴到左侧输入框。</p>
        <script>
            document.getElementById('copy-btn').addEventListener('click', function() {{
                const code = document.getElementById('license-key').innerText;
                navigator.clipboard.writeText(code).then(function() {{
                    alert('授权码已复制到剪贴板！');
                }}, function(err) {{
                    alert('复制失败，请手动复制。');
                }});
            }});
        </script>
        """
        st.markdown(copy_js, unsafe_allow_html=True)
        
        # 显示手动返回按钮，不自动刷新
        if st.button("✅ 返回并继续使用"):
            # 清除 URL 参数
            st.query_params.clear()
            st.rerun()
    else:
        st.error("❌ 支付失败或套餐无效，请联系客服。")
        st.query_params.clear()

# ================== 支付对话框 ==================
@st.dialog("购买+解锁")
def purchase_dialog():
    st.markdown("### 选择套餐")
    st.markdown("""
| 套餐 | 价格 | 次数 | 有效期 |
|------|------|------|--------|
| 单次通行 | 18元 / 3美元 | 1次 | 无限制 |
| 100次套餐 | 180元 / 30美元 | 100次 | 1个月 |
| 1200次套餐 | 1200元 / 200美元 | 1200次 | 12个月 |
""")
    st.markdown("#### 🌍 国际支付（Stripe）")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.link_button("🎟️ Single Pass\n$3", "https://buy.stripe.com/test_9B67sL0Wh7298Nuaxk8og00")
    with col2:
        st.link_button("📦 100 Credits\n$30", "https://buy.stripe.com/9B6cN5bAVcmt5Bi7l88og02")
    with col3:
        st.link_button("🚀 1200 Credits\n$200", "https://buy.stripe.com/9B67sL0Wh7298Nuaxk8og00")
    st.markdown("#### 🇨🇳 国内支付（支付宝/微信）")
    st.info("国内支付即将开放，敬请期待。")
    st.markdown("支付成功后会自动跳回本页面，授权码将自动填入并激活。")

# ================== 侧边栏 ==================
with st.sidebar:
    report_key_input = st.text_input(
        t["report_key_label"],
        value=st.session_state.current_report_key,
        type="password",
        key="report_key_widget",
        on_change=lambda: setattr(st.session_state, 'current_report_key', st.session_state.report_key_widget)
    )
    if report_key_input:
        valid, remaining, expiry_str, lic_type = activate_license(report_key_input)
        if valid:
            st.success(f"授权成功！剩余 {remaining} 次，有效期至 {expiry_str[:10]}")
            st.session_state.current_report_key = report_key_input
        else:
            st.error("授权码无效或已过期")
            st.session_state.current_report_key = ""
            st.session_state.current_license_type = None
    if st.session_state.admin_logged_in:
        st.info("管理员模式：无限使用")
    else:
        if report_key_input and is_premium_user(report_key_input):
            remaining_str, expiry_str = get_remaining_info(report_key_input)
            st.markdown(f"**{t['license_info']}**")
            st.write(f"{t['remaining_label']}: {remaining_str}")
            st.write(f"{t['expiry_label']}: {expiry_str}")
        else:
            st.warning(t["no_license"])
    st.markdown("---")
    st.markdown(t["contact_info"])
    st.markdown("---")
    
    # ================== 购买引导（侧边栏） ==================
    st.markdown(f"## {t['purchase_title']}")
    st.markdown("""
| 套餐 | 价格 | 次数 | 有效期 |
|------|------|------|--------|
| 单次通行 | 18元 / 3美元 | 1次 | 无限制 |
| 100次套餐 | 180元 / 30美元 | 100次 | 1个月 |
| 1200次套餐 | 1200元 / 200美元 | 1200次 | 12个月 |
""")
    st.markdown("#### 🌍 国际支付（Stripe）")
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.link_button("🎟️ Single Pass\n$3", "https://buy.stripe.com/test_9B67sL0Wh7298Nuaxk8og00")
    with col_s2:
        st.link_button("📦 100 Credits\n$30", "https://buy.stripe.com/9B6cN5bAVcmt5Bi7l88og02")
    with col_s3:
        st.link_button("🚀 1200 Credits\n$200", "https://buy.stripe.com/9B67sL0Wh7298Nuaxk8og00")
    st.markdown("#### 🇨🇳 国内支付（支付宝/微信）")
    st.info("国内支付即将开放，敬请期待。")
    st.info("支付成功后会自动跳回本页面，授权码将自动填入并激活。")
    st.markdown("---")
    
    st.markdown(f"## {t['sidebar_title']}")
    st.markdown(t["sidebar_basis"])
    for item in t["basis_items"]:
        st.markdown(f"- {item}")
    st.markdown("---")
    
    analyst_name = st.text_input(t["analyst_name_label"], placeholder=t["analyst_name_ph"])
    analyst_title = st.text_input(t["analyst_title_label"], placeholder=t["analyst_title_ph"])
    if analyst_name:
        st.markdown(f"**{t['analyst_name_label']}: {analyst_name}**")
        if analyst_title:
            st.markdown(f"_{analyst_title}_")
    else:
        st.caption(t["analyst_name_ph"])
    
    st.markdown("---")
    st.markdown(f"**{t['api_status']}**")
    if st.session_state.ai_api_key:
        st.success(t["api_configured"])
    else:
        st.error(t["api_not_configured"])

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

spinner_placeholder = st.empty()

# ================== 报告生成逻辑 ==================
if submitted:
    if not product_name:
        st.error(t["product_name_missing"])
    elif not st.session_state.ai_api_key:
        st.error(t["api_key_missing"])
    else:
        can_generate = True
        if st.session_state.admin_logged_in:
            can_generate = True
        elif is_premium_user(report_key_input):
            if not consume_usage(report_key_input):
                st.error(t["trial_ended"])
                can_generate = False
        else:
            can_generate = True
        if can_generate:
            st.session_state.pulse_active = True
            with spinner_placeholder.container():
                st.markdown(f'<div style="text-align: center; margin-top: 10px;">{t["generating"]}</div>', unsafe_allow_html=True)
                with st.spinner(""):
                    try:
                        if analyst_name:
                            if analyst_title:
                                analyst_info = f"{analyst_name} ({analyst_title})"
                            else:
                                analyst_info = analyst_name
                        else:
                            analyst_info = "AI 分析师（基于行业数据库）" if lang == "zh" else "AI Analyst (based on industry database)"
                        
                        client = openai.OpenAI(
                            api_key=st.session_state.ai_api_key,
                            base_url=st.session_state.ai_base_url,
                        )
                        prompt_template = t["report_prompt"]
                        target_markets_str = ", ".join(target_markets)
                        prompt = prompt_template.format(
                            product_name=product_name,
                            product_description=product_description or "未提供",
                            target_markets=target_markets_str,
                            target_users=target_users or "未提供",
                            channel_status=channel_status,
                            channel_detail=channel_detail or "未提供",
                            brand_status=brand_status
                        )
                        response = client.chat.completions.create(
                            model=st.session_state.ai_model_name,
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.7,
                        )
                        report_content = response.choices[0].message.content
                        
                        if lang == "zh":
                            current_date = datetime.now().strftime("%Y年%m月%d日")
                            report_content = re.sub(r'\d{4}年\d{1,2}月\d{1,2}日', current_date, report_content)
                            report_content = re.sub(r'\d{4}-\d{2}-\d{2}', current_date, report_content)
                        else:
                            current_date = datetime.now().strftime("%B %d, %Y")
                            report_content = re.sub(r'\d{4}-\d{2}-\d{2}', current_date, report_content)
                            report_content = re.sub(r'[A-Z][a-z]+ \d{1,2}, \d{4}', current_date, report_content)
                        
                        report_content = report_content.replace("{{CURRENT_DATE}}", current_date)
                        report_content = report_content.replace("{{ANALYST_INFO}}", analyst_info)
                        if lang == "zh":
                            report_content = re.sub(r'(\| 分析人 \|).*?(\|)', rf'\1 {analyst_info} \2', report_content, flags=re.DOTALL)
                        else:
                            report_content = re.sub(r'(\| Analyst \|).*?(\|)', rf'\1 {analyst_info} \2', report_content, flags=re.DOTALL)
                        report_content = re.sub(r'\*+', '', report_content)
                        
                        if lang == "zh":
                            st.session_state.report_content_zh = report_content
                        else:
                            st.session_state.report_content_en = report_content
                        
                        st.session_state.pulse_active = False
                        st.rerun()
                    except Exception as e:
                        st.session_state.pulse_active = False
                        st.error(f"{t['error_prefix']}{e}")

# ================== 显示报告 ==================
current_report = None
if lang == "zh":
    current_report = st.session_state.report_content_zh
else:
    current_report = st.session_state.report_content_en

if current_report:
    premium = is_premium_user(report_key_input)
    add_security_css(disable=premium)
    show_watermark = not premium
    add_dynamic_watermark(lang, hide=not show_watermark)
    st.markdown(f"## {t['report_title']}")
    st.markdown(current_report, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(f"### {t['download_section']}")
    if premium:
        doc = Document()
        markdown_to_docx(current_report, doc)
        doc_bytes = BytesIO()
        doc.save(doc_bytes)
        doc_bytes.seek(0)
        st.download_button(
            label=t["download_btn"],
            data=doc_bytes,
            file_name=f"{product_name}_Feasibility_Report.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    else:
        if st.button(t["download_unlock_btn"], use_container_width=True):
            purchase_dialog()
    
    if st.button(t["back_btn"]):
        if lang == "zh":
            st.session_state.report_content_zh = None
        else:
            st.session_state.report_content_en = None
        st.rerun()
else:
    st.markdown("---")
    st.caption(t["footer"])
