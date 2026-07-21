---
tags:
  - "#用途/工作学习"
  - "#类型/技术"
  - "#技术/linux"
  - "#状态/已验证"
created: 2026-07-02
updated: 2026-07-15
status: reviewed
---

# Linux 基础

> 后端开发、数据分析、AI 训练全是 Linux 环境。面试不专门考，但不会你连开发机都连不上。 | **面试重要度：中** | 预计阅读：20 分钟

## 视频资源

- YouTube: [freeCodeCamp: Linux Command Line](https://www.youtube.com/watch?v=ZtqBQ68cfJc) — 最好的 Linux 命令行教程
- B站: [尚硅谷 Linux 教程（韩顺平）](https://www.bilibili.com/video/BV1dW411X7DP/) — 中文最推荐的 Linux 入门
## 一、认识 Linux

### Linux 发行版选哪个？

| 发行版 | 特点 | 适合谁 |
|--------|------|--------|
| Ubuntu / Debian | 社区活跃，apt 包管理，新手友好 | 个人开发、AI/数据分析 |
| CentOS Stream / RHEL | 稳定性优先，yum/dnf 包管理 | 企业服务器（CentOS 7 已停更） |
| Rocky Linux / AlmaLinux | CentOS 的替代品 | 原 CentOS 用户的迁移目标 |
| Arch Linux | 滚动更新，高度自定义 | 极客、喜欢折腾的人 |
| Alpine | 超轻量（5MB） | Docker 镜像 |

**内核版本 vs 发行版版本**：Linux 内核由 Linus Torvalds 维护，发行版是在内核上打包了各种软件形成的完整系统。

```bash
# 查看发行版信息
cat /etc/os-release

# 查看内核版本
uname -r    # 例如 5.15.0-91-generic

# 查看系统架构
uname -m    # x86_64 或 aarch64
```

---

## 二、文件系统结构

### 根目录一览

Linux 没有 C 盘 D 盘，只有一个根 `/`，所有东西都挂在它下面：

```
/
├── /bin        # 基本命令（ls, cp, mv 等），所有用户都能用
├── /sbin       # 系统管理命令（fdisk, mkfs），需要 root 权限
├── /boot       # 内核和启动文件，别乱动
├── /dev        # 设备文件（硬盘是 /dev/sda，终端是 /dev/tty）
├── /etc        # 配置文件（nginx.conf, sshd_config 都在这里）
├── /home       # 用户主目录（普通用户的个人文件）
│   └── /home/username/
├── /root       # root 用户的主目录
├── /lib        # 库文件（.so 动态链接库）
├── /var        # 经常变化的数据（日志 /var/log、网站 /var/www）
├── /tmp        # 临时文件，重启可能被清空
├── /usr        # 用户安装的软件（/usr/bin, /usr/local）
│   └── /usr/local/  # 手动编译安装的软件放这里
├── /opt        # 第三方商业软件（如 Google Chrome）
├── /proc       # 虚拟文件系统，内核和进程信息（不占磁盘）
└── /mnt, /media # 挂载点（U盘、光盘）
```

**面试常问**：`/etc` 放配置，`/var` 放变化数据（日志），`/tmp` 放临时文件。

### 路径

```bash
# 绝对路径：从根开始
/home/user/project/main.py

# 相对路径：从当前目录开始
./main.py          # . 代表当前目录
../config/app.conf # .. 代表上级目录
~/.bashrc          # ~ 代表当前用户的主目录
```

---

## 三、常用命令速查

### 文件操作（最常用）

```bash
# 列出文件
ls                # 简单列表
ls -l             # 详细列表（权限、大小、日期）
ls -la            # 显示所有文件（包括 . 开头的隐藏文件）
ls -lh            # 人类可读的大小（KB/MB/GB）
ls -lt            # 按修改时间排序

# 目录操作
pwd               # 打印当前目录（Print Working Directory）
cd /path/to/dir   # 进入目录
cd -              # 回到上次的目录
cd ~              # 回到用户主目录
mkdir -p a/b/c    # 递归创建多层目录

# 复制/移动/删除
cp file1 file2           # 复制文件
cp -r dir1 dir2          # 递归复制目录
mv old_name new_name     # 移动或重命名
rm file                  # 删除文件
rm -r dir                # 递归删除目录
rm -rf dir               # 强制递归删除（危险！）

# 查看文件
cat file.txt             # 一次性显示全部（小文件用）
less file.txt            # 分页查看，上下翻页，q退出
tail -f /var/log/app.log # 实时追踪日志末尾
tail -n 100 file.log     # 看最后100行
head -n 20 file.csv      # 看前20行

# 文件统计
wc -l file.txt           # 统计行数
wc -w file.txt           # 统计字数
```

### 权限管理

Linux 权限模型：每个文件有三组权限——**所有者（u）**、**所属组（g）**、**其他人（o）**。

```
-rwxr-xr--  1  user  group  4096  Jun 20 10:30  script.sh
│││││││││
│└┬┘└┬┘└┬┘
│ │  │  └── 其他人的权限 (r--)
│ │  └───── 所属组的权限 (r-x)
│ └──────── 所有者的权限 (rwx)
└────────── 文件类型 (- 普通文件, d 目录, l 软链接)
```

**权限含义**：

| 权限 | 字母 | 数字 | 对文件的含义 | 对目录的含义 |
|------|------|------|-------------|-------------|
| 读 | r | 4 | 可以读文件内容 | 可以列出目录内容 |
| 写 | w | 2 | 可以修改文件内容 | 可以在目录中创建/删除文件 |
| 执行 | x | 1 | 可以执行该文件 | 可以进入该目录（cd） |

```bash
# 数字法设置权限（记住常用组合就行）
chmod 755 script.sh    # rwxr-xr-x（所有者全权限，其他人只读和执行）
chmod 644 config.conf  # rw-r--r--（所有者可读写，其他人只读）
chmod 700 private/     # rwx------（只有所有者能访问）

# 数字法的计算（记住不是每次都要算）：
# r=4, w=2, x=1
# rwx = 4+2+1 = 7
# rw- = 4+2   = 6
# r-x = 4+1   = 5
# r-- = 4     = 4

# 符号法（更直观但不常用）
chmod u+x script.sh           # 给所有者加执行权限
chmod g-w config.conf         # 去掉组的写权限
chmod o= file.txt             # 清空其他人的所有权限

# 修改所有者
chown user:group file.txt     # 改所有者和组
chown -R user:group dir/      # 递归修改目录下所有文件
```

**面试话术**："755 是目录和可执行文件的常见权限（所有者全权限，其他人可读可执行），644 是普通配置文件的常见权限。777 是最危险的——给所有人所有权限，尤其是 `/tmp` 下如果有 777 脚本可能被提权攻击。"

### 查找与搜索

```bash
# find：按条件查找文件
find /var/log -name "*.log"           # 在 /var/log 下找 .log 文件
find . -type f -mtime -7              # 最近7天修改过的文件
find . -type f -size +100M            # 大于 100MB 的文件
find . -name "*.pyc" -delete          # 找到并删除 .pyc 文件

# grep：在文件内容中搜索
grep "ERROR" app.log                  # 找包含 ERROR 的行
grep -i "error" app.log               # 忽略大小写
grep -n "error" app.log               # 显示行号
grep -r "TODO" src/                   # 递归搜索整个目录
grep -v "DEBUG" app.log               # 排除包含 DEBUG 的行
grep -A 3 -B 2 "ERROR" app.log        # ERROR 前后各几行的上下文

# | (管道)：把一个命令的输出传给另一个命令
cat app.log | grep "ERROR" | wc -l   # 统计 ERROR 出现次数
ps aux | grep nginx                   # 查找 nginx 进程
```

### 压缩与归档

```bash
# tar：打包（不压缩）
tar -cvf archive.tar dir/             # 打包（c=create, v=verbose, f=file）
tar -xvf archive.tar                  # 解包（x=extract）
tar -tvf archive.tar                  # 查看包内容（t=list）

# tar.gz / tgz：打包 + gzip 压缩
tar -czvf archive.tar.gz dir/         # 打包并压缩（z=gzip）
tar -xzvf archive.tar.gz              # 解压缩

# zip / unzip
zip -r archive.zip dir/               # 压缩为 zip
unzip archive.zip                     # 解压 zip
```

---

## 四、进程管理

### 查看进程

```bash
# ps：查看进程快照
ps aux                   # 查看所有进程（BSD 风格）
ps -ef                   # 查看所有进程（Unix 风格）
ps aux | grep python     # 找 Python 进程

# top：实时进程监控（按 q 退出）
top                      # CPU 使用率排序
top -u username          # 只看某个用户的进程
# 在 top 界面内：
#   M  → 按内存排序
#   P  → 按 CPU 排序
#   k  → 输入 PID 杀死进程
#   1  → 切换显示每个 CPU 核心

# htop：增强版 top（彩色、支持鼠标，需要安装）
htop
```

### 管理进程

```bash
# kill：给进程发信号
kill PID              # 默认信号 SIGTERM（15），礼貌地请进程退出
kill -9 PID           # SIGKILL（9），强制杀死（进程无法忽略）
kill -15 PID          # 等同于 kill PID
kill -l               # 查看所有信号列表

# pkill / killall：按名字杀进程
pkill -f python       # 杀死所有名字包含 python 的进程
killall nginx         # 杀死所有 nginx 进程

# & 和 nohup：后台运行
python app.py &                    # 后台运行，但关闭终端可能被杀
nohup python app.py &              # 后台运行，忽略 SIGHUP 信号，关闭终端也继续
nohup python app.py > output.log 2>&1 &  # 同时重定向输出

# jobs, fg, bg：管理当前 shell 的后台任务
jobs                 # 查看当前 shell 的后台任务
fg %1                # 把 1 号任务调到前台
bg %1                # 把停止的任务放后台继续
Ctrl+Z               # 把前台任务挂起（暂停）
Ctrl+C               # 中断前台任务

# systemctl（CentOS 7+ / Ubuntu 16.04+）：管理服务
systemctl status nginx       # 查看服务状态
systemctl start nginx        # 启动服务
systemctl stop nginx         # 停止服务
systemctl restart nginx      # 重启服务
systemctl enable nginx       # 设置开机自启
systemctl disable nginx      # 取消开机自启
journalctl -u nginx -f       # 查看 nginx 服务日志（实时追踪）
```

---

## 五、磁盘与存储

```bash
# df：查看磁盘使用情况
df -h                    # 人类可读的磁盘空间（h = human-readable）
df -i                    # 查看 inode 使用情况

# du：查看目录/文件大小
du -sh dir/              # 目录的总大小
du -sh * | sort -rh      # 当前目录下各文件/目录的大小排序
du -sh * | sort -rh | head -10  # 最大的 10 个

# 哪些文件占用最多
du -ah /var | sort -rh | head -20
```

---

## 六、Shell 脚本基础

Shell 脚本就是把命令写进文件批量执行。面试中能写简单的 Shell 脚本是加分项。

### 基础语法

```bash
#!/bin/bash
# 上面这行（shebang）告诉系统用哪个解释器

# ========== 变量 ==========
name="Alice"                    # 定义变量（等号两边不能有空格！）
echo "Hello, $name"             # 用 $ 取值
echo "当前用户: ${USER}"        # 花括号明确变量边界
readonly PI=3.14159            # 只读变量

# 特殊变量
echo "脚本名: $0"
echo "第1个参数: $1"
echo "第2个参数: $2"
echo "参数个数: $#"
echo "所有参数: $@"
echo "上一条命令的退出状态: $?"  # 0 表示成功，非0表示失败

# ========== 条件判断 ==========
if [ "$name" = "Alice" ]; then
    echo "你好 Alice"
elif [ "$name" = "Bob" ]; then
    echo "你好 Bob"
else
    echo "你是谁？"
fi

# 文件测试
if [ -f "config.txt" ]; then   # 文件存在
    echo "配置文件存在"
fi
if [ -d "/var/log" ]; then     # 目录存在
    echo "日志目录存在"
fi

# 数字比较
count=10
if [ $count -gt 5 ]; then      # -gt = greater than
    echo "大于 5"
fi
# -eq 等于  -ne 不等于  -lt 小于  -le 小于等于  -ge 大于等于

# ========== 循环 ==========
# for 循环
for i in {1..5}; do
    echo "第 $i 次"
done

for file in *.txt; do
    echo "处理 $file"
    wc -l "$file"
done

# while 循环
counter=1
while [ $counter -le 5 ]; do
    echo "计数: $counter"
    counter=$((counter + 1))
done

# 读取文件每一行
while IFS= read -r line; do
    echo "行内容: $line"
done < input.txt
```

### 实用脚本示例

```bash
#!/bin/bash
# 日志清理脚本：删除 30 天前的日志，保留最近 100 个文件

LOG_DIR="/var/log/myapp"
RETENTION_DAYS=30
KEEP_COUNT=100

# 检查目录是否存在
if [ ! -d "$LOG_DIR" ]; then
    echo "错误：目录 $LOG_DIR 不存在"
    exit 1
fi

# 方法1：删除 N 天前的日志
echo "清理 $RETENTION_DAYS 天前的日志..."
find "$LOG_DIR" -name "*.log" -type f -mtime +$RETENTION_DAYS -delete

# 方法2：保留最新的 N 个文件，删除其余
echo "保留最新的 $KEEP_COUNT 个日志文件..."
cd "$LOG_DIR" || exit
ls -t *.log 2>/dev/null | tail -n +$((KEEP_COUNT + 1)) | xargs rm -f

echo "清理完成。当前日志文件数：$(ls -1 *.log 2>/dev/null | wc -l)"
```

```bash
#!/bin/bash
# 批量重命名：将 .jpg.webp 改成 .webp

# 先预览（安全操作）
for file in *.jpg.webp; do
    [ -f "$file" ] || continue
    newname="${file%.jpg.webp}.webp"
    echo "$file → $newname"
done

# 确认无误后再实际执行
# for file in *.jpg.webp; do
#     [ -f "$file" ] || continue
#     mv "$file" "${file%.jpg.webp}.webp"
# done
```

---

## 七、包管理

### yum（CentOS/RHEL 7）

```bash
# 基本操作
yum install nginx                  # 安装
yum update nginx                   # 更新
yum remove nginx                   # 卸载
yum search keyword                 # 搜索
yum list installed                 # 列出已安装
yum info nginx                     # 查看软件包信息

# 仓库管理
yum repolist                       # 查看已启用的仓库
yum install epel-release           # 安装 EPEL（额外软件源）
```

### dnf（CentOS 8+ / Fedora）

```bash
# dnf 是 yum 的下一代，命令几乎一样
dnf install nginx
dnf update
dnf remove nginx
dnf search keyword
```

### apt（Ubuntu/Debian）

```bash
apt update                         # 更新软件源索引
apt install nginx                  # 安装
apt upgrade                        # 更新所有软件
apt remove nginx                   # 卸载
apt search keyword                 # 搜索
apt list --installed               # 列出已安装
```

---

## 八、环境变量与配置

```bash
# 查看环境变量
env                           # 列出所有环境变量
echo $PATH                    # 查看可执行文件搜索路径
echo $HOME                    # 用户主目录
echo $JAVA_HOME               # Java 安装路径（如果有）

# 临时设置（仅当前终端有效）
export MY_VAR="hello"
export PATH=$PATH:/opt/myapp/bin

# 永久设置（写入配置文件）
# ~/.bashrc       → 每次打开终端加载
# ~/.bash_profile → 登录时加载一次
# /etc/profile    → 全局，所有用户
```

---

## 九、文本处理三剑客

### grep — 搜索

见上文"查找与搜索"章节。

### sed — 流编辑器（行编辑）

```bash
# 替换（s/原内容/新内容/）
sed 's/old/new/' file.txt          # 每行第一个 old 换成 new
sed 's/old/new/g' file.txt         # 每行所有 old 换成 new
sed 's/old/new/g' file.txt > new.txt  # 输出到新文件

# 删除
sed '/^$/d' file.txt               # 删除空行
sed '2,5d' file.txt                # 删除第2到5行

# 实战：修改配置文件
sed -i 's/port 8080/port 9090/' config.conf   # -i 直接修改原文件
```

### awk — 列处理

```bash
# 按空格分割，打印第2列
awk '{print $2}' file.txt

# 按逗号分割
awk -F',' '{print $1, $3}' data.csv

# 条件过滤 + 统计
awk '$3 > 100 {sum += $3; count++} END {print sum/count}' data.txt
# 含义：第三列大于100的行，累加第三列求平均

# 实战：统计日志中每个 IP 的访问次数
awk '{print $1}' access.log | sort | uniq -c | sort -rn
```

### 组合使用

```bash
# 例子：统计 Nginx 日志中返回状态码 500 的 URL 和次数
grep " 500 " access.log | awk '{print $7}' | sort | uniq -c | sort -rn | head -10

# 管道串联逻辑：
# grep  " 500 "   → 筛选出状态码为500的行
# awk   '{print $7}' → 提取第7列（URL路径）
# sort            → 排序（uniq 需要先排序）
# uniq -c         → 去重并统计次数
# sort -rn        → 按次数降序排列
# head -10        → 取前10条
```

---

## 十、面试高频考点

| 考点 | 出题形式 | 必答要点 |
|------|----------|----------|
| 最常用的 10 个命令 | 直接问或假场景 | ls/cd/cp/mv/rm/chmod/ps/grep/find/tail |
| 权限 rwx / 数字 | 概念题 | r=4 w=2 x=1，755/644/700 的含义 |
| 查看日志 | 场景题 | tail -f 实时、grep 搜索、less 翻页 |
| 查找文件/内容 | 实操题 | find 按文件名/时间/大小，grep 按内容 |
| 后台运行程序 | 场景题 | &、nohup、screen/tmux |
| 杀死进程 | 场景题 | kill vs kill -9，pkill 按名字杀 |
| 查看端口占用 | 场景题 | netstat -tlnp 或 ss -tlnp |
| 软链接 vs 硬链接 | 概念题 | 路径快捷方式 vs 同一 inode 的别名 |
| 磁盘满了怎么办 | 场景题 | df -h 查看，du -sh * 定位大文件，清理日志 |
| Shell 脚本 | 手写题 | 变量、if/for、参数传递 |

### 面试场景模拟

**Q**: "服务突然访问不了，你怎么排查？"

**A**: 五步排查法：
```bash
# 1. 先看进程还在不在
ps aux | grep myapp

# 2. 看端口有没有在监听
netstat -tlnp | grep 8080    # 或用 ss -tlnp

# 3. 看日志有没有报错
tail -100 /var/log/myapp/error.log  # 先看最新
grep "ERROR\|FATAL" /var/log/myapp/error.log  # 搜关键错误

# 4. 看系统资源
top -n 1 | head -5       # CPU 和内存
df -h                    # 磁盘是不是满了
free -h                  # 内存使用

# 5. 如果是端口正常但连不上，检查防火墙
systemctl status firewalld    # 或 iptables -L
```

---

## 相关笔记

- [[工作学习/计算机基础/操作系统|操作系统]] — 进程管理、内存管理、文件系统原理
- [[工作学习/计算机基础/计算机科学导论|计算机科学导论]] — 计算机整体架构、网络基础
- [[工作学习/计算机基础/软件工程|软件工程]] — DevOps、CI/CD、部署
- [[工作学习/工程基础/Git基础与协作|Git 基础与协作]] — 版本控制
- [[工作学习/数据库与SQL/SQL查询优化|SQL 查询优化]] — SQL 优化
- [[工作学习/书架与学习路线|书架与学习路线]] — 知识体系全景
