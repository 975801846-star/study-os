#!/bin/bash
# StudyOS 一键初始化脚本
set -e

echo "========================================="
echo "  StudyOS — 环境初始化"
echo "========================================="
echo ""

# 检查 Python
if command -v python3 &> /dev/null; then
    echo "✅ Python: $(python3 --version)"
elif command -v python &> /dev/null; then
    echo "✅ Python: $(python --version)"
else
    echo "❌ Python 3.11+ 未安装，请先安装 Python"
    exit 1
fi

# 检查 Node
if command -v node &> /dev/null; then
    echo "✅ Node.js: $(node --version)"
else
    echo "❌ Node.js 20+ 未安装，请先安装 Node.js"
    exit 1
fi

# 检查 Git
if command -v git &> /dev/null; then
    echo "✅ Git: $(git --version | cut -d' ' -f3)"
else
    echo "⚠️  Git 未安装（非必需，但推荐安装）"
fi

echo ""

# 创建 .env
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 已创建 .env 文件，请编辑填入 API Key"
else
    echo "📝 .env 已存在，跳过"
fi

# 创建数据目录
mkdir -p data/chroma data/uploads data/exports
echo "📁 已创建数据目录"

# 安装后端依赖
echo ""
echo "📦 安装后端依赖..."
cd backend
if [ -f requirements.txt ]; then
    pip install -r requirements.txt -q
    echo "✅ 后端依赖安装完成"
else
    echo "⚠️  requirements.txt 不存在，跳过"
fi
cd ..

# 安装前端依赖
echo ""
echo "📦 安装前端依赖..."
cd frontend
if [ -f package.json ]; then
    npm install --silent 2>/dev/null || npm install
    echo "✅ 前端依赖安装完成"
else
    echo "⚠️  package.json 不存在，跳过"
fi
cd ..

echo ""
echo "========================================="
echo "  ✅ 初始化完成！"
echo ""
echo "  下一步："
echo "  1. 编辑 .env 填入 API Key"
echo "  2. make dev  启动开发环境"
echo "  3. 打开 http://localhost:3000"
echo "========================================="
