# PHP Code Audit POC Scripts

本目录包含 Typecho 插件安全审计中发现的高危漏洞 POC 脚本。

## 漏洞列表

| # | 漏洞 | CVSS | 文件 |
|---|-----|------|------|
| 1 | AUTO-UPDATE.php 命令注入 | 9.0 | `auto_update_rce.py` |
| 2 | PostRating SQL 注入 | 8.8 | `postrating_sqli.py` |
| 3 | MyPlayer 文件包含 | 8.5 | `myplayer_lfi.py` |
| 4 | AntiSpam create_function RCE | 7.5 | `antispam_rce.py` |
| 5 | TeStore ZIP 路径遍历 | 7.5 | `testore_zip_trav.py` |

## 使用方法

### Python 脚本

```bash
# PostRating SQL 注入
python3 postrating_sqli.py http://target.com/PostRating/rating.php

# MyPlayer 文件包含
python3 myplayer_lfi.py http://target.com/MyPlayer/api.php scan
python3 myplayer_lfi.py http://target.com/MyPlayer/api.php read /etc/passwd

# AntiSpam RCE
python3 antispam_rce.py http://target.com/comment/action

# TeStore ZIP 路径遍历
python3 testore_zip_trav.py generate

# AUTO-UPDATE 命令注入
python3 auto_update_rce.py /path/to/AUTO-UPDATE.php "whoami"
```

### Bash 扫描脚本

```bash
chmod +x scan.sh
./scan.sh /workspace
```

## 报告

详细漏洞分析请参见 `REPORT.md`。

## 免责声明

这些 POC 脚本仅供安全研究和教育目的使用。请勿用于未经授权的渗透测试或攻击行为。
