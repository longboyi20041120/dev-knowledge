---
tags:
  - "#用途/工作学习"
  - "#类型/技术"
  - "#技术/git"
  - "#状态/草稿"
created: 2026-06-26
updated: 2026-06-26
status: draft
---

# Git 基础与协作

简历上写"会用 Git"是基本要求。面试不会专门考 Git，但入职第一天就要用。

## 一、三个区域

```
工作区(Working) → 暂存区(Staging) → 本地仓库(Local) → 远程仓库(Remote)
    git add .        git commit         git push
```

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

## 四、冲突解决

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

## 五、回滚操作（入职最容易慌的）

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

## 六、入职后的典型工作流

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

## 七、面试可能被问

**Q: `git merge` 和 `git rebase` 的区别？**

A: merge 保留完整分支历史（产生一个 merge commit），rebase 把你的提交"搬到"主分支最新位置（历史是一条线，更干净）。团队协作时已 push 的分支不要 rebase。

**Q: 怎么撤销一次错误的 merge？**

A: 用 `git revert -m 1 <merge_commit>` 撤销 merge 引入的所有改动。不要 reset 后 force push。

## 相关笔记

- [[工程基础/Linux基础命令]]（待写）
