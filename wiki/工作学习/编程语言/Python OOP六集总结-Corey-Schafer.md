---
tags:
  - "#用途/工作学习"
  - "#类型/技术"
  - "#技术/python"
  - "#状态/已验证"
created: 2026-07-15
updated: 2026-07-15
status: reviewed
---

# Corey Schafer Python OOP 六集总结

> YouTube 上最清晰的 Python OOP 教程系列，六集 1.5 小时覆盖面试全部 OOP 考点。 | **面试重要度：极高** | 预计阅读：12 分钟

## 视频资源

- YouTube: [Python OOP Tutorials - Working with Classes](https://www.youtube.com/playlist?list=PL-osiE80TeTsqhIuOqKhwlXsIBIdSeYtc) — Corey Schafer，全六集
- 中文字幕方案：浏览器装**沉浸式翻译**插件，自动在英文字幕下方显示中文翻译

---

## 术语速查

```python
class  Dog:                              # 类
    species = "犬科"                      # 类变量

    def __init__(self, name):            # 构造方法
        self.name = name                 # 实例变量

    def bark(self):                      # 实例方法
        print(f"{self.name}：汪汪")

    @classmethod
    def get_species(cls):                # 类方法
        return cls.species

    @staticmethod
    def is_dog(name):                    # 静态方法
        return name != "猫"
```

| 代码 | 专有名称 | 说明 |
|------|----------|------|
| `class Dog:` | 类 | 模板 |
| `__init__(self, name)` | 构造方法 | 创建实例时自动调用 |
| `self.name` | 实例变量 | 每个实例独自拥有 |
| `species` | 类变量 | 所有实例共享 |
| `bark(self)` | 实例方法 | 通过 `self` 访问实例数据 |
| `get_species(cls)` | 类方法 | 通过 `cls` 访问类变量 |
| `is_dog(name)` | 静态方法 | 独立函数，不访问类也不访问实例 |

---

## ① Classes and Instances（类和实例）— 15 分钟

核心是讲 **class 是蓝图，instance 是产品**。

```python
class Employee:
    def __init__(self, first, last, pay):
        self.first = first
        self.last = last
        self.pay = pay
        self.email = first + '.' + last + '@company.com'

    def fullname(self):
        return f'{self.first} {self.last}'

# 实例化
emp_1 = Employee('John', 'Doe', 50000)
emp_1.fullname()           # 推荐
Employee.fullname(emp_1)   # 背后等价，Python 自动把前者转成后者
```

三个关键点：
- `__init__` 是初始化方法，创建实例时**自动调用**，不需要手动调用
- `self` 代表当前实例，必须作为方法的第一参数，但调用时**不用传**——Python 自动传入
- 忘记写 `self` → `TypeError: takes 0 positional arguments but 1 was given`（Python 试图传 self 但方法没接收）

**面试话术**："`__init__` 不是构造函数——`__new__` 才是，但 99% 的情况下你只需要 `__init__`。`self` 就是 Java 里的 `this`，只是 Python 要求你显式写在参数列表里。"

---

## ② Class Variables（类变量）— 12 分钟

**实例变量每人一份，类变量所有人共享**。

```python
class Employee:
    raise_amount = 1.04     # 类变量，所有人共享
    num_of_emps = 0         # 计数器

    def __init__(self, first, last, pay):
        self.first = first      # 实例变量
        self.pay = pay
        Employee.num_of_emps += 1  # 类变量通过类名修改

    def apply_raise(self):
        # self.raise_amount：先在实例 __dict__ 里找，找不到才往上找类变量
        self.pay = int(self.pay * self.raise_amount)
```

最容易踩的坑——两种修改方式完全不同：
```python
Employee.raise_amount = 1.05    # ✅ 修改了类变量，所有人都变
emp_1.raise_amount = 1.05       # ❌ 在 emp_1 的 __dict__ 里新建了一个实例属性
                                #    只影响 emp_1，其他人继续用类变量的 1.04
```

**面试话术**："类变量和实例变量重名时，实例属性会**遮蔽**类变量。Python 查找顺序是：实例 `__dict__` → 类 `__dict__` → 父类 `__dict__`。为了避免混淆，类变量只用于跨实例共享的数据，比如计数器、默认配置。"

### 2.1 类变量：可变 vs 不可变

```python
class Dog:
    species = "犬科"       # ✅ 不可变类变量（str）
    tricks = []            # ⚠️ 可变类变量（list），共享引用
```

| | 不可变 (`str`, `int`) | 可变 (`list`, `dict`) |
|---|---|---|
| 实例读 | 都一样，都读到同一个值 | 都一样 |
| 实例改 `d.xxx = 新值` | 只影响自己（创建实例属性） | 只影响自己 |
| 原地改 `d.xxx.append()` | 不存在这种操作 | **全实例受影响** |

**结论**：类变量只放不可变对象。可变对象放 `__init__` 里用 `self.xxx = []`。

---

## ③ classmethod 和 staticmethod — 13 分钟

三种方法对比：

| 类型 | 装饰器 | 第一个参数 | 能访问什么 | 典型用途 |
|------|--------|-----------|-----------|---------|
| 普通方法 | 无 | `self`（实例） | 实例 + 类 | 操作实例数据 |
| 类方法 | `@classmethod` | `cls`（类） | 类变量 | 替代构造函数 |
| 静态方法 | `@staticmethod` | 无 | 都不访问 | 工具函数 |

**类方法最经典的用法：替代构造函数**

```python
@classmethod
def from_string(cls, emp_str):
    first, last, pay = emp_str.split('-')
    return cls(first, last, pay)   # cls = Employee，自动处理继承

# 用法
emp = Employee.from_string('John-Doe-70000')
```

为什么用 `cls` 而不是 `Employee()`？因为子类继承时 `cls` 指向的是子类，能正确创建子类实例。

**静态方法：跟类逻辑相关但不需要实例/类数据的工具函数**

```python
@staticmethod
def is_workday(day):
    return day.weekday() not in (5, 6)
```

判断标准：方法里用了 `self` → 普通方法，用了 `cls` → `@classmethod`，两个都不用 → `@staticmethod`。

**面试话术**："类方法最常见的面试题是'用来做备选构造器'——当你需要从 JSON、CSV 或字符串解析数据来创建实例时。静态方法本质上就是放在类命名空间里的普通函数，用于不需要访问实例或类数据的工具逻辑。"

### 3.1 生活化理解

| | 需要什么 | 比方 |
|---|---|---|
| 实例方法 | 一只**具体的狗** | "旺财，叫" |
| 类方法 | **狗这个物种** | "狗是什么科？" |
| 静态方法 | **什么都不需要** | "猫是狗吗？" |

### 3.2 生产示例：电商订单

```python
class Order:
    tax_rate = 0.13                      # 类变量：所有订单税率一样

    def __init__(self, order_id, amount):
        self.order_id = order_id         # 实例变量
        self.amount = amount
        self.status = "待支付"

    # 实例方法：操作具体一张订单
    def pay(self):
        self.status = "已支付"

    def total(self):
        return self.amount * (1 + self.tax_rate)

    # 类方法：不需要具体订单，但要创建一张新的
    @classmethod
    def from_dict(cls, data):
        return cls(data["order_id"], data["amount"])

    # 静态方法：纯校验，跟订单本身没关系
    @staticmethod
    def is_valid_amount(amount):
        return 0 < amount < 1000000
```

```python
# 实例方法 — 处理具体订单
order = Order("ORD001", 100)
order.pay()              # ORD001 已支付
order.total()            # 113.0（含税）

# 类方法 — 从别处拿数据转成订单
order2 = Order.from_dict({"order_id": "ORD002", "amount": 250})

# 静态方法 — 用户输入前校验
Order.is_valid_amount(-5)   # False
Order.is_valid_amount(200)  # True
```

### 3.3 怎么判断用哪种

按顺序问自己三个问题：

1. 需要操作一个具体的实例吗？ → 需要 → **实例方法**
2. 需要访问类变量或创建实例吗？ → 需要 → **类方法**
3. 纯粹就是个工具函数？ → **静态方法**

---

## ④ Inheritance（继承）— 19 分钟

**子类自动继承父类的所有属性和方法**。

```python
class Developer(Employee):
    raise_amt = 1.10          # 覆盖父类类变量

    def __init__(self, first, last, pay, prog_lang):
        super().__init__(first, last, pay)  # 交给父类处理已有逻辑
        self.prog_lang = prog_lang          # 只写新增的

class Manager(Employee):
    def __init__(self, first, last, pay, employees=None):
        super().__init__(first, last, pay)
        self.employees = employees or []

    def add_emp(self, emp):
        if emp not in self.employees:
            self.employees.append(emp)

    def print_emps(self):
        for emp in self.employees:
            print('-->', emp.fullname())
```

两个内置函数要记住：
```python
isinstance(mgr_1, Employee)   # True — Manager 也是 Employee
issubclass(Manager, Employee) # True
```

### 4.1 `self.xxx` vs `ClassName.xxx` — 为什么优先用 `self.`

```python
class Order:
    tax_rate = 0.13

    def total_self(self):
        return self.amount * (1 + self.tax_rate)   # 动态绑定，跟实例走

    def total_hard(self):
        return self.amount * (1 + Order.tax_rate)  # 硬编码，写死了 Order

class CrossBorderOrder(Order):
    tax_rate = 0                                   # 子类覆盖：免税

o = CrossBorderOrder()
o.amount = 100

o.total_self()   # 100.0   ✅ self.tax_rate 找到了子类的 0
o.total_hard()   # 113.0   ❌ Order.tax_rate 写死，还是 13%
```

| 写法 | 术语 | 效果 |
|------|------|------|
| `self.tax_rate` | 动态绑定 | 从当前实例所属的类开始往上找，尊重子类覆盖 |
| `Order.tax_rate` | 类名硬编码 / 静态引用 | 无视子类，永远指向 Order |

只要存在被子类覆盖的可能，就用 `self.`。

**MRO（Method Resolution Order，方法解析顺序）**：`Developer → Employee → builtins.object`。Python 从下往上、从左往右搜索方法。用 `ClassName.mro()` 或 `help(ClassName)` 查看。

**面试话术**："`super()` 在多重继承下按照 MRO 顺序调用，不是只调用父类——这叫做 cooperative multiple inheritance。处理继承链中 `__init__` 参数时常用 `**kwargs` 让 `super()` 把不需要的参数继续往上传递。"

---

## ⑤ Special (Magic/Dunder) Methods（魔法方法）— 14 分钟

**双下划线开头结尾的方法，让自定义对象像内置对象一样好用**。

```python
class Employee:
    def __repr__(self):
        return f"Employee('{self.first}', '{self.last}', {self.pay})"

    def __str__(self):
        return f'{self.fullname()} - {self.email}'

    def __add__(self, other):
        return self.pay + other.pay

    def __len__(self):
        return len(self.fullname())
```

**`__repr__` vs `__str__` 的区分：**

| 方法 | 目标读者 | 目标 | 调用场景 |
|------|---------|------|---------|
| `__repr__` | 开发者 | 无歧义，最好能 `eval(repr(obj))` 重建 | `repr(obj)`、交互式终端直接输变量名 |
| `__str__` | 用户 | 可读性好 | `print(obj)`、`str(obj)`、f-string |

`print(obj)` 优先找 `__str__`，没找到就用 `__repr__`。所以**至少要实现 `__repr__`**。

常见魔法方法速查：

| 方法 | 触发 | 示例 |
|------|------|------|
| `__str__` | `print(obj)` | 人类可读输出 |
| `__repr__` | `repr(obj)` | 无歧义输出 |
| `__add__` | `a + b` | 自定义加法 |
| `__len__` | `len(obj)` | 返回对象长度 |
| `__eq__` | `a == b` | 自定义相等判断 |
| `__getitem__` | `obj[key]` | 索引访问 |
| `__iter__` | `for x in obj` | 迭代 |

**面试话术**："至少要实现 `__repr__`——它影响调试体验。`__str__` 是 `__repr__` 的可读替代品。用 `==` 比较自定义对象时如果不实现 `__eq__`，Python 默认比较的是内存地址（`is`），这几乎不是你想要的。"

---

## ⑥ Property Decorators（属性装饰器）— 13 分钟

**不改变外部调用方式，给属性加 getter/setter/deleter**。

```python
class Employee:
    def __init__(self, first, last):
        self.first = first
        self.last = last

    @property
    def email(self):
        """动态计算，自动跟随 first/last 变化"""
        return f'{self.first}.{self.last}@company.com'

    @property
    def fullname(self):
        return f'{self.first} {self.last}'

    @fullname.setter
    def fullname(self, name):
        first, last = name.split(' ')
        self.first = first
        self.last = last

    @fullname.deleter
    def fullname(self):
        self.first = None
        self.last = None
```

用法：
```python
emp = Employee('John', 'Doe')
print(emp.email)              # John.Doe@company.com  ← 不需要括号！
print(emp.fullname)           # John Doe

emp.fullname = 'Jane Smith'   # 触发 setter，自动更新 first/last
print(emp.first)              # Jane
print(emp.email)              # Jane.Smith@company.com  ← 自动跟着变了

del emp.fullname              # 触发 deleter，清空 first/last
```

**最大的坑：属性名和 getter 方法同名 → 无限递归**

```python
# ❌ 错误写法
class Foo:
    @property
    def name(self):
        return self.name   # ← 无限递归！self.name 又调用了这个 getter

# ✅ 正确写法
class Foo:
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name  # ← 背后存的是 _name，getter 叫 name
```

**面试话术**："`@property` 的核心价值是**向后兼容**——如果一开始设计了 `emp.email` 这种简单属性，后来发现需要动态计算，你不需要把所有 `emp.email` 改成 `emp.email()`，加个 `@property` 就好。这在 Java 里做不到。"

---

## 总体结构

六个视频按难度递进：

```
① 类与实例（基础）
  └─ ② 类变量 vs 实例变量（内存模型）
      └─ ③ 三种方法类型（@classmethod/@staticmethod）
          └─ ④ 继承 + super() + MRO（OOP 核心）
              ├─ ⑤ 魔法方法（自定义对象行为）
              └─ ⑥ @property（优雅的 getter/setter）
```

面试问 Python OOP，基本不出这六个视频的范围。

## 面试高频考点速查

| 考点 | 出处 | 关键点 |
|------|------|--------|
| `self` 是什么、为什么显式写 | 视频① | 代表实例，调用时自动传入 |
| `__init__` 是构造函数吗 | 视频① | 不是，`__new__` 才是，`__init__` 是初始化 |
| 类变量被实例遮蔽 | 视频② | 实例 `__dict__` 先查找 |
| `@classmethod` vs `@staticmethod` | 视频③ | 是否用 `cls`/是否需要类数据 |
| `super()` 的 MRO 顺序 | 视频④ | 多重继承下按 MRO 链调用 |
| `isinstance` vs `issubclass` | 视频④ | 对象检查 vs 类检查 |
| `__repr__` vs `__str__` | 视频⑤ | 开发者 vs 用户 |
| `@property` 解决什么问题 | 视频⑥ | 向后兼容，属性变方法不破坏 API |

## 相关笔记

- [[工作学习/编程语言/Python基础|Python 基础]] — 数据类型、装饰器、生成器
- [[工作学习/机器学习/梯度下降详解]] — gradient descent 里的 `@property` 用法
- [[书架与学习路线]] — Python 学习路线全景
