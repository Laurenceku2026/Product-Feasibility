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
        st.markdown("3次 · 无有效期")
        if st.button("生成单次通行码"):
            new_key, max_uses, expiry_str, _ = generate_report_key("custom", custom_uses=3, custom_months=9999)
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
    
    # 从 usage_db 中提取数据，按生成时间倒序排序
    records = []
    for key, data in st.session_state.usage_db.items():
        # 兼容旧记录（可能没有 generated_at）
        gen_time = data.get("generated_at")
        if gen_time:
            try:
                gen_dt = datetime.fromisoformat(gen_time)
            except:
                gen_dt = datetime.min
        else:
            gen_dt = datetime.min
        records.append({
            "授权码": key,
            "类型": data.get("type", "unknown"),
            "剩余次数": data["remaining"],
            "总使用次数": data.get("total_uses", 0),
            "有效期至": data["expiry"][:10] if data["expiry"] else "永久",
            "生成时间": gen_dt.strftime("%Y-%m-%d %H:%M:%S") if gen_dt != datetime.min else "未知"
        })
    # 按生成时间倒序排序（最新的在前）
    records.sort(key=lambda x: x["生成时间"], reverse=True)
    
    # 选择显示条数
    show_limit = st.selectbox("显示条数", ["最近10条", "最近20条", "最近50条", "全部"], index=0)
    if show_limit == "最近10条":
        limit = 10
    elif show_limit == "最近20条":
        limit = 20
    elif show_limit == "最近50条":
        limit = 50
    else:
        limit = len(records)
    
    display_records = records[:limit]
    
    # 显示表格
    if display_records:
        df = pd.DataFrame(display_records)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("暂无授权码记录")
    
    # 导出 Excel（所有记录，不限于显示条数）
    if st.button("📥 导出所有授权码为 Excel"):
        if records:
            df_all = pd.DataFrame(records)
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_all.to_excel(writer, sheet_name="授权码列表", index=False)
            excel_data = output.getvalue()
            st.download_button(
                label="点击下载 Excel 文件",
                data=excel_data,
                file_name=f"report_keys_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("暂无数据可导出")
    
    st.markdown("---")
    st.subheader("永久修改 API Key")
    st.markdown("请前往 [Streamlit Cloud Secrets](https://share.streamlit.io/) 修改 `AI_API_KEY`、`AI_BASE_URL` 和 `AI_MODEL_NAME`，然后重启应用。")
