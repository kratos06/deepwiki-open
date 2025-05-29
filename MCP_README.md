# DeepWiki MCP Server

DeepWiki MCP Server 为 [Model Context Protocol (MCP)](https://modelcontextprotocol.io) 客户端提供了访问 DeepWiki 代码分析和查询功能的能力。通过 MCP 协议，您可以在支持 MCP 的应用程序（如 Claude Desktop）中直接查询和分析代码仓库。

## 🚀 功能特性

### Tools (工具)
- **ask_deepwiki**: 使用完整的 RAG 管道询问代码仓库相关问题
- **query_code**: 使用检索增强生成 (RAG) 查询代码
- **get_file_content**: 获取仓库中特定文件的内容

### Resources (资源)
- **repo://structure/{repo_url}**: 获取仓库结构
- **wiki://cache/{owner}/{repo}/{repo_type}/{language}**: 获取缓存的 wiki 数据
- **repo://files/{repo_url}**: 获取仓库文件列表

### Prompts (提示模板)
- **analyze_code_structure**: 分析代码库结构
- **debug_code_issue**: 调试代码问题
- **explain_code_functionality**: 解释代码功能
- **code_review_checklist**: 代码审查清单

## 📦 安装和设置

### 1. 安装依赖

```bash
# 安装 MCP 依赖
pip install -r api/requirements.txt
```

### 2. 环境变量配置

创建 `.env` 文件并配置以下环境变量：

```bash
# 必需的 API 密钥
GOOGLE_API_KEY=your_google_api_key        # Google Gemini (推荐)
OPENAI_API_KEY=your_openai_api_key        # OpenAI (用于嵌入)

# 可选的 API 密钥
OPENROUTER_API_KEY=your_openrouter_api_key # OpenRouter
OLLAMA_HOST=http://localhost:11434         # Ollama (本地模型)
```

### 3. 运行 DeepWiki 服务

#### 推荐方式：集成启动
```bash
# 启动完整的 DeepWiki 服务（Web API + MCP Server）
python start_deepwiki.py

# 仅启动 Web API
python start_deepwiki.py --mode web

# 仅启动 MCP Server
python start_deepwiki.py --mode mcp

# 自定义端口
python start_deepwiki.py --port 8080
```

#### 独立 MCP Server 模式
```bash
# 使用 MCP CLI 开发模式
mcp dev mcp_deepwiki.py

# 或直接运行独立 MCP server
python mcp_deepwiki.py
```

#### 在 Claude Desktop 中安装
```bash
# 安装到 Claude Desktop
mcp install mcp_deepwiki.py --name "DeepWiki Code Assistant"

# 带环境变量安装
mcp install mcp_deepwiki.py --name "DeepWiki" -v GOOGLE_API_KEY=your_key -v OPENAI_API_KEY=your_key
```

## 🔧 使用方法

### 在 Claude Desktop 中使用

1. 安装 MCP server 后，在 Claude Desktop 中可以直接使用以下功能：

#### 询问代码仓库
```
请使用 ask_deepwiki 工具分析 https://github.com/microsoft/vscode 这个仓库的架构设计
```

#### 查询特定代码
```
使用 query_code 工具在 https://github.com/facebook/react 中搜索关于 hooks 的实现
```

#### 获取文件内容
```
请使用 get_file_content 工具获取 https://github.com/openai/gpt-3 仓库中的 README.md 文件内容
```

### 使用提示模板

#### 代码结构分析
```
使用 analyze_code_structure 提示模板分析 https://github.com/tensorflow/tensorflow 的项目结构
```

#### 调试问题
```
使用 debug_code_issue 提示模板帮我调试这个错误：在运行 npm start 时出现 "Module not found" 错误
```

### 访问资源

#### 获取仓库结构
```
请访问资源 repo://structure/https://github.com/vuejs/vue 获取 Vue.js 的项目结构
```

#### 获取缓存的 wiki 数据
```
访问资源 wiki://cache/microsoft/vscode/github/en 获取 VS Code 的缓存 wiki 数据
```

## 🛠️ 高级配置

### 支持的 AI 提供商

- **Google Gemini** (推荐): 设置 `GOOGLE_API_KEY`
- **OpenAI**: 设置 `OPENAI_API_KEY`
- **OpenRouter**: 设置 `OPENROUTER_API_KEY`
- **Ollama** (本地): 设置 `OLLAMA_HOST`

### 支持的仓库类型

- GitHub: `https://github.com/owner/repo`
- GitLab: `https://gitlab.com/owner/repo`
- Bitbucket: `https://bitbucket.org/owner/repo`

### 私有仓库访问

对于私有仓库，可以在工具调用时提供 `access_token` 参数：

```
使用 ask_deepwiki 工具查询私有仓库，设置 access_token 为你的 GitHub Personal Access Token
```

## 📝 示例对话

### 分析开源项目
```
用户: 我想了解 React 项目的架构，请帮我分析一下

助手: 我来使用 DeepWiki 的 ask_deepwiki 工具来分析 React 项目的架构。

[调用 ask_deepwiki 工具]
- repo_url: https://github.com/facebook/react
- question: 请分析 React 项目的整体架构设计，包括核心模块、设计模式和关键组件
- provider: google
- deep_research: true

基于分析结果，React 项目采用了以下架构设计...
```

### 调试代码问题
```
用户: 我在使用 React Hooks 时遇到了无限循环的问题

助手: 我来帮你分析 React Hooks 的无限循环问题。

[使用 debug_code_issue 提示模板]
[调用 query_code 工具搜索相关的 hooks 实现和最佳实践]

常见的无限循环原因包括...
```

## 🔍 故障排除

### 常见问题

1. **"No valid documents with embeddings found"**
   - 检查仓库 URL 是否正确
   - 确保有足够的磁盘空间用于克隆仓库
   - 检查网络连接

2. **"API key not valid"**
   - 验证环境变量是否正确设置
   - 检查 API 密钥是否有效且有足够的配额

3. **"Repository not found"**
   - 确认仓库 URL 格式正确
   - 对于私有仓库，提供有效的 access_token

### 日志和调试

MCP server 会输出详细的日志信息，可以帮助诊断问题：

```bash
# 查看详细日志
python mcp_deepwiki.py --verbose
```

## 🤝 贡献

欢迎贡献代码和提出建议！请查看主项目的贡献指南。

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。
