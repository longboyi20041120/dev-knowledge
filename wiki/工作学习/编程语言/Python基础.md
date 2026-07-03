---
tags:
  - "#用途/工作学习"
  - "#类型/技术"
  - "#技术/python"
  - "#状态/草稿"
created: 2026-07-02
updated: 2026-07-02
status: draft
---

# Python 基础

Python 是目前数据科学、后端开发、自动化运维的首选语言。面试中 Python 问题通常分两类：语言特性（装饰器、GIL）和工程能力（爬虫、数据处理）。

参考：《Python 3程序设计》《Python网络爬虫技术（微课视频版）》

## 一、Python 核心特点

| 特性   | 说明                    | 面试角度                |
| ---- | --------------------- | ------------------- |
| 动态类型 | 变量无需声明类型，运行时确定        | "动态类型和静态类型的优缺点？"    |
| 解释型  | 逐行解释执行（实际上有 .pyc 字节码） | "Python 是纯解释型吗？"    |
| 鸭子类型 | "如果它走路像鸭子，它就是鸭子"      | "什么是鸭子类型？"          |
| 强类型  | `"1" + 2` 会报错，不会隐式转换  | "Python 是强类型还是弱类型？" |
| GC   | 引用计数 + 标记清除 + 分代回收    | "Python 的垃圾回收机制？"   |
| GIL  | 全局解释器锁，限制多线程并行        | "GIL 是什么？怎么绕过？"     |

```python
# 鸭子类型示例：不检查类型，只检查行为
def double(obj):
    return obj * 2

print(double(5))         # 10，int 支持 *
print(double("Hi"))      # "HiHi"，str 支持 *
print(double([1, 2]))    # [1, 2, 1, 2]，list 也支持 *
# double 不关心参数类型，只要支持 * 操作就行
```

## 二、数据类型

### 2.1 四大容器类型对比

```python
# list：可变、有序、可重复
lst = [1, 2, 3, 2]
lst.append(4)          # [1, 2, 3, 2, 4]
lst[0] = 10            # [10, 2, 3, 2, 4]

# tuple：不可变、有序、可重复
tup = (1, 2, 3)
# tup[0] = 10          # TypeError！元组不可变
x, y, z = tup          # 解包：x=1, y=2, z=3

# dict：可变、无序（Python 3.7+ 保持插入顺序）、key 唯一
d = {"name": "Alice", "age": 25}
d["city"] = "北京"      # 添加
print(d.get("gender", "未知"))  # 安全取值，不存在返回默认值

# set：可变、无序、元素唯一
s = {1, 2, 3, 2}       # {1, 2, 3}，重复元素自动去重
a = {1, 2, 3}
b = {2, 3, 4}
print(a & b)            # {2, 3}  交集
print(a | b)            # {1, 2, 3, 4}  并集
print(a - b)            # {1}  差集
```

常用操作的时间复杂度：

| 操作 | list | tuple | dict | set |
|------|------|-------|------|-----|
| 按索引访问 | O(1) | O(1) | - | - |
| 按 key 查找 | - | - | O(1) 平均 | O(1) 平均 |
| 在末尾添加 | O(1) 均摊 | - | - | - |
| 在开头插入 | O(n) | - | - | - |
| 删除元素 | O(n) | - | O(1) | O(1) |
| 成员检查 `in` | O(n) | O(n) | O(1) | O(1) |

**面试话术**："查元素用 set 或 dict 是 O(1)，用 list 是 O(n)。如果你写的代码里频繁用 `if x in my_list` 做成员判断，应该把 my_list 转成 set。"

### 2.2 可变 vs 不可变对象

```python
# 不可变：int, float, str, tuple, frozenset
a = "hello"
b = a
a += " world"
print(a)  # "hello world"
print(b)  # "hello" —— b 没变，因为 += 创建了新字符串

# 可变：list, dict, set
a = [1, 2, 3]
b = a
a.append(4)
print(a)  # [1, 2, 3, 4]
print(b)  # [1, 2, 3, 4] —— b 也变了！因为 append 修改了原对象

# 默认参数陷阱——经典的面试题
def bad_append(item, lst=[]):     # 默认参数在函数定义时只创建一次！
    lst.append(item)
    return lst

print(bad_append(1))  # [1]
print(bad_append(2))  # [1, 2] —— 不是 [2]！上次的列表还在

# 正确做法
def good_append(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst
```

### 2.3 深拷贝与浅拷贝

```python
import copy

original = [[1, 2], [3, 4]]

# 浅拷贝：只复制外层容器，内部元素仍是引用
shallow = copy.copy(original)
shallow[0][0] = 999
print(original[0][0])  # 999 —— 原对象也被修改了！

# 深拷贝：递归复制所有层
deep = copy.deepcopy(original)
deep[0][0] = 888
print(original[0][0])  # 999 —— 原对象不受影响

# 面试口诀：浅拷贝只拷贝第一层，深拷贝递归拷贝所有层
```

## 三、函数

### 3.1 参数传递

```python
# Python 的参数传递是"传对象引用"（call by sharing）
# 不是传值，也不是传引用——面试时要能说清

def modify(num, lst):
    num += 1          # 不可变对象：创建新对象，不影响外部
    lst.append(4)     # 可变对象：修改原对象，影响外部

x = 10
y = [1, 2, 3]
modify(x, y)
print(x)  # 10 —— 不变
print(y)  # [1, 2, 3, 4] —— 变了

# 参数类型：位置参数、默认参数、可变参数、关键字参数
def demo(a, b=10, *args, **kwargs):
    print(f"a={a}, b={b}")
    print(f"args={args}")       # 多余的 位置参数
    print(f"kwargs={kwargs}")   # 多余的 关键字参数

demo(1, 2, 3, 4, name="Alice", age=25)
# 输出：
# a=1, b=2
# args=(3, 4)
# kwargs={'name': 'Alice', 'age': 25}
```

### 3.2 lambda 与高阶函数

```python
# lambda：一行匿名函数
add = lambda x, y: x + y
print(add(3, 5))  # 8

# 常用于排序的 key 参数
students = [("Alice", 85), ("Bob", 72), ("Carol", 90)]
students.sort(key=lambda s: s[1])  # 按成绩排序
print(students)  # [('Bob', 72), ('Alice', 85), ('Carol', 90)]

# map / filter / reduce
nums = [1, 2, 3, 4, 5]

squares = list(map(lambda x: x**2, nums))       # [1, 4, 9, 16, 25]
evens = list(filter(lambda x: x % 2 == 0, nums)) # [2, 4]

from functools import reduce
total = reduce(lambda acc, x: acc + x, nums)    # 15
```

### 3.3 装饰器——面试必考

```python
import time
from functools import wraps

# 装饰器本质：接受函数，返回新函数（增加额外行为）
def timer(func):
    @wraps(func)  # 保留原函数的元信息（__name__, __doc__）
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} 耗时: {elapsed:.4f} 秒")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(0.5)
    return "done"

print(slow_function())
# 输出：
# slow_function 耗时: 0.5001 秒
# done

# 带参数的装饰器：再加一层
def retry(max_attempts=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    print(f"重试 {attempt + 1}/{max_attempts}...")
                    time.sleep(1)
        return wrapper
    return decorator

@retry(max_attempts=3)
def unstable_network_call():
    import random
    if random.random() < 0.7:
        raise ConnectionError("网络超时")
    return "成功"
```

**面试话术**："装饰器本质是一个接受函数、返回函数的高阶函数。它利用闭包机制，在不修改原函数的情况下增加日志、计时、权限检查等横切关注点。`@wraps` 保持了原函数的元数据。"

### 3.4 生成器

```python
# 生成器：用 yield 代替 return，惰性产出值
def fibonacci(limit):
    a, b = 0, 1
    while a < limit:
        yield a
        a, b = b, a + b

for num in fibonacci(100):
    print(num, end=" ")  # 0 1 1 2 3 5 8 13 21 34 55 89

# 生成器表达式：（类似列表推导式，但用小括号）
squares = (x**2 for x in range(1000000))  # 不占内存
# squares = [x**2 for x in range(1000000)]  # 一次性生成 100 万个元素

# 生成器的优势：内存友好，适合处理大文件/大数据流
def read_large_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            yield line.strip()
# 即使文件有几十 GB，内存也只存当前行
```

## 四、面向对象

```python
class Employee:
    # 类属性——所有实例共享
    company = "TechCorp"
    employee_count = 0

    def __init__(self, name, salary):
        # 实例属性——每个实例独有
        self.name = name
        self._salary = salary      # 单下划线：约定"受保护"
        self.__id = None           # 双下划线：名称改写，外部无法直接访问
        Employee.employee_count += 1

    # 实例方法——最常用
    def introduce(self):
        return f"我是 {self.name}，在 {self.company} 工作"

    # property：让方法像属性一样访问
    @property
    def salary(self):
        return self._salary

    @salary.setter
    def salary(self, value):
        if value < 0:
            raise ValueError("薪资不能为负")
        self._salary = value

    # 类方法——第一个参数是 cls
    @classmethod
    def get_count(cls):
        return cls.employee_count

    # 静态方法——不需要 self 或 cls
    @staticmethod
    def is_valid_name(name):
        return len(name) >= 2

    # 魔法方法
    def __str__(self):
        return f"Employee({self.name})"

    def __repr__(self):
        return f"Employee(name='{self.name}', salary={self._salary})"

    def __eq__(self, other):
        return self.name == other.name and self._salary == other._salary


# 继承
class Manager(Employee):
    def __init__(self, name, salary, department):
        super().__init__(name, salary)   # 调用父类 __init__
        self.department = department

    # 方法重写
    def introduce(self):
        return f"{super().introduce()}，负责 {self.department} 部门"

# 多态
def print_intro(employee):
    print(employee.introduce())  # 不关心具体类型，只关心有 introduce 方法

print_intro(Employee("张三", 10000))    # 我是 张三，在 TechCorp 工作
print_intro(Manager("李四", 20000, "研发"))  # 我是 李四，在 TechCorp 工作，负责 研发 部门
```

## 五、异常处理

```python
# 基本结构
try:
    num = int(input("输入数字: "))
    result = 100 / num
except ValueError:
    print("请输入有效的数字！")
except ZeroDivisionError:
    print("不能除以 0！")
except (TypeError, KeyError) as e:  # 同时捕获多种
    print(f"出错: {e}")
else:
    print(f"结果: {result}")  # 没有异常才执行
finally:
    print("清理资源...")  # 无论如何都执行

# 自定义异常
class BusinessError(Exception):
    def __init__(self, message, code):
        super().__init__(message)
        self.code = code

def transfer_money(amount, balance):
    if amount > balance:
        raise BusinessError("余额不足", code=4001)
    print(f"转账 {amount} 元成功")
```

## 六、文件与 IO

```python
import csv
import json

# with 语句自动关闭文件——不需要手动 f.close()
with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()           # 一次读取全部
    # for line in f:            # 逐行读取，省内存
    #     print(line.strip())

# 写入
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("Hello, World!\n")
    f.writelines(["第 1 行\n", "第 2 行\n"])

# ==== CSV 读写 ====
# 写 CSV
with open("data.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["姓名", "年龄", "城市"])
    writer.writerows([["张三", 25, "北京"], ["李四", 30, "上海"]])

# 读 CSV
with open("data.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)   # 每行变成 dict，key 是表头
    for row in reader:
        print(f"{row['姓名']}，{row['年龄']} 岁，住在 {row['城市']}")

# ==== JSON 读写 ====
data = {"name": "张三", "skills": ["Python", "SQL"]}
json_str = json.dumps(data, ensure_ascii=False, indent=2)  # Python → JSON 字符串
print(json_str)

parsed = json.loads(json_str)   # JSON 字符串 → Python 对象
print(parsed["name"])           # 张三

# 直接读写 JSON 文件
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

## 七、爬虫基础

来自《Python网络爬虫技术》的核心用法：

```python
import requests
from bs4 import BeautifulSoup

# 1. 发送 GET 请求
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
resp = requests.get("https://httpbin.org/get", headers=headers, timeout=10)
print(f"状态码: {resp.status_code}")
print(f"编码: {resp.encoding}")
data = resp.json()  # JSON 响应 → dict

# 2. POST 请求
payload = {"username": "test", "password": "123456"}
resp = requests.post("https://httpbin.org/post", data=payload)

# 3. BeautifulSoup 解析 HTML
html = """
<html>
  <body>
    <div class="article">
      <h2 class="title">Python 爬虫入门</h2>
      <p class="content">这是一篇关于爬虫的教程。</p>
      <a href="/next">下一页</a>
    </div>
    <div class="article">
      <h2 class="title">数据分析实战</h2>
      <p class="content">用 pandas 做数据分析。</p>
    </div>
  </body>
</html>
"""
soup = BeautifulSoup(html, "html.parser")

# 提取所有文章标题
titles = soup.find_all("h2", class_="title")
for t in titles:
    print(t.text)  # Python 爬虫入门  数据分析实战

# CSS 选择器方式
contents = soup.select(".article .content")
for c in contents:
    print(c.text)
```

## 八、常用标准库

```python
# os：操作系统相关
import os
os.path.exists("file.txt")       # 文件是否存在
os.path.join("dir", "sub", "f")  # 跨平台的路径拼接
os.makedirs("a/b/c", exist_ok=True)  # 递归创建目录
os.listdir(".")                  # 列出目录内容
print(os.environ.get("PATH"))    # 环境变量

# sys：Python 运行时
import sys
print(sys.argv)          # 命令行参数列表
print(sys.path)          # 模块搜索路径
sys.exit(0)              # 退出程序

# collections：高级容器
from collections import defaultdict, Counter, deque

# defaultdict：带默认值的字典
word_count = defaultdict(int)
for word in ["a", "b", "a"]:
    word_count[word] += 1  # 不用判断 key 是否存在
print(dict(word_count))    # {'a': 2, 'b': 1}

# Counter：计数神器
print(Counter(["a", "b", "a", "c", "b", "a"]))  # Counter({'a': 3, 'b': 2, 'c': 1})

# deque：双端队列，两端操作 O(1)
dq = deque([1, 2, 3])
dq.appendleft(0)          # [0, 1, 2, 3]
dq.pop()                  # 3，[0, 1, 2]

# itertools：迭代器工具
from itertools import combinations, product
print(list(combinations("ABC", 2)))  # [('A','B'), ('A','C'), ('B','C')]
print(list(product("AB", "12")))     # [('A','1'), ('A','2'), ('B','1'), ('B','2')]

# datetime：时间处理
from datetime import datetime, timedelta
now = datetime.now()
yesterday = now - timedelta(days=1)
print(now.strftime("%Y-%m-%d %H:%M:%S"))   # 格式化输出
print(datetime.strptime("2026-07-02", "%Y-%m-%d"))  # 字符串解析为时间
```

## 面试高频考点

| 考点 | 出现频率 | 关键要点 |
|------|----------|----------|
| 可变 vs 不可变 | 极高 | list/dict 可变，str/tuple 不可变；默认参数陷阱 |
| 深拷贝 vs 浅拷贝 | 极高 | copy 只复制第一层，deepcopy 递归全部 |
| GIL | 高 | 为什么有 GIL、什么时候不影响、怎么绕过（多进程） |
| 装饰器 | 高 | 本质是闭包、@wraps、带参数装饰器 |
| 生成器 vs 列表 | 高 | yield、内存优势、惰性求值 |
| `*args` / `**kwargs` | 中高 | 可变参数和关键字参数的收集与解包 |
| `is` vs `==` | 中高 | is 比较身份（id），== 比较值 |
| `__init__` vs `__new__` | 中 | new 创建实例，init 初始化 |
| with 语句原理 | 中 | 上下文管理器，`__enter__` / `__exit__` |
| Python 的 GC | 中 | 引用计数 + 标记清除 + 分代回收 |

## 相关笔记

- [[工作学习/Python数据栈/pandas实战-电商订单分析|pandas 实战-电商订单分析]]
- [[工作学习/Python数据栈/numpy基础|numpy 基础]]
- [[工作学习/Python数据栈/matplotlib可视化|matplotlib 可视化]]
- [[工作学习/数据库与SQL/常见业务SQL场景|常见业务 SQL 场景]] — Python 连接数据库查询
- [[编程语言/C语言基础|C 语言基础]] — Python 底层是 C 写的
- [[编程语言/Java基础|Java 基础]] — 同是面向对象，对比学习静态类型
- [[编程语言/R语言基础|R 语言基础]] — 数据科学领域的两大主力语言对比
