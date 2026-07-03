---
tags:
  - "#用途/灵感"
  - "#类型/灵感"
  - "#状态/草稿"
  - 产品创意
  - AI
  - Android
created: 2026-06-22
updated: 2026-06-26
status: draft
---

# Vivo 手机 AI 操控助手

## 一句话

手机版 Claude Code——用户用自然语言下指令，AI 看懂屏幕、模拟操作、操控任意 App，像人手操作一样完成任务。

> 不是"整理桌面工具"，是一个**通用手机 AI Agent**。整理桌面只是它能干的无数事之一。

## 它和 Claude Code 是一个思路

```
电脑上：  用户说 "帮我重构这个模块"   → Claude Code → 读文件、改代码、跑测试
手机上：  用户说 "帮我把购物软件都放一个文件夹里" → 手机 Agent → 截图看懂、拖拽图标、搞定

本质一样：Screenshot（读屏幕）→ AI 决策 → AccessibilityService（操作手机）
相当于把 Claude Code 的 Computer Use 能力搬到 Android 上。
```

## 能干什么

任何用户能用手指做到的事，Agent 都应该能做到：

- "把桌面上的购物软件放进一个文件夹叫'买买买'"
- "打开微信，给张三发微信说我晚半小时到"
- "帮我把最近 3 天的照片发朋友圈，配文'周末快乐'"
- "打开美团，帮我点一杯拿铁，送到公司"
- "把系统字体调大一号"
- "所有通知里，只保留微信和邮件的，其他全关了"

## 怎么做到的

### 核心三件事

```
1. 看懂屏幕        → 截图 → Vision 模型（本地 Gemini Nano 或云端）
2. 理解意图        → LLM 把用户的话拆成操作步骤
3. 执行操作        → AccessibilityService 模拟人手操作
```

### 技术栈

```
Android App (Kotlin)
├── AccessibilityService     ← 模拟点击、滑动、输入文字、读控件树
├── Screenshot               ← MediaProjection 或 AccessibilityService 截图
├── Gemini Nano (AICore)     ← 本地 AI，免费、离线，看懂截图
├── TTS + 语音识别           ← 用户语音输入（可选，打字也行）
└── 云端 LLM 降级             ← 本地跑不了复杂推理时用
```

### 为什么 Gemini Nano 是关键

Android 14+ 内置了 AICore，Gemini Nano 跑在设备上：
- **本地跑**：截图不用上传，隐私有保障
- **免费**：没有 API 费用
- **不需要联网**：飞机上也能用

复杂推理本地搞不定时，再考虑降级到云端。

## 路线图

### 第一阶段：单步操作 MVP

用户说一句话 → 手机做一件事。

只做"看得见摸得着"的操作，不涉及跨 App 工作流：

- "打开设置把 WiFi 关了"
- "把桌面第三页的淘宝图标删掉"

验证核心链路：**语音/文字 → AI 理解 → 操作执行**

### 第二阶段：多步工作流

用户说一句话 → Agent 拆成多步 → 一步步执行：

- "把所有购物软件放进一个文件夹" → 需要扫描 App、识别分类、逐个拖拽、创建文件夹
- "打开微信给张三发消息" → 启动微信、搜索联系人、输入文字、发送

这一步要解决**任务规划**（LLM 把复杂指令拆成原子操作序列）。

### 第三阶段：跨 App 自主

类似 Claude Code 的 Loop 模式，给一个目标让 Agent 自己迭代：

- "帮我订一杯瑞幸的生椰拿铁，送到公司"
- 用户甚至可以中途介入纠正

## 关键挑战

| 挑战 | 严重度 | 思路 |
|------|--------|------|
| 不同 App 界面不一样 | 🔴 最高 | 靠 Vision 模型泛化，不写死控件坐标 |
| 无障碍权限用户不敢开 | 🔴 最高 | 开源 + 100% 本地运行 + 透明声明 |
| Vivo 杀后台 | 🟡 中 | 引导加白名单 |
| 操作出错了怎么办 | 🟡 中 | 每步操作前先截图验证，错了回退 |
| Google Play 无障碍政策 | 🟡 中 | 明确声明用途，非恶意软件 |

## 差异化和壁垒

| | Jovi / 小爱 | Tasker | **这个 Agent** |
|------|-------------|--------|----------------|
| 触发方式 | 固定关键词 | 手动编程 | **自然语言** |
| 能干什么 | 系统设置 | 自动化 | **任意 App** |
| 看懂屏幕 | ❌ | ❌ | **Vision 模型** |
| 泛化能力 | 无 | 无 | **不写死，AI 自己判断** |

## 实现指南

### 最小闭环（MVP 先跑通的）

```
用户输入文字指令
      ↓
MediaProjection 截图当前屏幕
      ↓
截图 + 指令 ≈ 发给 AI（Vision 模型）
      ↓
AI 返回操作：{ "action": "tap", "x": 540, "y": 1200 }
      ↓
AccessibilityService 执行操作
      ↓
再截图 → 给 AI 验证结果 → 完成或重试
```

### 工程结构

```
app/
├── service/
│   └── AgentAccessibilityService.kt   ← 核心：执行操作
├── screenshot/
│   └── ScreenshotCapture.kt           ← MediaProjection 截图
├── ai/
│   └── AiEngine.kt                    ← 调用 Vision 模型，解析响应
├── agent/
│   └── AgentLoop.kt                   ← 串联：截图→AI→执行→验证
├── ui/
│   └── MainActivity.kt                ← 最简 UI：输入框 + 执行按钮
└── res/
    └── xml/
        └── accessibility_service.xml  ← 无障碍服务配置
```

### 1. AccessibilityService 配置

`res/xml/accessibility_service.xml`：

```xml
<?xml version="1.0" encoding="utf-8"?>
<accessibility-service
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:accessibilityEventTypes="typeAllMask"
    android:accessibilityFeedbackType="feedbackGeneric"
    android:canPerformGestures="true"
    android:canRetrieveWindowContent="true"
    android:canTakeScreenshot="true"
    android:notificationTimeout="100" />
```

AndroidManifest 里声明：

```xml
<service
    android:name=".service.AgentAccessibilityService"
    android:permission="android.permission.BIND_ACCESSIBILITY_SERVICE"
    android:exported="true">
    <intent-filter>
        <action android:name="android.accessibilityservice.AccessibilityService" />
    </intent-filter>
    <meta-data
        android:name="android.accessibilityservice"
        android:resource="@xml/accessibility_service" />
</service>
```

### 2. AccessibilityService 核心代码

```kotlin
class AgentAccessibilityService : AccessibilityService() {

    // 点击指定坐标
    fun tap(x: Float, y: Float) {
        val gesture = GestureDescription.Builder()
            .addStroke(GestureDescription.StrokeDescription(
                Path().apply { moveTo(x, y) },
                0,
                100
            ))
            .build()
        dispatchGesture(gesture, null, null)
    }

    // 滑动
    fun swipe(x1: Float, y1: Float, x2: Float, y2: Float, duration: Long = 300) {
        val path = Path().apply {
            moveTo(x1, y1)
            lineTo(x2, y2)
        }
        val gesture = GestureDescription.Builder()
            .addStroke(GestureDescription.StrokeDescription(path, 0, duration))
            .build()
        dispatchGesture(gesture, null, null)
    }

    // 输入文字（需要先 focus 到输入框）
    fun typeText(text: String) {
        val node = findFocus(AccessibilityNodeInfo.FOCUS_INPUT)
        if (node != null) {
            val args = Bundle()
            args.putCharSequence(
                AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, text
            )
            node.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, args)
        }
    }

    // 按 Back 键
    fun pressBack() {
        performGlobalAction(GLOBAL_ACTION_BACK)
    }

    // 按 Home 键
    fun pressHome() {
        performGlobalAction(GLOBAL_ACTION_HOME)
    }

    // 打开某个 App（通过语音或搜索，绕过包名限制）
    fun openApp(appName: String) {
        // 先回桌面
        pressHome()
        Thread.sleep(500)
        // 从底部上滑打开搜索
        swipe(540f, 2000f, 540f, 500f, 200)
        Thread.sleep(300)
        // 输入 App 名称
        typeText(appName)
        Thread.sleep(500)
        // 点击第一个结果
        tap(540f, 400f)
    }

    // 截图
    fun takeScreenshot(): Bitmap? {
        return takeScreenshot(Display.DEFAULT_DISPLAY, 
            mainExecutor, 
            object : TakeScreenshotCallback {
                override fun onSuccess(result: ScreenshotResult) {
                    // 处理截图...
                }
                override fun onFailure(errorCode: Int) {}
            })
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent) {}
    override fun onInterrupt() {}
}
```

### 3. 截图：MediaProjection

AccessibilityService 的 `takeScreenshot()` 方法（Android 11+）可以直接截图。但更稳定的方案是用 MediaProjection：

```kotlin
class ScreengrabCapture(private val context: Context) {

    private var mediaProjection: MediaProjection? = null
    private var imageReader: ImageReader? = null

    // 用户在 MainActivity 里先授权
    fun setMediaProjection(mp: MediaProjection) {
        this.mediaProjection = mp
    }

    fun capture(): Bitmap {
        val displayMetrics = context.resources.displayMetrics
        val width = displayMetrics.widthPixels
        val height = displayMetrics.heightPixels

        imageReader = ImageReader.newInstance(width, height, 
            PixelFormat.RGBA_8888, 2)

        mediaProjection!!.createVirtualDisplay(
            "screengrab",
            width, height, displayMetrics.densityDpi,
            DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
            imageReader!!.surface, null, null
        )

        val image = imageReader!!.acquireLatestImage()
        val planes = image.planes
        val buffer = planes[0].buffer
        val bitmap = Bitmap.createBitmap(width, height, 
            Bitmap.Config.ARGB_8888)
        bitmap.copyPixelsFromBuffer(buffer)
        image.close()

        return bitmap
    }
}
```

MediaProjection 需要用户在 Activity 里授权（系统弹窗）：

```kotlin
// MainActivity.kt
private val mediaProjectionLauncher = registerForActivityResult(
    ActivityResultContracts.StartActivityForResult()
) { result ->
    if (result.resultCode == RESULT_OK) {
        val mp = (getSystemService(MEDIA_PROJECTION_SERVICE) 
            as MediaProjectionManager)
            .getMediaProjection(result.resultCode, result.data!!)
        screengrabCapture.setMediaProjection(mp)
    }
}

// 触发授权
val intent = (getSystemService(MEDIA_PROJECTION_SERVICE) 
    as MediaProjectionManager).createScreenCaptureIntent()
mediaProjectionLauncher.launch(intent)
```

### 4. AI Engine：截图 + 指令 → 操作

```kotlin
class AiEngine(private val apiKey: String) {

    private val client = OkHttpClient()
    private val gson = Gson()

    // AI 返回的操作格式
    data class AgentAction(
        val action: String,    // "tap", "swipe", "type", "back", "home", "done"
        val x: Float? = null,
        val y: Float? = null,
        val x2: Float? = null,
        val y2: Float? = null,
        val text: String? = null,
        val explanation: String? = null
    )

    fun decideNextAction(
        userGoal: String,
        screenshot: Bitmap,
        previousActions: List<AgentAction> = emptyList()
    ): AgentAction {
        // 1. 截图转 base64
        val base64Image = bitmapToBase64(screenshot)

        // 2. 构造 prompt
        val prompt = buildString {
            append("你是一个手机操作助手。用户的目标是：\"$userGoal\"\n")
            append("这是当前手机屏幕截图。\n")
            if (previousActions.isNotEmpty()) {
                append("之前已经执行的操作：${gson.toJson(previousActions)}\n")
            }
            append("请决定下一步操作。返回 JSON：\n")
            append("""{"action":"tap","x":540,"y":1200,"explanation":"点击设置图标"}""" + "\n")
            append("支持的动作：tap(x,y), swipe(x1,y1,x2,y2), type(text), back, home, done\n")
            append("如果目标已完成，返回 {\"action\":\"done\"}\n")
            append("屏幕尺寸：1080x2400 像素(x:0-1080, y:0-2400)")
        }

        // 3. 调用 Claude API（或 OpenAI）
        val response = callVisionApi(prompt, base64Image)

        // 4. 解析
        return gson.fromJson(response, AgentAction::class.java)
    }

    private fun bitmapToBase64(bitmap: Bitmap): String {
        val stream = ByteArrayOutputStream()
        bitmap.compress(Bitmap.CompressFormat.JPEG, 80, stream)
        return Base64.encodeToString(stream.toByteArray(), Base64.NO_WRAP)
    }

    private fun callVisionApi(prompt: String, base64Image: String): String {
        // POST https://api.anthropic.com/v1/messages
        // 或 POST https://api.openai.com/v1/chat/completions
        // 返回 AI 的 JSON 响应
        TODO("实现 API 调用")
    }
}
```

### 5. Agent Loop：串联整个流程

```kotlin
class AgentLoop(
    private val service: AgentAccessibilityService,
    private val ai: AiEngine,
    private val screenshot: ScreengrabCapture
) {
    private val maxSteps = 10  // 最多 10 步，防止死循环

    suspend fun execute(goal: String) {
        val history = mutableListOf<AiEngine.AgentAction>()

        for (step in 1..maxSteps) {
            // 1. 截图
            val bitmap = screenshot.capture()

            // 2. AI 决策
            val action = ai.decideNextAction(goal, bitmap, history)

            // 3. 检查是否完成
            if (action.action == "done") {
                break
            }

            // 4. 执行操作
            when (action.action) {
                "tap" -> {
                    service.tap(action.x!!, action.y!!)
                    history.add(action)
                }
                "swipe" -> {
                    service.swipe(action.x!!, action.y!!, action.x2!!, action.y2!!)
                    history.add(action)
                }
                "type" -> {
                    service.typeText(action.text!!)
                    history.add(action)
                }
                "back" -> {
                    service.pressBack()
                    history.add(action)
                }
                "home" -> {
                    service.pressHome()
                    history.add(action)
                }
            }

            // 5. 等 UI 响应
            delay(800)
        }
    }
}
```

### 6. MainActivity：极简入口

```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var agentLoop: AgentLoop

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // 一个输入框 + 一个按钮
        val input = findViewById<EditText>(R.id.goalInput)
        val button = findViewById<Button>(R.id.executeButton)

        button.setOnClickListener {
            val goal = input.text.toString()
            lifecycleScope.launch {
                agentLoop.execute(goal)
            }
        }
    }
}
```

### 关键提醒

**安全机制（必须加）**：
- 每步操作前弹 toast 显示"即将执行：xxx"，给用户 1 秒反应时间
- 加一个浮窗停止按钮，随时中断 Agent
- 禁止操作列表：不碰支付、不碰系统设置里的危险项

**先用什么 AI**：
- **最快跑通**：用 Claude API 或 OpenAI GPT-4V 的云端接口，截图传上去拿结果
- **跑通后再切本地**：换成 Gemini Nano（AICore），隐私和成本优势才能体现

**为什么先不用 Gemini Nano**：
- AICore 目前只支持 Pixel 和部分三星设备，Vivo 不一定有
- API 稳定性还不够，调试困难
- 云端先跑通核心闭环，验证产品可行性，再考虑本地化

### 第一个里程碑

> 用户在输入框打字"打开设置"，Agent 截图 → AI 识别 → 点击设置图标 → 设置页面打开。

这个闭环跑通，后面就是加能力、加场景、加可靠性。

## 下一步

- [ ] 在 Android Studio 创建项目，配好 AccessibilityService
- [ ] 跑通 MediaProjection 截图
- [ ] 接 Claude/OpenAI Vision API，验证"截图→AI→返回坐标"的链路
- [ ] 实现 tap 操作，打通"用户说打开设置→Agent 真的打开了设置"
- [ ] 加安全机制：每步确认、紧急停止按钮
- [ ] 验证第一个闭环后，再调研 Gemini Nano 本地化
