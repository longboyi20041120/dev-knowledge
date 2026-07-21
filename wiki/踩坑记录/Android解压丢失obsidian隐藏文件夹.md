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

Android 文件管理器默认不显示隐藏文件，解压 ZIP 时点号开头的 `.obsidian/` 文件夹被跳过。

## 解决

1. 文件管理器（vivo 自带或 ZArchiver 均可）→ 设置 → **打开"显示隐藏文件"**开关
2. 重新解压 ZIP，覆盖到 `Documents/devkb`
3. 确认 `.obsidian/` 存在后再用 Obsidian 打开

## 相关

- [[../wiki/手机同步配置|手机同步配置]]
