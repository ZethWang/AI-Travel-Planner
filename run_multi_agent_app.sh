#!/bin/bash

# AI旅行规划助手启动脚本 - 多智能体MCP版本

echo "🚀 AI旅行规划助手 - 多智能体MCP版本"
echo "=================================================="
echo "📍 项目路径: $(pwd)"
echo "🤖 模式: 多智能体协作"
echo "🔧 主应用: app.py"
echo ""

# 检查Python版本
echo "🐍 检查Python环境..."
python_version=$(python3 --version 2>&1)
if [[ $? -eq 0 ]]; then
    echo "✅ $python_version"
else
    echo "❌ Python3未找到，请安装Python 3.8+"
    exit 1
fi

# 检查必需文件
echo "📁 检查项目文件..."
required_files=("app.py" "multi_agent_travel.py" "requirements.txt" ".env")
missing_files=false
for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "✅ $file"
    else
        echo "❌ $file 缺失"
        missing_files=true
    fi
done

if [[ $missing_files == true ]]; then
    echo "请确保所有必需文件存在"
    exit 1
fi

# 检查依赖
echo "📦 检查依赖包..."
if ! python3 -c "import streamlit, agno, openai" 2>/dev/null; then
    echo "⚠️ 缺少必要依赖，正在安装..."
    pip install -r requirements.txt
    if [[ $? -ne 0 ]]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
else
    echo "✅ 核心依赖已安装"
fi

# 检查环境变量
echo "🔑 检查API配置..."
if [[ -f ".env" ]]; then
    source .env 2>/dev/null
    if [[ -n "$OPENAI_API_KEY" && "$OPENAI_API_KEY" != "your_openai_api_key_here" ]]; then
        echo "✅ OpenAI API密钥已配置"
    else
        echo "⚠️ OpenAI API密钥未配置"
    fi
    
    if [[ -n "$SEARCHAPI_API_KEY" && "$SEARCHAPI_API_KEY" != "your_searchapi_key_here" ]]; then
        echo "✅ SearchAPI密钥已配置"
    else
        echo "⚠️ SearchAPI密钥未配置"
    fi
else
    echo "⚠️ .env文件不存在，请创建并配置API密钥"
fi

echo ""
echo "🎯 启动多智能体旅行规划助手..."
echo "🌐 界面将在浏览器中打开 http://localhost:8501"
echo "💡 使用Ctrl+C停止服务"
echo ""

# 启动Streamlit应用
streamlit run app.py --server.port 8501 --server.address 0.0.0.0

echo ""
echo "🛑 服务器已停止"
