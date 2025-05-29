#!/usr/bin/env python3
"""
DeepWiki MCP Server 测试运行器

这个脚本运行所有的 MCP 测试并生成综合报告。
"""

import asyncio
import os
import subprocess
import sys
import time
from pathlib import Path

# 添加父目录到路径
sys.path.append(str(Path(__file__).parent.parent))

def print_header(title):
    """打印测试标题"""
    print("\n" + "=" * 60)
    print(f"🧪 {title}")
    print("=" * 60)

def print_section(title):
    """打印测试部分标题"""
    print(f"\n📋 {title}")
    print("-" * 40)

def run_python_test(test_file, description):
    """运行 Python 测试文件"""
    print(f"\n🔧 运行 {description}...")
    print(f"文件: {test_file}")
    
    try:
        # 从项目根目录运行测试
        result = subprocess.run(
            [sys.executable, test_file],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=120  # 2分钟超时
        )
        
        if result.returncode == 0:
            print(f"✅ {description} - 通过")
            return True, result.stdout
        else:
            print(f"❌ {description} - 失败")
            print(f"错误输出: {result.stderr}")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - 超时")
        return False, "测试超时"
    except Exception as e:
        print(f"💥 {description} - 异常: {str(e)}")
        return False, str(e)

def run_shell_test(test_file, description):
    """运行 Shell 测试文件"""
    print(f"\n🔧 运行 {description}...")
    print(f"文件: {test_file}")
    
    try:
        # 确保脚本可执行
        os.chmod(test_file, 0o755)
        
        result = subprocess.run(
            [test_file],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=60  # 1分钟超时
        )
        
        if result.returncode == 0:
            print(f"✅ {description} - 通过")
            return True, result.stdout
        else:
            print(f"❌ {description} - 失败")
            print(f"错误输出: {result.stderr}")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - 超时")
        return False, "测试超时"
    except Exception as e:
        print(f"💥 {description} - 异常: {str(e)}")
        return False, str(e)

def check_service_status():
    """检查 DeepWiki 服务状态"""
    print_section("检查服务状态")
    
    try:
        import requests
        
        # 检查健康状态
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            print("✅ DeepWiki API 服务正在运行")
            
            # 检查 MCP 状态
            mcp_response = requests.get("http://localhost:8001/mcp/status", timeout=5)
            if mcp_response.status_code == 200:
                mcp_data = mcp_response.json()
                mcp_running = mcp_data.get('mcp_server', {}).get('running', False)
                if mcp_running:
                    print("✅ MCP Server 组件正在运行")
                    return True
                else:
                    print("❌ MCP Server 组件未运行")
                    return False
            else:
                print("❌ 无法获取 MCP 状态")
                return False
        else:
            print("❌ DeepWiki API 服务未运行")
            return False
            
    except ImportError:
        print("⚠️  requests 库未安装，跳过服务状态检查")
        return True
    except Exception as e:
        print(f"❌ 服务状态检查失败: {str(e)}")
        print("💡 请确保 DeepWiki 服务正在运行:")
        print("   uv run python -m api.main")
        return False

def check_environment():
    """检查环境配置"""
    print_section("检查环境配置")
    
    # 检查必需的文件
    required_files = [
        "api/mcp_server.py",
        "api/mcp_service.py", 
        "mcp_deepwiki.py",
        ".env"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ 缺少必需文件: {', '.join(missing_files)}")
        return False
    else:
        print("✅ 所有必需文件存在")
    
    # 检查环境变量
    api_keys = ["GOOGLE_API_KEY", "OPENAI_API_KEY"]
    missing_keys = [key for key in api_keys if not os.environ.get(key)]
    
    if missing_keys:
        print(f"⚠️  缺少 API 密钥: {', '.join(missing_keys)}")
        print("   某些测试可能会失败或产生有限结果")
    else:
        print("✅ API 密钥已配置")
    
    return True

async def main():
    """主测试函数"""
    start_time = time.time()
    
    print_header("DeepWiki MCP Server 测试套件")
    
    # 加载环境变量
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ 环境变量已加载")
    except ImportError:
        print("⚠️  python-dotenv 未安装，跳过 .env 文件加载")
    
    # 检查环境
    if not check_environment():
        print("\n❌ 环境检查失败，退出测试")
        return False
    
    # 检查服务状态
    service_running = check_service_status()
    
    # 定义测试列表
    tests = [
        # 基础测试（不需要服务运行）
        ("test/test_integration.py", "集成测试", False),
        
        # 需要服务运行的测试
        ("test/test_mcp_curl.sh", "HTTP API 测试", True),
        ("test/test_mcp_protocol.py", "MCP 协议测试", True),
        ("test/test_mcp_server.py", "MCP 功能测试", True),
        ("test/test_mcp_client.py", "MCP 客户端测试", True),
    ]
    
    results = []
    
    print_section("开始运行测试")
    
    for test_file, description, needs_service in tests:
        if needs_service and not service_running:
            print(f"⏭️  跳过 {description} (需要服务运行)")
            results.append((description, False, "服务未运行"))
            continue
        
        if test_file.endswith('.py'):
            success, output = run_python_test(test_file, description)
        elif test_file.endswith('.sh'):
            success, output = run_shell_test(test_file, description)
        else:
            print(f"⚠️  未知测试文件类型: {test_file}")
            success, output = False, "未知文件类型"
        
        results.append((description, success, output))
        
        # 测试间短暂休息
        time.sleep(1)
    
    # 生成测试报告
    print_header("测试结果报告")
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print(f"\n📊 总体结果: {passed}/{total} 测试通过")
    
    print_section("详细结果")
    for description, success, output in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} - {description}")
        if not success and output:
            # 只显示错误输出的前几行
            error_lines = output.split('\n')[:3]
            for line in error_lines:
                if line.strip():
                    print(f"    {line}")
    
    # 性能统计
    end_time = time.time()
    duration = end_time - start_time
    print(f"\n⏱️  总耗时: {duration:.1f} 秒")
    
    # 建议和下一步
    print_section("建议和下一步")
    
    if passed == total:
        print("🎉 所有测试通过！MCP server 工作正常。")
        print("\n📋 可以进行的操作:")
        print("• 在 Claude Desktop 中安装: mcp install mcp_deepwiki.py --name 'DeepWiki'")
        print("• 开发测试: mcp dev mcp_deepwiki.py")
        print("• 部署到生产环境")
    else:
        print(f"⚠️  {total - passed} 个测试失败。")
        print("\n🔧 故障排除建议:")
        
        if not service_running:
            print("• 启动 DeepWiki 服务: uv run python -m api.main")
        
        missing_keys = [key for key in ["GOOGLE_API_KEY", "OPENAI_API_KEY"] if not os.environ.get(key)]
        if missing_keys:
            print(f"• 配置 API 密钥: {', '.join(missing_keys)}")
        
        print("• 检查网络连接")
        print("• 查看详细错误日志")
        print("• 运行单个测试进行调试")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
