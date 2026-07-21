---
tags:
  - "#用途/工作学习"
  - "#类型/技术"
  - "#技术/统计学"
  - "#技术/数据分析"
  - "#状态/已验证"
created: 2026-06-26
updated: 2026-07-15
status: reviewed
---

# 假设检验与 AB 测试

> p 值理解、t 检验、AB 测试完整流程 + 样本量计算——数据分析师面试必问。 | **面试重要度：极高** | 预计阅读：25 分钟

## 视频资源

- YouTube: [StatQuest: Hypothesis Testing](https://www.youtube.com/watch?v=0oc49DyA3hU) — 假设检验最直观的解释
- YouTube: [Khan Academy: Hypothesis Testing](https://www.khanacademy.org/math/statistics-probability/significance-tests-one-sample) — 可汗学院统计检验
- B站: [StatQuest 假设检验中文版](https://www.bilibili.com/video/BV1NE411j7Nc/) — 中文搬运

---

## 一、假设检验的核心逻辑

**反证法**：先假设"没区别"（零假设 H0），然后看数据是不是"太不可能"在这个假设下出现。如果是 → 拒绝 H0，认为有显著差异。

```
H0（零假设）：新算法和旧算法没区别
H1（备择假设）：新算法有区别

p 值 = 在 H0 为真的情况下，观察到这个结果（或更极端）的概率

p < 0.05 → "在 H0 下这个结果太不可能了" → 拒绝 H0 → 有显著差异
p ≥ 0.05 → "在 H0 下这个结果完全可能" → 不能拒绝 H0 → 没有显著证据
```

**面试话术**："p 值不是'H0 为真的概率'，而是'在 H0 为真的前提下，看到这个数据的概率'。p < 0.05 只是说数据与 H0 不一致，不代表 H1 一定对。"

---

## 二、第一类错误 vs 第二类错误

这是每次面试几乎必考的题。搞不清楚这两种错误就挂了。

### 2.1 直观理解

```
真相（你不知道的）  vs   你的决策（基于 p 值）

               H0 为真             H0 为假 (H1 为真)
           ┌──────────────────┬──────────────────┐
  拒绝 H0  │ 第一类错误 (α)    │ 正确 (1-β)        │  ← 你说"有差异"
           │ 假阳性/误报       │ 统计功效          │
           │ "没病当有病"      │ "真阳性"          │
           ├──────────────────┼──────────────────┤
不能拒绝H0 │ 正确 (1-α)       │ 第二类错误 (β)     │  ← 你说"没证据"
           │ 真阴性           │ 假阴性/漏报        │
           │ "正确诊断没病"    │ "有病没查出来"     │
           └──────────────────┴──────────────────┘
```

### 2.2 图解（ASCII 图）

```
H0 为真时的样本分布（新=旧，没差别）

         .d$$$$$c.
       .$$$$$$$$$$.
      $$$$$$$$$$$$$$          ← 拒绝域 (α/2 = 2.5%)
     d$$$$$$$$$$$$$$$c             p < 0.05，你说"有差别"
    .$$$$$$$$$$$$$$$$$$.          但真相是没差别 ← 第一类错误！
    $$$$$$$$$$$$$$$$$$$$$
    $$$$$$$$$$$$$$$$$$$$$
    $$$$$$$$$$$$$$$$$$$$$
    $$$$$$$$$$$$$$$$$$$$$
     $$$$$$$$$$$$$$$$$$$
      $$$$$$$$$$$$$$$$
       "$$$$$$$$$$$"
          """""""
     ├──────────────┼──────────────┤
   拒绝域          接受域          拒绝域
  (2.5%)          (95%)          (2.5%)

如果 H1 为真（新≠旧），真实分布的均值偏左或偏右了：

                              .d$$$$$c.
                            .$$$$$$$$$$.
         .d$$$$$c.         $$$$$$$$$$$$$$
       .$$$$$$$$$$.       d$$$$$$$$$$$$$$$
      $$$$$$$$$$$$$$     .$$$$$$$$$$$$$$$$$$.
     d$$$$$$$$$$$$$$$c   $$$$$$$$$$$$$$$$$$$$$
    .$$$$$$$$$$$$$$$$$$.  $$$$$$$$$$$$$$$$$$$$$
    $$$$$$$$$$$$$$$$$$$$$ $$$$$$$$$$$$$$$$$$$$$
    $$$$$$$$$$$$$$$$$$$$$  $$$$$$$$$$$$$$$$$$$$
    $$$$$$$$$$$$$$$$$$$$$   $$$$$$$$$$$$$$$$$$
    $$$$$$$$$$$$$$$$$$$$$    "$$$$$$$$$$$"
     $$$$$$$$$$$$$$$$$$$        """""""
      $$$$$$$$$$$$$$$$
       "$$$$$$$$$$$"
          """""""
     ├─────────────────────┼──────────────────────┤
     ← H0 分布（旧）        → H1 分布（新，偏右）

                    β = H0 分布中不显著的区域
                        被包在 H1 分布中 = 漏报
                        你说"没差别"，但其实有差别 ← 第二类错误！
```

### 2.3 α 和 β 的关系

| 指标 | 名称 | 含义 | 典型值 | 怎么调 |
|------|------|------|--------|--------|
| α | 显著性水平 | "我愿意接受多大误报风险" | 0.05 | 人为设定，越小越保守 |
| β | 第二类错误率 | "漏报的概率" | 通常 0.2 | 不能直接设，受样本量影响 |
| 1-β | 统计功效 (Power) | "真有差异时我能检出的概率" | 0.8 | 增大样本量可以提升 |

**面试追问**："α 和 β 能同时减小吗？"

答："在样本量固定的情况下不能——减小 α 必然增大 β（降低了误报率，但更容易漏报）。唯一同时减小两者的是**增大样本量**，但这受成本和时间制约。"

```python
import numpy as np
from scipy import stats
1
# 演示：α 和 β 的权衡
np.random.seed(42)
n = 100

# 模拟两种场景
# H0 为真（两组均值都是 100）
group1_h0 = np.random.normal(100, 15, n)
group2_h0 = np.random.normal(100, 15, n)

# H1 为真（旧=100, 新=103，有 3% 的提升）
group1_h1 = np.random.normal(100, 15, n)
group2_h1 = np.random.normal(103, 15, n)

# 如果 α = 0.05，用 t 检验
t0, p0 = stats.ttest_ind(group1_h0, group2_h0)
t1, p1 = stats.ttest_ind(group1_h1, group2_h1)

print(f"H0 为真时 p = {p0:.4f} → {'第一类错误!' if p0 < 0.05 else '正确（不拒绝 H0）'}")
print(f"H1 为真时 p = {p1:.4f} → {'正确（拒绝 H0）' if p1 < 0.05 else '第二类错误（漏报）!'}")
```

---

## 三、常见检验及选择

| 场景 | 用什么检验 | 例子 |
|------|---------|------|
| 两组均值是否不同（正态） | t 检验 | AB 测试：新版 vs 旧版转化率 |
| 两组均值是否不同（非正态） | Mann-Whitney U | 收入分布对比（通常右偏） |
| 多组的均值是否不同 | 方差分析（ANOVA） | 三种推荐算法的效果对比 |
| 两个分类变量是否独立 | 卡方检验 | 用户性别和购买行为是否相关 |
| 分布是否正态 | Shapiro-Wilk | 先检验数据是否符合正态分布 |
| 配对数据的均值差异 | 配对 t 检验 | 同一批用户使用前后对比 |

```python
from scipy import stats
import numpy as np

# t 检验：两组均值对比（AB测试最常用）
np.random.seed(42)
control = np.random.normal(100, 15, 1000)    # 对照组：均值100
treatment = np.random.normal(103, 15, 1000)  # 实验组：均值103（提升了3%）

t_stat, p_value = stats.ttest_ind(treatment, control)
print(f"t = {t_stat:.3f}, p = {p_value:.4f}")
# t = 4.212, p = 0.0000 → p < 0.05，显著！新算法确实更好

# 卡方检验：分类变量独立性
# 观察值：买了/没买 按性别分组
observed = np.array([[80, 120], [90, 110]])  # [男(买,没买), 女(买,没买)]
chi2, p_val, dof, expected = stats.chi2_contingency(observed)
print(f"卡方 = {chi2:.3f}, p = {p_val:.4f}")
# 如果 p > 0.05，性别和购买行为没有显著关系
```

---

## 四、样本量计算：公式推导 + Python 实现

### 4.1 为什么需要算样本量？

样本太少 → 功效不足 → 有差异也检不出（第二类错误）
样本太多 → 浪费资源 → 一点微小差异就显著（可能没有业务意义）

所以要提前算好：**在控制 α 和 β 的前提下，检测到预期效果需要多少人。**

### 4.2 公式推导（两独立样本比例检验）

设：
- 对照组转化率 = p1，实验组 = p2
- 预期效果量（effect size）= p2 - p1
- 显著性水平 = α，统计功效 = 1 - β

t 检验的检验统计量（在 H0 下近似正态）：

```
z = (p̂₂ - p̂₁) / SE

在 H0 下：SE₀ = sqrt(p(1-p) × (1/n₁ + 1/n₂))
在 H1 下：SE₁ = sqrt(p₁(1-p₁)/n₁ + p₂(1-p₂)/n₂)
```

设 n₁ = n₂ = n，令：

```
z_α/₂ × SE₀ + z_β × SE₁ = |p₂ - p₁|
```

解出：

```
n = (z_α/₂ × √[p₁(1-p₁) + p₂(1-p₂)] + z_β × √[2p₁(1-p₁)])² / (p₂ - p₁)²
```

简化版本（假设 H0 下 pooled p ≈ p₁）：

```
n = (z_α/₂ + z_β)² × [p₁(1-p₁) + p₂(1-p₂)] / (p₂ - p₁)²
```

**关键参数来源**：

| 参数 | 符号 | 谁决定的 | 怎么定 |
|------|------|---------|--------|
| 显著性水平 | α | 分析师/业务方 | 默认 0.05；风险高的场景设 0.01 |
| 统计功效 | 1-β | 分析师 | 默认 0.8；关键决策设 0.9 或 0.95 |
| 基线转化率 | p₁ | 历史数据 | 查报表，过去的 CTR / 转化率 |
| 最小可检测效应 | p₂-p₁ | 业务方 | "提升多少才算有意义"——业务拍板，不是统计师拍板 |

### 4.3 Python 完整实现

```python
from scipy.stats import norm
import numpy as np

def calc_sample_size(
    baseline: float,
    expected_lift: float,
    alpha: float = 0.05,
    power: float = 0.80,
    two_sided: bool = True
) -> dict:
    """
    计算 AB 测试每组所需样本量（两独立样本比例检验）

    参数：
        baseline: 基线转化率（如 0.10 表示 10%）
        expected_lift: 预期相对提升（如 0.10 表示提升 10%）
        alpha: 显著性水平
        power: 统计功效（1 - β）
        two_sided: 是否双尾检验

    返回：
        包含各组样本量、总样本量、关键中间值的字典
    """
    p1 = baseline
    p2 = baseline * (1 + expected_lift)

    # 1. 查 Z 分数
    if two_sided:
        z_alpha = norm.ppf(1 - alpha / 2)  # 双尾：如 α=0.05 → z=1.96
    else:
        z_alpha = norm.ppf(1 - alpha)      # 单尾

    z_beta = norm.ppf(power)  # power=0.8 → z=0.84

    # 2. 计算效应量（effect size）
    effect = abs(p2 - p1)

    # 3. 样本量公式
    numerator = (z_alpha + z_beta)**2 * (p1*(1-p1) + p2*(1-p2))
    n_per_group = numerator / (effect**2)

    return {
        'n_per_group': int(np.ceil(n_per_group)),
        'n_total': int(np.ceil(2 * n_per_group)),
        'z_alpha': round(z_alpha, 3),
        'z_beta': round(z_beta, 3),
        'effect_size': round(effect, 4),
        'baseline': baseline,
        'expected_p2': round(p2, 4),
    }

# === 使用示例 ===
print("=" * 60)
print("AB 测试样本量计算器")
print("=" * 60)

scenarios = [
    {"name": "大流量入口（CTR 10% → 11%）", "baseline": 0.10, "lift": 0.10},
    {"name": "小转化率（付费率 2% → 2.4%）", "baseline": 0.02, "lift": 0.20},
    {"name": "高风险决策（α=0.01, power=0.95）", "baseline": 0.10, "lift": 0.10},
]

for s in scenarios:
    result = calc_sample_size(
        baseline=s['baseline'],
        expected_lift=s['lift'],
        alpha=0.01 if 'α=0.01' in s['name'] else 0.05,
        power=0.95 if 'power=0.95' in s['name'] else 0.80,
    )
    print(f"\n场景: {s['name']}")
    print(f"  基线 p₁={result['baseline']}, 目标 p₂={result['expected_p2']}")
    print(f"  效应量={result['effect_size']}")
    print(f"  z_α={result['z_alpha']}, z_β={result['z_beta']}")
    print(f"  每组需要: {result['n_per_group']:,} 人")
    print(f"  总共需要: {result['n_total']:,} 人")
    # 估算需要的天数
    daily_users = 50000  # 假设每天有 50000 用户
    days_needed = result['n_total'] / daily_users
    print(f"  若日活 5 万，需要运行约 {days_needed:.1f} 天")

# 输出示例：
# 大流量入口：每组约 14,747 人，共 29,494 人
# 小转化率：每组约 24,023 人 — 基线越低、效应越小，所需样本量越大
# 高风险决策：更严格的 α 和更高的 power → 每组需要约 26,552 人
```

### 4.4 面试话术

> "样本量由四个因素决定：基线转化率（历史数据给）、预期提升幅度（业务方定）、显著性水平（默认 0.05）和统计功效（默认 0.8）。**关键是被面试官反问时，要能解释'最小可检测效应'必须由业务方拍板——检测 0.1% 的差异需要巨量样本，但 0.1% 的提升可能根本没业务价值。**"

---

## 五、多重检验校正

**核心问题：每做一次检验，就有 5% 的概率犯第一类错误。如果同时做 20 个检验，至少犯一次第一类错误的概率是多少？**

```
P(至少一次误报) = 1 - P(20 次都不误报)
                 = 1 - (1 - 0.05)²⁰
                 = 1 - 0.358
                 ≈ 0.642  ← 64.2% 的概率至少有一次假阳性！
```

不用算，直觉就能感受到：**检验做得越多，越可能"碰巧"显著**。这就是多重检验问题。

### 5.1 两种校正方法对比

| 方法 | 公式 | 原理 | 适用场景 | 严格程度 |
|------|------|------|---------|---------|
| Bonferroni | α_new = α / m | 把 α 平均分给每个检验 | 独立检验、控制 FWER | 非常严格，容易漏报 |
| Benjamini-Hochberg (FDR) | 对 p 值排序后动态调整 | 控制假阳性比例 | 探索性分析、基因组学 | 相对宽松，平衡性好 |

- **FWER** (Family-Wise Error Rate)：至少一次误报的概率。Bonferroni 控制这个。
- **FDR** (False Discovery Rate)：拒绝的假设中，假阳性的期望比例。BH 控制这个。

### 5.2 Python 完整对比

```python
import numpy as np
from scipy import stats
from statsmodels.stats.multitest import multipletests

# 模拟场景：测试 20 个指标，其中 3 个真的有差异，17 个没差异
np.random.seed(42)
m = 20  # 总共 20 个检验
n_true_signal = 3  # 其中 3 个真的有效果
n_per_group = 500

p_values = []
true_labels = []  # 记录每个检验的真实状态（只有上帝知道）

for i in range(m):
    if i < n_true_signal:
        # 真的有差异：均值差 0.5
        control = np.random.normal(0, 1, n_per_group)
        treatment = np.random.normal(0.5, 1, n_per_group)
        true_labels.append('H1（真有差异）')
    else:
        # 没有差异：两个分布完全一样
        control = np.random.normal(0, 1, n_per_group)
        treatment = np.random.normal(0, 1, n_per_group)
        true_labels.append('H0（没差异）')

    _, p = stats.ttest_ind(treatment, control)
    p_values.append(p)

p_values = np.array(p_values)

print("=" * 70)
print(f"共 {m} 个检验，其中 {n_true_signal} 个真的有差异")
print("=" * 70)

# 无校正：直接用 α=0.05
reject_raw = p_values < 0.05
print(f"\n[无校正] 发现 {reject_raw.sum()} 个显著结果")
print(f"  真阳性: {reject_raw[:n_true_signal].sum()} / {n_true_signal}")
print(f"  假阳性: {reject_raw[n_true_signal:].sum()} / {m - n_true_signal}")
# 通常假阳性多余真阳性！因为 17×0.05 ≈ 0.85，几乎总有 1 个假阳性

# Bonferroni 校正
reject_bonf, p_bonf, _, _ = multipletests(p_values, alpha=0.05, method='bonferroni')
print(f"\n[Bonferroni] 发现 {reject_bonf.sum()} 个显著结果")
print(f"  真阳性: {reject_bonf[:n_true_signal].sum()} / {n_true_signal}")
print(f"  假阳性: {reject_bonf[n_true_signal:].sum()} / {m - n_true_signal}")
print(f"  校正后 α 阈值: {0.05/m:.4f}")

# Benjamini-Hochberg FDR 校正
reject_bh, p_bh, _, _ = multipletests(p_values, alpha=0.05, method='fdr_bh')
print(f"\n[Benjamini-Hochberg FDR] 发现 {reject_bh.sum()} 个显著结果")
print(f"  真阳性: {reject_bh[:n_true_signal].sum()} / {n_true_signal}")
print(f"  假阳性: {reject_bh[n_true_signal:].sum()} / {m - n_true_signal}")

# 直观展示：排序后的 p 值与各种阈值
print("\n" + "=" * 70)
sorted_indices = np.argsort(p_values)
print(f"{'排名':<6} {'真实状态':<15} {'p值':<10} {'Bonferroni阈值':<16} {'BH阈值':<12} {'BH显著?':<10}")
print("-" * 70)

for rank, idx in enumerate(sorted_indices):
    bh_threshold = 0.05 * (rank + 1) / m  # BH 逐步阈值
    bf_threshold = 0.05 / m
    bh_sig = "Yes" if p_values[idx] <= bh_threshold else ""
    print(f"{rank+1:<6} {true_labels[idx]:<15} {p_values[idx]:<10.4f} "
          f"{bf_threshold:<16.4f} {bh_threshold:<12.4f} {bh_sig:<10}")
```

### 5.3 AB 测试中的应用

在 AB 测试中，多重检验问题最常出现在：

1. **同时看多个指标**：CTR、转化率、停留时长、跳出率...如果你看 10 个指标用 p<0.05，差不多总会有一个"显著"
2. **中途多次偷看**：每天看一次 p 值，等于做了 N 次独立检验
3. **分维度下钻**：男用户不显著看女用户，iOS 不显著看 Android...

**解决之道**：
- 提前锁定主指标（OEC），其余指标仅供参考，不做显著性判断
- 如果确实要看多个指标，用 Bonferroni 校正
- 采用序贯检验（sequential testing）框架，允许安全地多次查看

---

## 六、AB 测试完整流程（细化版）

面试标准回答不应该只背步骤，应该每步讲出"为什么"和"容易错在哪"。

### 步骤 1：明确假设与指标

**这一步没做好，后面全白做。**

- **主指标（OEC）**：唯一用来判断成功的指标。为什么只能有一个？因为多个指标多重检验问题严重。
- **辅助指标**：用于监控是否有副作用（如 CTR 升了但转化率降了 → 可能用户只是被标题党骗了）
- **护栏指标**：绝对不能恶化的指标（如崩溃率、退款率）——如果恶化了立刻停止实验

```
面试话术："我会先和产品方对齐一个 OEC（主评估指标），比如购买转化率。
同时设置护栏指标——如果实验组崩溃率显著上升，哪怕转化率提升了也不能上线。"
```

### 步骤 2：样本量计算

用历史数据算好需要多少人、跑多久。**提前定好结束时间和样本量，写到实验文档里，不到时间不偷看。**

### 步骤 3：随机分流

- 用 `hash(user_id + experiment_key) % 100` 做分流（保证同一用户始终在同一组）
- 分流完后做 **SRM 检验**（Sample Ratio Mismatch）：看各组人数是否接近预期比例
- 检查各组历史行为是否相似（AA 测试）

### 步骤 4：AA 验证（极其重要但常被忽略！）

在正式开始实验前，用历史数据做一次"假实验"：随机把用户分两组但不给任何不同的体验，跑统计检验——如果 p<0.05，说明分流机制有问题。

```python
# AA 验证：模拟验证分流是否均匀
np.random.seed(42)

# 假如我们有 10000 个用户的历史转化数据
n_users = 10000
historical_conversion = np.random.normal(0.10, 0.02, n_users)

# 随机分流（用 hash 模拟）
user_hash = np.array([hash(f"user_{i}") for i in range(n_users)])
group = np.where(user_hash % 2 == 0, 'A', 'B')
# 如果 hash 是均匀的，A 组和 B 组应该各 5000 人

group_a = historical_conversion[group == 'A']
group_b = historical_conversion[group == 'B']

t_aa, p_aa = stats.ttest_ind(group_a, group_b)
print(f"AA 测试: t={t_aa:.3f}, p={p_aa:.4f}")
print(f"A组={len(group_a)}人, B组={len(group_b)}人")
if p_aa < 0.05:
    print("WARNING: AA 测试显著！分流机制可能有问题，不能开始正式实验！")
else:
    print("AA 测试通过，分流机制正常")
```

### 步骤 5：运行实验

- 至少跑一个完整业务周期（通常 1-2 周，覆盖工作日+周末）
- **绝对不能中途偷看** p 值然后提前停止（这是最常见的实验作弊）
- 监控护栏指标，如果恶化到阈值以上，立即停止

### 步骤 6：分析结果

```
p < 0.05 且效应量(实际提升) ≥ 最小可检测效应 → 上线
p < 0.05 但效应量太小 → 统计显著但业务不显著，谨慎评估
p ≥ 0.05 → 不显著，分析是没效果还是样本不够（见第八节）
```

### 步骤 7：决策与记录

- 不管成功失败，都记录下来。失败的实验同样有价值——避免了拍脑袋上线一个无效的功能
- 实验记录应包含：假设、样本量、分流方式、运行时长、主要结论、为什么成功/失败

---

## 七、辛普森悖论：AB 测试最隐蔽的陷阱

**辛普森悖论**：分组看和整体看得到的结论完全相反。这在 AB 测试中是个致命的坑——你以为新版本赢了，实际是用户构成变了。

### 7.1 具体数值例子

假设你在测试新版支付页面。实验结束后看数据：

**整体数据（不分维度）**：
| 版本 | 用户数 | 转化人数 | 转化率 |
|------|--------|---------|--------|
| 旧版 | 10000 | 1500 | **15.0%** |
| 新版 | 10000 | 1600 | **16.0%** |

看起来新版赢了！转化率提升了 1 个百分点。

**按设备拆分**：
| 设备 | 版本 | 用户数 | 转化人数 | 转化率 |
|------|------|--------|---------|--------|
| PC | 旧版 | 8000 | 1400 | **17.5%** |
| PC | 新版 | 3000 | 540  | **18.0%** ← 新版本在 PC 上赢了 |
| 手机 | 旧版 | 2000 | 100  | **5.0%** |
| 手机 | 新版 | 7000 | 1060 | **15.1%** ← 新版本在手机上也赢了 |

**真相**：新版无论在 PC 还是手机上，转化率都更高。新版真正提升转化率了吗？**不一定。** 注意新版用户中手机用户占比 70%（7000/10000），旧版只占 20%（2000/10000）。手机用户转化率普遍更低——新版整体转化率从 15.0% 提升到 16.0% 很可能是**用户结构变了**，而不是页面改版真的更好。

这就是辛普森悖论的经典模式：**混淆变量（设备类型）同时影响了分组比例和结果指标。**

### 7.2 Python 演示

```python
import numpy as np
import pandas as pd

# 构造数据：模拟辛普森悖论
np.random.seed(42)

# 按版本和设备构造
def make_data(version, pc_n, mobile_n):
    """模拟 PC 和 Mobile 用户的转化数据"""
    records = []

    # PC 用户（转化率较高）
    pc_conv = np.random.binomial(1, 0.175, pc_n) if version == 'old' else \
              np.random.binomial(1, 0.18, pc_n)
    for c in pc_conv:
        records.append({'version': version, 'device': 'PC', 'converted': c})

    # Mobile 用户（转化率较低）
    mobile_conv = np.random.binomial(1, 0.05, mobile_n) if version == 'old' else \
                  np.random.binomial(1, 0.15, mobile_n)
    for c in mobile_conv:
        records.append({'version': version, 'device': 'Mobile', 'converted': c})

    return pd.DataFrame(records)

# 旧版：PC 用户多，Mobile 用户少
df_old = make_data('old', pc_n=8000, mobile_n=2000)
# 新版：PC 用户少，Mobile 用户多（用户结构发生了剧变）
df_new = make_data('new', pc_n=3000, mobile_n=7000)

df = pd.concat([df_old, df_new], ignore_index=True)

print("=" * 60)
print("辛普森悖论演示")
print("=" * 60)

# 整体对比
overall = df.groupby('version')['converted'].agg(['sum', 'count'])
overall['rate'] = overall['sum'] / overall['count']
print("\n[整体对比]")
print(overall)

# 按设备拆分
by_device = df.groupby(['device', 'version'])['converted'].agg(['sum', 'count'])
by_device['rate'] = by_device['sum'] / by_device['count']
print("\n[按设备拆分]")
print(by_device)

# 结论
print("\n" + "=" * 60)
print("结论解读：")
print("1. 如果只看整体：新版转化率更高 → 看起来新版赢了")
print("2. 如果按设备拆开：新版在 PC 和 Mobile 上也都赢了")
print("3. 但是：新版用户中 Mobile 占比大幅增加了！")
print("   旧版 Mobile 占比: 2000 / 10000 = 20%")
print("   新版 Mobile 占比: 7000 / 10000 = 70%")
print("4. 整体转化率提升可能主要来自用户结构变化，")
print("   而不是页面改版真正提升了转化率。")
print("=" * 60)
```

### 7.3 如何防范

| 方法 | 怎么做 |
|------|--------|
| 随机分流 | 保证各组用户构成理论上一致（最根本的防御） |
| AA 测试 | 验证各组基线指标和历史行为是否相近 |
| SRM 检验 | 检查各组人数是否符合预期比例 |
| 分层分析 | 按关键维度（设备、渠道、新老用户）分别看结果 |
| 回归调整 | 用 CUPED/方差缩减等协变量调整方法控制混淆因素 |

**面试话术**："辛普森悖论的核心原因是混淆变量同时影响了实验分组和结果。最根本的防范是做好随机分流和 AA 验证——如果分流是随机的，各组用户构成理论上应该一致，就不会出现新版本用户都是手机用户的怪事。"

---

## 八、面试专题：AB 测试不显著怎么办？

面试官问这个问题是想看：你会不会一看到 p>0.05 就说"版本没区别"然后交差。好的分析师应该追问"为什么不显著"。

### 四种可能性 + 对应策略

| 可能性 | 判断方法 | 怎么做 |
|--------|---------|--------|
| **1. 新版本真的没效果** | 效应量接近 0，置信区间包含 0 | 接受结论，记录并关掉实验。**这本身是有价值的信息**——帮你排除了一个无效方案 |
| **2. 样本量不够** | 效应量有业务意义但 p 不显著 | 检查样本量计算。算一下：以当前效应量，需要多少样本才能达到 80% 功效？如果成本可接受，延长实验 |
| **3. 实验时间太短** | 观察 p 值和效应量的趋势 | 继续跑，等数据积累。但要警惕停止规则——不能"p 值变显著了就停" |
| **4. 实验有设计问题** | 分流不均匀、新奇效应、用户交叉污染 | 检查 SRM、AA 测试结果；检查各组用户构成是否一致；去掉前几天数据 |

### Python 诊断工具

```python
def diagnose_ns_result(control_data, treatment_data, alpha=0.05, power=0.8):
    """
    AB 测试不显著时，帮你诊断原因。
    """
    # 1. 基本统计
    effect = np.mean(treatment_data) - np.mean(control_data)
    se = np.sqrt(np.var(control_data)/len(control_data) +
                 np.var(treatment_data)/len(treatment_data))
    ci_lower = effect - 1.96 * se
    ci_upper = effect + 1.96 * se

    # 2. 统计检验
    t_stat, p_value = stats.ttest_ind(treatment_data, control_data)

    print("=" * 50)
    print("AB 测试不显著 — 诊断报告")
    print("=" * 50)
    print(f"对照组均值: {np.mean(control_data):.4f}")
    print(f"实验组均值: {np.mean(treatment_data):.4f}")
    print(f"效应量: {effect:.4f} ({effect/np.mean(control_data)*100:.2f}%)")
    print(f"95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]")
    print(f"p 值: {p_value:.4f}")

    # 3. 判断
    print(f"\n--- 诊断意见 ---")
    if abs(effect) < 0.001:
        print("[建议] 效应量几乎为 0，大概率新版本真没效果，建议关停实验。")
    elif ci_lower <= 0 <= ci_upper:
        relative_effect = abs(effect) / np.mean(control_data)
        if relative_effect > 0.01:
            print(f"[建议] 效应量 {relative_effect*100:.1f}% 有业务意义，" +
                  f"但置信区间跨 0。可能样本量不够，建议延长实验或增大流量。")
        else:
            print("[建议] 效应量有统计方向但业务意义不大（<1%），" +
                  "即使显著可能也不值得上线。")
    else:
        print("[建议] 置信区间不跨 0 但 p 不显著？请检查数据分布是否严重偏离正态。")

    # 4. 反算所需样本量
    pooled_std = np.sqrt((np.var(control_data) + np.var(treatment_data)) / 2)
    cohens_d = abs(effect) / pooled_std
    print(f"\nCohen's d = {cohens_d:.4f}")

    if cohens_d > 0:
        z_alpha = norm.ppf(1 - alpha/2)
        z_beta = norm.ppf(power)
        required_n = int(np.ceil(2 * (z_alpha + z_beta)**2 / cohens_d**2))
        current_n = len(control_data) + len(treatment_data)
        print(f"以当前效应量，达到 {power*100:.0f}% 功效每组需要: {required_n} 人")
        print(f"当前总样本量: {current_n} 人")
        if current_n < required_n:
            print(f"→ 样本量不足，需要额外 {required_n - current_n} 人")
        else:
            print("→ 样本量已足够，不显著是因为效应量本身太小")

# 示例
np.random.seed(42)
control_ns = np.random.normal(100, 15, 500)       # 假阳性场景
treatment_ns = np.random.normal(100.5, 15, 500)   # 只有 0.3% 差异
diagnose_ns_result(control_ns, treatment_ns)
```

---

## 九、p-hacking：常见的"科研作弊"

### 9.1 定义

**p-hacking（数据挖掘偏差）是指：研究者通过反复调整分析方法或数据选择，直到得到 p < 0.05，然后只报告这个结果。**

这不是传统意义上的造假——每一步单独看都可能合理，但当无数次尝试叠加起来，就变成了对显著性的"钓鱼"。

### 9.2 常见 p-hacking 做法

| 做法 | 看起来的样子 | 为什么是错的 |
|------|------------|------------|
| 中途偷看 | "我就看一眼 p 值，不显著就继续跑" | 每次偷看 = 一次独立检验，多次偷看导致第一类错误累积 |
| p 值显著就停止 | "数据够了，p<0.05 了" | 等同于"等到抛硬币连续 5 次正面再停" |
| 反复清洗数据 | "踢掉这个异常值试试""换个分组方式" | 每次尝试 = 一次检验机会 |
| 挑指标 | 同时看 10 个指标，只报显著的 | 纯多重检验问题 |
| 挑对照组 | 换一个对照组、换一个时间段 | 同样是"钓鱼" |

### 9.3 如何避免

| 方法 | 怎么做 |
|------|--------|
| **预注册** | 开始实验前写好方案，锁定指标、样本量、分析方法，事后不能改 |
| **固定样本量和停止时间** | 写到实验文档里，不达标不停止，超标的也跑完 |
| **多个指标用校正** | Bonferroni 或 FDR |
| **要求效应量** | 不仅看 p 值，还看实际提升多大。p<0.05 但只提升 0.01% 通常不值一提 |
| **可复现性** | 同一个实验换一批用户再做一次 |

**面试话术**："p-hacking 的灵魂是'选择的自由度'——分析方法、数据范围、停止规则都留给你自由选择，就给了你操纵 p 值的机会。最好的预防是预注册——实验开始前把一切定死。"

---

## 十、非参数检验：Mann-Whitney U 检验

### 10.1 什么时候用？

t 检验的前提是**数据近似正态分布**且**方差齐性**。如果数据严重偏态（如用户收入、页面停留时长、订单金额），t 检验可能不可靠。这时候该用 Mann-Whitney U 检验（也叫 Wilcoxon 秩和检验）。

**核心思路**：不比较均值，而是比较两组的**秩次（rank）**。把所有样本混在一起从小到大排序，看哪组整体偏大。

### 10.2 与非参数检验的对比

| 场景 | 参数检验 | 非参数检验替代 |
|------|---------|--------------|
| 两组均值对比（正态） | t 检验 | Mann-Whitney U |
| 多组均值对比（正态） | ANOVA | Kruskal-Wallis |
| 配对数据对比 | 配对 t 检验 | Wilcoxon 符号秩检验 |
| 相关性 | Pearson 相关 | Spearman 秩相关 |

### 10.3 Python 示例：Mann-Whitney U vs t 检验

```python
from scipy.stats import mannwhitneyu

# 模拟右偏数据（如用户收入分布）
np.random.seed(42)
n = 200

# 两组收入数据，都是严重右偏（指数分布）
income_control = np.random.exponential(5000, n)   # 对照组：平均收入 5000
income_treatment = np.random.exponential(5200, n)  # 实验组：平均收入 5200（有微小提升）

# t 检验（数据不正态，t 检验可能不准确）
t_stat, t_p = stats.ttest_ind(income_treatment, income_control)
print(f"t 检验: t={t_stat:.3f}, p={t_p:.4f}")

# Mann-Whitney U 检验（不依赖正态假设）
u_stat, u_p = mannwhitneyu(income_treatment, income_control, alternative='two-sided')
print(f"Mann-Whitney U: U={u_stat:.0f}, p={u_p:.4f}")

# 经验：当数据右偏严重时，Mann-Whitney 通常比 t 检验给出更保守的 p 值

# 验证：模拟检测正态 vs 偏态下的表现差异
print("\n" + "=" * 50)
print("对比：正态数据 vs 偏态数据下两种检验的表现")
print("=" * 50)

def compare_tests(name, data_a, data_b):
    t_stat, t_p = stats.ttest_ind(data_a, data_b)
    u_stat, u_p = mannwhitneyu(data_a, data_b, alternative='two-sided')
    print(f"\n{name}:")
    print(f"  t 检验: p={t_p:.4f}")
    print(f"  MW-U:   p={u_p:.4f}")

# 正态数据：两个检验应该接近
np.random.seed(1)
compare_tests("正态数据（均值有微小差异）",
              np.random.normal(100, 15, 200),
              np.random.normal(102, 15, 200))

# 偏态数据：Mann-Whitney 更可靠
np.random.seed(1)
compare_tests("偏态数据（均值有微小差异）",
              np.random.exponential(100, 200),
              np.random.exponential(102, 200))
```

### 10.4 面试话术

> "t 检验假设数据正态分布，但很多业务数据（收入、时长、订单金额）天生是偏态的。这时候我用 Mann-Whitney U 检验——它比较的是两组的秩次序而非均值，对偏态和离群值更稳健。代价是统计功效略低于 t 检验（在数据确实正态时），以及结果解释是'分布位置不同'而不是'均值不同'。"

---

## 十一、常见陷阱（原版保留 + 补充）

| 陷阱 | 问题 | 解法 |
|------|------|------|
| 偷看（Peeking） | 天天看 p 值，等 p<0.05 就停 | 提前定好样本量和结束时间，到点再看 |
| 多重比较 | 同时测 20 个指标，总有一个 p<0.05 | Bonferroni 校正或 Benjamini-Hochberg FDR |
| 新奇效应 | 新东西刚出来数据好，过几天回归均值 | 跑够时间，去掉前几天数据 |
| 样本污染 | 同一用户同时看到新旧版本 | user_id 哈希固化分组 |
| 辛普森悖论 | 整体看赢了，拆开看没赢 | 分层分析 + AA 验证 + SRM 检验 |
| p-hacking | 反复调整分析方式直到显著 | 预注册方案，锁定分析方法 |
| 统计显著但业务不显著 | p<0.05 但只提升 0.01% | 事前和业务方约定最小可检测效应 |
| 只报显著不报不显著 | 选择性报告 | 所有实验结果归档 |

---

## 十二、面试高频考点小结

| 考点 | 高频程度 | 核心要点 |
|------|---------|---------|
| p 值的准确定义 | ★★★★★ | "在 H0 为真时观察到当前结果或更极端的概率"，不是"H0 为真的概率" |
| 第一类/第二类错误 | ★★★★★ | α（误报）vs β（漏报），不能同时减小除非增大样本量 |
| AB 测试全流程 | ★★★★★ | OEC→样本量→分流→AA→运行→分析→决策，每步讲出为什么 |
| 样本量由什么决定 | ★★★★☆ | 基线、预期提升、α、power，最小可检测效应必须由业务方定 |
| 多重检验校正 | ★★★★☆ | Bonferroni（保守）vs FDR（平衡），能解释"20 个检验，至少一个显著"的概率 |
| 辛普森悖论 | ★★★★☆ | 混淆变量同时影响分组和结果，靠随机分流+AA测试防范 |
| AB 测试不显著怎么办 | ★★★★☆ | 四种可能性：真没效果、样本不够、时间太短、设计问题 |
| p-hacking | ★★★☆☆ | 定义、常见做法（偷看、挑指标、洗数据）、预注册防 |
| 非参数检验 | ★★★☆☆ | Mann-Whitney U 适用偏态数据，秩次序替代均值比较 |
| SRM / AA 测试 | ★★★☆☆ | 分流均匀性验证，AB 测试的安全带 |

---

## 相关笔记

- [[工作学习/统计学基础/概率分布基础]] — 正态分布、CLT、分布拟合、Q-Q 图
- [[工作学习/机器学习/模型评估与调参]] — 交叉验证、偏差方差权衡、超参数搜索
- [[工作学习/统计学基础/描述性统计与可视化]] — 均值/中位数/方差、箱线图、EDA 流程
- [[工作学习/机器学习/AB测试平台搭建]] — 实验平台架构、分流引擎设计
