#!/usr/bin/env python3
"""Backup and restore scripts for the Technical Inspection Platform."""

import os
import sys
import gzip
import shutil
import tempfile
import subprocess
from datetime import datetime
from pathlib import Path

BACKUP_DIR = os.environ.get('BACKUP_DIR', '/backups')
DB_NAME = os.environ.get('PGDATABASE', os.environ.get('POSTGRES_DB', 'inspection_platform'))
DB_USER = os.environ.get('PGUSER', os.environ.get('POSTGRES_USER', 'inspection'))
DB_HOST = os.environ.get('PGHOST', 'localhost')
DB_PORT = os.environ.get('PGPORT', '5432')
DB_PASSWORD = os.environ.get('PGPASSWORD', os.environ.get('DB_PASSWORD', ''))

def run_backup():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(BACKUP_DIR, f'backup_{timestamp}.sql.gz')

    os.makedirs(BACKUP_DIR, exist_ok=True)

    env = os.environ.copy()
    env['PGPASSWORD'] = DB_PASSWORD

    dump_cmd = [
        'pg_dump',
        '-h', DB_HOST,
        '-p', DB_PORT,
        '-U', DB_USER,
        '-d', DB_NAME,
        '--no-owner',
        '--no-privileges',
        '--format=plain',
    ]

    try:
        with open(backup_file + '.tmp', 'wb') as raw, gzip.GzipFile(fileobj=raw, mode='wb', mtime=0) as compressed:
            proc = subprocess.Popen(dump_cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            assert proc.stdout is not None
            shutil.copyfileobj(proc.stdout, compressed)
            stderr = proc.stderr.read() if proc.stderr else b''
            code = proc.wait()
            if code != 0:
                raise subprocess.CalledProcessError(code, dump_cmd, stderr=stderr.decode(errors='replace'))
        os.replace(backup_file + '.tmp', backup_file)
        os.chmod(backup_file, 0o600)
        print(f'Backup created: {backup_file}')
        return backup_file
    except subprocess.CalledProcessError as e:
        try: os.unlink(backup_file + '.tmp')
        except FileNotFoundError: pass
        print(f'Backup failed: {e.stderr}', file=sys.stderr)
        sys.exit(1)

def run_restore(backup_file):
    if not os.path.exists(backup_file):
        print(f'Backup file not found: {backup_file}', file=sys.stderr)
        sys.exit(1)

    env = os.environ.copy()
    env['PGPASSWORD'] = DB_PASSWORD

    if os.environ.get('CONFIRM_RESTORE') != 'YES':
        print('Refusing restore: set CONFIRM_RESTORE=YES after verifying target database and backup.', file=sys.stderr)
        sys.exit(2)
    try:
        restore_cmd = [
            'psql',
            '-h', DB_HOST,
            '-p', DB_PORT,
            '-U', DB_USER,
            '-d', DB_NAME,
        ]

        with gzip.open(backup_file, 'rb') as source:
            result = subprocess.run(restore_cmd, stdin=source, env=env, capture_output=True, text=False, check=True)
        print(f'Restore completed from: {backup_file}')
    except subprocess.CalledProcessError as e:
        print(f'Restore failed: {e.stderr}', file=sys.stderr)
        sys.exit(1)

def list_backups():
    if not os.path.exists(BACKUP_DIR):
        print('No backup directory found.')
        return

    backups = sorted(Path(BACKUP_DIR).glob('backup_*.sql.gz'), reverse=True)
    if not backups:
        print('No backups found.')
        return

    for b in backups:
        size_mb = b.stat().st_size / (1024 * 1024)
        print(f'{b.name}  ({size_mb:.1f} MB)')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python backup_restore.py [backup|restore|list] [backup_file]')
        sys.exit(1)

    command = sys.argv[1]

    if command == 'backup':
        run_backup()
    elif command == 'restore':
        if len(sys.argv) < 3:
            print('Usage: python backup_restore.py restore <backup_file>')
            sys.exit(1)
        run_restore(sys.argv[2])
    elif command == 'list':
        list_backups()
    else:
        print(f'Unknown command: {command}')
        sys.exit(1)
