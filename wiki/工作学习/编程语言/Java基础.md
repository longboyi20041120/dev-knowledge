---
tags:
  - "#用途/工作学习"
  - "#类型/技术"
  - "#技术/java"
  - "#状态/草稿"
created: 2026-07-02
updated: 2026-07-02
status: draft
---

# Java 基础

Java 是后端开发的主力语言，国内大厂（阿里、美团、字节后端）广泛使用。面试中 Java 基础问得很深，尤其是**集合框架**和 **JVM**。

参考：《Java面向对象程序设计教程（微课视频版）》《Java语言实验与课程设计指导（第三版）》

## 一、Java 核心特点

| 特性 | 说明 | 面试角度 |
|------|------|----------|
| 跨平台 | 一次编译，到处运行（JVM 屏蔽平台差异） | "Java 为什么能跨平台？" |
| 强类型 | 每个变量必须有明确的类型 | "强类型的好处？" |
| 面向对象 | 封装、继承、多态（单继承、多实现） | "Java 支持多继承吗？" |
| 自动 GC | JVM 自动回收垃圾内存 | "GC 什么时候触发？" |
| 编译+解释 | `.java` → `.class`（字节码）→ JIT 编译为机器码 | "JIT 是什么？" |

### Java 与 C 的关键差异

```java
// Java：纯面向对象，没有全局函数
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, Java!");
    }
}

// C：面向过程，main 是全局函数
// #include <stdio.h>
// int main() {
//     printf("Hello, C!\n");
//     return 0;
// }
```

| 对比维度 | C | Java |
|----------|---|------|
| 编程范式 | 面向过程 | 面向对象 |
| 内存管理 | 手动 malloc/free | JVM 自动 GC |
| 指针 | 核心特性 | 无指针（只有引用） |
| 多重继承 | 不支持（结构体组合） | 不支持类多继承，接口多实现 |
| 平台 | 依赖平台编译 | 跨平台（JVM） |
| 数组 | `int arr[10]` 栈上分配 | `int[] arr = new int[10]` 堆上分配 |
| 编译产物 | 机器码 | 字节码 |

## 二、基本语法

### 数据类型

```java
// 8 种基本类型（Primitive Types）
byte b = 127;            // 1 字节，-128 ~ 127
short s = 32767;         // 2 字节
int i = 2147483647;      // 4 字节，默认整数字面量
long l = 9223372036854775807L;  // 8 字节，注意 L 后缀
float f = 3.14f;         // 4 字节，注意 f 后缀
double d = 3.1415926535; // 8 字节，默认浮点字面量
char c = 'A';            // 2 字节，Unicode（不同于 C 的 1 字节）
boolean flag = true;     // JVM 依赖实现，通常 1 字节

// 包装类：基本类型的对象版本
Integer iObj = 128;           // 自动装箱
int iVal = iObj;              // 自动拆箱

// 包装类缓存——面试经典陷阱！
Integer a = 127;
Integer bb = 127;
System.out.println(a == bb);     // true   (-128~127 被缓存，同一对象)

Integer ccc = 128;
Integer d = 128;
System.out.println(ccc == d);     // false  (超出缓存范围，不同对象)
System.out.println(ccc.equals(d)); // true   (比的是值)
```

### 字符串

```java
// String 是不可变对象——面试高频
String s1 = "hello";
String s2 = "hello";
System.out.println(s1 == s2);        // true（字符串常量池，同一对象）

String s3 = new String("hello");
System.out.println(s1 == s3);        // false（new 强制创建新对象）
System.out.println(s1.equals(s3));   // true（比较内容）

// StringBuilder：可变，线程不安全，性能好
StringBuilder sb = new StringBuilder();
sb.append("Hello").append(" ").append("World");
System.out.println(sb.toString());   // "Hello World"

// StringBuffer：可变，线程安全（synchronized），性能稍差
StringBuffer sbf = new StringBuffer();
```

## 三、面向对象

### 封装、继承、多态

```java
// 封装：用 private 隐藏内部实现，通过 public 方法暴露接口
public class BankAccount {
    private double balance;         // 外部无法直接访问

    public BankAccount(double initialBalance) {
        if (initialBalance < 0) {
            throw new IllegalArgumentException("初始余额不能为负");
        }
        this.balance = initialBalance;
    }

    public double getBalance() { return balance; }

    public void deposit(double amount) {
        if (amount <= 0) throw new IllegalArgumentException("存款金额必须为正");
        balance += amount;
    }

    public boolean withdraw(double amount) {
        if (amount > balance) return false;
        balance -= amount;
        return true;
    }
}

// 继承：子类获得父类的属性和方法
public class SavingsAccount extends BankAccount {
    private double interestRate;

    public SavingsAccount(double initialBalance, double interestRate) {
        super(initialBalance);               // 调用父类构造器
        this.interestRate = interestRate;
    }

    public void addInterest() {
        deposit(getBalance() * interestRate); // 调用父类方法
    }
}

// 多态：父类引用指向子类对象，调用的是实际类型的方法
BankAccount acc = new SavingsAccount(1000, 0.03);
// acc 的编译时类型是 BankAccount，运行时类型是 SavingsAccount
```

### 抽象类 vs 接口——面试必考

```java
// 抽象类：可以有构造器、成员变量、普通方法
abstract class Animal {
    protected String name;

    public Animal(String name) { this.name = name; }

    public abstract void makeSound();  // 抽象方法，子类必须实现

    public void sleep() {              // 普通方法，子类可继承或重写
        System.out.println(name + " 在睡觉");
    }
}

// 接口：Java 8+ 可以有 default 方法和 static 方法
interface Flyable {
    void fly();                        // 默认是 public abstract

    default void land() {              // 默认实现，子类可选重写
        System.out.println("降落了");
    }

    static boolean canFlyFast() {      // 静态工具方法
        return true;
    }
}

// 一个类只能继承一个父类，但可以实现多个接口
class Bird extends Animal implements Flyable {
    public Bird(String name) { super(name); }

    @Override
    public void makeSound() {
        System.out.println(name + " 叽叽喳喳");
    }

    @Override
    public void fly() {
        System.out.println(name + " 在飞翔");
    }
}
```

| 对比维度 | 抽象类 | 接口 |
|----------|--------|------|
| 关键字 | `abstract class` | `interface` |
| 构造器 | 可以有 | 不能有 |
| 成员变量 | 可以有任意类型 | 只能有 `public static final` 常量 |
| 方法 | 可以有抽象方法和普通方法 | 抽象方法 + default/static 方法 |
| 继承关系 | 单继承 `extends` | 多实现 `implements` |
| 设计意图 | "是什么"（is-a） | "能做什么"（can-do） |

**面试话术**："抽象类描述'是什么'，接口描述'能做什么'。当你需要在不同类的层次结构中共享代码时用抽象类，当你想让不相关的类具有共同行为时用接口。"

## 四、集合框架——面试重点

### 核心接口与类

```
Collection (接口)
├── List (接口)：有序、可重复
│   ├── ArrayList：动态数组，随机访问 O(1)，插入删除 O(n)
│   └── LinkedList：双向链表，随机访问 O(n)，头尾插入删除 O(1)
├── Set (接口)：无序、不可重复
│   ├── HashSet：基于 HashMap，O(1) 增删查
│   ├── LinkedHashSet：保持插入顺序
│   └── TreeSet：红黑树，元素有序，O(log n)
└── Queue (接口)：队列
    └── PriorityQueue：优先队列，二叉堆实现

Map (接口)：键值对
├── HashMap：哈希表，O(1)，允许 null key/value
├── LinkedHashMap：保持插入顺序
├── TreeMap：红黑树，key 有序
└── Hashtable：线程安全，老旧不用了
```

### HashMap 原理——面试重中之重

```java
// JDK 1.8 HashMap 数据结构：数组 + 链表 + 红黑树
// 默认容量 16，负载因子 0.75

Map<String, Integer> map = new HashMap<>();
map.put("Alice", 25);
map.put("Bob", 30);
map.put("Carol", 27);

// 执行流程（简化）：
// 1. 对 key 调用 hashCode() 得到哈希值
// 2. 哈希值 & (容量-1) 得到数组下标
// 3. 如果该位置为空，直接放入
// 4. 如果冲突，用链表（尾插法）或红黑树（链表长度 > 8 且数组长度 >= 64 时树化）
// 5. 如果 size > 容量 * 负载因子，扩容为 2 倍，重新 hash

System.out.println(map.get("Alice"));  // 25
System.out.println(map.getOrDefault("David", 0));  // 0，安全取值

// 遍历方式
for (Map.Entry<String, Integer> entry : map.entrySet()) {
    System.out.println(entry.getKey() + ": " + entry.getValue());
}

// Java 8 新增方法
map.computeIfAbsent("David", k -> 0);  // 不存在时计算放入
map.merge("Alice", 1, Integer::sum);    // Alice 的值 +1
```

**HashMap 面试话术**："JDK 1.7 是数组+链表，头插法，扩容时可能出现死循环。JDK 1.8 改为数组+链表+红黑树，尾插法，链表长度达到 8 且数组长度达到 64 时树化，退化为 6 时链化。负载因子 0.75 是时间和空间的折中。"

### ArrayList vs LinkedList

```java
// ArrayList：底层是数组
List<String> arrayList = new ArrayList<>();
arrayList.add("A");           // 末尾添加，O(1) 均摊
arrayList.add(0, "B");        // 指定位置插入，O(n)，需要移动元素
arrayList.get(3);             // 随机访问，O(1)
// 初始容量 10，扩容时增加 1.5 倍（oldCapacity + oldCapacity >> 1）

// LinkedList：底层是双向链表
List<String> linkedList = new LinkedList<>();
linkedList.add("A");          // 末尾添加，O(1)
linkedList.add(0, "B");       // 指定位置插入，需要遍历到达位置，O(n)
linkedList.get(3);            // 随机访问，O(n)，需要从头遍历
// 头尾操作 O(1)：addFirst / addLast / removeFirst / removeLast
```

| 操作 | ArrayList | LinkedList |
|------|-----------|------------|
| 随机访问 get/set | O(1) | O(n) |
| 末尾添加 | O(1) 均摊 | O(1) |
| 头部添加 | O(n) | O(1) |
| 中间插入 | O(n) | O(n)（遍历） |
| 内存占用 | 紧凑（只存数据） | 大（额外存前后指针） |
| 使用场景 | 读多写少 | 频繁头尾操作 |

## 五、异常处理

```java
// Java 异常体系
// Throwable
// ├── Error（严重问题，不应捕获，如 OutOfMemoryError）
// └── Exception
//     ├── RuntimeException（非受检异常，如 NullPointerException）
//     └── 其他（受检异常，必须 try-catch 或 throws，如 IOException）

// 受检异常（Checked Exception）：编译时强制处理
import java.io.*;

public class ExceptionDemo {
    public static void readFile(String path) {
        // 方式 1：try-catch-finally
        BufferedReader reader = null;
        try {
            reader = new BufferedReader(new FileReader(path));
            String line = reader.readLine();
            System.out.println(line);
        } catch (FileNotFoundException e) {
            System.out.println("文件没找到: " + e.getMessage());
        } catch (IOException e) {
            System.out.println("读取失败: " + e.getMessage());
        } finally {
            // finally 总会执行，即使 try 中有 return
            try {
                if (reader != null) reader.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        // 方式 2：try-with-resources（Java 7+），自动关闭
        try (BufferedReader br = new BufferedReader(new FileReader(path))) {
            System.out.println(br.readLine());
        } catch (IOException e) {
            e.printStackTrace();
        }
        // 括号内的资源必须实现 AutoCloseable 接口，退出时自动 close()
    }

    public static void main(String[] args) {
        readFile("不存在的文件.txt");
        // 输出：文件没找到: 不存在的文件.txt (系统找不到指定的文件。)
    }
}
```

| 对比 | Checked Exception | Unchecked Exception |
|------|-------------------|---------------------|
| 父类 | Exception（非 RuntimeException） | RuntimeException |
| 示例 | IOException, SQLException | NullPointerException, ArrayIndexOutOfBoundsException |
| 处理要求 | 必须 try-catch 或 throws | 不强制处理 |
| 设计意图 | 可预见的、可恢复的错误（文件不存在、网络断） | 编程 bug（空指针、越界） |

## 六、泛型

```java
// 泛型：编译时类型检查，运行时类型擦除
public class Box<T> {
    private T content;

    public void put(T content) { this.content = content; }
    public T get() { return content; }
}

Box<String> stringBox = new Box<>();
stringBox.put("Hello");
// stringBox.put(123);  // 编译错误，类型安全

// 类型擦除：编译后泛型信息被擦除
// Box<String> 和 Box<Integer> 在运行时是同一个类
System.out.println(stringBox.getClass());  // class Box
// 这意味着：不能创建泛型数组、不能用 instanceof 检查泛型类型

// 通配符
// ? extends T：上界通配符，只能读取
public static double sumOfList(List<? extends Number> list) {
    double sum = 0;
    for (Number n : list) sum += n.doubleValue();
    return sum;
    // list.add(1);  // 编译错误！生产者用 extends
}

// ? super T：下界通配符，只能写入
public static void addNumbers(List<? super Integer> list) {
    list.add(1);
    list.add(2);
    // Integer n = list.get(0);  // 编译错误！消费者用 super
}

// PECS 原则：Producer Extends, Consumer Super
```

## 七、多线程基础

```java
// 方式 1：继承 Thread
class MyThread extends Thread {
    @Override
    public void run() {
        System.out.println(Thread.currentThread().getName() + " 正在运行");
    }
}

// 方式 2：实现 Runnable（推荐，因为 Java 单继承）
class MyRunnable implements Runnable {
    @Override
    public void run() {
        System.out.println(Thread.currentThread().getName() + " 正在运行");
    }
}

public class ThreadDemo {
    private static int counter = 0;

    public static void main(String[] args) throws InterruptedException {
        // 启动线程
        new MyThread().start();                    // 方式 1
        new Thread(new MyRunnable()).start();      // 方式 2
        new Thread(() -> System.out.println("Lambda 方式")).start();

        // synchronized：保证同一时刻只有一个线程访问
        Object lock = new Object();

        Runnable task = () -> {
            for (int i = 0; i < 10000; i++) {
                synchronized (lock) {   // 获取锁
                    counter++;          // 临界区
                }                       // 释放锁
            }
        };

        Thread t1 = new Thread(task);
        Thread t2 = new Thread(task);
        t1.start();
        t2.start();
        t1.join();  // 等待 t1 执行完
        t2.join();  // 等待 t2 执行完

        System.out.println("counter = " + counter);  // 20000（正确）
        // 如果没有 synchronized，结果会小于 20000（竞态条件）
    }
}
```

### 线程状态与常用方法

```
NEW → RUNNABLE → BLOCKED/WAITING/TIMED_WAITING → TERMINATED
```

| 方法 | 作用 |
|------|------|
| `start()` | 启动线程 |
| `sleep(long ms)` | 当前线程休眠，不释放锁 |
| `wait()` | 等待，释放锁（在 synchronized 内调用） |
| `notify()/notifyAll()` | 唤醒等待的线程 |
| `join()` | 等待该线程执行完毕 |
| `yield()` | 让出 CPU，从运行态回到就绪态 |

## 八、JVM 内存模型（入门）

```java
// JVM 运行时数据区（简化版）
// ┌─────────────── 线程私有 ───────────────┐
// │ 程序计数器  │ 虚拟机栈  │ 本地方法栈   │
// └────────────────────────────────────────┘
// ┌─────────────── 线程共享 ───────────────┐
// │        堆（Heap）    │   方法区        │
// └────────────────────────────────────────┘

// 堆：存放对象实例和数组，GC 的主要区域
// 虚拟机栈：每个方法执行时创建栈帧（局部变量表、操作数栈等）
// 方法区：存放类信息、常量、静态变量（JDK 8 后用元空间 Metaspace）

public class JVMDemo {
    // 静态变量在方法区
    private static final String CONSTANT = "常量";

    public static void main(String[] args) {
        // 局部变量（基本类型）在栈上
        int x = 10;

        // 对象在堆上，引用在栈上
        String str = new String("hello");  // "hello" 对象在堆，str 引用在栈

        // 字符串常量池在堆中（JDK 7+）
        String s1 = "abc";  // 从常量池取
    }
}

// GC 基础知识
// Minor GC：清理新生代（Eden + Survivor），频繁，速度快
// Major GC / Full GC：清理整个堆（包括老年代），慢，会 STW（Stop The World）

// 判断对象可回收的算法：
// 1. 引用计数法（Python 用，Java 不用，因为有循环引用问题）
// 2. 可达性分析（Java 用）：从 GC Roots 出发，不可达的对象被回收

// GC Roots 包括：虚拟机栈中引用的对象、静态变量引用的对象、常量引用的对象等
```

## 面试高频考点

| 考点 | 出现频率 | 关键要点 |
|------|----------|----------|
| `==` vs `equals()` | 极高 | == 比引用地址，equals 比内容（Object 默认 ==，String 重写了） |
| HashMap 原理 | 极高 | 数组+链表+红黑树、put 流程、扩容机制、为什么线程不安全 |
| ArrayList vs LinkedList | 高 | 底层结构、时间复杂度、使用场景 |
| String 不可变 | 高 | 为什么不可变、常量池、StringBuilder vs StringBuffer |
| 抽象类 vs 接口 | 高 | 构造器、多继承、default 方法 |
| HashSet 去重原理 | 中高 | hashCode + equals 都要重写 |
| 异常体系 | 中高 | Checked vs Unchecked、try-with-resources |
| 泛型类型擦除 | 中 | 编译后泛型信息消失、PECS 原则 |
| JVM 内存结构 | 中 | 堆、栈、方法区、GC 基础 |
| 线程创建方式 | 中 | Thread vs Runnable、start vs run |

## 相关笔记

- [[编程语言/C语言基础|C 语言基础]] — Java 与 C 的语法对比
- [[编程语言/Python基础|Python 基础]] — 面向对象概念对照
- [[编程语言/Java Web基础|Java Web 基础]] — Servlet、JSP 等后续学习
- [[工作学习/数据结构与算法/哈希表与查找|哈希表与查找]] — HashMap 的算法基础
- [[工作学习/数据库与SQL/常见业务SQL场景|常见业务 SQL 场景]] — JDBC 连接数据库查询
- [[工作学习/工程基础/Git基础与协作|Git 基础与协作]] — Java 项目的版本管理
