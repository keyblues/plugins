# PHP 代码审计报告

生成日期：2026-03-29
审计范围：CVSS ≥ 6.0 高危漏洞
项目：Typecho Plugins

---

## 漏洞总览

| # | 漏洞类型 | 文件 | CVSS | 利用难度 | 风险等级 |
|---|---------|------|------|---------|---------|
| 1 | 命令注入 | AUTO-UPDATE.php:562 | 9.0 | 高 | 严重 |
| 2 | SQL 注入 | PostRating/rating.php:36 | 8.8 | 低 | 高危 |
| 3 | 文件包含 | MyPlayer/api.php:47 | 8.5 | 中 | 高危 |
| 4 | create_function RCE | AntiSpam/Plugin.php:75 | 7.5 | 高 | 高危 |
| 5 | 任意文件写入 | TeStore/Action.php:285 | 7.5 | 中 | 高危 |
| 6 | 任意文件写入 | UploadPlugin/Action.php:111 | 7.5 | 中 | 高危 |
| 7 | 任意文件写入 | Ueditor/.../Uploader.class.php | 7.5 | 中 | 高危 |
| 8 | 反序列化 | ThemeDemo/Plugin.php:184 | 6.5 | 高 | 中危 |
| 9 | 反序列化 | WeChatShare/Action.php:270 | 6.0 | 高 | 中危 |
| 10 | 反序列化 | AllowIp/Plugin.php:81 | 6.0 | 高 | 中危 |

---

## 1. AUTO-UPDATE.php 命令注入 (CVSS 9.0 Critical)

### 漏洞定位
- **文件**: `/workspace/AUTO-UPDATE.php:562`
- **危险函数**: `exec()`
- **CVSS 评分**: 9.0 (Critical)

### 漏洞代码
```php
// 第 90 行
$tmpDir = realpath('../') . '/TMP';

// 第 562 行
exec('find "' . $tmpDir . '" -mindepth 1 ! -name "updates.log" -exec rm -rf {} +');
```

### 污点分析
| 属性 | 值 |
|-----|-----|
| **污点源** | `$argv[1]`, `$argv[2]`, 运行目录 |
| **传播路径** | 命令行参数 → `realpath('../')` → `$tmpDir` → `exec()` |
| **过滤失效** | 无任何过滤，路径直接拼接进命令 |

### 利用链
```
控制运行目录 → realpath('../') 返回污染路径 → 命令注入
```

---

## 2. PostRating SQL 注入 (CVSS 8.8 High)

### 漏洞定位
- **文件**: `/workspace/PostRating/rating.php:36`
- **危险函数**: `$db->query()`
- **CVSS 评分**: 8.8 (High)

### 漏洞代码
```php
$ip = isset($_SERVER["HTTP_X_FORWARDED_FOR"]) ? $_SERVER["HTTP_X_FORWARDED_FOR"]
 : (isset($_SERVER["HTTP_CLIENT_IP"]) ? $_SERVER["HTTP_CLIENT_IP"] : $_SERVER["REMOTE_ADDR"]);

$name = $user->hasLogin() ? $user->screenName : Typecho_Cookie::get('__typecho_remember_author', '');

$db->query("INSERT INTO ". $db->getPrefix() ."postrating VALUES ('$cid', '$rating', '$ip', '$name', '$created')");
```

### 污点分析
| 属性 | 值 |
|-----|-----|
| **污点源** | `$_SERVER["HTTP_X_FORWARDED_FOR"]`, `$_COOKIE["__typecho_remember_author"]` |
| **传播路径** | HTTP Header → 直接拼入 SQL |
| **过滤失效** | 完全无过滤，单引号直接拼入 |

---

## 3. MyPlayer 文件包含 (CVSS 8.5 High)

### 漏洞定位
- **文件**: `/workspace/MyPlayer/api.php:47-49`
- **危险函数**: `include()`
- **CVSS 评分**: 8.5 (High)

### 漏洞代码
```php
if( TryGetParam( 'service', $service ) ) {
    $service = strtolower( $service );
    $apifile = "api/{$service}.php";
    if( file_exists( $apifile ) ){
        include( $apifile );
        $api = new $service( );
    }
}
```

### 污点分析
| 属性 | 值 |
|-----|-----|
| **污点源** | `$_GET['service']` |
| **传播路径** | `$_GET['service']` → `$apifile` → `include()` |
| **过滤失效** | 仅检查 `file_exists()`，可利用 php://filter 或 RFI |

---

## 4. AntiSpam create_function RCE (CVSS 7.5 High)

### 漏洞定位
- **文件**: `/workspace/AntiSpam/Plugin.php:75-76`
- **危险函数**: `create_function()` (内部使用 eval)
- **CVSS 评分**: 7.5 (High)

### 漏洞代码
```php
ob_start(create_function('$input','return preg_replace("#textarea(.*?)name=([\"\'])text([\"\'])(.+)/textarea>#",
"textarea$1name=$2comment$3$4/textarea><textarea name=\"text\" cols=\"100%\" rows=\"4\" style=\"display:none\">spam</textarea>",$input);') );
```

---

## 5. TeStore 任意文件写入 (CVSS 7.5 High)

### 漏洞定位
- **文件**: `/workspace/TeStore/Action.php:285`
- **危险函数**: `ZipArchive::extractTo()`
- **CVSS 评分**: 7.5 (High)

### 漏洞代码
```php
if (!$phpZip->extractTo($tempDir)) {
    // 无文件名验证！
}
```

### 利用链
```
构造恶意 ZIP → 文件名 ../Shell.php → 解压时路径遍历 → 覆盖/写入文件
```

---

## 修复建议

| 漏洞 | 修复方案 |
|-----|---------|
| AUTO-UPDATE.php | 使用 `escapeshellarg()` 或 PHP 原生文件操作替代 exec |
| PostRating | 使用预处理语句 `prepare()` |
| MyPlayer | 白名单验证 service 参数 |
| AntiSpam | 移除 `create_function`，使用匿名函数 |
| TeStore | 验证 ZIP 内部文件名，阻止 `..` 路径遍历 |

---

## 修复优先级

1. **AUTO-UPDATE.php** - 立即修复 (CVSS 9.0)
2. **PostRating** - 高优先级 (CVSS 8.8)
3. **MyPlayer** - 高优先级 (CVSS 8.5)
4. **TeStore** - 中优先级 (CVSS 7.5)
5. **AntiSpam** - 中优先级 (CVSS 7.5)
