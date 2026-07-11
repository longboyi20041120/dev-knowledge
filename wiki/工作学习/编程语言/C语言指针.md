---
tags:
  - "#用途/工作学习"
  - "#类型/技术"
  - "#技术/c"
  - "#状态/草稿"
created: 2026-07-07
updated: 2026-07-07
status: draft
---

# C 语言指针

指针是 C 语言区分高手和入门者的分水岭。理解指针就是理解计算机内存的工作原理。

参考：《C 和指针》《深入理解 C 指针》《C语言程序设计实验与习题指导（第4版）》

## 一、为什么需要指针

先搞清楚指针解决什么问题，否则学完只会写 `int *p = &x` 但不知道什么时候该用。

| 场景       | 不用指针        | 用指针                         |
| -------- | ----------- | --------------------------- |
| 函数修改外部变量 | 做不到（C 是值传递） | `void swap(int *a, int *b)` |
| 传递大结构体   | 拷贝整个结构体，慢   | 只传 8 字节地址                   |
| 动态分配内存   | 做不到         | `malloc` 返回 `void*`         |
| 实现数据结构   | 做不到         | 链表、树、图都需要指针                 |
| 回调/多态    | 做不到         | 函数指针实现策略模式                  |

**一句话**：指针让程序拥有了"间接访问"的能力——不想传值本身时，传它的地址。

## 二、内存模型

理解指针之前，先理解内存长什么样。

```
内存地址（示意）
0x7ffd8c3a2b48 │ 00 │
0x7ffd8c3a2b49 │ 00 │
0x7ffd8c3a2b4a │ 00 │
0x7ffd8c3a2b4b │ 2A │  ← int x = 42 存在这里（小端序：0x0000002A）
0x7ffd8c3a2b4c │ 00 │
0x7ffd8c3a2b4d │ 00 │
0x7ffd8c3a2b4e │ 00 │
0x7ffd8c3a2b4f │ 00 │
```

- 每个字节有唯一地址（像门牌号）
- 变量名是给程序员看的，编译后变成地址
- 指针变量存的就是这些地址数字

## 三、指针基础

```c
#include <stdio.h>

int main() {
    int x = 42;           // 普通变量，存的是值
    int *p = &x;          // 指针变量，存的是地址

    printf("x 的值: %d\n", x);        // 42
    printf("x 的地址: %p\n", &x);     // 如 0x7ffd8c3a2b4c
    printf("p 的值: %p\n", p);        // 同上，p 存的就是 x 的地址
    printf("p 的地址: %p\n", &p);     // p 自己也在内存中，有自己的地址
    printf("p 指向的值: %d\n", *p);   // 42，解引用

    *p = 100;             // 通过指针修改 x
    printf("现在 x = %d\n", x);       // 100

    return 0;
}
```

**三个关键符号**：

| 符号 | 出现位置 | 含义 | 例子 |
|------|----------|------|------|
| `&x` | 表达式 | 取地址 | `int *p = &x;` |
| `*p` | 声明 | 声明一个指针 | `int *p;` |
| `*p` | 表达式 | 解引用（去那个地址取值） | `printf("%d", *p);` |

**常见误区**：`int* p` 和 `int *p` 完全一样，但 `int* p, q` 中 `q` 是 `int` 不是指针——所以每个指针变量前面都要写 `*`：`int *p, *q;`

## 四、指针与数组

这是面试最高频的考点。

### 4.1 基本关系

```c
int arr[] = {10, 20, 30, 40, 50};
int *p = arr;          // 数组名就是首元素地址，等价于 &arr[0]

// 指针 +1 不是加一个字节，而是加一个元素的大小
printf("*p = %d\n", *p);         // 10
printf("*(p+1) = %d\n", *(p+1)); // 20
printf("*(p+2) = %d\n", *(p+2)); // 30

// 等价写法——面试常考
printf("p[2] = %d\n", p[2]);     // 30，指针可以当下标用
printf("arr[2] = %d\n", arr[2]); // 30，完全等价

// 指针遍历数组
for (int *q = arr; q < arr + 5; q++) {
    printf("%d ", *q);           // 10 20 30 40 50
}
```

**核心等价**：`arr[i]` ⟺ `*(arr + i)` ⟺ `*(i + arr)` ⟺ `i[arr]`（最后一种只作了解，不要写）

### 4.2 指针 vs 数组——面试必问

```c
int arr[5] = {1, 2, 3, 4, 5};
int *p = arr;

// sizeof 的区别——高频考点
printf("sizeof(arr) = %zu\n", sizeof(arr));  // 20（整个数组的大小，5×4）
printf("sizeof(p)   = %zu\n", sizeof(p));    // 8（指针本身的大小，64 位系统）

// arr 是常量指针，不能修改；p 可以修改
// arr = another_array;  // 编译错误！
p = another_array;       // 正确

// &arr vs arr——进阶考点
// arr 和 &arr 的值相同（都是首元素地址），但类型不同
// arr + 1 → 跳到第二个元素
// &arr + 1 → 跳到整个数组之后（加了 20 字节）
```

| 区别 | 数组 `arr` | 指针 `p` |
|------|-----------|---------|
| `sizeof` | 整个数组的字节数 | 指针本身大小（4/8 字节） |
| `&` 操作 | `&arr` 类型是 `int(*)[5]` | `&p` 类型是 `int**` |
| 可否修改 | 否（常量） | 是 |
| 内存位置 | 栈上或数据段 | 栈上（指向别处） |

## 五、指针与函数

### 5.1 指针参数——实现"引用传递"

C 语言只有值传递，但可以通过指针实现修改外部变量：

```c
#include <stdio.h>

// 错误示范：交换不了
void swap_bad(int a, int b) {
    int temp = a;
    a = b;
    b = temp;
}

// 正确：传地址
void swap(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

int main() {
    int x = 10, y = 20;
    swap(&x, &y);
    printf("x=%d, y=%d\n", x, y);  // x=20, y=10
    return 0;
}
```

### 5.2 返回指针——堆上分配

```c
// 危险！返回局部变量的地址
int* bad() {
    int local = 42;
    return &local;  // local 在栈上，函数返回后就失效了
}

// 正确：返回堆上分配的内存（调用者负责 free）
int* good() {
    int *p = (int*)malloc(sizeof(int));
    if (p == NULL) return NULL;
    *p = 42;
    return p;
}
```

### 5.3 函数指针

函数指针是 C 语言实现回调、策略模式、多态的基础。

```c
#include <stdio.h>

// 算数操作
int add(int a, int b) { return a + b; }
int sub(int a, int b) { return a - b; }
int mul(int a, int b) { return a * b; }

// 通用操作函数：接收函数指针
int operate(int x, int y, int (*func)(int, int)) {
    return func(x, y);
}

// typedef 让函数指针可读
typedef int (*BinaryOp)(int, int);

int main() {
    // 声明：返回类型 (*指针名)(参数类型列表)
    int (*fp)(int, int);

    fp = add;                        // 函数名本身就是地址，& 可省略
    printf("add(3,5) = %d\n", fp(3, 5));     // 8
    printf("add(3,5) = %d\n", (*fp)(3, 5));  // 8，两种调用等价

    // 同一个接口，不同行为——策略模式
    printf("operate(10,5,add) = %d\n", operate(10, 5, add));  // 15
    printf("operate(10,5,sub) = %d\n", operate(10, 5, sub));  // 5
    printf("operate(10,5,mul) = %d\n", operate(10, 5, mul));  // 50

    // 用 typedef 后更清晰
    BinaryOp ops[] = {add, sub, mul};
    for (int i = 0; i < 3; i++) {
        printf("ops[%d](10,5) = %d\n", i, ops[i](10, 5));
    }
    return 0;
}
```

**函数指针应用场景**：
- `qsort` 的比较函数 → `int (*cmp)(const void*, const void*)`
- 信号处理 → `signal(SIGINT, handler)`
- 状态机回调 → 状态切换时调用不同的处理函数

**面试话术**："函数指针让 C 语言也能实现面向对象的多态——同一个接口对不同数据类型或不同算法表现出不同行为。Linux 内核的 VFS（虚拟文件系统）就是通过函数指针表实现不同文件系统的统一接口。"

### 5.4 `void*` 泛型指针

```c
#include <stdio.h>
#include <stdlib.h>

// void* 可以指向任何类型，但解引用前必须强转
int main() {
    int x = 42;
    double y = 3.14;

    void *vp;

    vp = &x;
    printf("%d\n", *(int*)vp);      // 42，先强转再解引用

    vp = &y;
    printf("%.2f\n", *(double*)vp); // 3.14

    // malloc 返回 void* 就是这个原因——不知道你会存什么
    int *arr = (int*)malloc(10 * sizeof(int));

    // void* 不能做算术运算
    // vp++;  // 编译错误！不知道加多少

    return 0;
}
```

## 六、多级指针

```c
int x = 10;
int *p1 = &x;      // 一级指针 → int
int **p2 = &p1;    // 二级指针 → int*
int ***p3 = &p2;   // 三级指针 → int**

printf("x   = %d\n", x);     // 10
printf("*p1 = %d\n", *p1);   // 10
printf("**p2 = %d\n", **p2);  // 10
printf("***p3 = %d\n", ***p3); // 10
```

**实际使用场景**：

```c
// 1. 函数内部分配内存，需要修改调用者的指针
void create_array(int **arr, int size) {
    *arr = (int*)malloc(size * sizeof(int));
    // *arr 就是调用者的指针变量本身
}

int main() {
    int *data = NULL;
    create_array(&data, 10);  // 传一级指针的地址 → 二级指针
    data[0] = 42;
    free(data);
    return 0;
}

// 2. 动态二维数组
int **matrix = (int**)malloc(rows * sizeof(int*));
for (int i = 0; i < rows; i++) {
    matrix[i] = (int*)malloc(cols * sizeof(int));
}
matrix[2][3] = 100;

// 3. 链表删除头节点
void delete_head(Node **head) {
    if (*head == NULL) return;
    Node *temp = *head;
    *head = (*head)->next;
    free(temp);
}
```

## 七、野指针、空指针、悬空指针

```c
// 1. 野指针（Wild Pointer）—— 未初始化
int *wild;
// *wild = 10;  // 未定义行为！可能崩溃、可能破坏数据

// 解决方法：初始化为 NULL
int *safe = NULL;

// 2. 悬空指针（Dangling Pointer）—— 指向已释放的内存
int *dangling = (int*)malloc(sizeof(int));
*dangling = 42;
free(dangling);
// dangling 现在指向已释放的内存——危险！
// *dangling = 100;  // use-after-free

// 解决方法：free 后置 NULL
free(dangling);
dangling = NULL;

// 3. 返回局部变量的地址（特殊的悬空指针）
int* bad_return() {
    int local = 42;
    return &local;  // 返回后栈帧销毁，指针悬空
}
```

| 类型 | 成因 | 后果 | 预防 |
|------|------|------|------|
| 野指针 | 声明后未初始化 | 指向随机地址 | 初始化为 `NULL` |
| 空指针 | 主动设为 `NULL` | 解引用 → segfault | 使用前 `if (ptr != NULL)` |
| 悬空指针 | free 后未置 NULL | 可能破坏新分配的数据 | `free` 后立刻置 `NULL` |

## 八、const 与指针

这是一道经典面试题。关键是看 `const` 在 `*` 的哪一侧。

```c
int x = 10, y = 20;

// 1. 指向常量的指针——不能通过 p1 修改值
const int *p1 = &x;
// *p1 = 30;  // 编译错误
p1 = &y;      // 合法，p1 本身可以指向别处

// 2. 常量指针——p2 永远指向 x
int * const p2 = &x;
*p2 = 30;     // 合法，可以修改指向的值
// p2 = &y;   // 编译错误，不能改指向

// 3. 指向常量的常量指针——什么都不让改
const int * const p3 = &x;
// *p3 = 30;  // 编译错误
// p3 = &y;   // 编译错误

// 4. const int * 和 int const * 完全一样
const int *a;
int const *a;  // 等价
```

**面试口诀**：`const` 在 `*` 左边 → 指向的值不能改；`const` 在 `*` 右边 → 指针本身不能改。两边都有 → 都不能改。

## 九、指针与结构体

```c
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    char name[32];
    int age;
    double salary;
} Employee;

// 值传递：拷贝整个结构体（几十字节），慢
void print(Employee e) {
    printf("%s, %d, %.2f\n", e.name, e.age, e.salary);
}

// 指针传递：只传 8 字节，快
void raise(Employee *e, double pct) {
    e->salary *= (1 + pct);  // -> 是 (*e).salary 的简写
}

int main() {
    Employee *emp = (Employee*)malloc(sizeof(Employee));
    // emp 是指针，用 -> 访问成员
    emp->age = 30;
    strcpy(emp->name, "张三");
    emp->salary = 15000.0;

    raise(emp, 0.1);
    printf("涨薪后: %.2f\n", emp->salary);  // 16500.00

    free(emp);
    return 0;
}
```

**`.` vs `->`**：`obj.member` 用于变量本身；`ptr->member` 用于指针，等价于 `(*ptr).member`。

## 十、指针运算进阶

### 10.1 算术运算

```c
int arr[] = {10, 20, 30, 40, 50};
int *p = arr;

p++;       // p 移动到下一个 int（地址值 +4）
p--;       // 移回
p += 2;    // 前进 2 个 int（地址值 +8）

// 两个指针相减：得到元素个数（不是字节数）
int *start = arr;
int *end = arr + 5;
printf("元素个数: %td\n", end - start);   // 5

// 指针比较
while (p < end) {
    printf("%d ", *p++);  // *p++：先取 *p，再 p++
}
```

### 10.2 指针数组 vs 数组指针

这是面试易混淆点：

```c
// 指针数组：数组里装的是指针
int *ptr_arr[5];    // 5 个 int* 的数组
// 每个元素是一个 int* 指针

// 数组指针：指向一个数组的指针
int (*arr_ptr)[5];  // 指向 int[5] 的指针
// 只有一个指针，它指向整个数组

// 例子
int data[5] = {1, 2, 3, 4, 5};
int (*arr_ptr)[5] = &data;
printf("%d\n", (*arr_ptr)[2]);  // 3，先解引用拿到数组，再取下标
```

## 面试高频考点

| 考点 | 频率 | 关键要点 |
|------|------|----------|
| 指针与数组的区别 | ★★★★★ | sizeof 结果不同、数组名是常量 |
| `const` 在指针中的位置 | ★★★★★ | 口诀：const 在 * 左边/右边 |
| 野指针 vs 悬空指针 | ★★★★ | 野指针未初始化，悬空指针指向已释放 |
| 函数指针 | ★★★★ | 语法、用作回调、`qsort` 示例 |
| 指针数组 vs 数组指针 | ★★★★ | `int *p[5]` vs `int (*p)[5]` |
| `void*` 用法 | ★★★ | `malloc` 返回、`qsort`、不能做算术 |
| 二级指针使用场景 | ★★★ | 函数内修改指针、动态二维数组 |
| `->` vs `.` | ★★ | 指针用 `->`，变量用 `.` |

## 常见笔试题

### 题 1：写出输出

```c
int arr[] = {1, 2, 3, 4, 5};
int *p = arr;
printf("%d\n", *p++);      // ?
printf("%d\n", *++p);      // ?
printf("%d\n", (*p)++);    // ?
```

**答案**：`*p++` 输出 1（先取 `*p`，再 `p++`），p 现在指向 arr[2]；`*++p` 输出 3（先 `++p`，再取 `*p`）；`(*p)++` 输出 3（取 `*p`，然后把那个值 +1，arr[2] 变成 4）。

### 题 2：判断对错

```c
int x = 10;
const int *p1 = &x;
int * const p2 = &x;

*p1 = 20;   // (1) 对 or 错？
p1 = &y;    // (2) 对 or 错？
*p2 = 30;   // (3) 对 or 错？
p2 = &y;    // (4) 对 or 错？
```

**答案**：(1) 错，const 在 `*` 左边；(2) 对，p1 本身不是 const；(3) 对，p2 指向的值可变；(4) 错，p2 是常量指针。

### 题 3：写出输出

```c
char str[] = "hello";
char *p = str;
printf("%c\n", *(p + 1));   // ?
printf("%c\n", p[1]);        // ?
printf("%lu\n", sizeof(p));  // ?
printf("%lu\n", sizeof(str));// ?
```

**答案**：`e`, `e`, `8`（64 位系统）, `6`（5 字符 + `\0`）。

## 相关笔记

- [[工作学习/编程语言/C语言基础|C 语言基础]] — 内存管理、结构体、static/extern/const 完整用法
- [[工作学习/数据结构与算法/数组与双指针|数组与双指针]] — 算法中的"指针"思想（双指针、快慢指针、滑动窗口）
- [[工作学习/计算机基础/操作系统|操作系统]] — 虚拟内存、分页、inode 中的指针
- [[工作学习/编程语言/Java基础|Java 基础]] — Java 没有指针但有引用，对比学习
