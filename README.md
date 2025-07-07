# AI 旅行规划助手 - 多智能体MCP版本

## 项目概述

这是一个基于多智能体架构和模型上下文协议（MCP）的智能旅行规划系统。系统采用双智能体协作模式，结合强大的搜索和规划能力，为用户提供全面、详细的个性化旅行方案。

## 核心特性

- 🤖 **多智能体协作**：专业化分工的信息收集和行程规划智能体
- 🔍 **智能搜索**：集成Google Maps、Google Flights、Google Hotels等多个搜索API
- 📅 **日历集成**：自动创建和管理旅行日程
- 🌍 **全球支持**：支持全球目的地的旅行规划
- 💎 **多模型支持**：支持OpenAI GPT和Google Gemini模型
- 📱 **现代UI**：基于Streamlit的直观用户界面
- 📄 **PDF导出**：生成专业的旅行计划PDF文档

## 项目架构

### 文件结构

```
├── app.py                    # 主应用程序（多智能体版本）
├── app_single.py            # 单智能体版本
├── multi_agent_travel.py    # 核心多智能体旅行规划逻辑
├── multi_agent_streamlit_app.py # 多智能体Streamlit界面
├── travel_agent.py          # 旅行智能体定义
├── agent_prompts.py         # 智能体系统提示词
├── travel_prompts.py        # 旅行规划提示词模板
├── team_config.py           # 智能体团队配置
├── api_config.py            # API配置管理
├── calendar_mcp.py          # 日历MCP集成
├── requirements.txt         # 项目依赖
├── .env                     # 环境变量配置
├── run_app.sh              # 运行脚本
└── README.md               # 项目文档
```

### 智能体架构

#### 1. 信息收集智能体 (Information Collector Agent)
- **职责**：专门负责搜索和收集旅行相关信息
- **工具**：Google Maps、Google Flights、Google Hotels、SearchAPI
- **输出**：结构化的旅行信息JSON数据
- **特点**：
  - 目的地研究和文化信息收集
  - 航班选项和价格比较
  - 住宿推荐和评价分析
  - 餐厅美食和当地特色发现
  - 景点活动和娱乐项目搜索
  - 交通方案和路线规划
  - 天气预报和穿着建议
  - 多媒体内容收集（图片、视频）

#### 2. 行程规划智能体 (Itinerary Planner Agent)
- **职责**：基于收集的信息制定详细旅行方案
- **输入**：信息收集智能体提供的结构化数据
- **输出**：完整的旅行行程规划
- **特点**：
  - 智能行程安排和时间优化
  - 预算分析和成本控制
  - 个性化推荐和偏好匹配
  - 风险评估和安全建议
  - 紧急情况应对预案
  - 详细的日程表制作

#### 3. MCP 工具集成

##### 3.1 搜索工具
- **Google Maps API**：地点信息、路线规划、本地搜索
- **Google Flights API**：航班搜索、价格比较、时刻表
- **Google Hotels API**：酒店预订、价格对比、设施查询
- **SearchAPI**：通用搜索、实时信息获取

##### 3.2 日历工具
- **Google Calendar API**：自动创建旅行日程
- **事件管理**：时区处理、提醒设置
- **日程同步**：与个人日历集成

#### 4. 模型支持
- **OpenAI GPT-4/GPT-3.5**：强大的推理和文本生成能力
- **Google Gemini**：多模态理解和创新思维
- **灵活切换**：用户可根据需求选择最适合的模型

## 快速开始

### 环境要求

- **Python 3.8+**：确保已安装 Python 3.8 或更高版本
- **API 密钥**：需要以下服务的API密钥
  - OpenAI API 密钥（必需）
  - SearchAPI 密钥（必需）
  - Google API 密钥（可选，用于Gemini模型）

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd ai_travel_planner_mcp_agent_team
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置API密钥**
   
   创建 `.env` 文件并配置以下变量：
   ```env
   # 必需的API密钥
   OPENAI_API_KEY=your_openai_api_key_here
   SEARCHAPI_API_KEY=your_searchapi_key_here
   
   # 可选的API密钥
   OPENAI_API_KEY2=your_backup_openai_key_here
   GOOGLE_API_KEY=your_google_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

### 运行应用

#### 方式一：使用脚本运行
```bash
# 使用提供的运行脚本
./run_app.sh

# 或运行多智能体版本
./run_multi_agent.sh
```

#### 方式二：直接运行
```bash
# 多智能体版本（推荐）
streamlit run app.py

# 单智能体版本
streamlit run app_single.py

# 独立的多智能体界面
streamlit run multi_agent_streamlit_app.py
```

### 使用指南

1. **启动应用**：在浏览器中打开 `http://localhost:8501`

2. **配置设置**：
   - 在侧边栏输入API密钥（如果未在.env中配置）
   - 选择首选的AI模型（OpenAI或Gemini）
   - 设置其他偏好选项

3. **输入旅行需求**：
   - 目的地和旅行日期
   - 预算范围和住宿偏好
   - 兴趣爱好和特殊需求
   - 旅行人数和类型

4. **获取规划结果**：
   - 查看详细的旅行行程
   - 下载PDF版本的旅行计划
   - 导出到Google日历（如已配置）

## 技术特色

### 1. 多智能体协作
- **专业化分工**：信息收集和行程规划分别由专门的智能体处理
- **协同工作**：智能体间通过结构化数据交换实现无缝协作
- **质量保证**：双重验证确保信息准确性和方案可行性

### 2. MCP (Model Context Protocol) 集成
- **标准化接口**：统一的工具调用和数据交换协议
- **扩展性强**：易于集成新的API服务和工具
- **高效通信**：优化的模型-工具交互机制

### 3. 智能搜索与规划
- **实时数据**：获取最新的航班、酒店、活动信息
- **个性化推荐**：基于用户偏好和历史数据的智能推荐
- **多维度优化**：时间、成本、体验的综合优化

### 4. 现代化用户体验
- **响应式设计**：适配不同设备和屏幕尺寸
- **实时反馈**：智能体工作状态的实时显示
- **多格式输出**：支持网页查看、PDF下载、日历导出

## 核心功能详解

### 🔍 智能信息收集
- **目的地研究**：文化背景、最佳游览时间、当地习俗
- **交通规划**：航班比价、路线优化、当地交通
- **住宿推荐**：多价位选择、位置分析、设施对比
- **美食发现**：特色餐厅、当地美食、价格范围
- **活动安排**：景点门票、娱乐项目、文化体验
- **实用信息**：签证要求、货币汇率、紧急联系方式

### 📅 智能行程规划
- **时间优化**：基于地理位置的合理路线安排
- **预算管理**：详细的成本分析和预算建议
- **个性化定制**：根据用户兴趣和偏好调整行程
- **风险评估**：安全提醒和应急预案
- **灵活调整**：支持行程修改和实时优化

### 📊 数据可视化
- **行程图表**：直观的时间线和地图展示
- **预算分析**：详细的费用分解和比较
- **天气趋势**：旅行期间的天气预报图表

## API密钥获取指南

### 1. OpenAI API密钥 (必需)
1. 访问 [OpenAI Platform](https://platform.openai.com)
2. 注册或登录账户
3. 导航到 API Keys 页面
4. 创建新的API密钥
5. 复制密钥到 `.env` 文件

### 2. SearchAPI密钥 (必需)
1. 访问 [SearchAPI](https://www.searchapi.io)
2. 注册账户并验证邮箱
3. 获取免费或付费的API密钥
4. 将密钥添加到 `.env` 文件

### 3. Google API密钥 (可选)
1. 访问 [Google Cloud Console](https://console.cloud.google.com)
2. 创建新项目或选择现有项目
3. 启用所需的API服务：
   - Google Maps API
   - Google Calendar API
   - Gemini API (如使用Gemini模型)
4. 创建API密钥并配置访问权限
5. 将密钥添加到 `.env` 文件

## 开发与定制

### 添加新的智能体

1. **定义智能体类型**
   ```python
   # 在 team_config.py 中添加新的智能体配置
   "new_agent": {
       "name": "新智能体名称",
       "role": "Agent Role",
       "description": "智能体描述",
       "primary_tools": ["tool1", "tool2"],
       "goal": "智能体目标和职责"
   }
   ```

2. **创建提示词模板**
   ```python
   # 在 agent_prompts.py 中添加系统提示词
   NEW_AGENT_PROMPT = """
   你是新的专业智能体...
   """
   ```

3. **集成到团队**
   ```python
   # 在多智能体系统中注册新智能体
   new_agent = Agent(
       name=config["name"],
       role=config["role"],
       instructions=NEW_AGENT_PROMPT,
       tools=tools,
       model=model
   )
   ```

### 扩展MCP工具

1. **添加新的API集成**
   ```python
   # 在适当的工具配置中添加新的MCP工具
   new_tools = MultiMCPTools(
       servers=[
           {"type": "new_api", "url": "api_endpoint"},
       ]
   )
   ```

2. **自定义工具行为**
   ```python
   # 实现自定义工具类
   class CustomMCPTool:
       def __init__(self, api_key):
           self.api_key = api_key
       
       async def execute(self, params):
           # 实现工具逻辑
           pass
   ```

### 模型配置

支持的模型提供商：
- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Google**: Gemini-1.5-pro, Gemini-1.0-pro
- **扩展支持**: 易于添加其他模型提供商

模型选择建议：
- **GPT-4**: 复杂推理和详细规划
- **GPT-3.5**: 快速响应和基础规划
- **Gemini**: 多模态理解和创新建议

## 故障排除

### 常见问题

#### 1. API连接问题
**症状**: 无法获取搜索结果或智能体响应
**解决方案**:
- 检查网络连接
- 验证API密钥有效性
- 确认API服务状态
- 检查API配额和限制

#### 2. 模型响应缓慢
**症状**: 智能体响应时间过长
**解决方案**:
- 切换到更快的模型（如GPT-3.5）
- 减少请求复杂度
- 检查网络延迟
- 考虑使用缓存机制

#### 3. 依赖安装问题
**症状**: 模块导入错误
**解决方案**:
```bash
# 重新安装依赖
pip install --upgrade -r requirements.txt

# 检查Python版本
python --version

# 验证关键包安装
python -c "import agno, streamlit, openai"
```

#### 4. 权限和认证问题
**症状**: API访问被拒绝
**解决方案**:
- 验证API密钥格式
- 检查API服务权限
- 确认账户余额和状态
- 更新过期的密钥

### 调试模式

启用详细日志：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

测试API连接：
```bash
# 创建测试脚本验证API连接
python -c "
from api_config import validate_api_setup
result = validate_api_setup()
print('API设置验证结果:', result)
"
```

## 性能优化

### 1. 异步处理
- 智能体并行执行提高效率
- 非阻塞UI响应
- 后台任务管理

### 2. 缓存策略
- 搜索结果缓存
- 模型响应缓存  
- 会话状态持久化

### 3. 资源管理
- 智能的API调用频率控制
- 内存使用优化
- 连接池管理

## 贡献指南

### 开发环境设置
```bash
# 克隆开发分支
git clone -b develop <repository-url>

# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest tests/

# 代码格式化
black .
isort .
```

### 提交规范
- 遵循现有代码风格
- 添加适当的测试用例
- 更新相关文档
- 提供清晰的提交信息

### Pull Request流程
1. Fork项目仓库
2. 创建特性分支
3. 实现功能并测试
4. 提交Pull Request
5. 代码审查和合并

欢迎社区贡献，让AI旅行规划助手变得更加强大和易用！
