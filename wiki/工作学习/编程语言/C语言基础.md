---
tags:
  - "#用途/工作学习"
  - "#类型/技术"
  - "#技术/c"
  - "#状态/草稿"
created: 2026-07-02
updated: 2026-07-02
status: draft
---

# C语言基础

C 语言是大多数现代语言的"祖先"。学好 C，再学 C++/Java/Python 都能看到它的影子。面试中 C 语言问题集中在**指针**和**内存管理**。

参考：《C语言项目开发实战入门》《C语言程序设计实验与习题指导（第4版）》

## 一、C 语言特点与编译过程

### C 语言的定位

| 特性 | 说明 |
|------|------|
| 设计哲学 | 信任程序员，给你最大控制权 |
| 类型系统 | 静态弱类型（编译时检查类型，但允许隐式转换） |
| 内存管理 | 手动管理（malloc/free），没有 GC |
| 执行方式 | 编译型，直接生成机器码 |
| 典型用途 | 操作系统、嵌入式、高性能计算、数据库引擎 |

### 编译四阶段

```
源代码(.c) → 预处理 → 编译 → 汇编 → 链接 → 可执行文件(.exe)
```

```c
// 以一个简单程序为例，追踪编译过程

// hello.c
#include <stdio.h>
#define PI 3.14159

int main() {
    printf("PI = %f\n", PI);   // PI 会在预处理阶段被替换为 3.14159
    return 0;
}
```

| 阶段 | 做的事情 | 输出文件 | 命令（GCC） |
|------|----------|----------|-------------|
| **预处理** | 展开 `#include`、`#define`、去掉注释 | `.i` 文件 | `gcc -E hello.c -o hello.i` |
| **编译** | 将预处理后的代码翻译成汇编语言 | `.s` 文件 | `gcc -S hello.i -o hello.s` |
| **汇编** | 将汇编代码翻译成机器码（目标文件） | `.o` 文件 | `gcc -c hello.s -o hello.o` |
| **链接** | 将多个 `.o` 文件和库文件合并为可执行文件 | `.exe`/无后缀 | `gcc hello.o -o hello` |

**面试话术**："C 语言的编译分为预处理、编译、汇编、链接四个阶段。预处理主要处理宏定义和头文件包含，编译阶段做词法语法分析和优化，汇编生成目标机器的二进制代码，链接负责解析外部符号引用，把多个目标文件和库合并成最终的可执行文件。"

## 二、基本数据类型

### 整型家族

```c
#include <stdio.h>
#include <limits.h>

int main() {
    // 有符号整型
    short s = 32767;           // 通常 2 字节，范围 -32768 ~ 32767
    int i = 2147483647;        // 通常 4 字节，范围 -2^31 ~ 2^31-1
    long l = 9223372036854775807L;  // 通常 8 字节（64 位系统）
    long long ll = 9223372036854775807LL;

    // 无符号整型——没有负数，范围翻倍
    unsigned int ui = 4294967295U;  // 0 ~ 2^32-1

    printf("int 范围: %d ~ %d\n", INT_MIN, INT_MAX);
    printf("unsigned int 范围: 0 ~ %u\n", UINT_MAX);

    // 不同类型的大小（字节数，因平台而异）
    printf("short: %zu, int: %zu, long: %zu, long long: %zu\n",
           sizeof(short), sizeof(int), sizeof(long), sizeof(long long));
    return 0;
}
```

常见平台下各类型大小：

| 类型 | 32 位系统 | 64 位系统 | printf 格式 |
|------|-----------|-----------|-------------|
| `char` | 1 字节 | 1 字节 | `%c` |
| `short` | 2 字节 | 2 字节 | `%hd` |
| `int` | 4 字节 | 4 字节 | `%d` |
| `long` | 4 字节 | 8 字节（Linux）/ 4 字节（Windows） | `%ld` |
| `long long` | 8 字节 | 8 字节 | `%lld` |
| `float` | 4 字节 | 4 字节 | `%f` |
| `double` | 8 字节 | 8 字节 | `%lf` |
| 指针 | 4 字节 | 8 字节 | `%p` |

**面试易错点**：`unsigned int` 和 `int` 比较时会发生隐式类型转换，`-1 > 1U` 竟然是 true——因为 -1 会被转换为一个巨大的无符号数。

```c
int a = -1;
unsigned int b = 1;
if (a > b) {
    printf("-1 > 1 ？？\n");  // 这行会打印！因为 a 被隐式转为 unsigned
}
// 输出：-1 > 1 ？？
```

## 三、指针（核心中的核心）

指针是 C 语言区分高手和入门者的分水岭。理解指针就是理解计算机内存的工作原理。

### 3.1 指针基础

```c
#include <stdio.h>

int main() {
    int x = 42;           // 普通变量，存的是值
    int *p = &x;          // 指针变量，存的是地址

    printf("x 的值: %d\n", x);        // 42
    printf("x 的地址: %p\n", &x);     // 如 0x7ffd8c3a2b4c
    printf("p 的值: %p\n", p);        // 同上，p 存的就是 x 的地址
    printf("p 指向的值: %d\n", *p);   // 42，解引用

    *p = 100;             // 通过指针修改 x
    printf("现在 x = %d\n", x);       // 100

    return 0;
}
```

**记忆口诀**：`&` 是"取地址"，`*` 在声明时表示"这是一个指针"，在使用时表示"解引用（去那个地址取值）"。

### 3.2 指针运算

```c
#include <stdio.h>

int main() {
    int arr[] = {10, 20, 30, 40, 50};
    int *p = arr;          // 数组名就是首元素地址，等价于 &arr[0]

    // 指针 +1 不是加一个字节，而是加一个元素的大小
    printf("*p = %d\n", *p);         // 10
    printf("*(p+1) = %d\n", *(p+1)); // 20
    printf("*(p+2) = %d\n", *(p+2)); // 30

    // 等价写法
    printf("p[2] = %d\n", p[2]);     // 30，指针可以当下标用
    printf("arr[2] = %d\n", arr[2]); // 30，完全等价

    // 指针遍历数组
    for (int *q = arr; q < arr + 5; q++) {
        printf("%d ", *q);           // 10 20 30 40 50
    }
    printf("\n");

    return 0;
}
```

**关键理解**：`arr[i]` 本质上就是 `*(arr + i)`。编译器把 `arr[i]` 翻译成 `*(arr + i)`。

### 3.3 指针与数组的区别

```c
int arr[5] = {1, 2, 3, 4, 5};
int *p = arr;

// sizeof 的区别——面试高频考点！
printf("sizeof(arr) = %zu\n", sizeof(arr));  // 20（整个数组的大小，5*4）
printf("sizeof(p)   = %zu\n", sizeof(p));    // 8（指针本身的大小，64位系统）

// arr 是常量指针，不能修改；p 可以修改
// arr = another_array;  // 编译错误！
p = another_array;       // 正确
```

### 3.4 函数指针

```c
#include <stdio.h>

// 定义一个函数
int add(int a, int b) { return a + b; }
int sub(int a, int b) { return a - b; }

// 接收函数指针作为参数——用回调函数实现多态
int operate(int x, int y, int (*func)(int, int)) {
    return func(x, y);
}

int main() {
    // 声明函数指针：返回类型 (*指针名)(参数类型列表)
    int (*fp)(int, int);

    fp = add;                        // 函数名本身就是地址，不需要 &
    printf("add(3, 5) = %d\n", fp(3, 5));   // 8
    printf("add(3, 5) = %d\n", (*fp)(3, 5)); // 8，两种写法等价

    // 传入不同函数，实现不同行为
    printf("operate(10,5,add) = %d\n", operate(10, 5, add));  // 15
    printf("operate(10,5,sub) = %d\n", operate(10, 5, sub));  // 5

    return 0;
}
```

### 3.5 多级指针

```c
int x = 10;
int *p1 = &x;      // 一级指针，指向 int
int **p2 = &p1;     // 二级指针，指向 int*
int ***p3 = &p2;    // 三级指针，指向 int**

printf("%d\n", ***p3);  // 10，层层解引用
printf("%d\n", *p1);    // 10
```

**什么时候用多级指针**：函数需要修改指针本身（如动态分配内存并返回）、二维数组的动态分配、链表操作中的头指针修改。

### 3.6 野指针与空指针

```c
// 危险！野指针——指向未知内存
int *wild;
// *wild = 10;  // 未定义行为，可能崩溃

// 正确做法：初始化为 NULL
int *safe = NULL;

// 使用前检查
if (safe != NULL) {
    *safe = 10;
}

// free 后置 NULL，避免悬空指针
int *ptr = (int*)malloc(sizeof(int));
free(ptr);
ptr = NULL;  // 好习惯，防止重复 free 或误用
```

## 四、内存管理

### 4.1 栈 vs 堆

| 维度 | 栈（Stack） | 堆（Heap） |
|------|-----------|----------|
| 分配方式 | 编译器自动分配释放 | 程序员手动 malloc/free |
| 大小 | 较小（默认几 MB） | 较大（受系统内存限制） |
| 生命周期 | 出了作用域自动销毁 | 手动 free 才释放 |
| 访问速度 | 快（CPU 寄存器直接参与） | 慢（要通过指针间接访问） |
| 典型用途 | 局部变量、函数参数 | 动态数组、链表节点 |

```c
#include <stdio.h>
#include <stdlib.h>

// 栈上分配——函数返回后自动释放
void stack_example() {
    int arr[100];         // 栈上分配，函数结束自动释放
    arr[0] = 42;
    // 返回后 arr 就不存在了
}

// 堆上分配——需要手动释放
void heap_example() {
    int *arr = (int*)malloc(100 * sizeof(int));
    if (arr == NULL) {
        printf("内存分配失败！\n");
        return;                          // 分配失败时不应该继续
    }
    arr[0] = 42;
    // ... 使用 arr ...
    free(arr);                           // 必须手动释放
    arr = NULL;                          // 好习惯
}

// 常见错误：返回局部变量的地址
int* bad_function() {
    int local = 42;
    return &local;  // 危险！local 在栈上，函数返回后就失效了
}

// 正确做法：返回堆上分配的内存（调用者负责 free）
int* good_function() {
    int *p = (int*)malloc(sizeof(int));
    *p = 42;
    return p;       // 调用者用完要 free
}
```

### 4.2 malloc / calloc / realloc / free

```c
#include <stdio.h>
#include <stdlib.h>

int main() {
    // malloc：分配但不初始化（值随机）
    int *a = (int*)malloc(5 * sizeof(int));

    // calloc：分配并初始化为 0 （参数是"元素个数, 每个大小"）
    int *b = (int*)calloc(5, sizeof(int));

    // realloc：调整已分配内存的大小
    int *c = (int*)realloc(a, 10 * sizeof(int));  // 扩展到 10 个 int
    if (c != NULL) {
        a = c;  // realloc 可能返回新地址，原地址失效
    }

    // 记得全部释放
    free(a);
    free(b);
    // a 和 c 指向同一块内存，只需 free 一次
    return 0;
}
```

### 4.3 常见内存错误

```c
// 错误 1：忘记 free —— 内存泄漏
void leak() {
    int *p = malloc(1024);  // 分配了内存但从不释放
    // 函数返回后指针 p 丢失，但内存仍被占用
}

// 错误 2：重复 free —— 未定义行为
int *p = malloc(100);
free(p);
free(p);  // 崩溃或莫名错误

// 错误 3：使用已释放的内存（use-after-free）
int *p = malloc(100);
free(p);
*p = 42;  // 危险！可能写到已被别人使用的内存

// 错误 4：越界访问
int *arr = malloc(5 * sizeof(int));
arr[100] = 42;  // 写到分配范围外，可能破坏其他数据或崩溃
```

## 五、结构体与共用体

### 结构体

```c
#include <stdio.h>
#include <string.h>

// 定义结构体类型
typedef struct {
    char name[32];
    int age;
    double salary;
} Employee;

// 结构体可以作为函数参数和返回值
void print_employee(Employee e) {
    printf("姓名: %s, 年龄: %d, 薪资: %.2f\n", e.name, e.age, e.salary);
}

// 用指针传递，避免拷贝整个结构体（效率更高）
void raise_salary(Employee *e, double pct) {
    e->salary *= (1 + pct);  // -> 是 (*e).salary 的简写
}

int main() {
    // 初始化
    Employee emp = {"张三", 28, 15000.0};
    Employee emp2 = {.name = "李四", .salary = 20000.0};  // 指定初始化器（C99）

    print_employee(emp);
    raise_salary(&emp, 0.1);               // 涨薪 10%
    printf("涨薪后: %.2f\n", emp.salary);   // 16500.00

    // 结构体数组
    Employee team[3] = {
        {"Alice", 25, 12000},
        {"Bob",   30, 18000},
        {"Carol", 27, 15000}
    };

    return 0;
}
```

### 内存对齐——面试考点

```c
#include <stdio.h>

// 不同排列顺序导致不同大小
typedef struct {
    char c;    // 1 字节
    int  i;    // 4 字节
    char d;    // 1 字节
} BadLayout;   // 实际占 12 字节（补齐到了 4 的倍数）

typedef struct {
    char c;    // 1 字节
    char d;    // 1 字节
    int  i;    // 4 字节
} GoodLayout;  // 实际占 8 字节

int main() {
    printf("BadLayout:  %zu 字节\n", sizeof(BadLayout));   // 12
    printf("GoodLayout: %zu 字节\n", sizeof(GoodLayout));  // 8
    return 0;
}
```

**面试话术**："结构体成员是按声明顺序在内存中排列的，编译器会根据对齐规则在成员之间插入填充字节。把占用空间大的成员放在前面，小成员放后面，可以减少总大小。"

### 共用体（union）

```c
#include <stdio.h>

// union 所有成员共享同一块内存
typedef union {
    int i;
    float f;
    char c[4];
} Data;

int main() {
    Data d;
    d.i = 0x41424344;  // ASCII: ABCD

    printf("d.i = 0x%08X\n", d.i);     // 0x41424344
    printf("d.c[0] = %c\n", d.c[0]);   // 'D'（小端序）
    printf("d.c[1] = %c\n", d.c[1]);   // 'C'
    printf("sizeof(Data) = %zu\n", sizeof(Data));  // 4，按最大成员

    return 0;
}
```

## 六、文件操作

```c
#include <stdio.h>
#include <stdlib.h>

int main() {
    FILE *fp;

    // ===== 写入文件 =====
    fp = fopen("test.txt", "w");   // "w" 写模式（覆盖已有内容）
    if (fp == NULL) {
        perror("打开文件失败");     // perror 打印系统错误信息
        return 1;
    }
    fprintf(fp, "Hello, 文件操作！\n");
    fprintf(fp, "整数: %d, 浮点数: %.2f\n", 42, 3.14);
    fclose(fp);

    // ===== 读取文件 =====
    fp = fopen("test.txt", "r");   // "r" 读模式
    if (fp == NULL) {
        perror("打开文件失败");
        return 1;
    }
    char line[256];
    while (fgets(line, sizeof(line), fp) != NULL) {
        printf("%s", line);   // 逐行读取
    }
    fclose(fp);

    // ===== 二进制读写 =====
    int data[] = {1, 2, 3, 4, 5};
    fp = fopen("data.bin", "wb");       // "wb" 二进制写
    fwrite(data, sizeof(int), 5, fp);   // 一次写入 5 个 int
    fclose(fp);

    int read_back[5];
    fp = fopen("data.bin", "rb");       // "rb" 二进制读
    fread(read_back, sizeof(int), 5, fp);
    fclose(fp);

    for (int i = 0; i < 5; i++) {
        printf("%d ", read_back[i]);    // 1 2 3 4 5
    }
    printf("\n");

    return 0;
}
```

| 模式 | 含义 | 文件不存在 | 文件存在 |
|------|------|-----------|---------|
| `"r"` | 只读 | 返回 NULL | 从头读 |
| `"w"` | 只写 | 创建新文件 | 清空后从头写 |
| `"a"` | 追加写 | 创建新文件 | 在末尾追加 |
| `"r+"` | 读写 | 返回 NULL | 从头读写 |
| `"w+"` | 读写 | 创建新文件 | 清空后从头读写 |
| `"a+"` | 读写（追加） | 创建新文件 | 读从头，写在末尾 |

加 `b` 表示二进制模式，如 `"rb"`、`"wb"`。Windows 下文本模式会自动转换换行符。

## 七、预处理指令

### 宏定义

```c
#include <stdio.h>

// 1. 简单宏——纯文本替换
#define PI 3.14159
#define MAX_SIZE 1024

// 2. 带参数的宏——注意括号陷阱！
#define SQUARE(x) ((x) * (x))          // 正确：每个参数和整体都加括号
#define SQUARE_BAD(x) x * x            // 错误：SQUARE_BAD(1+2) → 1+2*1+2 = 5

// 3. 多行宏——用 do-while(0) 包装
#define SWAP(a, b) do { \
    typeof(a) temp = (a); \
    (a) = (b); \
    (b) = temp; \
} while(0)

int main() {
    printf("PI = %.5f\n", PI);
    printf("SQUARE(5) = %d\n", SQUARE(5));     // 25
    printf("SQUARE(1+2) = %d\n", SQUARE(1+2)); // 9，正确
    printf("SQUARE_BAD(1+2) = %d\n", SQUARE_BAD(1+2)); // 5，错误！

    int x = 10, y = 20;
    SWAP(x, y);
    printf("交换后: x=%d, y=%d\n", x, y);      // x=20, y=10

    return 0;
}
```

### 条件编译

```c
#include <stdio.h>

#define DEBUG       // 注释掉这行，调试代码就不会编译进去
#define VERSION 2

int main() {
    // 方法 1：#ifdef / #ifndef
#ifdef DEBUG
    printf("[DEBUG] 程序开始运行\n");
#endif

    // 方法 2：#if / #elif / #else
#if VERSION == 1
    printf("版本 1：基础功能\n");
#elif VERSION == 2
    printf("版本 2：高级功能\n");
#else
    printf("未知版本\n");
#endif

    // 方法 3：防止头文件重复包含（写在 .h 文件中）
    // #ifndef MY_HEADER_H
    // #define MY_HEADER_H
    // ... 头文件内容 ...
    // #endif

    return 0;
}
```

### 常用预定义宏

```c
printf("文件名: %s\n", __FILE__);
printf("行号: %d\n", __LINE__);
printf("日期: %s\n", __DATE__);
printf("时间: %s\n", __TIME__);
// C99 及以上:
printf("函数名: %s\n", __func__);
```

## 八、static / extern / const

这是面试高频考点，三者常被放在一起问。

```c
// ===== static =====
// 1. static 局部变量：生命周期是整个程序运行期，但作用域不变
void counter() {
    static int count = 0;  // 只初始化一次
    count++;
    printf("调用次数: %d\n", count);
}
// 每次调用 counter()，count 保留上次的值

// 2. static 全局变量/函数：只在当前 .c 文件内可见（内部链接）
static int internal_var = 42;    // 其他 .c 文件访问不到
static void helper() { /* ... */ }  // 其他 .c 文件调用不了

// ===== extern =====
// 声明一个在其他 .c 文件中定义的变量或函数
extern int global_from_another_file;  // 告诉编译器"这个变量在别处定义"
extern void func_from_another_file();

// ===== const =====
const int MAX = 100;          // 值不可修改
const int *p1;                 // 指向常量的指针——不能通过 p1 修改值
int * const p2 = &some_int;   // 常量指针——p2 不能指向别处
const int * const p3 = &x;    // 两者都是常量

// 面试口诀：const 在 * 左边，指向的值不能改；const 在 * 右边，指针本身不能改。
```

| 关键字 | 作用 | 面试常问 |
|--------|------|----------|
| `static` 局部变量 | 延长生命周期，保持值 | "static 局部变量和全局变量的区别？" |
| `static` 全局函数 | 限制可见性（文件作用域） | "为什么要用 static 修饰函数？" |
| `extern` | 跨文件引用 | "extern 和 include 的区别？" |
| `const` | 只读修饰 | "const 在指针声明中的位置含义？" |

## 面试高频考点

| 考点 | 出现频率 | 关键要点 |
|------|----------|----------|
| 指针与数组的区别 | 极高 | sizeof 结果不同、数组名是常量 |
| malloc vs calloc | 高 | calloc 会清零，参数格式不同 |
| 栈 vs 堆 | 高 | 分配方式、生命周期、大小 |
| static 的作用 | 高 | 三种用法：局部变量、全局变量、函数 |
| 内存泄漏 | 高 | 成因、如何检测（Valgrind） |
| 野指针 vs 悬空指针 | 中高 | 野指针未初始化，悬空指针指向已释放 |
| 结构体内存对齐 | 中 | 为什么会补齐、如何优化 |
| 编译四阶段 | 中 | 每个阶段的输入输出 |
| 函数指针 | 中 | 语法、用作回调 |
| 大小端 | 中 | 多字节数据在内存中的排列方式 |

## 相关笔记

- [[工作学习/数据结构与算法/数组与双指针|数组与双指针]] — 算法中大量用到指针思想
- [[工作学习/数据结构与算法/哈希表与查找|哈希表与查找]] — C 语言中可以用结构体+链表实现
- [[工作学习/工程基础/Git基础与协作|Git 基础与协作]] — 管理 C 语言项目
- [[编程语言/Java基础|Java 基础]] — Java 没有指针但有引用，对比学习
- [[编程语言/Python基础|Python 基础]] — Python 底层是 C 写的，CPython 解释器
