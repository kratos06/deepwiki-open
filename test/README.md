# DeepWiki MCP Server 测试套件

本目录包含了 DeepWiki MCP Server 的完整测试套件，用于验证 MCP 功能的正确性和可靠性。

## 📁 测试文件说明

### 🔧 功能测试

#### `test_mcp_server.py`
- **功能**: 测试 MCP server 的核心功能
- **测试内容**: 工具、资源、提示模板的基本功能
- **运行方式**: `python test/test_mcp_server.py`
- **依赖**: 需要 API 密钥配置

#### `test_mcp_protocol.py`
- **功能**: 直接测试 MCP 协议功能
- **测试内容**: 工具调用、资源访问、提示生成
- **运行方式**: `python test/test_mcp_protocol.py`
- **特点**: 直接调用 MCP 组件，无需网络请求

### 🌐 集成测试

#### `test_integration.py`
- **功能**: 测试 MCP server 与 DeepWiki 的集成
- **测试内容**: 服务管理器、FastAPI 集成、启动脚本
- **运行方式**: `python test/test_integration.py`
- **特点**: 验证完整的集成流程

#### `test_mcp_client.py`
- **功能**: 模拟 MCP 客户端进行协议测试
- **测试内容**: MCP 协议握手、工具调用、资源访问
- **运行方式**: `python test/test_mcp_client.py`
- **特点**: 真实的 MCP 协议通信测试

### 🌐 HTTP 测试

#### `test_mcp_curl.sh`
- **功能**: 使用 cURL 测试 HTTP API 和 MCP 状态
- **测试内容**: API 端点、MCP 状态、服务健康检查
- **运行方式**: `./test/test_mcp_curl.sh`
- **特点**: 无需 Python 环境，纯 HTTP 测试

## 🚀 快速开始

### 1. 环境准备

确保已安装依赖并配置环境变量：

```bash
# 安装依赖
uv sync

# 配置环境变量（复制并编辑 .env 文件）
cp .env.example .env
# 编辑 .env 文件，添加你的 API 密钥
```

### 2. 启动 DeepWiki 服务

在运行测试之前，需要启动 DeepWiki 服务：

```bash
# 启动完整服务（Web API + MCP Server）
uv run python -m api.main

# 或使用统一启动脚本
python start_deepwiki.py
```

### 3. 运行测试

#### 运行所有测试

```bash
# 从项目根目录运行
cd /path/to/deepwiki-open-1

# 运行功能测试
uv run python test/test_mcp_server.py

# 运行协议测试
uv run python test/test_mcp_protocol.py

# 运行集成测试
uv run python test/test_integration.py

# 运行客户端测试
uv run python test/test_mcp_client.py

# 运行 HTTP 测试
chmod +x test/test_mcp_curl.sh
./test/test_mcp_curl.sh
```

#### 运行特定测试

```bash
# 仅测试基本功能（不需要 API 密钥）
uv run python test/test_integration.py

# 仅测试 HTTP 端点
./test/test_mcp_curl.sh

# 仅测试 MCP 协议
uv run python test/test_mcp_client.py
```

## 📊 测试覆盖范围

### ✅ MCP 功能测试

- **工具 (Tools)**: 3个
  - `ask_deepwiki` - 智能代码问答
  - `query_code` - 代码检索
  - `get_file_content` - 文件内容获取

- **资源 (Resources)**: 3个
  - `repo://structure/{repo_url}` - 仓库结构
  - `wiki://cache/{owner}/{repo}/{type}/{lang}` - Wiki 缓存
  - `repo://files/{repo_url}/{pattern}` - 文件列表

- **提示模板 (Prompts)**: 4个
  - `analyze_code_structure` - 代码架构分析
  - `debug_code_issue` - 调试协助
  - `explain_code_functionality` - 代码功能解释
  - `code_review_checklist` - 代码审查清单

### ✅ 集成测试

- **服务管理**: MCP 服务生命周期管理
- **FastAPI 集成**: MCP 组件与 Web API 的集成
- **启动脚本**: 统一启动和管理脚本
- **状态监控**: HTTP 端点状态检查

### ✅ 协议测试

- **MCP 协议握手**: 初始化和连接建立
- **工具调用**: 真实的工具调用测试
- **资源访问**: 动态资源访问测试
- **错误处理**: 异常情况处理测试

## 🔍 故障排除

### 常见问题

1. **"ModuleNotFoundError: No module named 'api'"**
   - 确保从项目根目录运行测试
   - 检查 Python 路径设置

2. **"Connection refused" 错误**
   - 确保 DeepWiki 服务正在运行
   - 检查端口 8001 是否被占用

3. **"API key not valid" 错误**
   - 检查 `.env` 文件中的 API 密钥配置
   - 确保 API 密钥有效且有足够配额

4. **"No valid documents" 错误**
   - 这是正常行为，测试仓库可能没有足够的文档
   - 可以尝试使用其他有更多文档的仓库

### 调试技巧

1. **查看详细日志**:
   ```bash
   # 启用详细日志
   export LOG_LEVEL=DEBUG
   uv run python test/test_mcp_server.py
   ```

2. **单独测试组件**:
   ```bash
   # 仅测试提示模板（不需要 API 调用）
   uv run python -c "
   import sys
   sys.path.append('.')
   from test.test_mcp_protocol import test_mcp_prompts
   test_mcp_prompts()
   "
   ```

3. **检查服务状态**:
   ```bash
   curl -s http://localhost:8001/mcp/status | python3 -m json.tool
   ```

## 📈 测试报告

测试完成后，每个测试脚本都会生成详细的测试报告，包括：

- ✅ 通过的测试数量
- ❌ 失败的测试详情
- ⚠️ 警告和建议
- 📊 性能指标
- 🔧 故障排除建议

## 🎯 最佳实践

1. **定期运行测试**: 在修改代码后运行完整测试套件
2. **环境隔离**: 使用虚拟环境避免依赖冲突
3. **API 密钥管理**: 妥善保管 API 密钥，不要提交到版本控制
4. **测试数据**: 使用小型测试仓库避免长时间等待
5. **并行测试**: 可以同时运行多个独立的测试脚本

## 🤝 贡献

如果您发现测试中的问题或想要添加新的测试用例：

1. 在 `test/` 目录下创建新的测试文件
2. 遵循现有的测试模式和命名约定
3. 更新本 README 文件
4. 确保新测试通过现有的 CI/CD 流程

---

**注意**: 运行完整测试套件可能需要 5-10 分钟，具体时间取决于网络状况和 API 响应速度。
