#!/usr/bin/env python3
"""
DeepWiki MCP Server

This MCP server provides access to DeepWiki's code analysis and query capabilities
through the Model Context Protocol. It allows MCP clients to:

1. Query code repositories using RAG (Retrieval Augmented Generation)
2. Access repository structure and cached wiki content
3. Use predefined prompts for code analysis

Usage:
    python api/mcp_server.py

Or with MCP CLI:
    mcp dev api/mcp_server.py
"""

import json
import logging
import os
import sys
from typing import Dict, Optional

# Add the parent directory to the path so we can import api modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import DeepWiki modules
from api.rag import RAG
from api.data_pipeline import DatabaseManager
from api.api import read_wiki_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("DeepWiki")

# Global variables to store active RAG instances and database managers
active_rags: Dict[str, RAG] = {}
active_db_managers: Dict[str, DatabaseManager] = {}

def get_repo_key(repo_url: str, repo_type: str = "github") -> str:
    """Generate a unique key for a repository"""
    return f"{repo_type}:{repo_url}"

def parse_repo_url(repo_url: str) -> tuple[str, str, str]:
    """Parse repository URL to extract owner, repo name, and type"""
    if "github.com" in repo_url:
        parts = repo_url.replace("https://github.com/", "").replace("http://github.com/", "").split("/")
        return parts[0], parts[1], "github"
    elif "gitlab.com" in repo_url:
        parts = repo_url.replace("https://gitlab.com/", "").replace("http://gitlab.com/", "").split("/")
        return parts[0], parts[1], "gitlab"
    elif "bitbucket.org" in repo_url:
        parts = repo_url.replace("https://bitbucket.org/", "").replace("http://bitbucket.org/", "").split("/")
        return parts[0], parts[1], "bitbucket"
    else:
        # Default to github if unclear
        parts = repo_url.split("/")[-2:]
        return parts[0], parts[1], "github"

@mcp.tool()
async def query_code(
    repo_url: str,
    query: str,
    provider: str = "google",
    model: Optional[str] = None,
    repo_type: str = "github",
    access_token: Optional[str] = None,
    language: str = "en"
) -> str:
    """
    Query code repository using RAG (Retrieval Augmented Generation).
    
    This tool allows you to ask questions about a code repository and get
    intelligent answers based on the repository's content.
    
    Args:
        repo_url: URL of the repository (e.g., https://github.com/owner/repo)
        query: Your question about the code
        provider: AI provider to use (google, openai, openrouter, ollama)
        model: Specific model to use (optional, uses provider default)
        repo_type: Type of repository (github, gitlab, bitbucket)
        access_token: Access token for private repositories (optional)
        language: Response language (default: en)
    
    Returns:
        AI-generated answer based on the repository content
    """
    try:
        repo_key = get_repo_key(repo_url, repo_type)
        
        # Check if we already have a RAG instance for this repo
        if repo_key not in active_rags:
            logger.info(f"Creating new RAG instance for {repo_url}")
            rag = RAG(provider=provider, model=model)
            
            # Prepare the retriever for this repository
            rag.prepare_retriever(repo_url, repo_type, access_token)
            active_rags[repo_key] = rag
        else:
            rag = active_rags[repo_key]
            logger.info(f"Using existing RAG instance for {repo_url}")
        
        # Perform the query
        retrieved_documents = rag.call(query, language)
        
        if not retrieved_documents or len(retrieved_documents) == 0:
            return "No relevant information found in the repository for your query."
        
        # Extract the answer from the first retrieved document result
        if hasattr(retrieved_documents[0], 'documents') and retrieved_documents[0].documents:
            # Format the response with context
            context_info = []
            for doc in retrieved_documents[0].documents[:3]:  # Show top 3 relevant documents
                file_path = doc.meta_data.get('file_path', 'unknown')
                content_preview = doc.text[:200] + "..." if len(doc.text) > 200 else doc.text
                context_info.append(f"**File: {file_path}**\n{content_preview}")
            
            response = f"Based on the repository content, here are the most relevant findings:\n\n"
            response += "\n\n---\n\n".join(context_info)
            return response
        else:
            return "Retrieved documents but could not extract meaningful content."
            
    except Exception as e:
        logger.error(f"Error in query_code: {str(e)}")
        return f"Error processing query: {str(e)}"

@mcp.tool()
async def ask_deepwiki(
    repo_url: str,
    question: str,
    provider: str = "google",
    model: Optional[str] = None,
    repo_type: str = "github",
    access_token: Optional[str] = None,
    language: str = "en",
    deep_research: bool = False
) -> str:
    """
    Ask DeepWiki a question about a code repository using the full RAG pipeline.
    
    This is the main query interface that mimics the Ask functionality in DeepWiki's web interface.
    It provides comprehensive answers using the repository's indexed content.
    
    Args:
        repo_url: URL of the repository
        question: Your question about the codebase
        provider: AI provider (google, openai, openrouter, ollama)
        model: Specific model to use (optional)
        repo_type: Repository type (github, gitlab, bitbucket)
        access_token: Access token for private repos (optional)
        language: Response language
        deep_research: Enable deep research mode for comprehensive analysis
    
    Returns:
        Comprehensive AI-generated answer about the codebase
    """
    try:
        repo_key = get_repo_key(repo_url, repo_type)
        
        # Initialize RAG if needed
        if repo_key not in active_rags:
            logger.info(f"Initializing RAG for {repo_url}")
            rag = RAG(provider=provider, model=model)
            rag.prepare_retriever(repo_url, repo_type, access_token)
            active_rags[repo_key] = rag
        else:
            rag = active_rags[repo_key]
        
        # Add deep research prefix if enabled
        if deep_research:
            question = f"[DEEP RESEARCH] {question}"
        
        # Use the RAG generator to get a comprehensive answer
        retrieved_docs = rag.call(question, language)
        
        if not retrieved_docs:
            return "I couldn't find relevant information in the repository to answer your question."
        
        # Get the generated answer using RAG's generator
        try:
            # Update the generator's context with retrieved documents
            if hasattr(retrieved_docs[0], 'documents'):
                rag.generator.prompt_kwargs["contexts"] = retrieved_docs[0].documents
            
            # Generate the response
            response = rag.generator(input_str=question)
            
            if hasattr(response, 'answer'):
                return response.answer
            elif hasattr(response, 'data') and hasattr(response.data, 'answer'):
                return response.data.answer
            else:
                return str(response)
                
        except Exception as gen_error:
            logger.error(f"Error in generation: {str(gen_error)}")
            # Fallback to simple document retrieval
            if hasattr(retrieved_docs[0], 'documents') and retrieved_docs[0].documents:
                context = "\n\n".join([
                    f"**{doc.meta_data.get('file_path', 'Unknown file')}:**\n{doc.text[:500]}..."
                    for doc in retrieved_docs[0].documents[:3]
                ])
                return f"Based on the repository content:\n\n{context}"
            else:
                return "Retrieved information but couldn't generate a comprehensive answer."
        
    except Exception as e:
        logger.error(f"Error in ask_deepwiki: {str(e)}")
        return f"Error processing your question: {str(e)}"

@mcp.resource("repo://structure/{repo_url}")
async def get_repo_structure(repo_url: str) -> str:
    """
    Get the structure of a repository.
    
    Args:
        repo_url: URL of the repository
    
    Returns:
        JSON representation of the repository structure
    """
    try:
        # Parse the repo URL to get components
        _, _, repo_type = parse_repo_url(repo_url)
        repo_key = get_repo_key(repo_url, repo_type)
        
        # Initialize database manager if needed
        if repo_key not in active_db_managers:
            db_manager = DatabaseManager()
            db_manager.prepare_database(repo_url, repo_type)
            active_db_managers[repo_key] = db_manager
        else:
            db_manager = active_db_managers[repo_key]
        
        # Get repository structure
        if db_manager.repo_paths and os.path.exists(db_manager.repo_paths["save_repo_dir"]):
            repo_dir = db_manager.repo_paths["save_repo_dir"]
            structure = {}
            
            for root, dirs, files in os.walk(repo_dir):
                # Skip hidden directories and common build/cache directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'build', 'dist']]
                
                rel_path = os.path.relpath(root, repo_dir)
                if rel_path == '.':
                    rel_path = ''
                
                structure[rel_path] = {
                    'directories': dirs,
                    'files': files
                }
            
            return json.dumps(structure, indent=2)
        else:
            return json.dumps({"error": "Repository not found or not indexed"})
            
    except Exception as e:
        logger.error(f"Error getting repo structure: {str(e)}")
        return json.dumps({"error": str(e)})

@mcp.resource("wiki://cache/{owner}/{repo}/{repo_type}/{language}")
async def get_wiki_cache(owner: str, repo: str, repo_type: str, language: str = "en") -> str:
    """
    Get cached wiki content for a repository.

    Args:
        owner: Repository owner
        repo: Repository name
        repo_type: Repository type (github, gitlab, bitbucket)
        language: Wiki language

    Returns:
        JSON representation of cached wiki data
    """
    try:
        cached_data = await read_wiki_cache(owner, repo, repo_type, language)
        if cached_data:
            return json.dumps(cached_data.model_dump(), indent=2)
        else:
            return json.dumps({"message": "No cached wiki data found"})
    except Exception as e:
        logger.error(f"Error getting wiki cache: {str(e)}")
        return json.dumps({"error": str(e)})

@mcp.resource("repo://files/{repo_url}/{file_pattern}")
async def get_repo_files(repo_url: str, file_pattern: str = "*") -> str:
    """
    Get a list of files in the repository matching a pattern.

    Args:
        repo_url: URL of the repository
        file_pattern: File pattern to match (default: all files)

    Returns:
        JSON list of file paths
    """
    try:
        import fnmatch
        repo_key = get_repo_key(repo_url)

        # Initialize database manager if needed
        if repo_key not in active_db_managers:
            db_manager = DatabaseManager()
            db_manager.prepare_database(repo_url)
            active_db_managers[repo_key] = db_manager
        else:
            db_manager = active_db_managers[repo_key]

        files = []
        if db_manager.repo_paths and os.path.exists(db_manager.repo_paths["save_repo_dir"]):
            repo_dir = db_manager.repo_paths["save_repo_dir"]

            for root, dirs, filenames in os.walk(repo_dir):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]

                for filename in filenames:
                    if not filename.startswith('.'):
                        full_path = os.path.join(root, filename)
                        rel_path = os.path.relpath(full_path, repo_dir)
                        # Apply file pattern filter
                        if fnmatch.fnmatch(rel_path, file_pattern) or fnmatch.fnmatch(filename, file_pattern):
                            files.append(rel_path)

        return json.dumps({"files": files, "pattern": file_pattern}, indent=2)

    except Exception as e:
        logger.error(f"Error getting repo files: {str(e)}")
        return json.dumps({"error": str(e)})

@mcp.prompt()
def analyze_code_structure(repo_url: str) -> str:
    """
    Generate a prompt for analyzing the overall structure of a codebase.

    Args:
        repo_url: URL of the repository to analyze

    Returns:
        Structured prompt for code analysis
    """
    return f"""Please analyze the structure and architecture of the repository at {repo_url}.

Focus on:
1. **Project Structure**: Main directories and their purposes
2. **Technology Stack**: Programming languages, frameworks, and tools used
3. **Architecture Patterns**: Design patterns and architectural decisions
4. **Key Components**: Main modules, classes, or functions
5. **Dependencies**: External libraries and their purposes
6. **Documentation**: README files, comments, and documentation quality

Provide a comprehensive overview that would help a new developer understand the codebase quickly."""

@mcp.prompt()
def debug_code_issue(repo_url: str, error_description: str) -> str:
    """
    Generate a prompt for debugging a specific code issue.

    Args:
        repo_url: URL of the repository
        error_description: Description of the error or issue

    Returns:
        Structured prompt for debugging assistance
    """
    return f"""Help me debug an issue in the repository at {repo_url}.

**Issue Description:**
{error_description}

Please help me:
1. **Identify Potential Causes**: What could be causing this issue?
2. **Locate Relevant Code**: Which files or functions should I examine?
3. **Debugging Steps**: What steps should I take to diagnose the problem?
4. **Common Solutions**: What are typical solutions for this type of issue?
5. **Prevention**: How can I prevent similar issues in the future?

Please search through the codebase to provide specific, actionable advice."""

@mcp.prompt()
def explain_code_functionality(repo_url: str, file_path: str = "", function_name: str = "") -> str:
    """
    Generate a prompt for explaining specific code functionality.

    Args:
        repo_url: URL of the repository
        file_path: Specific file to focus on (optional)
        function_name: Specific function to explain (optional)

    Returns:
        Structured prompt for code explanation
    """
    focus = ""
    if file_path:
        focus += f"\n- Focus on file: {file_path}"
    if function_name:
        focus += f"\n- Focus on function: {function_name}"

    return f"""Please explain the functionality of code in the repository at {repo_url}.{focus}

Please provide:
1. **Purpose**: What does this code do?
2. **Input/Output**: What are the inputs and outputs?
3. **Algorithm**: How does it work step by step?
4. **Dependencies**: What other parts of the code does it depend on?
5. **Usage Examples**: How is this code typically used?
6. **Edge Cases**: What special cases or error conditions are handled?

Make the explanation clear and suitable for developers who are new to this codebase."""

@mcp.prompt()
def code_review_checklist(repo_url: str) -> list[base.Message]:
    """
    Generate a comprehensive code review checklist prompt.

    Args:
        repo_url: URL of the repository to review

    Returns:
        Structured conversation for code review
    """
    return [
        base.UserMessage(f"I need to perform a code review for the repository at {repo_url}. Can you help me create a comprehensive checklist?"),
        base.AssistantMessage("""I'll help you create a thorough code review checklist. Let me analyze the repository structure and provide a customized checklist based on the codebase.

**Code Review Checklist:**

**1. Code Quality & Style**
- [ ] Consistent coding style and formatting
- [ ] Meaningful variable and function names
- [ ] Appropriate comments and documentation
- [ ] No commented-out code or debug statements

**2. Functionality & Logic**
- [ ] Code does what it's supposed to do
- [ ] Edge cases are handled properly
- [ ] Error handling is appropriate
- [ ] No obvious bugs or logical errors

**3. Performance & Efficiency**
- [ ] No unnecessary computations or redundant code
- [ ] Efficient algorithms and data structures
- [ ] Proper resource management (memory, files, connections)
- [ ] No performance bottlenecks

**4. Security**
- [ ] Input validation and sanitization
- [ ] No hardcoded secrets or credentials
- [ ] Proper authentication and authorization
- [ ] Protection against common vulnerabilities

**5. Testing**
- [ ] Adequate test coverage
- [ ] Tests are meaningful and well-written
- [ ] All tests pass
- [ ] Integration tests where appropriate

**6. Documentation**
- [ ] README is up to date
- [ ] API documentation is complete
- [ ] Code comments explain complex logic
- [ ] Change log is updated

Would you like me to analyze specific files or aspects of the codebase?"""),
        base.UserMessage("Please analyze the repository and provide specific recommendations based on the actual code structure and patterns you find.")
    ]

@mcp.tool()
async def get_file_content(repo_url: str, file_path: str, repo_type: str = "github", access_token: Optional[str] = None) -> str:
    """
    Get the content of a specific file from the repository.

    Args:
        repo_url: URL of the repository
        file_path: Path to the file within the repository
        repo_type: Repository type (github, gitlab, bitbucket)
        access_token: Access token for private repositories (optional)

    Returns:
        Content of the specified file
    """
    try:
        repo_key = get_repo_key(repo_url, repo_type)

        # Initialize database manager if needed
        if repo_key not in active_db_managers:
            db_manager = DatabaseManager()
            db_manager.prepare_database(repo_url, repo_type, access_token)
            active_db_managers[repo_key] = db_manager
        else:
            db_manager = active_db_managers[repo_key]

        if db_manager.repo_paths and os.path.exists(db_manager.repo_paths["save_repo_dir"]):
            full_file_path = os.path.join(db_manager.repo_paths["save_repo_dir"], file_path)

            if os.path.exists(full_file_path) and os.path.isfile(full_file_path):
                try:
                    with open(full_file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    return f"File: {file_path}\n\n{content}"
                except UnicodeDecodeError:
                    # Try with different encoding for binary files
                    try:
                        with open(full_file_path, 'r', encoding='latin-1') as f:
                            content = f.read()
                        return f"File: {file_path} (binary content)\n\n{content[:1000]}..."
                    except Exception:
                        return f"File: {file_path}\n\nError: Cannot read file content (binary file)"
            else:
                return f"Error: File '{file_path}' not found in repository"
        else:
            return "Error: Repository not found or not indexed"

    except Exception as e:
        logger.error(f"Error getting file content: {str(e)}")
        return f"Error reading file: {str(e)}"

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
