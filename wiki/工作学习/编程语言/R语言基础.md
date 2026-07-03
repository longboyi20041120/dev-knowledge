---
tags:
  - "#用途/工作学习"
  - "#类型/技术"
  - "#技术/r"
  - "#技术/数据分析"
  - "#状态/草稿"
created: 2026-07-02
updated: 2026-07-02
status: draft
---

# R 语言基础

R 是统计学家为统计学家设计的语言，在学术界和数据分析领域广泛应用。如果你做数据分析和统计建模，R 和 Python 至少要精通一个。

参考：《R语言程序设计》

## 一、R 语言定位与特点

| 特性 | 说明 |
|------|------|
| 设计初衷 | 统计计算和数据可视化 |
| 核心优势 | 丰富的统计包（CRAN 超过 2 万个包） |
| 数据类型 | 向量化操作是核心，一切皆向量 |
| 语法风格 | 函数式 + 向量化，和 Python/C 差异大 |
| 索引 | **从 1 开始**（不是 0！） |
| 赋值 | `<-` 是传统写法，`=` 也可以用 |
| 适用场景 | 统计建模、学术论文、数据可视化、生物信息学 |

### R 与 Python 在数据科学中的对比

| 对比维度 | R | Python |
|----------|---|--------|
| 上手难度 | 中等（语法独特） | 低（语法直观） |
| 数据可视化 | 极强（ggplot2 是业界标杆） | 强（matplotlib/seaborn/plotly） |
| 统计分析 | 极强（内置 + CRAN 海量包） | 强（scipy/statsmodels） |
| 机器学习 | 强（caret/tidymodels） | 极强（sklearn 生态） |
| 深度学习 | 弱 | 极强（PyTorch/TensorFlow） |
| 工程能力 | 弱（不擅长做 Web/API） | 强（Django/Flask） |
| 社区 | 学术界为主 | 工业界为主 |
| 数据操作 | dplyr 优雅 | pandas 功能强大 |

**面试话术**："R 的强项是统计建模和数据可视化，Python 的强项是机器学习和工程部署。实际工作中两者经常互补：用 R 做探索性分析和统计检验，用 Python 做模型训练和线上部署。"

## 二、基本数据类型

### 2.1 向量（Vector）——最核心的数据结构

```r
# R 中最基本的数据结构，一切皆向量
# 标量也是长度为 1 的向量

# 创建向量
x <- c(1, 2, 3, 4, 5)        # c() = combine，最常用
y <- seq(1, 10, by = 2)      # seq: 1, 3, 5, 7, 9
z <- rep(1, times = 5)       # rep: 1, 1, 1, 1, 1
names <- c("Alice", "Bob", "Carol")

# 向量化操作——R 的灵魂（无需循环）
x <- c(1, 2, 3, 4, 5)
print(x + 2)          # 3, 4, 5, 6, 7   （每个元素 +2）
print(x * 2)          # 2, 4, 6, 8, 10
print(x^2)            # 1, 4, 9, 16, 25
print(sqrt(x))        # 1.00, 1.41, 1.73, 2.00, 2.24

# 两个向量按元素运算（长度不等时会循环补齐）
a <- c(1, 2, 3)
b <- c(10, 20, 30)
print(a + b)          # 11, 22, 33

# 索引——注意从 1 开始！
x <- c(10, 20, 30, 40, 50)
print(x[1])           # 10（不是 0！）
print(x[1:3])         # 10, 20, 30
print(x[c(1, 3, 5)]) # 10, 30, 50
print(x[-2])          # 10, 30, 40, 50（负索引表示排除）

# 逻辑索引
print(x[x > 25])      # 30, 40, 50
print(x[x %% 20 == 0]) # 20, 40（能被 20 整除的）

# 向量的类型
# numeric（数值）、character（字符）、logical（逻辑）、factor（因子）
```

### 2.2 矩阵（Matrix）

```r
# 矩阵：二维、同类型数据
mat <- matrix(1:12, nrow = 3, ncol = 4)
print(mat)
#      [,1] [,2] [,3] [,4]
# [1,]    1    4    7   10
# [2,]    2    5    8   11
# [3,]    3    6    9   12

mat <- matrix(1:12, nrow = 3, byrow = TRUE)  # 按行填充
#      [,1] [,2] [,3] [,4]
# [1,]    1    2    3    4
# [2,]    5    6    7    8
# [3,]    9   10   11   12

# 矩阵运算
A <- matrix(1:4, nrow = 2)
B <- matrix(c(1, 0, 0, 1), nrow = 2)
print(A %*% B)       # 矩阵乘法（不是 A * B，那是按元素乘）
print(t(A))          # 转置
print(solve(A))      # 逆矩阵

# 行列命名
rownames(mat) <- c("行1", "行2", "行3")
colnames(mat) <- c("col_A", "col_B", "col_C", "col_D")
```

### 2.3 数据框（Data Frame）——数据分析的核心

```r
# 数据框：类似 Excel 表格或 SQL 表，每列可以是不同类型
df <- data.frame(
    id = 1:4,
    name = c("Alice", "Bob", "Carol", "David"),
    age = c(25, 30, 27, 35),
    salary = c(12000, 18000, 15000, 22000),
    stringsAsFactors = FALSE  # 不让字符自动变因子
)
print(df)
#   id  name age salary
# 1  1 Alice  25  12000
# 2  2   Bob  30  18000
# 3  3 Carol  27  15000
# 4  4 David  35  22000

# 基本信息
str(df)           # 数据结构概览
summary(df)       # 每列的统计摘要
nrow(df)          # 行数
ncol(df)          # 列数
colnames(df)      # 列名

# 访问数据
df$name           # 取一列，返回向量
df[1, ]           # 取第一行
df[, "salary"]    # 取 salary 列
df[1:2, c("name", "age")]  # 前两行的 name 和 age
df[df$age > 28, ]           # 年龄大于 28 的行

# 添加新列
df$bonus <- df$salary * 0.1
print(df)
```

### 2.4 列表（List）与因子（Factor）

```r
# 列表：可以存放任意类型和长度的元素
my_list <- list(
    name = "张三",
    scores = c(85, 90, 78),
    passed = TRUE,
    details = list(age = 25, city = "北京")
)
print(my_list$name)             # "张三"
print(my_list$scores[2])        # 90
print(my_list[["details"]]$age) # 25

# 因子：用于分类变量，有 levels（水平）的概念
gender <- factor(c("男", "女", "男", "女", "男"))
print(gender)
# [1] 男 女 男 女 男
# Levels: 男 女

print(levels(gender))  # "男" "女"
print(table(gender))   # 频数统计: 男=3, 女=2

# 有序因子
grade <- factor(
    c("优秀", "良好", "及格", "优秀", "不及格"),
    levels = c("不及格", "及格", "良好", "优秀"),
    ordered = TRUE
)
print(grade[1] > grade[3])  # TRUE（"优秀" > "良好"）
```

## 三、数据操作：dplyr

dplyr 是 R 生态中处理数据最优雅的包，五个核心函数被称为"数据处理五虎将"。

```r
# 安装和加载
# install.packages("dplyr")
library(dplyr)

# 创建示例数据
employees <- data.frame(
    id = 1:8,
    name = c("张三","李四","王五","赵六","孙七","周八","吴九","郑十"),
    department = c("研发","研发","市场","市场","研发","人事","市场","人事"),
    salary = c(15000, 18000, 12000, 13000, 22000, 10000, 11000, 9500),
    years = c(3, 5, 2, 4, 7, 1, 3, 2),
    stringsAsFactors = FALSE
)

# ===== filter()：筛选行 =====
filter(employees, department == "研发")        # 研发部员工
filter(employees, salary > 12000 & years >= 3) # 高薪且老员工
filter(employees, department %in% c("研发", "市场"))  # 研发或市场

# ===== select()：选择列 =====
select(employees, name, salary)              # 选两列
select(employees, -id)                       # 排除 id 列
select(employees, starts_with("s"))           # salary 列（以 s 开头）
select(employees, name, department, everything())  # 把 name 和 department 移到前面

# ===== mutate()：创建/修改列 =====
mutate(employees,
    bonus = salary * 0.15,                   # 新增奖金列
    total_comp = salary + bonus,             # 新增总薪酬列
    senior = if_else(years >= 3, "老员工", "新员工")  # 新增分类列
)

# ===== arrange()：排序 =====
arrange(employees, salary)                   # 按薪资升序
arrange(employees, desc(salary))             # 按薪资降序
arrange(employees, department, desc(years))  # 先按部门，再按年限降序

# ===== summarise()：汇总 =====
summarise(employees,
    avg_salary = mean(salary),
    total_people = n(),
    max_years = max(years)
)

# ===== 管道操作符 %>%：串联多个操作 =====
result <- employees %>%
    filter(years >= 2) %>%                    # 1. 筛选工作2年以上的
    group_by(department) %>%                  # 2. 按部门分组
    summarise(                                # 3. 汇总统计
        人数 = n(),
        平均薪资 = mean(salary),
        最高薪资 = max(salary),
        平均年限 = mean(years)
    ) %>%
    arrange(desc(平均薪资))                    # 4. 按平均薪资降序

print(result)
# A tibble: 3 x 5
#   department  人数 平均薪资 最高薪资 平均年限
#   <chr>      <int>    <dbl>    <dbl>    <dbl>
# 1 研发          3    18333.   22000      5
# 2 市场          3    12000.   13000      4
# 3 人事          2     9750.   10000      1.5
```

### dplyr 常用函数速查

| 函数 | 作用 | 类比 SQL |
|------|------|----------|
| `filter()` | 筛选行 | `WHERE` |
| `select()` | 选择列 | `SELECT` 指定列 |
| `mutate()` | 新增/修改列 | `SELECT ... AS` |
| `arrange()` | 排序 | `ORDER BY` |
| `summarise()` | 汇总 | `GROUP BY ... HAVING` + 聚合函数 |
| `group_by()` | 分组 | `GROUP BY` |
| `left_join()` | 左连接 | `LEFT JOIN` |
| `inner_join()` | 内连接 | `INNER JOIN` |
| `bind_rows()` | 纵向拼接 | `UNION ALL` |

## 四、数据可视化：ggplot2

ggplot2 是 R 数据可视化的王牌，基于"图形语法"（Grammar of Graphics），用图层叠加来构建图形。

```r
# install.packages("ggplot2")
library(ggplot2)

# 使用 R 内置的 mpg 数据集（汽车燃油效率）
head(mpg)
# manufacturer model displ year cyl trans      drv cty hwy fl   class
# <chr>        <chr> <dbl> <int> <int> <chr>    <chr> <int> <int> <chr> <chr>
# 1 audi         a4      1.8  1999     4 auto(l5) f        18    29 p     compact

# ===== ggplot2 核心三要素 =====
# 1. 数据（data）
# 2. 美学映射（aes）：x/y 轴、颜色、形状等
# 3. 几何对象（geom_*）：点、线、柱、箱线等

# ===== 散点图 =====
ggplot(mpg, aes(x = displ, y = hwy)) +
    geom_point()                                    # 基础散点图

ggplot(mpg, aes(x = displ, y = hwy, color = class)) +
    geom_point(size = 2, alpha = 0.7) +             # 颜色按车型分类
    labs(title = "发动机排量与高速油耗",
         x = "发动机排量 (L)", y = "高速油耗 (mpg)",
         color = "车型") +
    theme_minimal()

# ===== 箱线图 =====
ggplot(mpg, aes(x = class, y = hwy, fill = class)) +
    geom_boxplot() +
    labs(title = "各车型高速油耗分布", x = "车型", y = "高速油耗 (mpg)") +
    theme(axis.text.x = element_text(angle = 45, hjust = 1))

# ===== 直方图 =====
ggplot(mpg, aes(x = hwy)) +
    geom_histogram(binwidth = 3, fill = "steelblue", color = "white") +
    labs(title = "高速油耗分布", x = "高速油耗 (mpg)", y = "频数")

# ===== 柱状图 =====
ggplot(mpg, aes(x = class, fill = class)) +
    geom_bar() +
    labs(title = "各车型数量", x = "车型", y = "数量")

# ===== 折线图（时间序列模拟）=====
time_data <- data.frame(
    month = 1:12,
    sales = c(120, 135, 140, 155, 170, 190, 195, 200, 185, 175, 160, 180)
)
ggplot(time_data, aes(x = month, y = sales)) +
    geom_line(color = "steelblue", size = 1) +
    geom_point(size = 2) +
    scale_x_continuous(breaks = 1:12) +
    labs(title = "2026 年月度销售额趋势", x = "月份", y = "销售额 (万元)")

# ===== 分面（facet）——按类别拆分子图 =====
ggplot(mpg, aes(x = displ, y = hwy)) +
    geom_point(alpha = 0.5) +
    facet_wrap(~ class, nrow = 2) +      # 按车型拆分子图
    labs(title = "各车型：排量 vs 高速油耗")
```

### 常用 geom 一览

| geom | 图形 | 使用场景 |
|------|------|----------|
| `geom_point()` | 散点图 | 两个连续变量的关系 |
| `geom_line()` | 折线图 | 时间序列趋势 |
| `geom_bar()` | 柱状图 | 分类变量的计数 |
| `geom_col()` | 柱状图 | 带具体高度的柱（x/y 都有） |
| `geom_histogram()` | 直方图 | 连续变量的分布 |
| `geom_boxplot()` | 箱线图 | 分组数据的分布 |
| `geom_density()` | 密度图 | 概率密度分布 |
| `geom_smooth()` | 平滑趋势线 | 拟合回归线 |

## 五、统计分析

R 的看家本领——几行代码完成一个完整的统计分析。

### t 检验

```r
# 独立样本 t 检验：比较两组均值是否有显著差异
set.seed(42)
group_A <- rnorm(30, mean = 75, sd = 10)  # 30 人，均值 75
group_B <- rnorm(30, mean = 80, sd = 10)  # 30 人，均值 80

result <- t.test(group_A, group_B)
print(result)
# Welch Two Sample t-test
# t = -2.13, df = 57.8, p-value = 0.037
# alternative hypothesis: true difference in means is not equal to 0
# 95 percent confidence interval: [-10.25, -0.32]
# sample estimates: mean of x = 74.2, mean of y = 79.5

# 解读：p-value = 0.037 < 0.05，拒绝原假设，两组均值有显著差异

# 配对 t 检验（同一组人前后测）
before <- c(70, 75, 80, 72, 68, 78, 73, 76, 71, 74)
after  <- c(85, 82, 88, 78, 75, 86, 80, 84, 77, 82)
t.test(before, after, paired = TRUE)  # 看干预是否有效果
```

### 线性回归

```r
# 使用 mtcars 内置数据集
head(mtcars)

# 简单线性回归：mpg（油耗）~ wt（车重）
model <- lm(mpg ~ wt, data = mtcars)
summary(model)

# 输出解读：
# Call:
# lm(formula = mpg ~ wt, data = mtcars)
#
# Coefficients:
#             Estimate Std. Error t value Pr(>|t|)
# (Intercept)  37.2851     1.8776  19.858  < 2e-16 ***
# wt           -5.3445     0.5591  -9.559 1.29e-10 ***
# ---
# Residual standard error: 3.046 on 30 degrees of freedom
# Multiple R-squared:  0.7528,    Adjusted R-squared:  0.7446
# F-statistic: 91.38 on 1 and 30 DF,  p-value: 1.294e-10

# 解读：
# - wt 系数 -5.34：车重每增加 1000 磅，油耗减少 5.34 mpg
# - R-squared 0.75：车重解释了 75% 的油耗变化
# - p-value < 0.05：车重对油耗的影响显著

# 多元线性回归
model2 <- lm(mpg ~ wt + hp + cyl, data = mtcars)
summary(model2)

# 模型诊断图
par(mfrow = c(2, 2))
plot(model)
# 依次是：残差拟合图、QQ 图、标准化残差开方图、Cook 距离图
```

### 逻辑回归

```r
# 二分类问题：根据成绩预测是否录取
admit <- data.frame(
    score = c(55, 60, 65, 70, 75, 80, 85, 90, 95, 100,
              58, 62, 68, 72, 78, 82, 88, 92, 96, 98),
    admitted = c(0, 0, 0, 0, 0, 1, 1, 0, 1, 1,
                  0, 0, 0, 1, 1, 1, 1, 1, 1, 1)
)

model <- glm(admitted ~ score, data = admit, family = binomial)
summary(model)

# 预测
new_students <- data.frame(score = c(73, 83, 93))
pred <- predict(model, new_students, type = "response")
print(pred)  # 如：0.31, 0.67, 0.91（录取概率）
```

### 方差分析（ANOVA）

```r
# 单因素方差分析：比较三个以上组的均值
data("PlantGrowth")  # 内置数据集：三种处理对植物产量的影响
print(PlantGrowth)
#    weight group
# 1    4.17  ctrl
# 2    5.58  ctrl
# ...

result <- aov(weight ~ group, data = PlantGrowth)
summary(result)
#             Df Sum Sq Mean Sq F value Pr(>|F|)
# group        2  3.766  1.8832   4.846 0.0159 *
# Residuals   27 10.492  0.3886

# p < 0.05，说明至少有一组和其他组有显著差异
# 进一步做事后检验（Tukey HSD）找出哪组不同
TukeyHSD(result)
```

## 六、R Markdown 基础

R Markdown 可以混合 Markdown 文本和可执行的 R 代码，一键生成 HTML/PDF/Word 报告。

````r
# 在 RStudio 中创建 .Rmd 文件
# 文件结构示例：

# ---
# title: "销售数据分析报告"
# author: "你的名字"
# date: "2026-07-02"
# output: html_document
# ---

# ```{r setup, include=FALSE}
# knitr::opts_chunk$set(echo = TRUE, warning = FALSE)
# library(ggplot2)
# library(dplyr)
# ```

# ## 数据概览

# ```{r}
# data(mpg)
# summary(mpg)
# ```

# ## 油耗分布

# ```{r, fig.width=8, fig.height=5}
# ggplot(mpg, aes(x = hwy)) +
#     geom_histogram(binwidth = 3, fill = "steelblue", color = "white") +
#     labs(title = "高速油耗分布")
# ```

# 点击 Knit 按钮即可生成报告
````

## 面试高频考点

| 考点 | 出现频率 | 关键要点 |
|------|----------|----------|
| R 与 Python 的区别 | 极高 | 使用场景、各自优势、个人偏好 + 理由 |
| 向量化操作 | 高 | 为什么要向量化、和循环的对比 |
| dplyr 五个核心函数 | 高 | filter/select/mutate/arrange/summarise + group_by |
| ggplot2 图层语法 | 高 | aes + geom_* 的组合方式、和 matplotlib 的对比 |
| t 检验 | 中高 | 独立样本 vs 配对样本、p 值解读 |
| 线性回归输出解读 | 中高 | R-squared、p-value、系数含义 |
| 数据框操作 | 中 | 索引（从 1 开始）、筛选、新增列 |
| 因子（factor） | 中 | 和字符向量的区别、levels、有序因子 |
| 管道操作 %>% | 中 | 和 Unix 管道的类比、提高可读性 |
| R Markdown | 中 | 可重复研究报告、代码和文本混合 |

## 常见错误与调试

```r
# 错误 1：索引从 0 开始
x <- c(10, 20, 30)
# x[0]  # 返回 integer(0)，不是 10！

# 错误 2：== 和 = 混淆
# if (x = 5)  # 错误！赋值返回不可见值
if (x[1] == 10) print("正确")  # 用 ==

# 错误 3：数据框的字符串自动变因子
# R 4.0 之前，data.frame() 默认 stringsAsFactors = TRUE
# 解决：加 stringsAsFactors = FALSE

# 错误 4：NA 的处理
v <- c(1, 2, NA, 4, 5)
mean(v)              # NA（因为有一个 NA）
mean(v, na.rm = TRUE) # 3（排除 NA）
```

## 相关笔记

- [[编程语言/Python基础|Python 基础]] — 数据科学领域的对比与互补
- [[工作学习/Python数据栈/pandas实战-电商订单分析|pandas 实战-电商订单分析]] — R 的 dplyr 相当于 Python 的 pandas
- [[工作学习/Python数据栈/numpy基础|numpy 基础]] — R 的向量化操作对应 NumPy 的广播机制
- [[工作学习/Python数据栈/matplotlib可视化|matplotlib 可视化]] — R 的 ggplot2 和 Python 的 matplotlib 对比
- [[工作学习/统计学基础/假设检验与AB测试|假设检验与 AB 测试]] — R 实现 t 检验和方差分析
- [[工作学习/统计学基础/概率分布基础|概率分布基础]] — R 中的 dnorm/pnorm/qnorm/rnorm
- [[工作学习/机器学习/线性回归与梯度下降|线性回归与梯度下降]] — R 的 lm() 函数实现
- [[工作学习/机器学习/模型评估与调参|模型评估与调参]] — R 中的 caret/tidymodels
- [[工作学习/数据库与SQL/常见业务SQL场景|常见业务 SQL 场景]] — R 连接数据库（RMySQL/DBI）
