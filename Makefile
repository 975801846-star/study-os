.PHONY: help install dev backend frontend db test lint clean

help: ## 显示帮助信息
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## 安装所有依赖
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

dev: ## 启动开发环境 (后端 + 前端)
	@echo "启动后端 http://localhost:8000 ..."
	cd backend && uvicorn src.main:app --reload --port 8000 &
	@echo "启动前端 http://localhost:3000 ..."
	cd frontend && npm run dev --port 3000

backend: ## 仅启动后端
	cd backend && uvicorn src.main:app --reload --port 8000

frontend: ## 仅启动前端
	cd frontend && npm run dev --port 3000

db-init: ## 初始化数据库
	cd backend && python -c "from src.database import init_db; init_db()"

db-reset: ## 重置数据库（危险）
	rm -f data/studyos.db
	rm -rf data/chroma/
	$(MAKE) db-init

test: ## 运行测试
	cd backend && pytest -v

lint: ## 代码检查
	cd backend && ruff check src/
	cd frontend && npm run lint

format: ## 代码格式化
	cd backend && ruff format src/
	cd frontend && npm run format

docker-up: ## Docker Compose 启动
	docker compose up -d

docker-down: ## Docker Compose 停止
	docker compose down

clean: ## 清理临时文件
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .next/ dist/ .pytest_cache/

seed: ## 填充测试数据
	cd backend && python -m scripts.seed_data
