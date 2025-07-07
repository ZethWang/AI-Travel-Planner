"""
多智能体AI旅行规划系统
使用两个专门的智能体协作完成详细的旅行规划：
1. 信息收集智能体 - 负责搜索和收集所有旅行相关信息
2. 行程规划智能体 - 负责整合信息并制定详细的旅行方案
"""

import asyncio
import os
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from agno.agent import Agent
from agno.tools.mcp import MultiMCPTools
from agno.models.openai import OpenAIChat
from agno.models.google import Gemini

# 导入API配置
from api_config import get_api_key, validate_api_setup

# 导入提示词模块
from travel_prompts import (
    TRAVEL_MESSAGE_TEMPLATE,
    CONTEXT_MESSAGE_TEMPLATE
)

# 导入智能体提示词
try:
    from agent_prompts import (
        INFORMATION_COLLECTOR_PROMPT,
        ITINERARY_PLANNER_PROMPT,
        FOLLOW_UP_AGENT_PROMPT,
        FOLLOW_UP_NO_SEARCH_PROMPT
    )
except ImportError:
    # 如果无法导入，使用内联简化版本
    INFORMATION_COLLECTOR_PROMPT = "你是旅行信息收集专家，负责搜索和收集全面的旅行信息。按JSON格式组织输出。"
    ITINERARY_PLANNER_PROMPT = "你是旅行行程规划专家，基于收集的信息制定详细、实用的旅行方案。"
    FOLLOW_UP_AGENT_PROMPT = "你是旅行咨询专家，回答用户对已有旅行计划的追问和修改需求。"
    FOLLOW_UP_NO_SEARCH_PROMPT = "你是旅行咨询专家，基于已有旅行计划回答用户追问。"


@dataclass
class TravelInfo:
    """旅行信息数据结构"""
    destination_info: Dict[str, Any] = None
    flights_info: Dict[str, Any] = None
    hotels_info: Dict[str, Any] = None
    restaurants_info: Dict[str, Any] = None
    attractions_info: Dict[str, Any] = None
    transportation_info: Dict[str, Any] = None
    weather_info: Dict[str, Any] = None
    local_tips: Dict[str, Any] = None
    media_info: Dict[str, Any] = None  # 多媒体信息字段，包含图片和视频



class MultiAgentTravelPlanner:
    """多智能体旅行规划系统"""
    
    def __init__(self, model_provider="OpenAI", openai_key=None, gemini_key=None, searchapi_key=None):
        """
        初始化多智能体旅行规划系统
        
        Args:
            model_provider: 模型提供商 ("OpenAI" 或 "Gemini")
            openai_key: OpenAI API密钥（可选，将从环境变量获取）
            gemini_key: Gemini API密钥（可选，将从环境变量获取）
            searchapi_key: SearchAPI密钥（可选，将从环境变量获取）
        """
        self.model_provider = model_provider
        # 优先使用传入的参数，否则从环境变量获取
        self.openai_key = openai_key or get_api_key("openai_key")
        self.gemini_key = gemini_key or get_api_key("gemini_key") 
        self.searchapi_key = searchapi_key or get_api_key("searchapi_key")
        
    def _validate_keys(self):
        """验证API密钥是否完整"""
        if not self.searchapi_key:
            raise ValueError("🚨 缺少 SearchAPI API 密钥")
        elif self.model_provider == 'OpenAI' and not self.openai_key:
            raise ValueError("🚨 缺少 OpenAI API 密钥")
        elif self.model_provider == 'Gemini' and not self.gemini_key:
            raise ValueError("🚨 缺少 Gemini API 密钥")
    
    def _get_model(self):
        """根据提供商获取相应的模型实例"""
        if self.model_provider == 'OpenAI':
            return OpenAIChat(
                id="gpt-4.1",  # 使用xi-ai支持的模型
                api_key=self.openai_key,
                base_url="https://api.xi-ai.cn/v1",
            )
        elif self.model_provider == 'Gemini':
            return Gemini(id="gemini-2.0-flash-exp", api_key=self.gemini_key)
        else:
            raise ValueError(f"不支持的模型提供商: {self.model_provider}")
    
    def _get_environment(self):
        """获取环境变量配置"""
        env = {
            **os.environ,
            "SEARCHAPI_API_KEY": self.searchapi_key
        }
        
        if self.model_provider == 'OpenAI':
            env["OPENAI_API_KEY"] = self.openai_key
        elif self.model_provider == 'Gemini':
            env["GOOGLE_API_KEY"] = self.gemini_key
            
        return env
    
    async def collect_travel_information(self, travel_request: str, progress_callback=None):
        """
        使用信息收集智能体收集旅行信息
        
        Args:
            travel_request: 旅行请求
            progress_callback: 进度回调函数
            
        Returns:
            str: 收集到的详细旅行信息（JSON格式）
        """
        if progress_callback:
            progress_callback(1, 8, "正在启动信息收集智能体...")
        
        # 验证API密钥
        self._validate_keys()
        
        # 获取环境变量和模型
        env = self._get_environment()
        model = self._get_model()
        
        async with MultiMCPTools(
            ["python /mnt/public/code/zzy/wzh/doremi/searchAPI-mcp/mcp_server.py"],
            env=env,
        ) as mcp_tools:
            
            if progress_callback:
                progress_callback(2, 8, "信息收集智能体开始工作...")
            
            # 创建信息收集智能体
            collector_agent = Agent(
                tools=[mcp_tools],
                model=model,
                name="旅行信息收集专家",
                instructions=INFORMATION_COLLECTOR_PROMPT,
                goal="全面收集旅行相关信息，为后续规划提供详实数据"
            )
            
            # 构建信息收集请求
            collection_request = f"""
            请为以下旅行需求收集全面的信息：

            {travel_request}

            请搜索并收集以下所有类别的详细信息：
            1. 目的地基本信息和文化特色
            2. 航班选项和价格信息
            3. 各类住宿选择（豪华、中档、经济型）
            4. 餐厅和美食推荐
            5. 主要景点和活动信息
            6. 当地交通方式和费用
            7. 天气预报和穿着建议
            8. 实用信息（签证、货币、习俗等）

            请确保信息详实、准确，包含具体的价格、时间、联系方式等实用细节。
            最后请按照指定的JSON格式组织所有收集到的信息。
            """
            
            if progress_callback:
                progress_callback(3, 8, "正在搜索目的地信息...")
            
            # 运行信息收集智能体
            collection_result = await collector_agent.arun(collection_request)
            
            if progress_callback:
                progress_callback(4, 8, "信息收集完成！")
            
            # 获取收集结果
            if hasattr(collection_result, 'content'):
                return collection_result.content
            elif hasattr(collection_result, 'messages') and collection_result.messages:
                return collection_result.messages[-1].content if hasattr(collection_result.messages[-1], 'content') else str(collection_result.messages[-1])
            else:
                return str(collection_result)
    
    async def create_detailed_itinerary(self, travel_request: str, collected_info: str, progress_callback=None):
        """
        使用行程规划智能体制定详细行程
        
        Args:
            travel_request: 原始旅行请求
            collected_info: 收集到的旅行信息
            progress_callback: 进度回调函数
            
        Returns:
            str: 详细的旅行行程方案
        """
        if progress_callback:
            progress_callback(5, 8, "正在启动行程规划智能体...")
        
        # 获取模型（不需要重新验证密钥和环境）
        model = self._get_model()
        
        if progress_callback:
            progress_callback(6, 8, "行程规划智能体开始制定方案...")
        
        # 创建行程规划智能体（不需要搜索工具，基于已收集的信息进行规划）
        planner_agent = Agent(
            model=model,
            name="旅行行程规划专家",
            instructions=ITINERARY_PLANNER_PROMPT,
            goal="基于收集的信息制定详细、实用的旅行行程方案"
        )
        
        # 构建行程规划请求
        planning_request = f"""
        基于以下收集到的详细旅行信息，请制定一个完整的旅行行程方案。

        ## 用户的旅行需求：
        {travel_request}

        ## 收集到的详细旅行信息：
        {collected_info}

        请基于以上信息制定一个详细、实用的旅行方案，包括：

        ### 🛫 航班预订建议
        - 具体推荐的航班信息（航班号、时间、价格、预订建议）
        - 机场信息和注意事项

        ### 🏨 住宿安排  
        - 根据用户偏好和预算推荐最适合的住宿
        - 包含具体酒店信息、价格、特色、预订建议

        ### 📅 详细日程安排
        - 按天分解的详细活动安排
        - 每日包含：时间安排、景点游览、餐饮安排、交通方式、预估费用
        - 确保时间安排合理，不过于紧张

        ### 🍽️ 餐饮推荐
        - 每餐的具体餐厅推荐
        - 特色菜品、价格区间、预订建议

        ### 🚗 交通安排
        - 机场往返交通方案
        - 日常出行交通规划
        - 交通费用预算

        ### 💰 详细预算分解
        - 各项费用的详细分解
        - 确保总费用在用户预算范围内
        - 提供节省费用的建议

        ### 📝 实用信息与注意事项
        - 天气和穿着建议
        - 重要联系方式
        - 当地习俗和注意事项
        - 安全提醒

        ### 🔄 备选方案
        - 雨天或突发情况的备选活动
        - 不同预算级别的选择
        - 行程调整建议

        请确保方案具体可行，包含足够的细节供用户直接执行。
        """
        
        if progress_callback:
            progress_callback(7, 8, "正在制定详细行程方案...")
        
        # 运行行程规划智能体
        planning_result = await planner_agent.arun(planning_request)
        
        if progress_callback:
            progress_callback(8, 8, "详细旅行方案制定完成！")
        
        # 获取规划结果
        if hasattr(planning_result, 'content'):
            return planning_result.content
        elif hasattr(planning_result, 'messages') and planning_result.messages:
            return planning_result.messages[-1].content if hasattr(planning_result.messages[-1], 'content') else str(planning_result.messages[-1])
        else:
            return str(planning_result)
    
    async def plan_travel_with_multi_agents(self, message: str, progress_callback=None):
        """
        使用多智能体系统完成完整的旅行规划
        
        Args:
            message: 用户的旅行规划请求消息
            progress_callback: 可选的进度回调函数
            
        Returns:
            dict: 包含详细信息收集结果和完整行程方案的字典
        """
        try:
            # 第一阶段：信息收集
            collected_info = await self.collect_travel_information(message, progress_callback)
            
            # 第二阶段：行程规划
            detailed_itinerary = await self.create_detailed_itinerary(message, collected_info, progress_callback)
            
            return {
                'collected_info': collected_info,
                'detailed_itinerary': detailed_itinerary,
                'success': True
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    async def handle_follow_up_question(self, question: str, travel_context: dict, progress_callback=None):
        """
        处理基于现有旅行计划的追问
        
        Args:
            question: 用户的追问
            travel_context: 旅行上下文信息
            progress_callback: 进度回调函数
            
        Returns:
            str: 针对追问的详细回答
        """
        if progress_callback:
            progress_callback(1, 4, "正在分析您的问题...")
        
        # 验证API密钥
        self._validate_keys()
        
        # 获取环境变量和模型
        env = self._get_environment()
        model = self._get_model()
        
        # 根据问题类型决定是否需要搜索工具
        needs_search = any(keyword in question.lower() for keyword in [
            '搜索', '查找', '推荐更多', '其他选择', '最新', '价格', '评价', 
            '替代', '附近', '比较', '更好的', '便宜', '高档', '最佳'
        ])
        
        if needs_search:
            if progress_callback:
                progress_callback(2, 4, "正在搜索最新信息...")
            
            async with MultiMCPTools(
                ["python /mnt/public/code/zzy/wzh/doremi/searchAPI-mcp/mcp_server.py"],
                env=env,
            ) as mcp_tools:
                # 使用带搜索工具的智能体
                follow_up_agent = Agent(
                    tools=[mcp_tools],
                    model=model,
                    name="旅行咨询专家",
                    instructions=FOLLOW_UP_AGENT_PROMPT,
                    goal="为用户的旅行计划追问提供专业、详细的咨询服务"
                )
                
                if progress_callback:
                    progress_callback(3, 4, "正在生成详细回答...")
                
                # 构建追问处理请求
                follow_up_request = f"""
                用户的旅行计划上下文信息：
                {travel_context}
                
                用户的具体问题：
                {question}
                
                请基于上述旅行计划上下文，针对用户的问题提供详细、实用的回答。
                如果需要最新信息，请主动搜索获取。
                """
                
                result = await follow_up_agent.arun(follow_up_request)
        else:
            if progress_callback:
                progress_callback(2, 4, "正在分析现有计划...")
            
            # 不需要搜索的问题，直接基于现有信息回答
            follow_up_agent = Agent(
                model=model,
                name="旅行咨询专家",
                instructions=FOLLOW_UP_NO_SEARCH_PROMPT,
                goal="为用户提供基于现有计划的专业咨询"
            )
            
            if progress_callback:
                progress_callback(3, 4, "正在生成专业建议...")
            
            # 构建基于现有信息的回答请求
            follow_up_request = f"""
            基于以下旅行计划上下文，请回答用户的问题：
            
            旅行计划上下文：
            {travel_context}
            
            用户问题：
            {question}
            
            请提供详细、实用的回答。
            """
            
            result = await follow_up_agent.arun(follow_up_request)
        
        if progress_callback:
            progress_callback(4, 4, "回答生成完成！")
        
        # 获取回答结果
        if hasattr(result, 'content'):
            return result.content
        elif hasattr(result, 'messages') and result.messages:
            return result.messages[-1].content if hasattr(result.messages[-1], 'content') else str(result.messages[-1])
        else:
            return str(result)


def build_travel_message(source, destination, travel_dates, budget, travel_preferences, 
                        accommodation_type, transportation_mode, dietary_restrictions):
    """
    构建旅行规划消息
    
    Args:
        source: 出发地
        destination: 目的地
        travel_dates: 旅行日期 [开始日期, 结束日期]
        budget: 预算
        travel_preferences: 旅行偏好列表
        accommodation_type: 住宿类型
        transportation_mode: 交通方式列表
        dietary_restrictions: 饮食限制列表
        
    Returns:
        str: 格式化的旅行规划请求消息
    """
    return TRAVEL_MESSAGE_TEMPLATE.format(
        source=source,
        destination=destination,
        start_date=travel_dates[0],
        end_date=travel_dates[1],
        budget=budget,
        preferences=', '.join(travel_preferences),
        accommodation_type=accommodation_type,
        transportation_mode=', '.join(transportation_mode),
        dietary_restrictions=', '.join(dietary_restrictions)
    )


def build_context_message(travel_plan, travel_context, user_question):
    """
    构建包含旅行计划上下文的对话消息
    
    Args:
        travel_plan: 当前的旅行计划内容
        travel_context: 旅行基本信息字典
        user_question: 用户的追问
        
    Returns:
        str: 包含上下文的完整消息
    """
    # 处理旅行日期
    travel_dates = travel_context.get('travel_dates', ['未设定', '未设定'])
    start_date = travel_dates[0] if isinstance(travel_dates, list) and len(travel_dates) > 0 else '未设定'
    end_date = travel_dates[1] if isinstance(travel_dates, list) and len(travel_dates) > 1 else '未设定'
    
    return CONTEXT_MESSAGE_TEMPLATE.format(
        travel_plan=travel_plan,
        source=travel_context.get('source', '未设定'),
        destination=travel_context.get('destination', '未设定'),
        start_date=start_date,
        end_date=end_date,
        budget=travel_context.get('budget', 0),
        preferences=', '.join(travel_context.get('preferences', [])),
        user_question=user_question
    )


# 异步运行多智能体系统的便捷函数
async def run_multi_agent_travel_planner(message: str, model_provider="OpenAI", 
                                       openai_key=None, gemini_key=None, searchapi_key=None, progress_callback=None):
    """
    运行多智能体旅行规划系统的便捷函数
    
    Args:
        message: 旅行规划请求消息
        model_provider: 模型提供商
        openai_key: OpenAI API密钥
        gemini_key: Gemini API密钥
        searchapi_key: SearchAPI密钥
        progress_callback: 进度回调函数
        
    Returns:
        dict: 包含收集信息和详细行程的结果字典
    """
    planner = MultiAgentTravelPlanner(
        model_provider=model_provider,
        openai_key=openai_key,
        gemini_key=gemini_key,
        searchapi_key=searchapi_key
    )
    
    return await planner.plan_travel_with_multi_agents(message, progress_callback)


# 异步处理追问的便捷函数
async def handle_multi_agent_follow_up(question: str, travel_context: dict, 
                                     model_provider="OpenAI", openai_key=None, gemini_key=None, 
                                     searchapi_key=None, progress_callback=None):
    """
    处理多智能体系统的追问
    
    Args:
        question: 用户追问
        travel_context: 旅行上下文
        model_provider: 模型提供商
        openai_key: OpenAI API密钥
        gemini_key: Gemini API密钥
        searchapi_key: SearchAPI密钥
        progress_callback: 进度回调函数
        
    Returns:
        str: 追问的详细回答
    """
    planner = MultiAgentTravelPlanner(
        model_provider=model_provider,
        openai_key=openai_key,
        gemini_key=gemini_key,
        searchapi_key=searchapi_key
    )
    
    return await planner.handle_follow_up_question(question, travel_context, progress_callback)