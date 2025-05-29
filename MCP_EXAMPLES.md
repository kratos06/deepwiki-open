# DeepWiki MCP Server 使用示例

本文档提供了 DeepWiki MCP Server 的详细使用示例，展示如何在 Claude Desktop 或其他 MCP 客户端中使用各种功能。

## 🚀 快速开始

### 1. 安装和配置

```bash
# 安装依赖
uv sync

# 复制配置文件
cp .env.example .env
# 编辑 .env 文件，添加你的 API 密钥

# 测试 MCP server
uv run python test_mcp_server.py

# 在 Claude Desktop 中安装
mcp install mcp_deepwiki.py --name "DeepWiki Code Assistant"
```

### 2. 基本使用

在 Claude Desktop 中，你可以直接使用以下命令：

## 🔧 工具 (Tools) 使用示例

### ask_deepwiki - 智能代码问答

这是最强大的工具，提供完整的 RAG 功能：

```
请使用 ask_deepwiki 工具分析 https://github.com/microsoft/vscode 的架构设计，包括：
1. 主要模块结构
2. 扩展系统设计
3. 核心技术栈

参数：
- repo_url: https://github.com/microsoft/vscode
- question: 请分析这个项目的架构设计，包括主要模块结构、扩展系统设计和核心技术栈
- provider: google
- deep_research: true
```

### query_code - 代码检索

快速检索代码片段：

```
使用 query_code 工具在 https://github.com/facebook/react 中搜索 hooks 相关的实现

参数：
- repo_url: https://github.com/facebook/react
- query: React hooks implementation useState useEffect
- provider: google
```

### get_file_content - 获取文件内容

获取特定文件的内容：

```
请使用 get_file_content 工具获取 https://github.com/vuejs/vue 项目的 package.json 文件内容

参数：
- repo_url: https://github.com/vuejs/vue
- file_path: package.json
```

## 📚 资源 (Resources) 使用示例

### 仓库结构

```
请访问资源 repo://structure/https://github.com/tensorflow/tensorflow 获取 TensorFlow 的项目结构
```

### 文件列表

```
访问资源 repo://files/https://github.com/nodejs/node/*.js 获取 Node.js 项目中的所有 JavaScript 文件
```

### Wiki 缓存

```
访问资源 wiki://cache/microsoft/vscode/github/en 获取 VS Code 的缓存 wiki 数据
```

## 💬 提示模板 (Prompts) 使用示例

### 代码结构分析

```
使用 analyze_code_structure 提示模板分析 https://github.com/django/django 的项目结构
```

### 调试问题

```
使用 debug_code_issue 提示模板帮我调试这个问题：

仓库：https://github.com/my-org/my-project
错误描述：在运行 npm start 时出现 "Cannot resolve module" 错误，具体错误信息是找不到 './components/Header' 模块
```

### 代码功能解释

```
使用 explain_code_functionality 提示模板解释以下代码：

仓库：https://github.com/expressjs/express
文件：lib/router/index.js
函数：Router.prototype.use
```

### 代码审查清单

```
使用 code_review_checklist 提示模板为 https://github.com/my-team/new-feature 创建代码审查清单
```

## 🎯 实际应用场景

### 场景 1：学习开源项目

```
我想学习 React 的源码，请帮我分析一下：

1. 首先使用 ask_deepwiki 工具：
   - repo_url: https://github.com/facebook/react
   - question: 请为初学者介绍 React 源码的整体架构，包括核心概念、主要模块和学习路径
   - deep_research: true

2. 然后使用 analyze_code_structure 提示模板深入了解项目结构

3. 最后使用 explain_code_functionality 解释具体的核心函数
```

### 场景 2：调试生产问题

```
我们的 Node.js 应用在生产环境出现内存泄漏，请帮我分析：

1. 使用 debug_code_issue 提示模板：
   - 仓库：https://github.com/our-company/api-server
   - 错误描述：生产环境出现内存泄漏，内存使用量持续增长，最终导致 OOM

2. 使用 query_code 搜索相关的内存管理代码

3. 使用 get_file_content 查看具体的问题文件
```

### 场景 3：代码审查

```
请帮我审查这个 PR：

1. 使用 code_review_checklist 生成审查清单
2. 使用 ask_deepwiki 分析新增代码的影响
3. 使用 query_code 检查是否有类似的实现
```

## 🔧 高级配置

### 使用不同的 AI 提供商

```
# 使用 OpenAI
ask_deepwiki(
    repo_url="https://github.com/example/repo",
    question="分析这个项目",
    provider="openai",
    model="gpt-4"
)

# 使用 OpenRouter
ask_deepwiki(
    repo_url="https://github.com/example/repo", 
    question="分析这个项目",
    provider="openrouter",
    model="anthropic/claude-3-sonnet"
)

# 使用本地 Ollama
ask_deepwiki(
    repo_url="https://github.com/example/repo",
    question="分析这个项目", 
    provider="ollama",
    model="llama3"
)
```

### 私有仓库访问

```
ask_deepwiki(
    repo_url="https://github.com/private-org/private-repo",
    question="分析私有仓库",
    access_token="ghp_your_github_token_here"
)
```

## 🚨 故障排除

### 常见错误和解决方案

1. **"No valid documents with embeddings found"**
   ```
   # 检查仓库 URL 是否正确
   # 确保有网络连接
   # 对于私有仓库，提供 access_token
   ```

2. **"API key not valid"**
   ```
   # 检查 .env 文件中的 API 密钥
   # 确保 API 密钥有足够的配额
   ```

3. **"Repository not found"**
   ```
   # 确认仓库 URL 格式正确
   # 检查仓库是否存在且可访问
   ```

## 📝 最佳实践

1. **使用 deep_research 模式**：对于复杂问题，启用深度研究模式获得更全面的分析

2. **合理选择 AI 提供商**：
   - Google Gemini：平衡性能和成本
   - OpenAI：高质量输出
   - OpenRouter：多模型选择
   - Ollama：本地部署，隐私保护

3. **缓存利用**：重复查询同一仓库时，系统会自动使用缓存提高响应速度

4. **组合使用工具**：结合使用不同的工具和提示模板获得最佳效果
