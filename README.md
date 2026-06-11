# KGWave — Code Repository Graph Generator

通过 AST / tree-sitter 静态分析，将任意代码仓库解析为结构化的依赖图谱（JSON 格式）。

## 当前支持状态

| 语言 | 解析器 | 状态 |
|------|--------|------|
| Python | 标准库 `ast` | ✅ 完整支持 |
| JavaScript | tree-sitter | ⚠️ 需安装 `tree-sitter-javascript` |
| TypeScript | tree-sitter | ⚠️ 需安装 `tree-sitter-typescript` |
| Java | tree-sitter | ⚠️ 需安装 `tree-sitter-java` |
| C | tree-sitter | ⚠️ 需安装 `tree-sitter-c` |
| C++ | tree-sitter | ⚠️ 需安装 `tree-sitter-cpp` |
| C# | tree-sitter | ⚠️ 需安装 `tree-sitter-c-sharp` |
| PHP | tree-sitter | ⚠️ 需安装 `tree-sitter-php` |
| Kotlin | tree-sitter | ⚠️ 需安装 `tree-sitter-kotlin` |

> 当前已完整测试 Python 仓库的解析。其他语言需要额外安装对应的 tree-sitter 语法包，未安装的语言会被自动跳过。

## 安装依赖

```bash
# 基础依赖（仅解析 Python 仓库时不需要额外安装）
pip install tree-sitter

# 按需安装其他语言的语法包
pip install tree-sitter-python tree-sitter-javascript tree-sitter-typescript \
            tree-sitter-java tree-sitter-c tree-sitter-cpp tree-sitter-c-sharp \
            tree-sitter-php tree-sitter-kotlin
```

## 使用方式

使用这个工具只需要提供**任意一个代码仓库的路径**，工具会自动遍历目录、识别语言、解析 AST 并生成图谱。

### 命令行调用

```bash
# 最简用法：解析任意代码仓库
python stage_one/code_parse.py --repo_path /path/to/your/repo

# 指定输出路径
python stage_one/code_parse.py --repo_path /path/to/repo --output graph.json

# 排除特定文件类型
python stage_one/code_parse.py --repo_path /path/to/repo --exclude-ext .spec.ts .test.py

# 手动指定仓库名（格式：owner#repo#commit）
python stage_one/code_parse.py --repo_path /path/to/repo --repo-name "myorg#myrepo#abc123"
```

### Python API 调用

```python
from stage_one.code_parse import IDAllocator, GraphOutput, RepoWalker, analyze_file, resolve_calls, resolve_imports

# 1. 初始化
id_alloc = IDAllocator(start=10)
graph = GraphOutput()

# 2. 遍历仓库目录树，创建 Repo/Package/File 节点
walker = RepoWalker(
    repo_path="/path/to/repo",
    repo_name="owner#repo#commit",
    id_alloc=id_alloc,
    graph=graph
)
walker.walk()

# 3. 按语言分组，逐文件解析 AST
files_by_lang = {}
for file_id, (abs_path, language) in graph.file_paths.items():
    files_by_lang.setdefault(language, []).append((file_id, abs_path))

for lang, files in files_by_lang.items():
    for file_id, abs_path in files:
        with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        analyze_file(file_id, abs_path, content, lang, id_alloc, graph)

# 4. 跨文件解析：通过符号表连接调用和导入关系
resolve_calls(graph)
resolve_imports(graph)

# 5. 获取结果
print(f"节点数: {len(graph.nodes)}")
print(f"边数: {len(graph.edges)}")

# 6. 写入 JSON 文件
graph.to_json("output.graph.json")
```

### 全部命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--repo_path` | 要分析的仓库路径（必填） | — |
| `--output`, `-o` | 输出 JSON 文件路径 | `output.graph.json` |
| `--repo-name` | 仓库名，格式 `owner#repo#commit` | 自动从 git 检测 |
| `--exclude-ext` | 要排除的文件扩展名列表 | 无 |

## 输入数据格式

工具接受任意代码仓库目录作为输入。目录结构示例：

```
/path/to/repo/
├── src/
│   ├── main.py
│   ├── utils.py
│   └── models/
│       └── model.py
├── tests/
│   └── test_main.py
├── README.md
└── requirements.txt
```

- 代码文件（`.py`, `.js`, `.java` 等）会被解析为 `File` 节点，提取其中的函数、类、变量
- 非代码文件（`.md`, `.txt`, `.json` 等）会被记录为 `TextFile` 节点
- 自动跳过 `.git`, `node_modules`, `__pycache__` 等目录

## 输出格式

输出为 JSON 文件，包含 `nodes` 和 `edges` 两个数组。

### 节点类型（8 种）

**Repo** — 仓库根节点
```json
{
  "id": 10,
  "nodeType": "Repo",
  "repoName": "owner#repo#abc123",
  "groupName": ""
}
```

**Package** — 目录/包
```json
{
  "id": 11,
  "nodeType": "Package",
  "name": "src/utils"
}
```

**File** — 代码文件
```json
{
  "id": 13,
  "nodeType": "File",
  "fileName": "main.py",
  "filePath": "src",
  "text": "完整源码..."
}
```

**TextFile** — 非代码文件
```json
{
  "id": 14,
  "nodeType": "TextFile",
  "name": "README.md",
  "path": "",
  "text": "完整内容..."
}
```

**Function** — 函数/方法
```json
{
  "id": 26,
  "nodeType": "Function",
  "name": "parse_data",
  "col": 0,
  "startLoc": 10,
  "endLoc": 25,
  "header": "def parse_data(input: str) -> dict:",
  "text": "完整函数源码...",
  "comment": "docstring 或注释，无则为 \"null\""
}
```

**Class** — 类
```json
{
  "id": 27,
  "nodeType": "Class",
  "className": "DataLoader",
  "col": 0,
  "startLoc": 30,
  "endLoc": 50,
  "text": "完整类源码...",
  "comment": "null"
}
```

**Attribute** — 模块/类级别的变量
```json
{
  "id": 20,
  "nodeType": "Attribute",
  "name": "logger",
  "col": 0,
  "startLoc": 5,
  "endLoc": 5,
  "text": "logger = logging.getLogger(__name__)",
  "comment": "null",
  "attributeType": "getLogger"
}
```

**Lambda** — 匿名函数
```json
{
  "id": 126,
  "nodeType": "Lambda",
  "col": 23,
  "startLoc": 42,
  "endLoc": 42,
  "text": "lambda x: x + 1"
}
```

### 边类型（3 种）

**contains** — 层级包含关系
```json
{ "edgeType": "contains", "source": 10, "target": 11 }
```
连接：Repo → Package → File → Function / Class / Attribute / Lambda

**calls** — 函数调用关系（跨文件解析）
```json
{ "edgeType": "calls", "source": 38, "target": 26 }
```

**imports** — 导入依赖关系
```json
{ "edgeType": "imports", "source": 13, "target": 45 }
```

## 图谱结构总览

```
Repo
 └─ Package (目录)
     ├─ Package (子目录)
     ├─ File (代码文件)
     │   ├─ Function
     │   │   └─ [calls] → Function (跨文件调用)
     │   ├─ Class
     │   │   ├─ Function (方法)
     │   │   └─ Attribute (成员变量)
     │   ├─ Attribute (模块级变量)
     │   └─ Lambda
     └─ TextFile (非代码文件)

File --[imports]→ File (导入依赖)
```

## 构建流程

```
Phase 1: 遍历仓库目录树
         os.walk → 创建 Repo / Package / File / TextFile 节点

Phase 2: 逐文件 AST 解析
         Python  → 标准库 ast.NodeVisitor
         其他    → tree-sitter 递归遍历

Phase 3: 跨文件解析
         全局符号表 → 解析 calls 和 imports 边

Phase 4: 序列化输出
         写入 JSON 文件
```

## 示例运行统计

以本项目自身为输入：

```
节点分布:  Repo=1, Package=5, File=4, Function=108, Class=14, Attribute=17, Lambda=1
边分布:    contains=149, calls=33
```
