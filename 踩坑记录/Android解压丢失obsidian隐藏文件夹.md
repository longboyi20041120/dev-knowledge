---
tags:
  - "#类型/bug"
  - "#状态/已验证"
created: 2026-07-12
updated: 2026-07-12
---

# Android 解压 ZIP 丢失 .obsidian 隐藏文件夹

## 现象

GitHub 下载 ZIP → 解压到手机 → Obsidian 打开 vault → **图视图没有颜色分组、插件配置丢失**。

## 原因

Android 自带文件管理器（vivo/小米/OPPO 等）解压 ZIP 时会**跳过点号开头的隐藏文件夹**，导致 `.obsidian/` 整个目录丢失。

## 解决

1. 装 **ZArchiver**（酷安或 Google Play）
2. ZArchiver 右上角 → 设置 → **打开"显示隐藏文件"开关**
3. 用 ZArchiver 重新解压 ZIP，选"解压到..." → 指定 `Documents/devkb`
4. 确认 `.obsidian/` 存在后再用 Obsidian 打开

## 相关

- [[../wiki/手机同步配置|手机同步配置]]
