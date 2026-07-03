---
tags:
  - "#用途/工作学习"
  - "#类型/技术"
  - "#技术/git"
  - "#状态/草稿"
created: 2026-06-26
updated: 2026-07-03
status: draft
---

# Git 基础与协作

简历上写"会用 Git"是基本要求。面试不会专门考 Git，但入职第一天就要用。

---

## 一、Git 三区模型（深入版）

Git 的核心概念只有三个区域，搞清楚这三个区域，所有命令都活了。

```
┌─────────────┐    git add    ┌─────────────┐   git commit   ┌─────────────┐
│   工作区     │  ──────────→  │   暂存区     │  ──────────→   │   本地仓库    │
│  Working    │               │   Staging   │               │ Repository  │
│  Directory  │  ←──────────  │    Index    │  ←──────────   │             │
└─────────────┘  git restore  └─────────────┘  git reset     └──────┬──────┘
     │                (已 git add 的文件被修改后，恢复)               │
     │                                                      git push │ git fetch
     │                                                               │
     │                                                        ┌──────┴──────┐
     │                                                        │   远程仓库    │
     └──────────────────────────────────────────────────────→ │   Remote    │
                         git pull = fetch + merge              │  (origin)   │
                                                              └─────────────┘
```

**三条核心流程**：

```
写代码流程：  工作区改动 → git add → 暂存区 → git commit → 本地仓库 → git push → 远程
撤销流程：    远程 → git pull → 本地仓库 → git reset → 暂存区 → git restore → 工作区
查看差异：    git diff（工作区 vs 暂存区） | git diff --staged（暂存区 vs 仓库）| git diff HEAD（工作区 vs 仓库）
```

每个区域的角色：

| 区域 | 实质 | 关键操作 |
|------|------|----------|
| 工作区 (Working Directory) | 你正在编辑的文件，操作系统里的真实文件 | `git restore <file>` 丢弃修改 |
| 暂存区 (Staging Area / Index) | 下一次 commit 的快照预览，藏在 `.git/index` | `git reset HEAD <file>` 取消暂存 |
| 本地仓库 (Local Repository) | `.git` 目录，所有历史版本都在这里 | `git reset --soft HEAD~1` 撤销 commit |
| 远程仓库 (Remote) | GitHub/GitLab 上的仓库副本 | `git revert` 安全回滚已 push 的提交 |

---

## 二、日常操作

```bash
# 克隆项目
git clone git@github.com:user/repo.git

# 创建分支
git checkout -b feature/new-algorithm

# 查看改了啥
git status
git diff                     # 工作区 vs 暂存区
git diff --staged            # 暂存区 vs 上次提交

# 提交
git add file.py              # 只加指定文件
git add .                    # 加所有改动
git commit -m "feat: 实现协同过滤推荐算法"

# 推送
git push origin feature/new-algorithm

# 拉取主分支最新
git checkout main
git pull origin main

# 合并自己的分支
git merge feature/new-algorithm

# 删除已完成的分支
git branch -d feature/new-algorithm
```

---

## 三、提交信息规范

```
feat: 新功能
fix:  修复bug
docs: 文档改动
refactor: 重构（不改功能）
test: 测试
chore: 杂活（配置、依赖更新）

例子：
feat: 添加用户留存率计算脚本
fix: 修复数据库连接池泄漏问题
```

---

## 四、分支模型详解

团队协作中，分支策略决定代码怎么合、什么时候发布。三种主流模型：

### 4.1 Git Flow vs GitHub Flow vs Trunk-Based Development

| 维度 | Git Flow | GitHub Flow | Trunk-Based |
|------|----------|-------------|-------------|
| 长期分支 | `main` + `develop` 两根主线 | 只有 `main` 一根主线 | 只有 `main`（trunk）一根主线 |
| 短期分支 | `feature/` `release/` `hotfix/` 三种 | 只有 `feature/` 一种 | 短命 `feature/`，1-2 天内合入 |
| 发布节奏 | 有专门的 `release` 分支做发布准备 | 分支合入 `main` 即上线 | 每次 commit 都可能上线 |
| 适合场景 | 有明确版本号的产品（如 App、嵌入式软件） | Web 服务、持续部署 | 成熟的 CI/CD 团队，微服务 |
| 复杂度 | 高，新手容易搞混分支 | 低，流程简单 | 极低，但要求高自动化测试 |
| 代表公司 | 传统软件公司、部分游戏公司 | GitHub、大多数互联网公司 | Google、Facebook |
| feature flag | 不需要 | 不需要 | 必须，靠 feature flag 控制未完成功能 |

**实际公司里最常见的做法**：GitHub Flow + 一点点 Git Flow 的 hotfix 概念。

### 4.2 GitHub Flow 详细流程（入职必备）

```
main ────●────●────●────●────●  （可部署状态）
           \          /
feature/A   ●──●──●─┘   （开发完 → PR → 合入）
                 \
feature/B        ●──●──●──●  （还在开发中）
```

```bash
# 完整流程，一天的操作
# 1. 从最新的 main 切分支
git checkout main
git pull origin main
git checkout -b feature/add-recommendation

# 2. 开发，频繁小步提交
git add src/recommend.py
git commit -m "feat: 实现协同过滤核心算法"
git add tests/test_recommend.py
git commit -m "test: 添加推荐算法单元测试"

# 3. 推到远程，提 PR
git push origin feature/add-recommendation
# → 去 GitHub 网页点 "New Pull Request"

# 4. 同事 review 时你可能需要改代码
# ... 本地改完 ...
git add .
git commit -m "fix: 修复 review 提出的性能问题"
git push origin feature/add-recommendation  # PR 会自动更新

# 5. CI 通过 + 同事 Approve → 在网页上点 "Squash and merge"
# 6. 切回 main，拉最新，删本地分支
git checkout main
git pull origin main
git branch -d feature/add-recommendation
```

---

## 五、冲突解决

```bash
# 你和同事改了同一个文件
git pull origin main
# CONFLICT: models.py

# 打开文件，看到冲突标记：
<<<<<<< HEAD
model = LogisticRegression(C=1.0)
=======
model = RandomForestClassifier(n_estimators=100)
>>>>>>> main

# 手动选择保留哪个（或者合并两者），删掉标记，保存
# 然后：
git add models.py
git commit -m "merge: 合并 models.py 冲突"

# 技巧：如果你确定用某一方的版本
git checkout --theirs models.py   # 用对方的
git checkout --ours models.py     # 用自己的
```

### 5.1 冲突实战演练：模拟两个人改同一行

场景：你和同事都改了 `config.py` 里的 `BATCH_SIZE`，你先 push，同事 pull 时冲突。

```bash
# === 你的操作（先 push 的人）===
git checkout -b feature/batch-size
echo 'BATCH_SIZE = 64' >> config.py
git add config.py
git commit -m "feat: 把 batch_size 从 32 改为 64"
git push origin feature/batch-size
# 合入 main ← 操作成功

# === 同事的操作（后 pull 的人）===
# 同事在切分支前没 pull 最新 main，他直接基于旧 main 改了 config.py
git checkout -b feature/learning-rate  # 基于旧 main
echo 'BATCH_SIZE = 128' >> config.py   # 他也改了同一行！
git add config.py
git commit -m "feat: 增大 batch_size 到 128"

# 同事想合入 main 前先 pull
git checkout main
git pull origin main  # main 已经包含你的 BATCH_SIZE = 64

# 尝试 merge 自己的分支
git merge feature/learning-rate
# CONFLICT (content): Merge conflict in config.py
# Automatic merge failed; fix conflicts and then commit the result.

# 同事打开 config.py 看到：
# <<<<<<< HEAD
# BATCH_SIZE = 64
# =======
# BATCH_SIZE = 128
# >>>>>>> feature/learning-rate

# 同事的决策：
# 选项 A：用你的（main 最新）→ git checkout --ours config.py
# 选项 B：用自己的     → git checkout --theirs config.py
# 选项 C：两个人讨论后手动写最终值 → 删掉标记，写 BATCH_SIZE = 128

# 假设选 C，手动改为 BATCH_SIZE = 128，然后：
git add config.py
git commit -m "merge: 解决 BATCH_SIZE 冲突，统一用 128"
git push origin feature/learning-rate
```

---

## 六、回滚操作（入职最容易慌的）

```bash
# 1. 改坏了但还没 git add（丢弃工作区改动）
git checkout -- file.py

# 2. 已经 git add 了，想取消暂存
git reset HEAD file.py

# 3. 已经 commit 了，想撤销 commit（保留改动）
git reset --soft HEAD~1     # commit 没了，改动回暂存区

# 4. commit 全不要了，回到上次提交
git reset --hard HEAD~1     # ⚠️ 改动永久丢失

# 5. 已经 push 了，想回滚远程 → revert（安全，不破坏历史）
git revert HEAD             # 创建一个新的撤销 commit
git push origin main

# ⚠️ 不要用 reset --hard 后 force push！会把同事的提交也搞没
```

### 6.1 git reset 三种模式深入对比

`git reset` 是"后悔药"，但三种模式移动的范围不同。

| 模式 | HEAD 指针 | 暂存区 | 工作区 | 使用场景 |
|------|----------|--------|--------|----------|
| `--soft` | 回退 | 保留（改动在暂存区） | 保留 | commit 错了但改动还要，想重新 commit |
| `--mixed`（默认） | 回退 | 清空（改动掉回工作区） | 保留 | "这个 commit 包含了一些不该提交的文件" |
| `--hard` | 回退 | 清空 | **清空（改动永久丢失！）** | 彻底放弃所有改动，回到干净状态 |

用 ASCII 画一下三种模式的效果（假设当前有三笔 commit: A → B → C，HEAD 在 C）：

```
初始状态：
A ─── B ─── C (HEAD, main)

git reset --soft HEAD~1  后的状态：
A ─── B (HEAD, main)      ← C 的改动全在暂存区，等你重新 commit

git reset --mixed HEAD~1 后的状态（默认）：
A ─── B (HEAD, main)      ← C 的改动全在工作区，需要重新 git add + commit

git reset --hard HEAD~1 后的状态：
A ─── B (HEAD, main)      ← C 的改动彻底没了，工作区干干净净
```

**面试话术**："reset 的三参数本质上是 Git 的三个树（HEAD、Index、Working Tree）分别回退到哪个程度。--soft 只动 HEAD，--mixed 动 HEAD 和暂存区，--hard 全动。"

### 6.2 git reflog：救回"误删"的 commit

你手滑 `git reset --hard` 把一天的工作搞没了？别慌，reflog 是你的救命稻草。

```bash
# 场景：你不小心 reset --hard 了
git reset --hard HEAD~3   # 完了！三天的代码没了！

# 不要急，看 reflog
git reflog
# 输出如下：
# a1b2c3d HEAD@{0}: reset: moving to HEAD~3
# e4f5g6h HEAD@{1}: commit: feat: 完成推荐算法性能优化   ← 这是你"弄丢"的 commit
# i7j8k9l HEAD@{2}: commit: feat: 添加用户画像特征
# m0n1o2p HEAD@{3}: commit: fix: 修复缓存过期逻辑

# 回到那个"丢失"的 commit
git reset --hard e4f5g6h   # 或者 git reset --hard HEAD@{1}
# 代码全回来了！
```

**reflog 原理**：Git 记录 `HEAD` 的所有移动历史（默认保留 90 天），即使 commit 不再被任何分支引用，只要 reflog 里还有就能找回。只有 `git gc`（垃圾回收）才会真正清除。

**面试追问应对**："reflog 只能找回本地操作过的 commit。如果 force push 覆盖了远程，且本地 reflog 也没有了（比如重新 clone 的），那就真的丢了——所以永远不要 force push 共享分支。"

---

## 七、git stash：暂存现场

写了一半代码，突然要切分支修紧急 bug？`git stash` 把当前工作暂存起来。

```bash
# === 基本用法 ===

# 1. 暂存当前所有改动（工作区 + 暂存区）
git stash
# 等价于 git stash push -m "WIP: 推荐算法写到一半"

# 2. 暂存时加上描述（强烈建议每次都加）
git stash push -m "feat: 推荐算法冷启动方案，完成 80%"

# 3. 暂存包含 untracked 文件（新建但没 git add 的文件）
git stash push -u -m "包含新建文件的暂存"

# === 查看 stash 列表 ===
git stash list
# stash@{0}: On feature/recommend: feat: 推荐算法冷启动，完成 80%
# stash@{1}: On main: WIP: 修复日志格式

# === 恢复 stash ===

# 4. 弹出最新的 stash（恢复 + 删除 stash 记录）
git stash pop

# 5. 应用但不删除 stash 记录（可以把一个 stash 应用到多个分支）
git stash apply

# 6. 应用指定的 stash（不是最新的那个）
git stash apply stash@{1}

# 7. 删除 stash
git stash drop stash@{0}     # 删除指定的
git stash clear               # 清空所有 stash

# === 进阶：只 stash 部分文件 ===
git stash push -m "只暂存 config 文件" -- config.py
```

**常见踩坑**：`git stash pop` 后如果有冲突，stash 不会被自动删除（安全机制）。解决完冲突后记得手动 `git stash drop`。

---

## 八、git cherry-pick：挑 commit

把某个分支上的**某一个 commit** 复制到当前分支。

```bash
# 场景：你在 feature/A 上修了一个 bug，feature/B 也需要这个修复，但两个分支差异太大不能 merge

# 在 feature/A 上找到那个修复 commit 的 hash
git log --oneline
# a1b2c3d fix: 修复数据库连接池泄漏
# d4e5f6g feat: 完成推荐算法           ← 只需要上面那个 fix

# 切换到需要这个修复的分支
git checkout feature/B

# 挑选那个 fix commit
git cherry-pick a1b2c3d
# 如果顺利，这个修复就复制到 feature/B 了

# === 冲突了怎么办 ===
# 执行 cherry-pick 后可能冲突（两个分支代码差异大）
# Git 会暂停 cherry-pick，让你解决冲突

# 1. 解决冲突（和 merge 冲突一样的手动方式）
# 编辑冲突文件，删掉 <<<<<< ======= >>>>>>> 标记

# 2. 标记已解决
git add .
# 3. 继续 cherry-pick
git cherry-pick --continue

# 4. 或者放弃这次 cherry-pick
git cherry-pick --abort
```

**什么时候用 cherry-pick**：
- 把一个 hotfix 同时应用到 `main` 和 `release` 分支
- 你只想合分支里的一部分 commit（虽然更推荐拆分支）
- 从废弃的分支里"抢救"有用的 commit

**面试话术**："cherry-pick 本质是计算这个 commit 的 diff，然后作为 patch 应用到当前分支。如果两个分支的上下文差异太大，cherry-pick 不如 merge 可靠。"

---

## 九、git rebase vs merge：深度对比

### 9.1 原理图解

**merge 做了什么**（保留真实历史）：

```
合并前：
      A──B──C  feature
     /
D──E──F──G  main

git merge feature 后（在 main 上）：
      A──B──C
     /       \
D──E──F──G────M  main  ← M 是 merge commit，记录"feature 从哪里分叉，又在哪里合并"
```

**rebase 做了什么**（改写历史，变直线）：

```
变基前：
      A──B──C  feature
     /
D──E──F──G  main

git rebase main 后（在 feature 上）：
              A'──B'──C'  feature  ← 注意：这是新的 commit，hash 变了！
             /
D──E──F──G  main

# 然后再 merge（已经是快进合并了）：
D──E──F──G──A'──B'──C'  main, feature  ← 一条直线，没有分叉
```

### 9.2 对比表格

| 维度 | merge | rebase |
|------|-------|--------|
| 历史形态 | 保留分叉，有 merge commit | 一条直线，干净整洁 |
| commit hash | 原有 commit 不变 | 原有 commit 被重写（hash 变了） |
| 冲突解决 | 解决一次（在 merge commit 里） | 可能每个 commit 都要解决一次 |
| git blame | 准确显示谁写的 | 可能显示 rebase 操作者（history 被重写了） |
| 适合场景 | 合并 feature 到 main（保留合入痕迹） | 把 main 最新代码同步到自己的 feature 分支 |
| 风险 | 低 | 中——如果 feature 已经 push 给别人，会搞乱别人的仓库 |

### 9.3 黄金法则：不要 rebase 已经 push 的分支

```
为什么不能 rebase 已经 push 的分支？

假设你和同事都在 feature/A 上开发：
1. 你 push 了 commit X, Y, Z
2. 同事 pull 了你的 X, Y, Z，基于它们继续写代码
3. 你突然 rebase，X, Y, Z 变成了 X', Y', Z'（hash 全变了）
4. 你 force push 覆盖远程
5. 同事 pull 时发现历史对不上 → 大量冲突，他的本地 commit 无处安放

结论：
- rebase 只能在自己本地、还没 push 的分支上做
- 一旦 push 给别人了，就老老实实 merge
```

### 9.4 场景选择决策树

```
你要把 main 的最新代码同步到你的 feature 分支？
  ├── feature 分支只有你在用，没 push 过？ → git rebase main（保持历史干净）
  └── feature 分支已经 push 了，或者别人也在用？ → git merge main（保留真实历史）

你要把 feature 分支合入 main？
  ├── 团队有"Squash and merge"习惯？ → 在 GitHub 上点 Squash and merge（所有 commit 压成一个）
  ├── 团队想看完整开发过程？ → git merge --no-ff feature（保留 feature 上的每个 commit）
  └── feature 本身已经 rebase 过？ → git merge feature（默认快进，历史是线性的）
```

---

## 十、.gitignore 配置技巧

### 10.1 常用模板

**Python 项目**：

```gitignore
# 虚拟环境
venv/
env/
.venv/
__pycache__/
*.py[cod]
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo

# 环境变量
.env
.env.local

# Jupyter
.ipynb_checkpoints/

# 数据文件（太大的别提交）
data/raw/
*.pkl
*.h5
*.parquet

# 日志
*.log
logs/
```

**Java / Spring Boot 项目**：

```gitignore
# 编译产物
target/
*.class
*.jar
*.war

# IDE
.idea/
*.iml
.settings/
.classpath
.project

# 日志
*.log
logs/

# 系统和临时文件
*.swp
*.bak
.DS_Store
Thumbs.db

# 敏感配置（用模板文件代替）
application-local.yml
application-prod.yml
```

**Node.js / 前端项目**：

```gitignore
# 依赖
node_modules/

# 构建产物
dist/
build/
.next/
out/

# 环境
.env
.env.local
.env.production

# IDE
.vscode/
.idea/

# 日志和缓存
*.log
.cache/
.eslintcache
```

### 10.2 .gitignore 生效规则

```bash
# 注意：如果一个文件已经被 git 跟踪了，再加 .gitignore 不会生效！
# 需要先从 Git 中移除（但保留本地文件）
git rm --cached secrets.yml      # 从 Git 移走，文件保留在本地
git commit -m "chore: 从版本控制移除 secrets.yml"

# 提交后 .gitignore 才会对该文件生效

# 查看某个文件为什么被 ignore
git check-ignore -v logs/debug.log
# .gitignore:5:logs/*    logs/debug.log
```

---

## 十一、git bisect：二分法找 bug

当你知道某个版本有 bug，但之前某个版本没有，中间有几百个 commit——`git bisect` 用二分法帮你精确定位是哪个 commit 引入的。

```bash
# 场景：v2.0 运行正常，v2.1 的推荐准确率暴跌。
# 中间有 200 个 commit，不知道是哪个改坏的。

# 1. 启动 bisect
git bisect start

# 2. 标记"坏的"commit（当前版本）
git bisect bad HEAD

# 3. 标记"好的"commit（正常工作的版本）
git bisect good v2.0

# Git 自动跳到中间位置（第 ~100 个 commit）
# Bisecting: 100 revisions left to test after this (roughly 7 steps)

# 4. 你在这个版本上跑测试
python test_recommend_accuracy.py
# 结果：准确率只有 60%，还是坏的

git bisect bad     # 告诉 Git 这个版本还是坏的
# Git 再跳到前半段的中间位置

# 5. 继续跑测试
python test_recommend_accuracy.py
# 结果：准确率 92%，这个是好的！

git bisect good    # 告诉 Git 这个版本是好的

# ... 重复 6-7 次后 ...
# a1b2c3d is the first bad commit
# commit a1b2c3d
#     feat: 把相似度从余弦改为欧氏距离  ← 找到凶手了！

# 6. 结束 bisect，回到正常状态
git bisect reset
```

**还有更自动化的用法**：

```bash
# 如果 bug 可以用脚本自动检测，直接让 Git 帮你跑
git bisect start HEAD v2.0
git bisect run python test_recommend_accuracy.py
# Git 自动二分 + 自动运行脚本，全程不需要你动手
```

---

## 十二、入职后的典型工作流

```bash
# 周一早上
git checkout main
git pull origin main

# 开始新任务
git checkout -b feature/weekly-report

# ... 写代码，一天中多次 ...
git add .
git commit -m "feat: 实现周报数据聚合"

# 下班前推上去备份
git push origin feature/weekly-report

# 完成 → 提 Pull Request（在 GitHub 网页上操作）

# 同事 review 完，合并到 main
# 第二天早上重复
```

---

## 十三、面试专题

### 13.1 怎么回滚一个已经 push 的 commit？

这是最常见的 Git 面试题。核心考点：你知道 `revert` 和 `reset + force push` 的区别。

**方案对比**：

| 方案 | 命令 | 原理 | 历史 | 风险 |
|------|------|------|------|------|
| revert（推荐） | `git revert <commit>` + `git push` | 创建一个新的"反向 commit"，抵消目标 commit 的改动 | 保留完整历史 | 低，不会影响同事 |
| reset + force push | `git reset --hard <commit>` + `git push -f` | 直接把 HEAD 指针挪回去，后面的 commit 全部丢弃 | 历史被改写 | **高**，同事本地会乱掉，需要全员协调 |

```bash
# 正确做法：revert
git revert a1b2c3d           # 对那个错误的 commit 创建一个反向操作
git push origin main          # 正常 push，和普通提交一样

# 结果：
# 历史是 A → B → C → D(revert C)
# C 的改动被 D 抵消了，但 C 还在历史中，可追溯

# 错误做法：force push（除非你是分支的唯一使用者且完全确定）
git reset --hard a1b2c3d~1   # 回退
git push -f origin main       # 强制覆盖远程
# 后果：同事 pull 时会报错，他们的本地 commit 无从合并
```

**面试话术**："已经 push 到共享分支的，必须用 revert，因为它不破坏历史，同事可以正常 pull。reset + force push 只能在个人分支或紧急情况且与全员沟通清楚后才用。revert 之后如果又想恢复，再 revert 一次那个 revert commit 就行。"

### 13.2 rebase 和 merge 的区别？（附场景决策树）

面试标准回答框架：

1. **本质区别**：merge 保留真实的分支历史（有分叉，有 merge commit）；rebase 改写历史（把你的 commit 接到目标分支最新处，变成一条直线）
2. **使用场景**：merge 用于"合入主线"（保留合入痕迹，方便追溯）；rebase 用于"同步主线最新代码到自己的分支"（保持自己的 feature 分支历史干净）
3. **黄金法则**：不要 rebase 已经 push 给别人的分支
4. **Squash and merge** 是第三选项：把 feature 分支上所有 commit 压成一个，历史最干净但丢失了开发过程细节

**追问应对**："你个人更倾向于哪个？" → "看团队规范。我习惯在 feature 分支上 rebase main 来同步最新代码，因为这样我的 PR 只有一个干净的 diff。合入 main 时用 GitHub 的 Squash and merge，保持 main 历史简洁。但如果团队要求保留完整开发过程，就老实 merge。"

### 13.3 Git 内部原理简介

面试官问你"Git 怎么存储数据的"，不要慌，核心概念很简单：

**Git 是一个内容寻址的文件系统**——所有数据以"对象"形式存在 `.git/objects/` 里，用内容的 SHA-1 哈希值作为文件名。

四种对象类型：

| 对象 | 含义 | 例子 |
|------|------|------|
| **blob** | 文件内容（不含文件名） | 一个 `.py` 文件的全部文字内容 |
| **tree** | 目录结构（记录文件名 → blob 的映射） | "这个目录下有 a.py → blob abc, b.py → blob def" |
| **commit** | 一次提交：指向一个 tree + 父 commit + 提交信息 | "父 commit 是 xyz，这时的目录快照是 tree 123" |
| **tag** | 指向某个 commit 的标签（用于版本号） | `v2.0` 指向 commit deadbeef |

```
commit 的结构：
┌──────────────────────────────┐
│ tree: a1b2...                │ ← 指向根目录的 tree 对象
│ parent: c3d4...              │ ← 上一个 commit
│ author: zhangsan             │
│ message: "feat: 实现推荐算法" │
└──────────────────────────────┘

tree 的结构：
┌──────────────────────────────┐
│ src/     → tree e5f6...      │ ← 子目录
│ README   → blob g7h8...      │ ← 文件
│ setup.py → blob i9j0...      │ ← 文件
└──────────────────────────────┘

blob：
┌──────────────────────────────┐
│ import numpy as np           │
│ def recommend(user_id): ...  │
│ ...                          │
└──────────────────────────────┘
```

**HEAD 和 refs**：

```bash
# HEAD 是一个指针，指向当前你在哪个分支
cat .git/HEAD
# ref: refs/heads/feature/recommend

# refs/heads/ 下的每个文件就是一个分支，内容是该分支最新的 commit hash
cat .git/refs/heads/main
# a1b2c3d4e5f6...  ← 一个 SHA-1 哈希值

# tag 同理
cat .git/refs/tags/v2.0
# deadbeef1234...
```

**面试话术**："Git 的底层是一个非常简洁的键值存储数据库。每个文件内容作为 blob 存一次，如果内容没变（即使文件名改了），blob 也不会重复存储。commit 之间通过 parent 指针形成 DAG（有向无环图），这就是 git log 能追溯历史的原理。"

---

## 十四、面试高频考点小结

| 考点 | 频率 | 核心回答要点 |
|------|------|-------------|
| merge vs rebase 区别 | 极高 | merge 保留分叉历史，rebase 变直线；已 push 不要 rebase |
| 怎么回滚已 push 的 commit | 极高 | revert 创建反向 commit，不要 reset --hard + force push |
| reset 三种模式 | 高 | --soft（保留暂存区）、--mixed（默认，保留工作区）、--hard（全丢） |
| 冲突怎么解决 | 高 | 手动编辑冲突标记 → git add → git commit；--ours/--theirs 快速选边 |
| git stash 怎么用 | 中 | 暂存工作区现场，pop 恢复，解决"写到一半要切分支"的痛点 |
| cherry-pick 是什么 | 中 | 把某个 commit 复制到另一分支；冲突时 --continue 或 --abort |
| git reflog 有什么用 | 中 | 找回误删的 commit，记录 HEAD 移动历史（默认 90 天） |
| Git Flow vs GitHub Flow | 中 | Git Flow 复杂双主线适合版本发布，GitHub Flow 简单单主线适合持续部署 |
| git bisect | 低 | 二分法定位引入 bug 的 commit，可配合脚本自动化 |
| Git 内部存储原理 | 低 | 内容寻址、四种对象（blob/tree/commit/tag）、SHA-1 哈希 |

---

## 相关笔记

- [[工程基础/Linux基础命令]] — Shell 常用命令、管道与重定向、权限管理
- [[工程基础/Docker与容器化]] — Dockerfile 编写、docker-compose 多容器编排
- [[工程基础/CI_CD流水线]] — GitHub Actions、自动化测试与部署流程
- [[工作学习/编程语言/Python工程化]] — Python 项目结构、虚拟环境、包管理
