# PPT Agent 素材复选框故障排查

日期：2026-08-03

## 现象

用户在逐章生成阶段点击"本章使用的文件素材"复选框，提示"无法连接本地服务，请重新打开软件后重试"。

## 排查过程

### 第一层：变量名错误

**位置**：`src/ppt_agent/ui/static/app.js` 第 797 行

**根因**：素材复选框的 `change` 事件处理中使用了不存在的 `state.activeChapterId`，正确变量名是 `state.selectedSectionId`。

```javascript
// 错误
const sectionId = state.activeChapterId;  // undefined!

// 正确
const sectionId = state.selectedSectionId;
```

**修复**：将 `activeChapterId` 改为 `selectedSectionId`。

**为什么这个错误容易被忽视**：因为 `section_id` 为 `undefined` 时，请求仍然发送了，服务端校验"章节编号无效"返回了 HTTP 400。前端能收到响应，所以没有触发"无法连接本地服务"。真正的"无法连接"是下一个 bug。

---

### 第二层：后台路径覆盖用户选择

**位置**：`src/ppt_agent/ui/server.py` 第 902-906 行

**根因**：`start-chapter-generation` 的后台工作函数无视用户勾选，直接从 `source-manifest.json` 读取全部素材 ID。

```python
# 修复前：总是读全部素材
source_ids = tuple(
    source.source_id
    for source in repository.get_source_manifest(task_id).sources
    if source.status is SourceStatus.EXTRACTED
)

# 修复后：从前端 payload 读取
source_ids = tuple(
    str(sid) for sid in (payload.get("source_ids") or [])
)
```

**影响**：生成章节后刷新，素材复选框全部被勾上。

---

### 第三层：路由响应崩溃（核心故障）

**位置**：`src/ppt_agent/ui/server.py` 第 736-744 行

**根因**：`update-chapter-sources` 路由处理完后，公共响应代码要访问 `record.to_dict()`，但该路由没有给 `record` 变量赋值。

```python
# 错误：update-chapter-sources 分支只设置了 outline，没设置 record
elif path == "/api/tasks/update-chapter-sources":
    ...
    self._repository().save_chapter_material(material)
    outline = self._repository().get_outline(task_id)
    # 缺少：record = self._repository().get(task_id)

# 公共响应代码（所有路由共用）
self._send_json(HTTPStatus.OK, {
    "record": record.to_dict(),  # ← UnboundLocalError!
    "outline": outline.to_dict(),
    ...
})
```

**为什么表现为"无法连接本地服务"**：

1. Python 抛 `UnboundLocalError`
2. `BaseHTTPRequestHandler.handle_one_request()` 的 `except Exception` 捕获了这个异常，调用 `send_error(400)` 尝试返回错误响应
3. `send_error(400)` 写入了 `self.wfile`（BufferedWriter），但 `wfile.flush()` 后数据没有立即发送到 TCP 缓冲区（Windows 上 `socket.makefile('wb')` 的已知行为）
4. `BaseRequestHandler.finish()` 调用了 `wfile.close()`，但 `BufferedWriter.close()` 在 Windows 上可能丢弃未刷新的数据
5. WebView 的 `fetch()` 等待响应，但服务端连接被关闭了，没有收到任何数据 → 抛出 `TypeError: Failed to fetch` → 前端 catch 后显示"无法连接本地服务"

**关键教训**：服务端 Python 异常被静默吞掉，前端只看到网络错误。排查时要关注服务端 stderr。

**修复**：
```python
elif path == "/api/tasks/update-chapter-sources":
    ...
    self._repository().save_chapter_material(material)
    record = self._repository().get(task_id)     # ← 新增
    outline = self._repository().get_outline(task_id)
```

---

### 第四层：state 字段遗漏

**位置**：`src/ppt_agent/ui/static/app.js` 第 53-72 行

**根因**：`state` 初始化对象中没有 `chapterDrafts` 字段。

```javascript
const state = {
    task: null,
    outline: null,
    ...
    chapterDirty: false,
    // 缺少：chapterDrafts: {},
    selectedSectionId: null,
    ...
};
```

**修复**：添加 `chapterDrafts: {}`。

---

## 经验和教训

1. **代码审查要逐行验证**：新加的 `elif` 分支要确保它设置了公共代码依赖的所有变量
2. **服务端静默异常是排查盲区**：HTTP handler 的 `except Exception` 吞掉异常后，前端只能看到"连接断开"
3. **Windows socket 缓冲不同于 Linux**：`makefile('wb')` 的 BufferedWriter 在 Windows 上不可靠，生产环境应设置 `wbufsize = 0`
4. **前端 JS 不能假定 state 字段都存在**：访问动态属性前应做空值检查或用 Optional Chaining

## 涉及文件

| 文件 | 改动数 |
|---|---|
| `src/ppt_agent/ui/static/app.js` | 3处 |
| `src/ppt_agent/ui/server.py` | 4处 |
| `src/ppt_agent/rendering/enterprise_engine.py` | 1处（页面标题10→32字符） |
| `src/ppt_agent orchesstration/enterprise_mapper.py` | 全部版式padding |
