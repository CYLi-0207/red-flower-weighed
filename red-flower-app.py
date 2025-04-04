import streamlit as st
import pandas as pd
from io import BytesIO

# ===== 页面基础配置 =====
st.set_page_config(page_title="小红花分析系统", layout="wide")
st.title("🏵️ 小红花数据分析系统")
st.warning("""
**重要提示**  
本系统根据2025.4.4版本的小红花数据设计，数据格式变更可能导致错误，请联系管理员
""")

# ===== 文件上传模块 =====
with st.sidebar:
    uploaded_flower = st.file_uploader("上传小红花数据 (Excel)", type="xlsx")
    uploaded_roster = st.file_uploader("上传花名册数据 (Excel)", type="xlsx")

# ===== 字段校验函数 =====
def validate_columns(flower_df, roster_df):
    required_flower = {'收花人系统号', '送花人系统号', '收花人姓名'}
    required_roster = {'员工系统号', '三级组织', '四级组织', '花名'}
    
    errors = []
    if missing := required_flower - set(flower_df.columns):
        errors.append(f"小红花数据缺少字段: {', '.join(missing)}")
    if missing := required_roster - set(roster_df.columns):
        errors.append(f"花名册数据缺少字段: {', '.join(missing)}")
    return errors

# ===== 数据处理函数 =====
def process_data(flower_df, roster_df):
    # 示例处理步骤（根据实际需求修改）
    # Step 1: 合并花名册数据
    merged_df = pd.merge(
        flower_df,
        roster_df[['员工系统号', '三级组织', '花名']],
        left_on='收花人系统号',
        right_on='员工系统号',
        how='left'
    )
    
    # Step 2: 生成统计报表
    org_stats = merged_df.groupby('三级组织')['收花人系统号'].count().reset_index(name='收花总数')
    
    # Step 3: 格式化输出
    final_df = org_stats.sort_values('收花总数', ascending=False)
    return merged_df, final_df

# ===== Excel文件生成器 =====
def generate_excel(*dfs):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for i, df in enumerate(dfs, 1):
            df.to_excel(writer, sheet_name=f'Sheet{i}', index=False)
    return output.getvalue()

# ===== 主流程控制 =====
if st.button("🚀 开始分析", type="primary"):
    if not (uploaded_flower and uploaded_roster):
        st.error("请先上传两个数据文件")
        st.stop()
    
    try:
        # 读取数据
        flower_df = pd.read_excel(uploaded_flower)
        roster_df = pd.read_excel(uploaded_roster)
        
        # 字段校验
        if errors := validate_columns(flower_df, roster_df):
            st.error("## 字段校验失败")
            for err in errors:
                st.error(f"🔥 {err}")
            st.stop()
            
        # 数据处理
        with st.spinner("正在生成分析报告..."):
            processed_df, result_df = process_data(flower_df, roster_df)
            excel_file = generate_excel(processed_df, result_df)
            
        # 结果展示
        st.success("分析完成！")
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="下载完整数据",
                data=generate_excel(processed_df),
                file_name="processed_data.xlsx"
            )
        with col2:
            st.download_button(
                label="下载统计报告",
                data=generate_excel(result_df),
                file_name="summary_report.xlsx"
            )
            
        # 显示预览
        with st.expander("数据预览"):
            st.dataframe(result_df.head(10))
            
    except Exception as e:
        st.error(f"发生错误: {str(e)}")
