"""
多智能体AI旅行规划助手 - Streamlit前端界面
使用两个专门的智能体协作完成详细的旅行规划
"""

import streamlit as st
import asyncio
import os
import base64
from datetime import date
from fpdf import FPDF

# 导入多智能体模块
from multi_agent_travel import (
    MultiAgentTravelPlanner,
    run_multi_agent_travel_planner,
    handle_multi_agent_follow_up,
    build_travel_message,
    build_context_message
)

# 导入提示词模块
from travel_prompts import QUICK_QUESTIONS

# 配置页面 - 必须是第一个 Streamlit 命令
st.set_page_config(
    page_title="多智能体AI旅行规划助手",
    page_icon="🤖✈️",
    layout="wide"
)

# 设置默认的API密钥环境变量
os.environ.setdefault("SEARCHAPI_API_KEY", "5722Vw5rYoJTVHyffqNph3F4")
os.environ.setdefault("OPENAI_API_KEY", "sk-widDrKmkgrnCsmVg281bD224F984400eBb4586657a519a68")
os.environ.setdefault("SEARCHAPI_API_KEY", "ESHHZnUfrzw6yWyzfnXxA2jz")


def create_travel_plan_pdf(travel_plan_text, source, destination, travel_dates, budget):
    """创建旅行计划的PDF文档"""
    try:
        # 创建PDF对象
        pdf = FPDF()
        pdf.add_page()
        
        # 设置字体
        pdf.set_font('Arial', 'B', 16)
        
        # 处理文本，转换为ASCII兼容格式
        def clean_text(text):
            return text.encode('ascii', 'ignore').decode('ascii')
        
        # 清理输入数据
        source_clean = clean_text(source)
        destination_clean = clean_text(destination)
        
        # 标题
        try:
            pdf.cell(0, 10, f'Multi-Agent Travel Plan: {source_clean} to {destination_clean}', 0, 1, 'C')
        except:
            pdf.cell(0, 10, 'Multi-Agent Travel Plan', 0, 1, 'C')
        pdf.ln(5)
        
        # 基本信息
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, f'From: {source_clean}', 0, 1)
        pdf.cell(0, 8, f'To: {destination_clean}', 0, 1)
        pdf.cell(0, 8, f'Dates: {travel_dates[0]} to {travel_dates[1]}', 0, 1)
        pdf.cell(0, 8, f'Budget: ${budget} USD', 0, 1)
        pdf.ln(8)
        
        # 旅行计划内容
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 8, 'Multi-Agent Travel Plan Details:', 0, 1)
        pdf.ln(3)
        
        # 处理旅行计划文本
        clean_plan = clean_text(travel_plan_text)
        
        # 分行处理
        lines = clean_plan.split('\n')
        for line in lines:
            if len(line.strip()) > 0:
                try:
                    pdf.cell(0, 6, line[:90], 0, 1)  # 限制每行长度
                except:
                    continue
        
        # 返回PDF字节数据
        return pdf.output(dest='S').encode('latin-1')
    except Exception as e:
        # 如果还是失败，创建一个简化版本
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Multi-Agent Travel Plan', 0, 1, 'C')
            pdf.ln(10)
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 8, f'From: {source}', 0, 1)
            pdf.cell(0, 8, f'To: {destination}', 0, 1)
            pdf.cell(0, 8, f'Budget: ${budget}', 0, 1)
            return pdf.output(dest='S').encode('latin-1')
        except Exception as e2:
            return None


def create_download_link(pdf_bytes, filename):
    """创建PDF下载链接"""
    if pdf_bytes:
        b64 = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}">📄 下载PDF旅行计划</a>'
        return href
    return None


def create_text_download_link(text_content, filename):
    """创建文本文件下载链接"""
    try:
        # 清理文本内容
        clean_content = text_content.encode('utf-8', errors='ignore').decode('utf-8')
        b64 = base64.b64encode(clean_content.encode('utf-8')).decode()
        href = f'<a href="data:text/plain;charset=utf-8;base64,{b64}" download="{filename}">📄 下载文本版旅行计划</a>'
        return href
    except Exception as e:
        return None


def display_multi_agent_status():
    """显示多智能体系统状态和工作流程"""
    with st.expander("🤖 多智能体AI旅行规划系统", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🔍 信息收集智能体")
            st.markdown("""
            **主要职责：**
            - 🌍 目的地研究与分析
            - ✈️ 航班信息搜索
            - 🏨 住宿选项收集
            - 🍽️ 餐饮信息搜索
            - 🎯 景点活动收集
            - 🚗 交通方案研究
            - 🌤️ 天气信息获取
            - 📋 实用信息整理
            """)
            
        with col2:
            st.markdown("### 📅 行程规划智能体")
            st.markdown("""
            **主要职责：**
            - 🛫 航班预订建议
            - 🏨 住宿方案推荐
            - 📅 详细日程安排
            - 🍽️ 餐饮计划制定
            - 🚗 交通路线规划
            - 💰 预算分配管理
            - 🔄 备选方案设计
            - 📝 实用指南编制
            """)
        
        st.markdown("### 🔄 多智能体协作流程")
        st.markdown("""
        1. **信息收集阶段** (3-4分钟)
           - 🔍 信息收集智能体启动，全面搜索目的地相关信息
           - 📊 收集航班、酒店、餐厅、景点、交通等各类详细数据
           - 🗂️ 按类别整理所有收集到的信息
        
        2. **行程规划阶段** (2-3分钟)  
           - 📋 行程规划智能体接收收集到的信息
           - 🎯 基于用户偏好和预算制定个性化方案
           - 📅 生成详细的日程安排和预算分解
        
        3. **方案优化阶段** (1分钟)
           - 🔧 优化行程安排，确保时间合理
           - 💡 提供备选方案和实用建议
           - ✅ 最终输出完整的旅行规划方案
        """)


def create_progress_tracker():
    """创建多智能体进度跟踪器"""
    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    
    def update_progress(step, total_steps, message):
        progress = step / total_steps
        progress_placeholder.progress(progress)
        
        # 根据步骤显示不同的图标和消息
        if step <= 4:
            status_placeholder.info(f"🔍 **信息收集智能体**: {message}")
        else:
            status_placeholder.success(f"📅 **行程规划智能体**: {message}")
    
    return update_progress


def setup_sidebar():
    """设置侧边栏API密钥配置"""
    with st.sidebar:
        st.header("🔑 API 密钥配置")
        st.markdown("请输入您的 API 密钥以使用多智能体旅行规划系统。")
        
        # 模型提供商选择
        st.session_state.model_provider = st.selectbox(
            "🤖 选择AI模型提供商",
            ["OpenAI", "Gemini"],
            index=["OpenAI", "Gemini"].index(st.session_state.model_provider),
            help="选择您喜欢的AI模型提供商"
        )

        # API 密钥输入字段
        st.session_state.searchapi_key = st.text_input(
            "SearchAPI 密钥",
            value=st.session_state.searchapi_key,
            type="password",
            help="用于信息收集智能体访问Google搜索、地图、酒店、航班等所有搜索功能"
        )
        
        # 根据选择的模型提供商显示相应的API密钥输入
        if st.session_state.model_provider == "OpenAI":
            st.session_state.openai_key = st.text_input(
                "OpenAI API 密钥",
                value=st.session_state.openai_key,
                type="password",
                help="用于两个智能体的AI推理能力"
            )
        elif st.session_state.model_provider == "Gemini":
            st.session_state.gemini_key = st.text_input(
                "Gemini API 密钥",
                value=st.session_state.gemini_key,
                type="password",
                help="用于两个智能体的AI推理能力"
            )
        
        # 检查是否填写了所有必需的 API 密钥
        required_keys = [st.session_state.searchapi_key]
        
        # 根据选择的模型添加相应的API密钥检查
        if st.session_state.model_provider == "OpenAI":
            required_keys.append(st.session_state.openai_key)
        elif st.session_state.model_provider == "Gemini":
            required_keys.append(st.session_state.gemini_key)
        
        all_keys_filled = all(required_keys)

        if not all_keys_filled:
            st.error("❌ 请填写所有必需的 API 密钥以启用多智能体系统")
        else:
            st.success("✅ 多智能体系统已就绪")
        
        # 显示当前选择的模型信息
        if st.session_state.model_provider == "OpenAI":
            st.info("🤖 使用 OpenAI GPT-4o-mini 驱动两个智能体")
        elif st.session_state.model_provider == "Gemini":
            st.info("🤖 使用 Google Gemini 2.0 驱动两个智能体")
        
        # 多智能体系统介绍
        with st.expander("🤖 多智能体系统优势"):
            st.markdown("""
            ### 🎯 专业分工优势：
            - **信息收集智能体**: 专注于全面、准确的信息搜索
            - **行程规划智能体**: 专注于个性化方案制定
            
            ### 📈 质量提升：
            - 更详细的信息收集
            - 更专业的行程安排  
            - 更完整的旅行方案
            - 更好的用户体验
            
            ### ⚡ 效率优势：
            - 并行处理，提高速度
            - 专业分工，提高质量
            - 结构化输出，便于理解
            """)
        
        # 添加帮助链接
        with st.expander("📋 如何获取 API 密钥？"):
            st.markdown("""
            **SearchAPI 密钥:**
            1. 访问 [SearchAPI.io](https://www.searchapi.io/)
            2. 注册账户并获取免费API密钥
            3. 支持Google搜索、地图、酒店、航班搜索
            
            **OpenAI API 密钥:**
            1. 访问 [OpenAI Platform](https://platform.openai.com/)
            2. 注册并获取API密钥
            3. 或使用兼容的API服务
            
            **Gemini API 密钥:**
            1. 访问 [Google AI Studio](https://aistudio.google.com/)
            2. 获取免费的Gemini API密钥
            """)
        
        with st.expander("📦 多智能体功能说明"):
            st.markdown("""
            **信息收集智能体** 将搜索：
            - 🌍 目的地详细信息
            - ✈️ 航班选项和价格
            - 🏨 各类住宿推荐
            - 🍽️ 餐厅和美食信息
            - 🎯 景点和活动
            - 🚗 交通方式和费用
            
            **行程规划智能体** 将制定：
            - 📅 详细日程安排
            - 💰 预算分配方案
            - 🔄 备选计划
            - 📝 实用旅行指南
            """)
    
    return all_keys_filled


def setup_input_form():
    """设置输入表单"""
    # 标题和描述
    st.title("🤖✈️ 多智能体AI旅行规划助手")
    
    # 检查是否已有旅行计划
    if st.session_state.get('travel_plan'):
        st.success("🎉 您已有一个由多智能体系统制定的详细旅行计划！可以在下方对话区进行追问，或重新规划新的旅行。")
        
        # 显示当前计划概要
        with st.expander("📋 多智能体旅行计划概要", expanded=False):
            if st.session_state.get('collected_info'):
                st.markdown("#### 🔍 信息收集智能体收集的信息")
                st.text(st.session_state['collected_info'][:1000] + "..." if len(st.session_state['collected_info']) > 1000 else st.session_state['collected_info'])
                
            st.markdown("#### 📅 行程规划智能体制定的方案")
            st.text(st.session_state['travel_plan'][:1000] + "..." if len(st.session_state['travel_plan']) > 1000 else st.session_state['travel_plan'])
    
    st.markdown("""
    这个**多智能体AI旅行规划助手**使用先进的**双智能体协作架构**，通过专业分工提供更详细、更完整的旅行规划服务：

    ### 🤖 双智能体协作系统
    - **🔍 信息收集智能体**: 专门负责全面搜索和收集旅行相关信息
    - **📅 行程规划智能体**: 专门负责基于收集信息制定详细的个性化行程
    - **🤝 智能协作**: 两个智能体协作，确保信息全面性和方案完整性

    ### ✨ 核心功能特色
    - 🤖 灵活模型选择：支持OpenAI GPT-4o-mini 或 Google Gemini 2.0
    - 🔍 **专业信息收集**: 系统性搜索航班、酒店、景点、餐厅等所有旅行信息
    - 📋 **详细行程规划**: 基于收集信息制定日程安排、预算分配、交通规划
    - 🗺️ 地图搜索和地点发现（通过SearchAPI的Google Maps功能）
    - 🏨 酒店和住宿全方位搜索和比较
    - ✈️ 航班信息和价格深度比较
    - 📍 地点评论和评级详细分析
    - ⏰ 智能时间管理和行程优化
    - 🎯 高度个性化推荐系统
    - 💰 精确预算控制和成本优化
    - 💬 智能对话系统，支持计划修改和详细询问
    - 🔄 多层次备选方案设计

    ### 🚀 多智能体优势
    - **更全面的信息**: 专门的信息收集智能体确保信息的完整性和准确性
    - **更详细的规划**: 专门的规划智能体基于丰富信息制定更细致的方案
    - **更高的效率**: 分工合作，提高处理速度和质量
    - **更好的体验**: 结构化的输出，更易理解和执行
    """)

    # 创建两列用于输入
    col1, col2 = st.columns(2)

    with col1:
        # 出发地和目的地
        source = st.text_input("出发地", placeholder="输入您的出发城市")
        destination = st.text_input("目的地", placeholder="输入您的目的地城市")
        
        # 旅行日期
        travel_dates = st.date_input(
            "旅行日期",
            [date.today(), date.today()],
            min_value=date.today(),
            help="选择您的旅行日期"
        )

    with col2:
        # 预算
        budget = st.number_input(
            "预算（美元）",
            min_value=0,
            max_value=20000,
            step=100,
            help="输入您的旅行总预算"
        )
        
        # 旅行偏好
        travel_preferences = st.multiselect(
            "旅行偏好",
            ["冒险", "休闲", "观光", "文化体验", 
             "海滩", "山区", "豪华", "经济实惠", "美食",
             "购物", "夜生活", "家庭友好", "摄影", "历史探索"],
            help="选择您的旅行偏好"
        )

    # 其他偏好设置
    st.subheader("其他偏好设置")
    col3, col4 = st.columns(2)

    with col3:
        accommodation_type = st.selectbox(
            "首选住宿类型",
            ["任何", "酒店", "青年旅社", "公寓", "度假村", "民宿"],
            help="选择您首选的住宿类型"
        )
        
        transportation_mode = st.multiselect(
            "首选交通方式",
            ["火车", "巴士", "飞机", "租车", "地铁", "出租车"],
            help="选择您首选的交通方式"
        )

    with col4:
        dietary_restrictions = st.multiselect(
            "饮食限制",
            ["无", "素食", "纯素", "无麸质", "清真", "犹太洁食", "低盐", "低糖"],
            help="选择任何饮食限制"
        )
    
    return {
        'source': source,
        'destination': destination,
        'travel_dates': travel_dates,
        'budget': budget,
        'travel_preferences': travel_preferences,
        'accommodation_type': accommodation_type,
        'transportation_mode': transportation_mode,
        'dietary_restrictions': dietary_restrictions
    }


def handle_multi_agent_travel_planning(form_data, all_keys_filled):
    """处理多智能体旅行规划请求"""
    # 提交按钮和重置按钮
    col_submit, col_reset = st.columns([3, 1])

    with col_submit:
        submit_button = st.button("🚀 启动多智能体规划系统", type="primary", disabled=not all_keys_filled)

    with col_reset:
        if st.session_state.get('travel_plan'):
            if st.button("🔄 重新规划", help="清除当前计划，开始新的规划"):
                st.session_state['travel_plan'] = None
                st.session_state['collected_info'] = None
                st.session_state['travel_context'] = {}
                st.session_state['messages'] = []
                st.rerun()

    if submit_button:
        if not form_data['source'] or not form_data['destination']:
            st.error("❌ 请填写出发地和目的地")
        elif not form_data['travel_preferences']:
            st.error("❌ 请至少选择一个旅行偏好")
        else:
            # 构建旅行消息
            travel_message = build_travel_message(
                form_data['source'],
                form_data['destination'], 
                form_data['travel_dates'],
                form_data['budget'],
                form_data['travel_preferences'],
                form_data['accommodation_type'],
                form_data['transportation_mode'],
                form_data['dietary_restrictions']
            )
            
            # 显示多智能体状态
            display_multi_agent_status()
            
            # 创建进度跟踪器
            progress_callback = create_progress_tracker()
            
            # 运行多智能体系统
            with st.spinner("🤖 多智能体系统正在工作..."):
                try:
                    # 使用 asyncio 运行异步函数
                    result = asyncio.run(run_multi_agent_travel_planner(
                        travel_message,
                        model_provider=st.session_state.model_provider,
                        openai_key=st.session_state.openai_key,
                        gemini_key=st.session_state.gemini_key,
                        searchapi_key=st.session_state.searchapi_key,
                        progress_callback=progress_callback
                    ))
                    
                    if result['success']:
                        # 保存结果到会话状态
                        st.session_state['collected_info'] = result['collected_info']
                        st.session_state['travel_plan'] = result['detailed_itinerary']
                        st.session_state['travel_context'] = {
                            'source': form_data['source'],
                            'destination': form_data['destination'],
                            'travel_dates': form_data['travel_dates'],
                            'budget': form_data['budget'],
                            'preferences': form_data['travel_preferences']
                        }
                        
                        st.success("🎉 多智能体旅行规划完成！")
                        
                        # 显示结果
                        st.markdown("---")
                        st.header("📋 多智能体旅行规划结果")
                        
                        # 创建标签页显示不同内容
                        tab1, tab2 = st.tabs(["📅 完整旅行方案", "🔍 收集的信息详情"])
                        
                        with tab1:
                            st.markdown("### 📅 行程规划智能体制定的详细方案")
                            st.markdown(result['detailed_itinerary'])
                        
                        with tab2:
                            st.markdown("### 🔍 信息收集智能体收集的详细信息")
                            st.markdown(result['collected_info'])
                        
                        # 生成下载选项
                        generate_download_options(result['detailed_itinerary'], form_data)
                        
                    else:
                        st.error(f"❌ 多智能体规划失败: {result.get('error', '未知错误')}")
                        
                except Exception as e:
                    st.error(f"❌ 系统错误: {str(e)}")


def generate_download_options(response, form_data):
    """生成下载选项"""
    try:
        pdf_bytes = create_travel_plan_pdf(
            response, 
            form_data['source'], 
            form_data['destination'], 
            form_data['travel_dates'], 
            form_data['budget']
        )
        
        st.markdown("---")
        st.markdown("### 📥 下载选项")
        
        if pdf_bytes:
            pdf_filename = f"multi_agent_travel_plan_{form_data['source']}_{form_data['destination']}_{form_data['travel_dates'][0]}.pdf"
            pdf_download_link = create_download_link(pdf_bytes, pdf_filename)
            if pdf_download_link:
                st.markdown(pdf_download_link, unsafe_allow_html=True)
        
        # 提供文本版本下载作为备用
        text_filename = f"multi_agent_travel_plan_{form_data['source']}_{form_data['destination']}_{form_data['travel_dates'][0]}.txt"
        text_download_link = create_text_download_link(response, text_filename)
        if text_download_link:
            st.markdown(text_download_link, unsafe_allow_html=True)
            
    except Exception as e:
        st.warning(f"PDF生成遇到问题: {str(e)}")
        # 至少提供文本下载
        try:
            text_filename = f"multi_agent_travel_plan_{form_data['destination']}.txt"
            text_download_link = create_text_download_link(response, text_filename)
            if text_download_link:
                st.markdown(text_download_link, unsafe_allow_html=True)
        except:
            st.info("请复制上方内容保存您的旅行计划")


def display_image_gallery(images_data, title="图片展示"):
    """显示图片画廊"""
    if not images_data:
        return
    
    st.subheader(f"🖼️ {title}")
    
    # 根据不同的数据结构处理图片
    if isinstance(images_data, dict):
        for category, images in images_data.items():
            if images and len(images) > 0:
                st.write(f"**{category.replace('_', ' ').title()}:**")
                
                # 创建图片列
                cols = st.columns(3)
                for idx, img in enumerate(images[:6]):  # 最多显示6张图片
                    col_idx = idx % 3
                    with cols[col_idx]:
                        try:
                            if isinstance(img, dict) and 'url' in img:
                                st.image(
                                    img['url'], 
                                    caption=img.get('title', '未知标题'),
                                    use_column_width=True
                                )
                                if img.get('description'):
                                    st.caption(img['description'])
                            elif isinstance(img, str):
                                # 处理简单的URL字符串
                                st.image(img, caption="旅行图片", use_column_width=True)
                        except Exception as e:
                            st.error(f"无法加载图片: {e}")
    
    elif isinstance(images_data, list):
        cols = st.columns(3)
        for idx, img in enumerate(images_data[:9]):  # 最多显示9张图片
            col_idx = idx % 3
            with cols[col_idx]:
                try:
                    if isinstance(img, dict) and 'url' in img:
                        st.image(
                            img['url'],
                            caption=img.get('title', '未知标题'),
                            use_column_width=True
                        )
                        if img.get('description'):
                            st.caption(img['description'])
                    elif isinstance(img, str):
                        st.image(img, caption="旅行图片", use_column_width=True)
                except Exception as e:
                    st.error(f"无法加载图片: {e}")


def display_videos_section(videos_data):
    """显示视频部分"""
    if isinstance(videos_data, dict):
        for category, videos in videos_data.items():
            if videos and len(videos) > 0:
                st.write(f"**{category.replace('_', ' ').title()}:**")
                
                # 创建视频列
                cols = st.columns(2)  # 视频使用2列布局
                for idx, video in enumerate(videos[:4]):  # 最多显示4个视频
                    col_idx = idx % 2
                    with cols[col_idx]:
                        try:
                            if isinstance(video, dict):
                                # 显示视频信息
                                st.write(f"**{video.get('title', '未知标题')}**")
                                
                                # 显示缩略图（如果有）
                                if video.get('thumbnail_url'):
                                    st.image(
                                        video['thumbnail_url'],
                                        caption=f"视频时长: {video.get('duration', '未知')}",
                                        use_column_width=True
                                    )
                                
                                # 显示视频链接
                                if video.get('url'):
                                    st.markdown(f"🔗 [观看视频]({video['url']})")
                                
                                # 显示描述
                                if video.get('description'):
                                    st.caption(video['description'])
                                
                                # 显示发布信息
                                if video.get('channel'):
                                    st.caption(f"频道: {video['channel']}")
                                if video.get('published_date'):
                                    st.caption(f"发布日期: {video['published_date']}")
                                
                                st.markdown("---")
                            
                        except Exception as e:
                            st.error(f"无法加载视频信息: {e}")


def display_media_gallery(media_data, title="多媒体展示"):
    """显示多媒体画廊（图片和视频）"""
    if not media_data:
        return
    
    st.subheader(f"🎬 {title}")
    
    # 创建图片和视频的标签页
    if isinstance(media_data, dict):
        images_data = media_data.get('images', {})
        videos_data = media_data.get('videos', {})
        
        if images_data or videos_data:
            # 只有在有内容时才创建标签页
            tabs = []
            tab_labels = []
            
            if images_data:
                tab_labels.append("🖼️ 图片")
                
            if videos_data:
                tab_labels.append("🎥 视频")
            
            if len(tab_labels) > 1:
                tabs = st.tabs(tab_labels)
                tab_idx = 0
                
                # 显示图片
                if images_data:
                    with tabs[tab_idx]:
                        display_images_section(images_data)
                    tab_idx += 1
                
                # 显示视频
                if videos_data:
                    with tabs[tab_idx]:
                        display_videos_section(videos_data)
            else:
                # 只有一种类型的内容
                if images_data:
                    display_images_section(images_data)
                if videos_data:
                    display_videos_section(videos_data)
    else:
        # 兼容旧格式
        display_image_gallery(media_data, title)


def display_travel_info_with_media(travel_info):
    """显示包含多媒体的旅行信息"""
    st.header("🔍 信息收集智能体 - 详细旅行信息")
    
    # 创建标签页
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏛️ 目的地信息", "✈️ 航班信息", "🏨 住宿信息", 
        "🍽️ 餐饮信息", "🎯 景点活动", "🎬 多媒体展示"
    ])
    
    with tab1:
        if travel_info.get('destination_info'):
            st.json(travel_info['destination_info'])
        else:
            st.info("暂无目的地信息")
    
    with tab2:
        if travel_info.get('flights_info'):
            st.json(travel_info['flights_info'])
        else:
            st.info("暂无航班信息")
    
    with tab3:
        if travel_info.get('hotels_info'):
            st.json(travel_info['hotels_info'])
        else:
            st.info("暂无住宿信息")
    
    with tab4:
        if travel_info.get('restaurants_info'):
            st.json(travel_info['restaurants_info'])
        else:
            st.info("暂无餐饮信息")
    
    with tab5:
        if travel_info.get('attractions_info'):
            st.json(travel_info['attractions_info'])
        else:
            st.info("暂无景点信息")
    
    with tab6:
        # 优先使用新的media_info格式
        if travel_info.get('media_info'):
            display_media_gallery(travel_info['media_info'], "旅行目的地多媒体")
        elif travel_info.get('images_info'):
            # 兼容旧格式
            display_image_gallery(travel_info['images_info'], "旅行目的地图片")
        else:
            st.info("🎬 暂无多媒体信息 - 智能体将在下次搜索时收集更多图片和视频")


# 保持向后兼容
def display_travel_info_with_images(travel_info):
    """显示包含图片的旅行信息（向后兼容）"""
    display_travel_info_with_media(travel_info)


# ...existing code...


def init_session_state():
    """初始化会话状态"""
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []
    if 'travel_plan' not in st.session_state:
        st.session_state['travel_plan'] = None
    if 'collected_info' not in st.session_state:
        st.session_state['collected_info'] = None
    if 'travel_context' not in st.session_state:
        st.session_state['travel_context'] = {}
    if 'model_provider' not in st.session_state:
        st.session_state.model_provider = "OpenAI"
    if 'searchapi_key' not in st.session_state:
        st.session_state.searchapi_key = os.environ.get("SEARCHAPI_API_KEY", "")
    if 'openai_key' not in st.session_state:
        st.session_state.openai_key = os.environ.get("OPENAI_API_KEY", "")
    if 'gemini_key' not in st.session_state:
        st.session_state.gemini_key = ""
    if 'quick_question' not in st.session_state:
        st.session_state['quick_question'] = None


def main():
    """主函数"""
    # 初始化会话状态
    init_session_state()
    
    # 设置侧边栏
    all_keys_filled = setup_sidebar()
    
    # 设置输入表单
    form_data = setup_input_form()
    
    # 如果已有旅行计划，显示查看选项
    if st.session_state.get('travel_plan'):
        st.markdown("---")
        st.info("🎉 多智能体系统已为您制定了详细的旅行计划！您可以继续在下方进行深度对话。")
    
    # 处理多智能体旅行规划
    handle_multi_agent_travel_planning(form_data, all_keys_filled)


if __name__ == "__main__":
    main()
