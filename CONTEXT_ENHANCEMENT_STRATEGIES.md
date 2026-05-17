# Context Enhancement Strategies for Multi-Agent PR Review

**Document Version:** 1.0  
**Date:** May 15, 2026  
**Purpose:** Improve agent understanding by providing richer context beyond just code diffs

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Context Enhancement Strategies](#context-enhancement-strategies)
3. [Implementation Guide](#implementation-guide)
4. [Priority Matrix](#priority-matrix)
5. [Code Examples](#code-examples)
6. [Best Practices](#best-practices)

---

## Problem Statement

### Current Limitation

Currently, agents only see **code diffs (patches)** when reviewing PRs:

```diff
@@ -10,7 +10,8 @@ def calculate_total(items):
     total = 0
     for item in items:
-        total += item.price
+        # Apply discount
+        total += item.price * 0.9
     return total
```

### Why This Is Insufficient

**Agents miss critical context:**
- ❌ Don't see the full function/class
- ❌ Don't understand file dependencies
- ❌ Don't know project coding standards
- ❌ Can't see how changes affect other parts of system
- ❌ No awareness of project documentation
- ❌ Missing historical context (why was old code written that way?)

### Impact on Review Quality

Without context:
- **False Positives:** Flag "issues" that aren't actually problems in this project's context
- **False Negatives:** Miss real issues because they don't understand broader implications
- **Poor Recommendations:** Suggest fixes that violate project standards
- **Low Confidence:** Can't make confident assessments without full picture

---

## Context Enhancement Strategies

### 1. Repository-Level Context

**What:** High-level information about the entire project

**Why:** Helps agents understand the project domain, language, and purpose

**Implementation:**

```python
def get_repository_context(repo_full_name: str) -> dict:
    """Fetch high-level repository information"""
    repo = g.get_repo(repo_full_name)
    
    return {
        "name": repo.name,
        "description": repo.description,
        "language": repo.language,
        "topics": repo.get_topics(),
        "readme_preview": repo.get_readme().decoded_content.decode()[:2000],
        "license": repo.license.name if repo.license else None,
        "size": repo.size,
        "stars": repo.stargazers_count,
        "open_issues": repo.open_issues_count,
        "default_branch": repo.default_branch,
        "created_at": repo.created_at.isoformat(),
        "updated_at": repo.updated_at.isoformat()
    }
```

**Example Output:**

```json
{
  "name": "fastapi",
  "description": "FastAPI framework, high performance, easy to learn",
  "language": "Python",
  "topics": ["fastapi", "async", "api", "python"],
  "readme_preview": "# FastAPI\n\nFastAPI is a modern...",
  "license": "MIT",
  "stars": 50000
}
```

**Benefit:** Agent knows this is a Python web framework, can tailor advice accordingly

---

### 2. Project Documentation

**What:** README, CONTRIBUTING, ARCHITECTURE, and other docs

**Why:** Project-specific guidelines that agents should follow

**Implementation:**

```python
def fetch_project_docs(repo) -> dict:
    """Get important documentation files"""
    docs = {}
    
    important_files = [
        "README.md",
        "CONTRIBUTING.md",
        "ARCHITECTURE.md",
        "SECURITY.md",
        "CODE_OF_CONDUCT.md",
        "STYLE_GUIDE.md",
        ".github/CODING_STANDARDS.md",
        "docs/development.md",
        "docs/architecture.md",
        "docs/style-guide.md"
    ]
    
    for file_path in important_files:
        try:
            content = repo.get_contents(file_path)
            decoded = content.decoded_content.decode()
            
            # Keep first 5000 chars to avoid context overflow
            docs[file_path] = {
                "content": decoded[:5000],
                "full_length": len(decoded),
                "truncated": len(decoded) > 5000,
                "url": content.html_url
            }
        except:
            continue
    
    return docs
```

**Example Usage in Agent Prompt:**

```python
prompt = f"""
Review this PR according to project standards:

## Project Guidelines
{docs.get('CONTRIBUTING.md', 'No guidelines found')}

## Security Policy
{docs.get('SECURITY.md', 'No security policy found')}

Now review the changes...
"""
```

**Benefit:** Agents follow project-specific conventions (e.g., "We use pytest, not unittest")

---

### 3. Full File Context (Not Just Diffs)

**What:** Complete file content before AND after changes

**Why:** Understand surrounding code, imports, class structure

**Implementation:**

```python
def get_full_file_context(pr, file) -> dict:
    """Get complete file content before and after changes"""
    
    context = {
        "filename": file.filename,
        "patch": file.patch
    }
    
    # Get file content AFTER changes (from PR head)
    try:
        file_after = pr.head.repo.get_contents(
            file.filename, 
            ref=pr.head.sha
        )
        content_after = file_after.decoded_content.decode()
        context["after"] = {
            "content": content_after,
            "size": len(content_after),
            "lines": content_after.count('\n')
        }
    except Exception as e:
        context["after"] = None
        context["after_error"] = str(e)
    
    # Get file content BEFORE changes (from PR base)
    try:
        file_before = pr.base.repo.get_contents(
            file.filename,
            ref=pr.base.sha
        )
        content_before = file_before.decoded_content.decode()
        context["before"] = {
            "content": content_before,
            "size": len(content_before),
            "lines": content_before.count('\n')
        }
    except Exception as e:
        context["before"] = None
        context["before_error"] = str(e)
    
    return context
```

**Visual Comparison:**

**❌ Without Full Context (what agents see now):**
```python
# Just the diff
+    total += item.price * 0.9
```

**✅ With Full Context:**
```python
# Full function
def calculate_total(items):
    """Calculate total price with discounts"""
    if not items:
        return 0
    
    total = 0
    for item in items:
        # Apply discount  ← CHANGE HERE
        total += item.price * 0.9
    
    # Apply tax
    total *= 1.1
    
    return round(total, 2)
```

**Benefit:** Agent can see:
- Function signature and docstring
- Input validation (`if not items`)
- What happens after the changed line (tax calculation)
- Return type (rounded float)

---

### 4. Dependency Analysis

**What:** What this file imports and what imports this file

**Why:** Understanding dependencies reveals security risks, performance implications

**Implementation:**

```python
def analyze_dependencies(file_path: str, file_content: str, language: str = "python") -> dict:
    """Extract imports and dependencies"""
    
    dependencies = {
        "imports": [],
        "from_imports": [],
        "local_imports": [],
        "external_packages": [],
        "standard_library": []
    }
    
    if language == "python":
        dependencies = analyze_python_dependencies(file_content)
    elif language == "javascript":
        dependencies = analyze_javascript_dependencies(file_content)
    # Add other languages as needed
    
    return dependencies


def analyze_python_dependencies(file_content: str) -> dict:
    """Python-specific dependency analysis"""
    import ast
    import sys
    
    dependencies = {
        "imports": [],
        "from_imports": [],
        "local_imports": [],
        "external_packages": [],
        "standard_library": []
    }
    
    try:
        tree = ast.parse(file_content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name
                    dependencies["imports"].append({
                        "module": module_name,
                        "alias": alias.asname
                    })
                    
                    # Categorize
                    if module_name.split('.')[0] in sys.stdlib_module_names:
                        dependencies["standard_library"].append(module_name)
                    else:
                        dependencies["external_packages"].append(module_name)
            
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    full_import = f"{module}.{alias.name}" if module else alias.name
                    dependencies["from_imports"].append({
                        "module": module,
                        "name": alias.name,
                        "alias": alias.asname
                    })
                    
                    # Local imports start with '.'
                    if module.startswith('.'):
                        dependencies["local_imports"].append(full_import)
                    elif module.split('.')[0] in sys.stdlib_module_names:
                        dependencies["standard_library"].append(full_import)
                    else:
                        dependencies["external_packages"].append(full_import)
    
    except Exception as e:
        dependencies["parse_error"] = str(e)
    
    return dependencies
```

**Example Output:**

```json
{
  "imports": [
    {"module": "os", "alias": null},
    {"module": "requests", "alias": null}
  ],
  "from_imports": [
    {"module": "typing", "name": "Dict", "alias": null},
    {"module": "sqlalchemy", "name": "create_engine", "alias": null}
  ],
  "local_imports": [".utils", ".models.user"],
  "external_packages": ["requests", "sqlalchemy"],
  "standard_library": ["os", "typing"]
}
```

**Security Agent Usage:**

```python
# Security agent can flag risky dependencies
risky_packages = ["eval", "exec", "pickle", "yaml.load"]
for pkg in dependencies["external_packages"]:
    if pkg in risky_packages:
        flag_security_risk(f"Risky package used: {pkg}")
```

**Benefit:** 
- Security agents spot dangerous imports (e.g., `pickle`, `eval`)
- Performance agents see expensive operations (e.g., `pandas` in hot path)
- Architecture agents check proper layering (e.g., "controllers shouldn't import models directly")

---

### 5. Related Files Discovery

**What:** Files that interact with the changed code

**Why:** Changes might break other parts of the system

**Implementation:**

```python
def find_related_files(repo, changed_file: str, file_content: str) -> list:
    """Find files that import or are imported by the changed file"""
    
    related = []
    
    # Extract what this file exports/defines
    exports = extract_exports(file_content)
    
    # Convert file path to module name
    file_module = changed_file.replace("/", ".").replace(".py", "")
    
    # Search repository for files importing this one
    try:
        # Method 1: GitHub code search
        search_terms = [
            f"import {file_module}",
            f"from {file_module} import"
        ]
        
        for term in search_terms:
            query = f"{term} repo:{repo.full_name} language:python"
            results = g.search_code(query)
            
            for result in results[:10]:  # Limit to top 10
                if result.path != changed_file:  # Don't include self
                    related.append({
                        "file": result.path,
                        "relationship": "imports_this_file",
                        "search_term": term,
                        "url": result.html_url,
                        "score": result.score
                    })
    except Exception as e:
        related.append({"error": f"Search failed: {e}"})
    
    # Method 2: Check imports in changed file
    imports = extract_imports(file_content)
    for imp in imports:
        # Try to locate the imported file
        possible_paths = [
            imp.replace(".", "/") + ".py",
            f"src/{imp.replace('.', '/')}.py",
            f"lib/{imp.replace('.', '/')}.py"
        ]
        
        for path in possible_paths:
            try:
                repo.get_contents(path)
                related.append({
                    "file": path,
                    "relationship": "imported_by_this_file",
                    "module": imp
                })
                break
            except:
                continue
    
    return related


def extract_exports(file_content: str) -> list:
    """Extract functions/classes defined in file"""
    import ast
    
    exports = []
    try:
        tree = ast.parse(file_content)
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                exports.append({
                    "type": "function",
                    "name": node.name,
                    "lineno": node.lineno
                })
            elif isinstance(node, ast.ClassDef):
                exports.append({
                    "type": "class",
                    "name": node.name,
                    "lineno": node.lineno
                })
    except:
        pass
    
    return exports
```

**Example Output:**

```json
{
  "related_files": [
    {
      "file": "app/controllers/user_controller.py",
      "relationship": "imports_this_file",
      "preview": "from app.services.auth import authenticate_user"
    },
    {
      "file": "app/models/user.py",
      "relationship": "imported_by_this_file",
      "module": "app.models.user"
    }
  ]
}
```

**Benefit:**
- "This function is called in 15 places - any breaking change affects many files"
- "This imports a deprecated module - suggest alternative"

---

### 6. File History & Evolution

**What:** Recent commits and changes to this file

**Why:** Understand why code exists, who maintains it, recent patterns

**Implementation:**

```python
def get_file_history(repo, file_path: str, limit: int = 10) -> dict:
    """Get recent commits affecting this file"""
    
    history = {
        "commits": [],
        "total_commits": 0,
        "first_commit": None,
        "last_commit": None,
        "main_contributors": []
    }
    
    try:
        # Get commits for this file
        commits = repo.get_commits(path=file_path)
        
        commit_list = []
        authors = {}
        
        for i, commit in enumerate(commits):
            if i >= limit:
                break
            
            commit_data = {
                "sha": commit.sha[:7],
                "author": commit.author.login if commit.author else "Unknown",
                "date": commit.commit.author.date.isoformat(),
                "message": commit.commit.message.split("\n")[0][:100],
                "stats": {
                    "additions": commit.stats.additions,
                    "deletions": commit.stats.deletions,
                    "total": commit.stats.total
                },
                "url": commit.html_url
            }
            
            commit_list.append(commit_data)
            
            # Track authors
            author = commit_data["author"]
            authors[author] = authors.get(author, 0) + 1
            
            # First and last commits
            if i == 0:
                history["last_commit"] = commit_data
            if i == limit - 1:
                history["first_commit"] = commit_data
        
        history["commits"] = commit_list
        history["total_commits"] = commits.totalCount
        
        # Top contributors
        history["main_contributors"] = sorted(
            authors.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
    
    except Exception as e:
        history["error"] = str(e)
    
    return history


def get_related_prs(repo, file_path: str, limit: int = 5) -> list:
    """Find recent PRs that touched this file"""
    
    related_prs = []
    
    try:
        # Search closed PRs
        prs = repo.get_pulls(state="all", sort="updated", direction="desc")
        
        for pr in prs:
            if len(related_prs) >= limit * 2:  # Get more to filter
                break
            
            try:
                # Check if PR touched this file
                files = [f.filename for f in pr.get_files()]
                if file_path in files:
                    related_prs.append({
                        "number": pr.number,
                        "title": pr.title,
                        "state": pr.state,
                        "merged": pr.merged,
                        "author": pr.user.login,
                        "created": pr.created_at.isoformat(),
                        "url": pr.html_url
                    })
                    
                    if len(related_prs) >= limit:
                        break
            except:
                continue
    
    except Exception as e:
        return [{"error": str(e)}]
    
    return related_prs
```

**Example Output:**

```json
{
  "commits": [
    {
      "sha": "abc123f",
      "author": "john_doe",
      "date": "2026-05-10T10:30:00Z",
      "message": "Fix authentication bug in login flow",
      "stats": {"additions": 15, "deletions": 8, "total": 23}
    },
    {
      "sha": "def456a",
      "author": "jane_smith",
      "date": "2026-05-01T14:20:00Z",
      "message": "Refactor auth service for better testability",
      "stats": {"additions": 120, "deletions": 95, "total": 215}
    }
  ],
  "total_commits": 47,
  "main_contributors": [
    ["john_doe", 25],
    ["jane_smith", 18],
    ["alice_jones", 4]
  ]
}
```

**Benefit:**
- "This file was recently refactored - new change might conflict"
- "This is actively maintained by john_doe - low risk"
- "This hasn't been touched in 2 years - higher risk of breakage"

---

### 7. Test Coverage Information

**What:** Whether changed code has tests, where they are

**Why:** Know if changes are risky (untested) or safe (well-tested)

**Implementation:**

```python
def find_related_tests(repo, changed_file: str, pr) -> dict:
    """Find test files related to the changed file"""
    
    test_info = {
        "test_files": [],
        "coverage_estimate": "unknown",
        "tests_modified_in_pr": False
    }
    
    # Common test file patterns
    filename = changed_file.split('/')[-1]
    base_name = filename.replace('.py', '')
    
    test_patterns = [
        # Pattern 1: test_filename.py in tests/ directory
        f"tests/test_{filename}",
        f"test/test_{filename}",
        
        # Pattern 2: filename_test.py in same directory
        changed_file.replace('.py', '_test.py'),
        
        # Pattern 3: Mirror directory structure
        changed_file.replace('src/', 'tests/test_'),
        changed_file.replace('lib/', 'tests/test_'),
        
        # Pattern 4: Subdirectory tests
        changed_file.replace('.py', '/test_' + base_name + '.py')
    ]
    
    # Search for test files
    for pattern in test_patterns:
        try:
            content = repo.get_contents(pattern)
            test_info["test_files"].append({
                "path": pattern,
                "size": content.size,
                "url": content.html_url,
                "exists": True
            })
        except:
            continue
    
    # Check if any tests were modified in this PR
    pr_files = [f.filename for f in pr.get_files()]
    test_files_in_pr = [f for f in pr_files if 'test' in f.lower()]
    
    test_info["tests_modified_in_pr"] = len(test_files_in_pr) > 0
    test_info["test_files_in_pr"] = test_files_in_pr
    
    # Estimate coverage
    if len(test_info["test_files"]) >= 2:
        test_info["coverage_estimate"] = "good"
    elif len(test_info["test_files"]) == 1:
        test_info["coverage_estimate"] = "moderate"
    else:
        test_info["coverage_estimate"] = "none"
    
    return test_info


def check_test_quality(test_file_content: str) -> dict:
    """Analyze test file quality"""
    import re
    
    quality = {
        "test_count": 0,
        "has_setup": False,
        "has_teardown": False,
        "uses_mocking": False,
        "uses_fixtures": False
    }
    
    # Count test functions
    quality["test_count"] = len(re.findall(r'def test_\w+', test_file_content))
    
    # Check for setup/teardown
    quality["has_setup"] = 'setUp' in test_file_content or '@pytest.fixture' in test_file_content
    quality["has_teardown"] = 'tearDown' in test_file_content
    
    # Check for mocking
    quality["uses_mocking"] = 'mock' in test_file_content.lower() or 'patch' in test_file_content
    
    # Check for fixtures
    quality["uses_fixtures"] = '@pytest.fixture' in test_file_content or '@fixture' in test_file_content
    
    return quality
```

**Example Output:**

```json
{
  "test_files": [
    {
      "path": "tests/test_auth_service.py",
      "size": 4567,
      "exists": true
    }
  ],
  "coverage_estimate": "moderate",
  "tests_modified_in_pr": true,
  "test_files_in_pr": ["tests/test_auth_service.py"],
  "test_quality": {
    "test_count": 12,
    "has_setup": true,
    "uses_mocking": true
  }
}
```

**Benefit:**
- "✅ This change includes tests - lower risk"
- "⚠️ No tests found for this critical authentication code - HIGH RISK"
- "✅ 12 existing tests cover this code"

---

### 8. Coding Standards & Linting Rules

**What:** Project-specific configuration files (.pylintrc, .flake8, etc.)

**Why:** Agents should enforce project standards, not generic rules

**Implementation:**

```python
def get_project_rules(repo) -> dict:
    """Extract project-specific rules and standards"""
    
    rules = {
        "linting": {},
        "formatting": {},
        "testing": {},
        "pre_commit": {}
    }
    
    # Linting configs
    linting_configs = {
        ".pylintrc": "pylint",
        ".flake8": "flake8",
        "setup.cfg": "setup_cfg",
        "tox.ini": "tox",
        "pyproject.toml": "pyproject"
    }
    
    for config_file, rule_type in linting_configs.items():
        try:
            content = repo.get_contents(config_file)
            decoded = content.decoded_content.decode()
            rules["linting"][rule_type] = {
                "content": decoded[:3000],  # First 3k chars
                "full_length": len(decoded),
                "url": content.html_url
            }
        except:
            continue
    
    # Formatting configs
    formatting_configs = {
        ".editorconfig": "editorconfig",
        ".prettierrc": "prettier",
        "pyproject.toml": "black_config"  # Black config in pyproject.toml
    }
    
    for config_file, rule_type in formatting_configs.items():
        try:
            content = repo.get_contents(config_file)
            decoded = content.decoded_content.decode()
            rules["formatting"][rule_type] = {
                "content": decoded[:2000],
                "url": content.html_url
            }
        except:
            continue
    
    # Pre-commit hooks
    try:
        content = repo.get_contents(".pre-commit-config.yaml")
        rules["pre_commit"] = {
            "content": content.decoded_content.decode(),
            "hooks": extract_pre_commit_hooks(content.decoded_content.decode())
        }
    except:
        pass
    
    # Extract key rules
    rules["summary"] = extract_rule_summary(rules)
    
    return rules


def extract_rule_summary(rules: dict) -> dict:
    """Extract key rules from config files"""
    import re
    
    summary = {
        "line_length": None,
        "indent_style": None,
        "quote_style": None,
        "required_checks": []
    }
    
    # Parse common settings
    for config_type, configs in rules.items():
        for rule_name, rule_data in configs.items():
            if not isinstance(rule_data, dict):
                continue
            
            content = rule_data.get("content", "")
            
            # Line length
            line_length_match = re.search(r'max[-_]line[-_]length\s*[=:]\s*(\d+)', content, re.IGNORECASE)
            if line_length_match and not summary["line_length"]:
                summary["line_length"] = int(line_length_match.group(1))
            
            # Indent style
            if 'indent_style' in content:
                indent_match = re.search(r'indent_style\s*=\s*(\w+)', content)
                if indent_match:
                    summary["indent_style"] = indent_match.group(1)
    
    return summary


def extract_pre_commit_hooks(yaml_content: str) -> list:
    """Extract hooks from pre-commit config"""
    import re
    
    hooks = []
    
    # Simple regex extraction (for more robust parsing, use yaml library)
    hook_ids = re.findall(r'id:\s*([^\n]+)', yaml_content)
    
    for hook_id in hook_ids:
        hooks.append(hook_id.strip())
    
    return hooks
```

**Example Output:**

```json
{
  "linting": {
    "flake8": {
      "content": "[flake8]\nmax-line-length = 88\nignore = E203, W503",
      "url": "https://github.com/..."
    }
  },
  "formatting": {
    "editorconfig": {
      "content": "indent_style = space\nindent_size = 4"
    }
  },
  "pre_commit": {
    "hooks": ["black", "flake8", "mypy", "isort"]
  },
  "summary": {
    "line_length": 88,
    "indent_style": "space",
    "required_checks": ["black", "flake8", "mypy"]
  }
}
```

**Benefit:**
- "This project uses line length 88, not 80"
- "Black is enforced via pre-commit - don't suggest manual formatting"
- "Project requires type hints (mypy enabled)"

---

### 9. Enhanced PR Payload Structure

**What:** Unified data structure with all context

**Why:** Single source of truth for all agents

**Implementation:**

```python
def crawl_pr_with_full_context(repo_full_name: str, pr_number: int) -> dict:
    """
    Enhanced PR crawler with comprehensive context
    
    Returns enriched PR data with:
    - Repository metadata
    - Project documentation
    - Full file contents
    - Dependency information
    - Related files
    - Historical context
    - Test coverage
    - Coding standards
    """
    
    repo = g.get_repo(repo_full_name)
    pr = repo.get_pull(pr_number)
    
    # Start with basic PR info
    pr_data = {
        "id": pr.number,
        "title": pr.title,
        "description": pr.body,
        "author": pr.user.login,
        "state": pr.state,
        "created_at": pr.created_at.isoformat(),
        "updated_at": pr.updated_at.isoformat(),
        
        # Branches
        "base_branch": pr.base.ref,
        "head_branch": pr.head.ref,
        
        # Stats
        "additions": pr.additions,
        "deletions": pr.deletions,
        "changed_files_count": pr.changed_files,
        "comments_count": pr.comments,
        "review_comments_count": pr.review_comments,
        
        # Status
        "mergeable": pr.mergeable,
        "draft": pr.draft,
        "labels": [label.name for label in pr.labels]
    }
    
    # === CONTEXT LAYER 1: Repository ===
    logger.info("Fetching repository context...")
    pr_data["repository_context"] = get_repository_context(repo_full_name)
    
    # === CONTEXT LAYER 2: Project Documentation ===
    logger.info("Fetching project documentation...")
    pr_data["project_docs"] = fetch_project_docs(repo)
    
    # === CONTEXT LAYER 3: Coding Standards ===
    logger.info("Fetching coding standards...")
    pr_data["coding_standards"] = get_project_rules(repo)
    
    # === CONTEXT LAYER 4: File-Level Context ===
    logger.info("Processing changed files with full context...")
    pr_data["files"] = []
    
    for file in pr.get_files():
        logger.info(f"Processing file: {file.filename}")
        
        file_data = {
            # Basic file info
            "filename": file.filename,
            "status": file.status,
            "additions": file.additions,
            "deletions": file.deletions,
            "changes": file.changes,
            "patch": file.patch,
            "raw_url": file.raw_url,
            "blob_url": file.blob_url,
            
            # CONTEXT: Full file content (before and after)
            "full_context": get_full_file_context(pr, file),
            
            # CONTEXT: Dependencies
            "dependencies": None,
            
            # CONTEXT: Related files
            "related_files": None,
            
            # CONTEXT: History
            "history": None,
            
            # CONTEXT: Related PRs
            "related_prs": None,
            
            # CONTEXT: Tests
            "test_coverage": None
        }
        
        # Only fetch detailed context for text files (not binary/images)
        if file.patch:  # Has a patch = text file
            try:
                # Get full file content
                full_content = file_data["full_context"]["after"]["content"] if file_data["full_context"]["after"] else file.patch
                
                # Analyze dependencies
                file_data["dependencies"] = analyze_dependencies(
                    file.filename,
                    full_content,
                    language=pr_data["repository_context"]["language"]
                )
                
                # Find related files (expensive, limit usage)
                file_data["related_files"] = find_related_files(
                    repo, 
                    file.filename,
                    full_content
                )
                
                # Get file history
                file_data["history"] = get_file_history(repo, file.filename, limit=5)
                
                # Get related PRs (expensive, limit usage)
                file_data["related_prs"] = get_related_prs(repo, file.filename, limit=3)
                
                # Check test coverage
                file_data["test_coverage"] = find_related_tests(repo, file.filename, pr)
                
            except Exception as e:
                logger.error(f"Error processing context for {file.filename}: {e}")
                file_data["context_error"] = str(e)
        
        pr_data["files"].append(file_data)
    
    # Add metadata
    pr_data["context_metadata"] = {
        "crawled_at": datetime.now().isoformat(),
        "context_version": "2.0",
        "layers": [
            "repository_context",
            "project_docs",
            "coding_standards",
            "full_file_content",
            "dependencies",
            "related_files",
            "history",
            "test_coverage"
        ]
    }
    
    return pr_data
```

---

### 10. Smart Context Filtering by Agent Type

**What:** Give each agent only the context they need

**Why:** Avoid context overflow, reduce costs, improve focus

**Implementation:**

```python
def filter_context_for_agent(pr_data: dict, agent_type: str) -> dict:
    """
    Filter PR context based on agent specialization
    
    Args:
        pr_data: Full PR data with all context
        agent_type: 'security', 'performance', or 'architecture'
    
    Returns:
        Filtered context relevant to agent
    """
    
    # Base context (all agents get this)
    filtered = {
        "pr_id": pr_data["id"],
        "title": pr_data["title"],
        "description": pr_data["description"],
        "repository": pr_data["repository_context"]["name"],
        "language": pr_data["repository_context"]["language"]
    }
    
    # === SECURITY AGENT CONTEXT ===
    if agent_type == "security":
        filtered["context_type"] = "security"
        filtered["relevant_docs"] = pr_data["project_docs"].get("SECURITY.md")
        
        filtered["files"] = []
        for file in pr_data["files"]:
            filtered["files"].append({
                "filename": file["filename"],
                "patch": file["patch"],
                "full_content": file["full_context"]["after"]["content"] if file["full_context"]["after"] else None,
                
                # Security-relevant context
                "dependencies": file["dependencies"],
                "external_packages": file["dependencies"]["external_packages"] if file["dependencies"] else [],
                "imports": file["dependencies"]["imports"] if file["dependencies"] else []
            })
        
        # Security-specific summary
        filtered["risk_indicators"] = {
            "uses_dangerous_functions": check_dangerous_functions(pr_data),
            "new_dependencies": extract_new_dependencies(pr_data),
            "accesses_secrets": check_secret_access(pr_data)
        }
    
    # === PERFORMANCE AGENT CONTEXT ===
    elif agent_type == "performance":
        filtered["context_type"] = "performance"
        
        filtered["files"] = []
        for file in pr_data["files"]:
            filtered["files"].append({
                "filename": file["filename"],
                "patch": file["patch"],
                "full_content": file["full_context"]["after"]["content"] if file["full_context"]["after"] else None,
                
                # Performance-relevant context
                "file_size_change": file["changes"],
                "history": file["history"],  # See if file has performance history
                "related_files": file["related_files"],  # Understand call chains
                "dependencies": file["dependencies"]
            })
        
        # Performance-specific summary
        filtered["performance_indicators"] = {
            "large_file_changes": [f for f in pr_data["files"] if f["changes"] > 500],
            "loop_intensive_files": check_for_loops(pr_data),
            "database_queries": check_for_db_queries(pr_data)
        }
    
    # === ARCHITECTURE AGENT CONTEXT ===
    elif agent_type == "architecture":
        filtered["context_type"] = "architecture"
        filtered["relevant_docs"] = {
            "CONTRIBUTING": pr_data["project_docs"].get("CONTRIBUTING.md"),
            "ARCHITECTURE": pr_data["project_docs"].get("ARCHITECTURE.md"),
            "STYLE_GUIDE": pr_data["project_docs"].get("STYLE_GUIDE.md")
        }
        filtered["coding_standards"] = pr_data["coding_standards"]
        
        filtered["files"] = []
        for file in pr_data["files"]:
            filtered["files"].append({
                "filename": file["filename"],
                "patch": file["patch"],
                "full_content": file["full_context"]["after"]["content"] if file["full_context"]["after"] else None,
                
                # Architecture-relevant context
                "dependencies": file["dependencies"],
                "related_files": file["related_files"],
                "history": file["history"],
                "test_coverage": file["test_coverage"]
            })
        
        # Architecture-specific summary
        filtered["architecture_indicators"] = {
            "new_files": [f for f in pr_data["files"] if f["status"] == "added"],
            "deleted_files": [f for f in pr_data["files"] if f["status"] == "removed"],
            "cross_layer_changes": analyze_layer_violations(pr_data),
            "missing_tests": [f for f in pr_data["files"] if f["test_coverage"]["coverage_estimate"] == "none"]
        }
    
    return filtered


# Helper functions for risk indicators
def check_dangerous_functions(pr_data: dict) -> list:
    """Check for dangerous function usage"""
    dangerous = []
    dangerous_patterns = ['eval(', 'exec(', 'pickle.loads', '__import__', 'os.system']
    
    for file in pr_data["files"]:
        if file["patch"]:
            for pattern in dangerous_patterns:
                if pattern in file["patch"]:
                    dangerous.append({
                        "file": file["filename"],
                        "function": pattern,
                        "severity": "high"
                    })
    
    return dangerous


def extract_new_dependencies(pr_data: dict) -> list:
    """Find newly added dependencies"""
    new_deps = []
    
    for file in pr_data["files"]:
        if file["filename"] in ["requirements.txt", "package.json", "Pipfile"]:
            if file["patch"]:
                # Lines starting with '+' in requirements
                import re
                added_lines = re.findall(r'^\+([^+].*)', file["patch"], re.MULTILINE)
                new_deps.extend([line.strip() for line in added_lines if line.strip()])
    
    return new_deps


def check_secret_access(pr_data: dict) -> list:
    """Check for potential secret access"""
    secrets = []
    secret_patterns = ['API_KEY', 'SECRET', 'PASSWORD', 'TOKEN', 'CREDENTIAL']
    
    for file in pr_data["files"]:
        if file["patch"]:
            for pattern in secret_patterns:
                if pattern in file["patch"].upper():
                    secrets.append({
                        "file": file["filename"],
                        "pattern": pattern
                    })
    
    return secrets
```

**Example Filtered Output for Security Agent:**

```json
{
  "context_type": "security",
  "pr_id": 123,
  "title": "Add user authentication",
  "files": [
    {
      "filename": "auth/login.py",
      "patch": "...",
      "dependencies": {
        "external_packages": ["bcrypt", "jwt"]
      }
    }
  ],
  "risk_indicators": {
    "uses_dangerous_functions": [],
    "new_dependencies": ["PyJWT==2.8.0"],
    "accesses_secrets": [
      {"file": "auth/login.py", "pattern": "SECRET_KEY"}
    ]
  }
}
```

**Benefit:**
- Security agent gets security-relevant context only
- Reduces token usage (cheaper)
- Improves focus (less noise)
- Faster processing (smaller context)

---

### 11. Prompt Engineering with Context

**What:** Update agent prompts to use the rich context

**Why:** Context is useless if agents don't use it properly

**Example: Enhanced Security Agent Prompt**

```python
SECURITY_AGENT_SYSTEM_PROMPT = """
You are a security auditor reviewing a pull request.

Your role: Identify security vulnerabilities in code changes.
"""

def create_security_prompt(filtered_context: dict) -> str:
    """Generate security analysis prompt with context"""
    
    repo_name = filtered_context["repository"]
    language = filtered_context["language"]
    
    # Build context sections
    context_sections = []
    
    # 1. Repository info
    context_sections.append(f"""
## Repository Information
- Name: {repo_name}
- Language: {language}
- Type: {get_repo_type(filtered_context)}
""")
    
    # 2. Security guidelines (if available)
    if filtered_context.get("relevant_docs"):
        context_sections.append(f"""
## Project Security Guidelines
{filtered_context["relevant_docs"][:1000]}
""")
    
    # 3. Risk indicators
    risk_indicators = filtered_context.get("risk_indicators", {})
    if risk_indicators.get("new_dependencies"):
        context_sections.append(f"""
## ⚠️ New Dependencies Added
This PR introduces new dependencies:
{format_list(risk_indicators["new_dependencies"])}

Please verify these are from trusted sources and don't have known vulnerabilities.
""")
    
    if risk_indicators.get("accesses_secrets"):
        context_sections.append(f"""
## ⚠️ Secret Access Detected
The following files access secrets/credentials:
{format_list(risk_indicators["accesses_secrets"])}

Verify secrets are handled securely (not hardcoded, properly encrypted).
""")
    
    # 4. File-by-file analysis
    files_section = []
    for file in filtered_context["files"]:
        files_section.append(f"""
### File: `{file["filename"]}`

**External Dependencies Used:**
{format_list(file.get("external_packages", []))}

**Full File Content (after changes):**
```{language}
{file["full_content"][:3000]}  # First 3000 chars
```

**Changes Made (diff):**
```diff
{file["patch"]}
```
""")
    
    # Combine all sections
    full_prompt = f"""
{SECURITY_AGENT_SYSTEM_PROMPT}

{chr(10).join(context_sections)}

## Code Changes to Review

{chr(10).join(files_section)}

## Your Task

Perform a security review and provide:

1. **Vulnerabilities Found** (if any):
   - Type (e.g., SQL Injection, XSS, Auth Bypass)
   - Severity (Critical / High / Medium / Low)
   - Location (file and line)
   - Description
   - Recommendation

2. **Security Best Practices**:
   - Areas following good practices
   - Suggestions for improvement

3. **Overall Assessment**:
   - Risk Level: (Low / Medium / High / Critical)
   - Confidence: (0-100%)
   - Approval Recommendation: (Approve / Request Changes / Needs Discussion)

Respond in structured JSON format.
"""
    
    return full_prompt
```

---

## Implementation Guide

### Phase 1: Quick Wins (Week 1)

**Priority: High Impact, Low Effort**

1. **Full File Content** ✅
   ```python
   # Add to crawler.py
   file_data["full_content"] = get_full_file_context(pr, file)
   ```

2. **Basic Dependencies** ✅
   ```python
   file_data["imports"] = extract_imports(file.patch)
   ```

3. **README Context** ✅
   ```python
   pr_data["readme"] = repo.get_readme().decoded_content.decode()[:2000]
   ```

**Expected Impact:** +30% improvement in review quality

---

### Phase 2: Medium Enhancements (Week 2)

**Priority: Medium Impact, Medium Effort**

1. **Project Documentation**
   - Fetch CONTRIBUTING.md, SECURITY.md
   - Parse coding standards

2. **Related Files Discovery**
   - Find files that import changed code
   - Show files imported by changed code

3. **Coding Standards**
   - Extract .pylintrc, .flake8 rules
   - Include in agent prompts

**Expected Impact:** +20% improvement

---

### Phase 3: Advanced Context (Week 3+)

**Priority: High Impact, High Effort**

1. **Historical Context**
   - Recent commits to file
   - Related PRs

2. **Test Coverage Analysis**
   - Find test files
   - Estimate coverage

3. **Smart Context Filtering**
   - Agent-specific context
   - Token optimization

**Expected Impact:** +15% improvement

---

## Priority Matrix

| Enhancement | Impact | Effort | Priority | Implementation Time |
|-------------|--------|--------|----------|-------------------|
| **Full file content** | 🔴 Very High | 🟢 Low | **1** | 1-2 hours |
| **Dependencies/imports** | 🔴 Very High | 🟢 Low | **2** | 1-2 hours |
| **README context** | 🟠 High | 🟢 Low | **3** | 30 minutes |
| **Project docs** | 🟠 High | 🟡 Medium | **4** | 2-3 hours |
| **Coding standards** | 🟠 High | 🟡 Medium | **5** | 2-3 hours |
| **Related files** | 🟡 Medium | 🟠 High | **6** | 4-6 hours |
| **File history** | 🟡 Medium | 🟡 Medium | **7** | 2-3 hours |
| **Test coverage** | 🟡 Medium | 🟡 Medium | **8** | 3-4 hours |
| **Related PRs** | 🟢 Low | 🟠 High | **9** | 4-6 hours |
| **Smart filtering** | 🟠 High | 🟠 High | **10** | 4-6 hours |

---

## Best Practices

### 1. **Balance Context vs Cost**

**Problem:** More context = more tokens = higher cost

**Solution:**
- Start with essential context (full file, imports, README)
- Add advanced context only for complex PRs
- Implement tiered context levels:
  - **Level 1 (Basic):** Full file + imports (~2K tokens extra)
  - **Level 2 (Standard):** + docs + standards (~5K tokens extra)
  - **Level 3 (Deep):** + history + related files (~10K tokens extra)

```python
def get_context_level(pr: dict) -> str:
    """Determine appropriate context level"""
    
    # Large PRs need less per-file context
    if pr["changed_files_count"] > 20:
        return "basic"
    
    # Security-sensitive files need deep context
    security_files = ["auth", "login", "password", "token", "api_key"]
    if any(keyword in pr["title"].lower() for keyword in security_files):
        return "deep"
    
    # Default
    return "standard"
```

---

### 2. **Cache Expensive Operations**

**Problem:** Fetching full files and history is slow

**Solution:**
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_file_content_cached(repo_name: str, file_path: str, sha: str) -> str:
    """Cache file contents by SHA"""
    repo = g.get_repo(repo_name)
    content = repo.get_contents(file_path, ref=sha)
    return content.decoded_content.decode()
```

---

### 3. **Graceful Degradation**

**Problem:** Some context may not be available (private repos, deleted files)

**Solution:**
```python
def safe_get_context(func, *args, **kwargs):
    """Wrapper for safe context fetching"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.warning(f"Failed to fetch context: {e}")
        return {
            "error": str(e),
            "available": False
        }

# Usage
file_data["history"] = safe_get_context(get_file_history, repo, file.filename)
```

---

### 4. **Progressive Context Loading**

**Problem:** Loading all context upfront is slow

**Solution:**
```python
async def load_context_async(pr_data: dict) -> dict:
    """Load context progressively"""
    
    # Load in parallel
    tasks = [
        asyncio.create_task(get_repository_context_async(pr_data["repo"])),
        asyncio.create_task(fetch_project_docs_async(pr_data["repo"])),
        asyncio.create_task(get_project_rules_async(pr_data["repo"]))
    ]
    
    results = await asyncio.gather(*tasks)
    
    return {
        "repository_context": results[0],
        "project_docs": results[1],
        "coding_standards": results[2]
    }
```

---

### 5. **Token Budget Management**

**Problem:** Context might exceed LLM token limits

**Solution:**
```python
def enforce_token_budget(context: dict, max_tokens: int = 100000) -> dict:
    """Ensure context fits within token budget"""
    
    # Rough estimate: 1 token ≈ 4 characters
    estimated_tokens = sum(len(str(v)) for v in context.values()) / 4
    
    if estimated_tokens > max_tokens:
        # Prioritize and truncate
        context = truncate_context(context, max_tokens)
    
    return context


def truncate_context(context: dict, max_tokens: int) -> dict:
    """Intelligently truncate context"""
    
    # Priority order
    priority = [
        "files",  # Most important
        "dependencies",
        "coding_standards",
        "project_docs",
        "history",
        "related_files"
    ]
    
    # Keep trimming lowest priority items
    for key in reversed(priority):
        if key in context:
            estimated = sum(len(str(v)) for v in context.values()) / 4
            if estimated <= max_tokens:
                break
            
            # Truncate this item
            if isinstance(context[key], str):
                context[key] = context[key][:len(context[key])//2]
            elif isinstance(context[key], list):
                context[key] = context[key][:len(context[key])//2]
    
    return context
```

---

## Evaluation Metrics

### How to Measure Improvement

After implementing context enhancements, measure:

1. **Precision** (fewer false positives)
   - Before: Agent flags 20 issues, 10 are false positives → 50% precision
   - After: Agent flags 15 issues, 2 are false positives → 87% precision ✅

2. **Recall** (fewer false negatives)
   - Before: 20 real issues, agent finds 12 → 60% recall
   - After: 20 real issues, agent finds 17 → 85% recall ✅

3. **Confidence Scores**
   - Track agent confidence in findings
   - Higher confidence = better context

4. **Conflicting Findings**
   - Fewer conflicts between agents = better understanding

---

## Code Integration Points

### Where to Add Context in Current Codebase

1. **In `crawler/crawler.py`:**
   ```python
   # Add to crawl_pr() method
   pr_payload["repository_context"] = get_repository_context(repo_full_name)
   pr_payload["project_docs"] = fetch_project_docs(repo)
   ```

2. **In `crawler/llm_formatter.py`:**
   ```python
   # Add context sections to prompts
   def _build_context_section(self, pr: Dict) -> str:
       """Build comprehensive context section"""
       # Implementation here
   ```

3. **In `agents/base_agent.py` (when created):**
   ```python
   class BaseAgent:
       def prepare_context(self, pr_data: dict) -> dict:
           """Filter context for this agent type"""
           return filter_context_for_agent(pr_data, self.agent_type)
   ```

---

## Conclusion

### Key Takeaways

1. **Context is Critical**
   - Agents reviewing only diffs = limited understanding
   - Full context = better reviews

2. **Start Simple**
   - Phase 1: Full files + imports (2 hours work)
   - Immediate 30% quality improvement

3. **Balance Cost vs Quality**
   - More context = better reviews but higher cost
   - Smart filtering maximizes value

4. **Measure Impact**
   - Track precision, recall, confidence
   - Prove context improves results (for thesis!)

### Implementation Checklist

- [ ] Phase 1: Full file content (2 hours)
- [ ] Phase 1: Basic dependencies (2 hours)  
- [ ] Phase 1: README context (30 minutes)
- [ ] Phase 2: Project documentation (3 hours)
- [ ] Phase 2: Coding standards (3 hours)
- [ ] Phase 2: Related files (6 hours)
- [ ] Phase 3: Historical context (3 hours)
- [ ] Phase 3: Test coverage (4 hours)
- [ ] Phase 3: Smart filtering (6 hours)
- [ ] Evaluation: Measure improvement
- [ ] Documentation: Update thesis

**Total Estimated Time:** 30-35 hours

**Expected Quality Improvement:** +65% overall

---

## References & Further Reading

1. **GitHub API Documentation**
   - https://docs.github.com/en/rest

2. **Context Window Optimization**
   - OpenAI: https://platform.openai.com/docs/guides/optimizing-tokens
   - Anthropic: https://docs.anthropic.com/claude/docs/optimizing-your-prompt

3. **Code Review Best Practices**
   - Google Engineering Practices: https://google.github.io/eng-practices/review/

4. **Static Analysis Tools**
   - Semgrep: https://semgrep.dev/
   - CodeQL: https://codeql.github.com/

---

**Document End**

*For questions or clarifications, refer to PROJECT_OVERVIEW.md and LIMITATIONS_AND_IMPROVEMENTS.md*
