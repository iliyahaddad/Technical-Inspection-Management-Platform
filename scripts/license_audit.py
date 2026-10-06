#!/usr/bin/env python3
"""
License compliance audit script.
Checks installed packages for prohibited licenses (GPLv3, AGPLv3, etc.).
"""
import json
import subprocess
import sys
from pathlib import Path

PROHIBITED_LICENSES = {'GPLv3', 'AGPLv3', 'SSPL'}

def get_installed_packages():
    result = subprocess.run([sys.executable, '-m', 'pip', 'list', '--format=json'], capture_output=True, text=True)
    return json.loads(result.stdout)

def get_license_info(package_name):
    result = subprocess.run([sys.executable, '-m', 'pip', 'show', package_name], capture_output=True, text=True)
    info = {}
    for line in result.stdout.splitlines():
        if ':' in line:
            key, value = line.split(':', 1)
            info[key.strip().lower()] = value.strip()
    return info

def audit():
    packages = get_installed_packages()
    violations = []
    for pkg in packages:
        name = pkg['name']
        info = get_license_info(name)
        license_name = info.get('license', 'Unknown')
        for prohibited in PROHIBITED_LICENSES:
            if prohibited.lower() in license_name.lower():
                violations.append({'package': name, 'version': pkg['version'], 'license': license_name})
    if violations:
        print('LICENSE COMPLIANCE VIOLATIONS FOUND:')
        for v in violations:
            print(f"  - {v['package']} ({v['version']}): {v['license']}")
        sys.exit(1)
    else:
        print(f'License audit passed. {len(packages)} packages checked, no prohibited licenses found.')
        sys.exit(0)

if __name__ == '__main__':
    audit()
