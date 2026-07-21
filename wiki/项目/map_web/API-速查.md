---
tags:
  - "#用途/项目"
  - "#类型/项目"
  - "#项目/map_web"
created: 2026-06-22
updated: 2026-06-22
status: reviewed
---

# API 速查 — map_web

## 全部端点

| Method | Path | 服务 | 说明 |
|--------|------|------|------|
| GET | `/api/buildings/list` | Java :8080 | 89 栋建筑元数据 |
| GET | `/api/path/waypoints` | Java :8080 | 156 个路点 |
| POST | `/api/path/route` | Java :8080 | A* 路径（路点→路点） |
| POST | `/api/path/navigate` | Java :8080 | 校园导航（建筑→建筑） |
| GET | `/api/weather/current` | Java :8080 | 天气 + AQI |
| POST | `/api/ai/chat` | Python :8000 | AI 对话，支持 NAV 标记 |
| GET | `/api/ai/health` | Python :8000 | AI 服务健康检查 |

## 统一响应格式

```json
{
  "code": 200,
  "message": "操作成功",
  "data": [...]
}
```

## 认证

- JWT + BCrypt
- 前端 `getToken()` 获取，`authHeaders()` 拼接 Bearer 头
- `window.isAdmin` 由 `updateAuthUI()` 自动检测

## AI 对话请求

```json
POST /api/ai/chat
{
  "message": "从一教到三食堂怎么走",
  "context": { "weather": "...", "aqi": "..." }
}
```

## AI 响应中的 NAV 标记

AI 返回 `[NAV:fromId:toId]` 时，前端自动触发导航。例如：
```
[NAV:teaching_1:canteen_3]
```
前端解析后自动调用 `POST /api/path/navigate`。
