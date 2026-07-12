---
tags:
  - "#类型/bug"
  - "#项目/map_web"
  - "#技术/java"
  - "#状态/已验证"
created: 2026-07-12
updated: 2026-07-12
---

# map_web 天气 API 返回乱码：RestTemplate gzip 二次解压

## 现象

调用 `/api/weather/current` 报错：`天气数据获取失败: 401 : "<乱码>"`。curl 直接调 API 返回 200 OK，但 Java 后端始终报错。

## 原因

**根因**：`RestTemplate` + `SimpleClientHttpRequestFactory`（底层 `HttpURLConnection`）对 gzip 响应的解压行为不可控：

1. 和风天气 API 返回 `Content-Encoding: gzip` 的 JSON 数据
2. 原代码手动用 `GZIPInputStream` 解压
3. **但 JDK 的 `HttpURLConnection` 默认会自动解压 gzip**，导致代码手动再解压一次 → **二次解压** → 乱码

修复过程中还踩了两个连带坑：

- **受限请求头**：想用 `Accept-Encoding: identity` 禁用 gzip，但 JDK 将此头列为受限头，`setRequestProperty` 静默忽略
- **URL 参数尾随空格**：YAML 配置读取的 `qweatherKey` / `qweatherLocation` 可能带尾随空格，`URI.create()` 报 `Illegal character in query`

## 解决

放弃 `RestTemplate`，改用 **Java 17 原生 `java.net.http.HttpClient`**：

```java
// 替换 RestTemplate 为 HttpClient
private final HttpClient httpClient = HttpClient.newBuilder()
        .followRedirects(HttpClient.Redirect.NORMAL)
        .build();

private String fetchDecompress(String url) throws Exception {
    HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(url))
            .header("Accept-Encoding", "gzip")
            .GET().build();
    HttpResponse<InputStream> response = httpClient.send(request,
            HttpResponse.BodyHandlers.ofInputStream());
    InputStream in = response.body();
    // HttpClient 不会自动解压，手动检测 Content-Encoding
    String encoding = response.headers().firstValue("Content-Encoding").orElse("");
    if ("gzip".equalsIgnoreCase(encoding)) {
        in = new GZIPInputStream(in);
    }
    // ... 读取为字符串
}
```

同时 URL 参数加 `.trim()` 去空格。

## 教训

- **别信 JDK 的自动行为**：`HttpURLConnection` 的 gzip 自动解压在不同版本、不同 CDN 域名下表现不一
- **受限头不报错**：`setRequestProperty` 设受限头只会静默忽略，不会抛异常，debug 极其困难
- **Java 17 `HttpClient` 更可控**：行为透明，无隐藏的自动处理，适合需要精确控制 HTTP 的场景

## 相关

- [[../wiki/工作学习/编程语言/Java学习路线|Java 学习路线]]
