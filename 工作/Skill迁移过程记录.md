---
tags:
  - "#类型/项目"
  - "#用途/工作"
  - "#状态/草稿"
created: 2026-07-30
updated: 2026-07-30
---

# Skill 迁移过程记录

> 目标：建立一套可复现的 Skill 迁移流程 —— 工具链从零搭建，流程从零定义。
> 
> **决策**：迁移工具链（analyze / pack / check / test）需要从零开发。先建工具，再做第一次真实迁移验证。

---

## 一、核心原则

1. **不改变原意**：迁移的是能力，不是重写。原脚本/原 Skill 的设计思想 100% 保留。
2. **可追溯**：每一步都能回退，迁移前后行为一致。
3. **降级兼容**：如果目标环境缺依赖，Skill 能自检并给出明确提示，而不是静默失败。

---

## 二、Skill vs 脚本：先判断再迁移

### 2.1 判断标准

| 特征 | 脚本 | Skill |
|------|------|-------|
| 形态 | 单个 .py / .sh / .js 文件 | 包含 system prompt + 工具定义 + 执行逻辑 |
| 调用方式 | 命令行直接执行 | 由 AI Agent 在对话中按需调用 |
| 输入输出 | 固定参数 → 固定结果 | 自然语言上下文 → 工具调用 → 结果回传 |
| 独立性 | 完全独立运行 | 依赖 Agent 框架（Claude Code / Hermes） |
| 可发现性 | 需要记住路径和参数 | Agent 根据描述自动匹配 |

### 2.2 判断流程

```
拿到一个东西
├── 有 skill.md / prompt.md / 工具定义？ → 已经是 Skill → 直接迁移
├── 有 requirements.txt / package.json？ → 是脚本 → 进入"脚本转 Skill"
└── 就是一个 .py / .sh？ → 是脚本 → 进入"脚本转 Skill"
```

---

## 三、脚本转 Skill（不改思想）

### 3.1 分析阶段（理解它做了什么）

1. **读入口**：找到 main() / 入口函数 / 参数解析
2. **画流程**：输入 → 处理 → 输出，画出数据流
3. **提取核心逻辑**：干掉命令行参数解析、文件路径硬编码，保留纯逻辑
4. **记录依赖**：Python 包、系统工具、环境变量、外部 API

### 3.2 包装阶段（加上 Skill 外壳）

在**不修改**原脚本核心逻辑的前提下，加三层：

```
原脚本（核心逻辑，不动）
    │
    ├── 第1层：工具函数（把原脚本的函数暴露为可调用的 tool）
    │   例：原来 def generate_ppt(content, template)
    │       → 变成 tool: generate_ppt(content: str, template: str) -> str
    │
    ├── 第2层：System Prompt（告诉 AI 什么时候用、怎么用）
    │   例："当用户需要生成 PPT 时，先用 ask_clarification 确认时长和风格，
    │        然后调用 generate_ppt。生成后调用 validate_pptx 检查格式。"
    │
    └── 第3层：自检脚本（check_dependencies）
        检查 Python 版本、pip 包、外部工具是否可用
        缺什么 → 返回明确的安装指令，不让用户猜
```

### 3.3 验证阶段

- [ ] 同样输入 → 同样输出（对比迁移前后结果）
- [ ] 缺依赖时报错信息能指导修复
- [ ] Agent 能在对话中正确调用（不只是命令行能跑）

---

## 四、传输方式

### 4.1 Git（推荐，适合代码）

```
源机器                          目标机器
  │                                │
  ├─ git push origin main ────────→ git clone / git pull
  │                                │
  └─ 记得一起传：                  └─ git clone 后：
      - 源码                          - pip install -r requirements.txt
      - requirements.txt              - 运行自检脚本
      - .env.example                  - 配置 .env
      - 迁移记录（本文件）
```

**优点**：版本控制、diff 可见、可回退
**缺点**：需要网络、私有仓库或 SSH key

### 4.2 实体硬盘 / U 盘（适合大文件或无网络）

```
源机器                          目标机器
  │                                │
  ├─ 打包：                        └─ 解压后：
  │   tar -czf skill.tar.gz           - 检查 Python 版本
  │     src/                          - pip install -r requirements.txt
  │     requirements.txt              - 运行自检脚本
  │     .env.example                  - 对比文件 hash 确认完整性
  │     SKILL_MIGRATION.md
  │
  └─ 验证：sha256sum skill.tar.gz > checksum.txt
```

**优点**：不需要网络、传输快
**缺点**：无版本历史、容易产生"哪个是最新版"的问题

### 4.3 传输包应该包含什么

```
skill-migration-bundle/
├── src/                    # 源码
├── requirements.txt        # Python 依赖
├── .env.example            # 环境变量模板（不含真实密钥）
├── SKILL_MIGRATION.md      # 迁移说明（本文件）
├── checksum.txt            # 文件完整性校验
├── test_input/             # 测试用例输入
├── test_expected/          # 测试用例预期输出
└── install.sh              # 一键安装脚本（可选）
```

---

## 五、迁移 SOP（标准操作流程）

### 源机器

```bash
# 1. 分析
python analyze_skill.py --path ./my-skill    # 自动分析依赖和结构

# 2. 打包
python pack_skill.py --path ./my-skill --output ./skill-bundle/

# 3. 生成校验
cd skill-bundle && sha256sum **/* > checksum.txt

# 4. 传输（选一种）
git push          # Git
# 或
cp -r skill-bundle /media/usb/   # U 盘
```

### 目标机器

```bash
# 1. 校验完整性
sha256sum -c checksum.txt

# 2. 自检环境
python check_env.py    # 输出：缺什么、怎么装

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置
cp .env.example .env
nano .env    # 填入实际的 key 和路径

# 5. 验证
python run_tests.py    # 跑测试用例，对比预期输出

# 6. 注册为 Skill（Claude Code）
# 把 skill 目录放到 .claude/skills/ 下
# 或写到 settings.json 的 hooks/skills 里
```

---

## 六、常见坑

| 问题 | 预防 |
|------|------|
| 硬编码路径 | 分析阶段扫描所有 `/home/xxx/` `/Users/xxx/` `C:\Users\xxx\` |
| Python 版本差异 | `check_env.py` 第一行就检查 `sys.version_info` |
| 缺少系统依赖（ffmpeg、wkhtmltopdf 等） | `shutil.which()` 逐个检查 |
| .env 里的 key 泄露到 git | `.env` 在 .gitignore，只传 `.env.example` |
| 两个机器都改了同一个文件 | Git 优先，U 盘传输时用 checksum 对比差异 |
| 脚本里嵌了 AI prompt 但格式不对 | 统一改用 `SKILL.md` 的 frontmatter + body 格式 |

---

## 七、待办：工具链从零搭建

### 7.1 analyze_skill.py（优先级最高）

```python
# 功能：
# 1. 扫描目录结构，识别入口文件、配置文件、依赖声明
# 2. 提取所有 import / require / 外部命令调用
# 3. 扫描硬编码路径（/home/xxx/、C:\Users\xxx\、~/xxx）
# 4. 输出：依赖清单 + 路径风险报告 + 结构树
```

### 7.2 pack_skill.py

```python
# 功能：
# 1. 根据 analyze_skill 的结果，只打包必要文件
# 2. 生成 checksum.txt（sha256）
# 3. 输出：skill-bundle.tar.gz + 安装说明
```

### 7.3 check_env.py

```python
# 功能（在目标机器上跑）：
# 1. 检查 Python 版本 (>= 3.10)
# 2. 检查 pip 包是否已安装
# 3. shutil.which() 检查系统工具（ffmpeg、git 等）
# 4. 检查环境变量是否已配
# 5. 输出：红/黄/绿报告，缺什么 + 怎么装
```

### 7.4 开发顺序

1. `analyze_skill.py`（先能看清一个东西是什么）
2. `check_env.py`（先能在目标机器上自检）
3. `pack_skill.py`（打包 + 校验）
4. 用 PPT Agent 的 Skill 做第一次真实迁移验证
