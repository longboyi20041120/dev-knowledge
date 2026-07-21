---
tags:
  - "#用途/工作学习"
  - "#类型/技术"
  - "#技术/java"
  - "#技术/web"
  - "#状态/已验证"
created: 2026-07-02
updated: 2026-07-15
status: reviewed
---

# Java Web 基础

> HTTP、Servlet、MVC、Cookie/Session、JDBC — 后端面试必问。 | **面试重要度：高** | 预计阅读：20 分钟

## 视频资源

- B站: [黑马程序员 Java Web 教程](https://www.bilibili.com/video/BV1Qf4y1T7Hx/) — Java Web 最全中文教程
- B站: [尚硅谷 Servlet 详解](https://www.bilibili.com/video/BV1yJ411c7wq/) — Servlet 和 HTTP 协议精讲

参考：《Java Web程序设计任务教程》

## 一、HTTP 协议基础

HTTP 是 Web 开发的通用语言，无论用 Java、Python 还是 Node.js，都要理解它。

### 请求与响应结构

```
客户端（浏览器）                          服务端（Tomcat）
     │                                        │
     │  ──── HTTP 请求（Request） ────→       │
     │  请求行：GET /api/users HTTP/1.1        │
     │  请求头：Host, User-Agent, Cookie...    │
     │  请求体：{"name":"张三"} (POST/PUT)     │
     │                                        │
     │  ←──── HTTP 响应（Response） ────      │
     │  状态行：HTTP/1.1 200 OK               │
     │  响应头：Content-Type, Set-Cookie...    │
     │  响应体：{"id":1,"name":"张三"}         │
```

### HTTP 方法

| 方法 | 语义 | 幂等性 | 请求体 | 典型场景 |
|------|------|--------|--------|----------|
| GET | 获取资源 | 是 | 无 | 查询用户列表、查看文章 |
| POST | 创建资源 | 否 | 有 | 注册用户、提交订单 |
| PUT | 全量更新 | 是 | 有 | 修改用户全部信息 |
| DELETE | 删除资源 | 是 | 通常无 | 删除文章 |
| PATCH | 部分更新 | 否 | 有 | 只修改用户昵称 |

**面试话术**："GET 和 POST 的核心区别：GET 是获取数据，参数在 URL 中，有长度限制，会被浏览器缓存和保存到历史记录，幂等；POST 是提交数据，参数在请求体中，没有长度限制，不会被缓存，不幂等。从安全性角度，POST 比 GET 稍好，但都不是真正的安全——需要 HTTPS。"

### 常见状态码

```java
// 2xx：成功
200 OK              // 请求成功
201 Created         // 创建成功（POST 后返回）
204 No Content      // 成功但无返回内容（DELETE 后返回）

// 3xx：重定向
301 Moved Permanently  // 永久重定向（域名迁移）
302 Found               // 临时重定向（登录后跳转）
304 Not Modified        // 资源未修改，使用缓存

// 4xx：客户端错误
400 Bad Request         // 请求参数有误
401 Unauthorized        // 未认证（没登录）
403 Forbidden           // 已认证但无权限（权限不足）
404 Not Found           // 资源不存在
405 Method Not Allowed  // 方法不允许（如用 GET 访问 POST 接口）

// 5xx：服务端错误
500 Internal Server Error  // 服务器内部错误（代码抛异常）
502 Bad Gateway            // 网关错误（上游服务挂了）
503 Service Unavailable    // 服务暂时不可用（过载维护）
```

## 二、Servlet 生命周期

Servlet 是 Java Web 的核心组件，运行在 Servlet 容器（如 Tomcat）中。

```java
import javax.servlet.*;
import javax.servlet.http.*;
import javax.servlet.annotation.*;
import java.io.*;

// @WebServlet 注解配置 URL 映射（替代 web.xml 配置）
@WebServlet("/hello")
public class HelloServlet extends HttpServlet {

    // 1. 初始化：Servlet 第一次被访问时调用，只调用一次
    @Override
    public void init() throws ServletException {
        System.out.println("HelloServlet 初始化完成");
        // 适合做：加载配置、初始化数据库连接池
    }

    // 2. 处理 GET 请求
    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        // 设置响应内容类型和编码
        resp.setContentType("text/html;charset=UTF-8");

        // 获取请求参数
        String name = req.getParameter("name");  // URL 中的 ?name=张三
        if (name == null) name = "世界";

        // 输出响应
        PrintWriter out = resp.getWriter();
        out.println("<html><body>");
        out.println("<h1>你好，" + name + "！</h1>");
        out.println("</body></html>");
    }

    // 3. 处理 POST 请求
    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        // POST 请求中文乱码解决——必须在获取参数之前设置
        req.setCharacterEncoding("UTF-8");
        resp.setContentType("text/html;charset=UTF-8");

        String username = req.getParameter("username");
        String password = req.getParameter("password");

        PrintWriter out = resp.getWriter();
        out.println("登录用户: " + username);
    }

    // 4. 销毁：服务器关闭或应用卸载时调用，只调用一次
    @Override
    public void destroy() {
        System.out.println("HelloServlet 被销毁");
        // 适合做：释放资源、关闭连接
    }
}
```

### Servlet 生命周期图解

```
                    ┌─ init() ─┐
                    │  只调用1次  │
                    ▼            │
客户端请求 → 容器加载Servlet → 初始化
                    │
                    ▼
              ┌ service() ──────┐
              │ 每次请求都调用    │
              │ 根据请求方法分发   │
              │ doGet/doPost... │←── 多次调用
              └─────────────────┘
                    │
                    ▼ (服务器关闭时)
              ┌ destroy() ──────┐
              │ 只调用1次         │
              └─────────────────┘
```

**面试话术**："Servlet 生命周期分为三个阶段：初始化 init()、服务 service()、销毁 destroy()。init 在首次访问时调用一次，service 每次请求都调用并根据 HTTP 方法分发到 doGet/doPost 等方法，destroy 在容器关闭时调用一次做资源释放。"

## 三、JSP 基础

JSP（Java Server Pages）本质是一个 Servlet，Tomcat 会把 JSP 翻译成 Servlet 再编译执行。

```jsp
<%-- page.jsp --%>
<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ page import="java.util.*, java.text.*" %>  <%-- 导入包 --%>

<!DOCTYPE html>
<html>
<head>
    <title>JSP 示例</title>
</head>
<body>
    <%-- 1. 脚本段：写 Java 代码 --%>
    <%
        String username = "张三";
        Date now = new Date();
        List<String> items = Arrays.asList("Java", "Python", "JavaScript");
    %>

    <%-- 2. 表达式：输出变量，相当于 out.print() --%>
    <h1>欢迎 <%= username %></h1>
    <p>当前时间：<%= new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(now) %></p>

    <%-- 3. 声明：定义成员变量和方法 --%>
    <%!
        private int visitCount = 0;

        public String getGreeting() {
            return "你好！";
        }
    %>

    <%-- 4. EL 表达式（Expression Language）--%>
    <%-- 优先级：先读 request.setAttribute，如果没有读 session/cookie --%>
    <p>${username}</p>  <%-- 等价于 request.getAttribute("username") --%>
    <p>${empty param.name ? "未输入姓名" : param.name}</p>  <%-- 三元运算 --%>

    <%-- 循环 --%>
    <ul>
    <%
        for (String item : items) {
    %>
        <li><%= item %></li>
    <%
        }
    %>
    </ul>
</body>
</html>
```

**注意**：JSP 在现代项目中越来越少用，前后端分离后，后端只返回 JSON，前端用 Vue/React 渲染。但理解 JSP 有助于理解 MVC 模式。

## 四、MVC 模式

MVC 是 Java Web 最核心的架构模式。

```
┌──────────┐      ┌──────────┐      ┌──────────┐
│  Model   │ ←──  │Controller│ ←──  │   View   │
│ (数据+逻辑)│      │(流程控制) │      │  (展示)   │
│ JavaBean │ ──→  │ Servlet  │ ──→  │   JSP    │
└──────────┘      └──────────┘      └──────────┘
```

### 完整示例：用户登录

```java
// ========== Model：JavaBean ==========
// User.java —— 数据模型
public class User {
    private int id;
    private String username;
    private String password;

    public User() {}
    public User(int id, String username, String password) {
        this.id = id;
        this.username = username;
        this.password = password;
    }

    // getter / setter 略
}

// UserService.java —— 业务逻辑
public class UserService {
    // 模拟数据库查询
    private static final Map<String, User> DB = new HashMap<>();
    static {
        DB.put("admin", new User(1, "admin", "123456"));
        DB.put("zhangsan", new User(2, "zhangsan", "password"));
    }

    public User login(String username, String password) {
        User user = DB.get(username);
        if (user != null && user.getPassword().equals(password)) {
            return user;
        }
        return null;
    }
}

// ========== Controller：Servlet ==========
@WebServlet("/login")
public class LoginServlet extends HttpServlet {
    private UserService userService = new UserService();

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        req.setCharacterEncoding("UTF-8");

        String username = req.getParameter("username");
        String password = req.getParameter("password");

        User user = userService.login(username, password);

        if (user != null) {
            // 登录成功：保存用户到 session，跳转到首页
            req.getSession().setAttribute("user", user);
            resp.sendRedirect("home.jsp");  // 重定向
        } else {
            // 登录失败：设置错误信息，转发回登录页
            req.setAttribute("error", "用户名或密码错误");
            req.getRequestDispatcher("login.jsp").forward(req, resp);
        }
    }
}

// ========== View：JSP ==========
// login.jsp 略（表单页面，显示 ${error}）
// home.jsp 略（欢迎页面，显示 ${user.username}）
```

### 转发 vs 重定向——面试高频

```java
// 转发（forward）
request.getRequestDispatcher("/target.jsp").forward(request, response);
// 特点：
// - 服务器内部行为，浏览器地址栏不变
// - 一次请求，request 数据（Attribute）可以带到目标页面
// - 只能在同一个应用内跳转

// 重定向（redirect）
response.sendRedirect("/target.jsp");
// 特点：
// - 浏览器地址栏会变成新 URL
// - 两次请求，第一次请求的 request 数据会丢失
// - 可以跳转到其他网站（如 response.sendRedirect("https://www.baidu.com")）
```

| 对比维度 | 转发（forward） | 重定向（redirect） |
|----------|----------------|-------------------|
| 浏览器地址栏 | 不变 | 变 |
| 请求次数 | 1 次 | 2 次 |
| request 数据 | 可传递 | 丢失 |
| 跨应用跳转 | 不可以 | 可以 |
| 代码 | `req.getRequestDispatcher().forward()` | `resp.sendRedirect()` |

## 五、会话管理

### Cookie 与 Session

```java
// ===== Cookie：存储在浏览器端 =====
// 设置 Cookie
@WebServlet("/set-cookie")
public class SetCookieServlet extends HttpServlet {
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws IOException {
        Cookie cookie = new Cookie("lastVisit", "2026-07-02");
        cookie.setMaxAge(60 * 60 * 24 * 7);  // 保存 7 天（秒）
        cookie.setPath("/");                  // 整个应用都能访问
        cookie.setHttpOnly(true);             // 禁止 JS 读取（防 XSS）
        resp.addCookie(cookie);
        resp.getWriter().write("Cookie 已设置");
    }
}

// 读取 Cookie
@WebServlet("/get-cookie")
public class GetCookieServlet extends HttpServlet {
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws IOException {
        Cookie[] cookies = req.getCookies();
        if (cookies != null) {
            for (Cookie c : cookies) {
                if ("lastVisit".equals(c.getName())) {
                    resp.getWriter().write("上次访问: " + c.getValue());
                    return;
                }
            }
        }
        resp.getWriter().write("没有找到 Cookie");
    }
}

// ===== Session：存储在服务器端 =====
// 设置 Session
@WebServlet("/set-session")
public class SetSessionServlet extends HttpServlet {
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws IOException {
        HttpSession session = req.getSession();  // 没有则自动创建
        session.setAttribute("username", "张三");
        session.setAttribute("role", "admin");
        session.setMaxInactiveInterval(30 * 60);  // 30 分钟无操作则过期
        resp.getWriter().write("Session 已设置");
    }
}

// 读取 Session
@WebServlet("/get-session")
public class GetSessionServlet extends HttpServlet {
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws IOException {
        HttpSession session = req.getSession(false);  // 不自动创建
        if (session != null) {
            String username = (String) session.getAttribute("username");
            resp.getWriter().write("当前用户: " + username);
        } else {
            resp.getWriter().write("未登录");
        }
    }
}
```

| 对比 | Cookie | Session |
|------|--------|---------|
| 存储位置 | 浏览器 | 服务器 |
| 安全性 | 低（用户可修改） | 高 |
| 容量 | 4KB（单个） | 无限制（取决于服务器内存） |
| 性能 | 每次请求携带（增加带宽） | 服务器内存占用 |
| 有效期 | 可长期保存 | 默认 30 分钟，关闭浏览器失效 |
| 跨域 | 可以设置 | 不支持 |

**面试话术**："Cookie 存在客户端，Session 存在服务端。Session 的机制依赖于 Cookie——服务器通过 Cookie 中的 JSESSIONID 来识别不同用户的 Session。如果浏览器禁用 Cookie，可以通过 URL 重写来传递 Session ID。"

### Token 认证（现代趋势）

```java
// 传统 Session 的问题：
// - 服务端存储，分布式系统需要 Session 共享（Redis）
// - 不支持移动端、小程序

// JWT Token 方案（无状态认证）
// 登录时服务端生成 Token → 客户端存 Token → 每次请求带 Token → 服务端验证签名

// Token 结构：Header.Payload.Signature
// Header:  {"alg": "HS256", "typ": "JWT"}
// Payload: {"userId": 1, "username": "zhangsan", "exp": 1700000000}
// Signature: HMAC-SHA256(base64UrlEncode(header) + "." + base64UrlEncode(payload), secret)
```

## 六、过滤器与监听器

### 过滤器（Filter）

```java
import javax.servlet.*;
import javax.servlet.annotation.*;
import javax.servlet.http.*;
import java.io.*;

// 过滤器：对所有请求/响应做预处理和后处理
@WebFilter("/*")  // 拦截所有请求
public class AuthFilter implements Filter {

    @Override
    public void init(FilterConfig config) {
        System.out.println("过滤器初始化");
    }

    @Override
    public void doFilter(ServletRequest req, ServletResponse resp,
                         FilterChain chain) throws IOException, ServletException {
        HttpServletRequest httpReq = (HttpServletRequest) req;
        String uri = httpReq.getRequestURI();

        // 放行登录页面和静态资源
        if (uri.contains("/login") || uri.contains(".css") || uri.contains(".js")) {
            chain.doFilter(req, resp);  // 放行，继续执行后续过滤器或 Servlet
            return;
        }

        // 检查是否登录
        HttpSession session = httpReq.getSession(false);
        if (session != null && session.getAttribute("user") != null) {
            chain.doFilter(req, resp);  // 已登录，放行
        } else {
            // 未登录，重定向到登录页
            ((HttpServletResponse) resp).sendRedirect("login.jsp");
        }
    }

    @Override
    public void destroy() {
        System.out.println("过滤器销毁");
    }
}
```

**过滤器的典型应用**：权限检查、编码设置、日志记录、XSS 防御、压缩响应内容。

### 监听器（Listener）

```java
// 监听 ServletContext 的创建和销毁——应用启动时初始化
@WebListener
public class AppStartupListener implements ServletContextListener {

    @Override
    public void contextInitialized(ServletContextEvent sce) {
        System.out.println("===== 应用启动了 =====");
        // 初始化数据库连接池、加载全局配置
    }

    @Override
    public void contextDestroyed(ServletContextEvent sce) {
        System.out.println("===== 应用关闭了 =====");
        // 释放资源
    }
}

// 监听 Session 的创建和销毁——统计在线人数
@WebListener
public class OnlineCounter implements HttpSessionListener {
    private static int onlineCount = 0;

    @Override
    public void sessionCreated(HttpSessionEvent se) {
        onlineCount++;
        System.out.println("当前在线: " + onlineCount);
    }

    @Override
    public void sessionDestroyed(HttpSessionEvent se) {
        onlineCount--;
        System.out.println("当前在线: " + onlineCount);
    }
}
```

## 七、JDBC 数据库连接

```java
import java.sql.*;

public class JDBCDemo {

    // JDBC 六大步骤：
    // 1. 加载驱动  2. 获取连接  3. 创建 Statement
    // 4. 执行 SQL  5. 处理结果  6. 关闭资源

    public static void main(String[] args) {
        // MySQL 连接信息
        String url = "jdbc:mysql://localhost:3306/mydb?useSSL=false&serverTimezone=Asia/Shanghai";
        String user = "root";
        String password = "123456";

        Connection conn = null;
        PreparedStatement pstmt = null;
        ResultSet rs = null;

        try {
            // 1. 加载驱动（MySQL 8.0+ 驱动类名）
            Class.forName("com.mysql.cj.jdbc.Driver");

            // 2. 获取连接
            conn = DriverManager.getConnection(url, user, password);

            // 3. 查询——用 PreparedStatement 防止 SQL 注入
            String querySql = "SELECT id, name, salary FROM employees WHERE department = ?";
            pstmt = conn.prepareStatement(querySql);
            pstmt.setString(1, "研发部");  // ? 占位符从 1 开始
            rs = pstmt.executeQuery();

            while (rs.next()) {
                int id = rs.getInt("id");
                String name = rs.getString("name");
                double salary = rs.getDouble("salary");
                System.out.printf("ID:%d, 姓名:%s, 薪资:%.2f\n", id, name, salary);
            }
            rs.close();
            pstmt.close();

            // 4. 插入/更新/删除——用 executeUpdate()
            String insertSql = "INSERT INTO employees (name, department, salary) VALUES (?, ?, ?)";
            pstmt = conn.prepareStatement(insertSql);
            pstmt.setString(1, "新员工");
            pstmt.setString(2, "研发部");
            pstmt.setDouble(3, 15000.0);
            int rows = pstmt.executeUpdate();
            System.out.println("插入 " + rows + " 行");

            // 5. 事务操作
            conn.setAutoCommit(false);  // 开启事务
            try {
                pstmt = conn.prepareStatement("UPDATE accounts SET balance = balance - 1000 WHERE id = 1");
                pstmt.executeUpdate();

                pstmt = conn.prepareStatement("UPDATE accounts SET balance = balance + 1000 WHERE id = 2");
                pstmt.executeUpdate();

                conn.commit();  // 提交事务
                System.out.println("转账成功");
            } catch (SQLException e) {
                conn.rollback();  // 回滚
                System.out.println("转账失败，已回滚");
            }

        } catch (ClassNotFoundException e) {
            System.out.println("驱动类找不到: " + e.getMessage());
        } catch (SQLException e) {
            System.out.println("数据库错误: " + e.getMessage());
        } finally {
            // 6. 按顺序关闭资源（后创建的先关）
            try { if (rs != null) rs.close(); } catch (SQLException e) {}
            try { if (pstmt != null) pstmt.close(); } catch (SQLException e) {}
            try { if (conn != null) conn.close(); } catch (SQLException e) {}
        }
    }
}
```

### Statement vs PreparedStatement

| 对比 | Statement | PreparedStatement |
|------|-----------|-------------------|
| SQL 注入防护 | 不安全，拼接字符串 | 安全，参数化查询 |
| 预编译 | 每次都要编译 | 只编译一次，重复使用 |
| 性能 | 低（重复编译） | 高（预编译 + 缓存） |
| 代码可读性 | 字符串拼接，难读 | 占位符 ? ，清晰 |
| 使用场景 | 几乎不用 | **始终使用** |

## 八、前端基础概览

配合 Java Web 开发时需要了解的基础前端知识。

```html
<!-- HTML 基础结构 -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>页面标题</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1>一级标题</h1>
    <p>段落文本</p>
    <a href="https://example.com">超链接</a>
    <img src="photo.jpg" alt="图片描述">

    <!-- 表单——与后端交互的核心 -->
    <form action="/login" method="POST">
        <input type="text" name="username" placeholder="用户名">
        <input type="password" name="password" placeholder="密码">
        <button type="submit">登录</button>
    </form>

    <!-- 块级元素（独占一行）：div, h1-h6, p, form -->
    <!-- 行内元素（不换行）：span, a, img, input -->

    <script src="script.js"></script>
</body>
</html>
```

```css
/* CSS 基础选择器 */
/* 标签选择器 */
p { color: #333; font-size: 16px; }

/* 类选择器——最常用 */
.btn {
    background-color: #1890ff;
    padding: 8px 16px;
    border-radius: 4px;
}

/* ID 选择器——尽量少用 */
#header { height: 60px; }

/* CSS 盒模型：margin(外边距) > border(边框) > padding(内边距) > content(内容) */
```

```javascript
// JavaScript 基础——让页面动起来
// 获取 DOM 元素
document.getElementById("btn").addEventListener("click", function() {
    alert("按钮被点击了！");
});

// AJAX：异步请求，不刷新页面
fetch("/api/users")
    .then(response => response.json())
    .then(data => {
        console.log(data);
        document.getElementById("result").innerText = JSON.stringify(data);
    })
    .catch(error => console.error("请求失败:", error));
```

## 面试高频考点

| 考点 | 出现频率 | 关键要点 |
|------|----------|----------|
| GET vs POST | 极高 | 参数位置、长度限制、缓存、幂等性 |
| Cookie vs Session | 极高 | 存储位置、安全性、原理、禁用 Cookie 怎么办 |
| Servlet 生命周期 | 高 | init → service → destroy，各阶段做什么 |
| 转发 vs 重定向 | 高 | 地址栏是否变化、请求次数、能否传数据 |
| MVC 流程 | 高 | Model/View/Controller 各自的职责 |
| HTTP 状态码 | 中高 | 200/301/302/304/400/401/403/404/500 |
| PreparedStatement 防注入 | 中高 | 为什么安全、和 Statement 的区别 |
| JSP 四大作用域 | 中 | page < request < session < application |
| Filter 过滤器 | 中 | 典型用途：权限拦截、编码、日志 |
| Token vs Session | 中 | 为什么需要 Token、JWT 原理 |

## 相关笔记

- [[工作学习/编程语言/Java基础|Java 基础]] — 先掌握 Java 基础再学 Java Web
- [[工作学习/数据库与SQL/常见业务SQL场景|常见业务 SQL 场景]] — JDBC 查询的实际 SQL
- [[工作学习/工程基础/Git基础与协作|Git 基础与协作]] — 管理 Java Web 项目
- [[工作学习/编程语言/Python基础|Python 基础]] — Python 也有类似 Web 框架（Flask/Django）
- [[工作学习/编程语言/C语言基础|C 语言基础]] — HTTP 协议底层通过 socket 传输
