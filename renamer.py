#!/usr/bin/env python3
import hashlib
import os
import re
import sys
import shutil
import datetime

def sha1_8(filepath):
    h = hashlib.sha1()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()[:8]

def extract_hash_from_filename(filename):
    m = re.search(r'_([0-9a-fA-F]{8})\.', filename)
    if m:
        return m.group(1).lower()
    return None

def backup_file(src_path, backup_dir, timestamp=None):
    os.makedirs(backup_dir, exist_ok=True)
    filename = os.path.basename(src_path)
    if src_path.endswith('.html'):
        if timestamp is None:
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        backup_name = f"{filename.rsplit('.',1)[0]}_{timestamp}.html.bak"
    else:
        backup_name = f"{filename}.bak"
    backup_path = os.path.join(backup_dir, backup_name)
    shutil.copy2(src_path, backup_path)
    msg = f"Backed up {src_path} to {backup_path}"
    print(msg)
    return backup_path, msg

def rename_with_hash(filepath, hash8, log, backup_dir):
    dir_, filename = os.path.split(filepath)
    base, ext = os.path.splitext(filename)
    base_no_hash = re.sub(r'_[0-9a-fA-F]{8}$', '', base)
    new_filename = f"{base_no_hash}_{hash8}{ext}"
    new_path = os.path.join(dir_, new_filename)

    backup_path, msg = backup_file(filepath, backup_dir)
    log.append(msg)

    if filename != new_filename:
        if os.path.exists(new_path):
            os.remove(new_path)
            msg = f"Removed existing file: {new_filename}"
            print(msg)
            log.append(msg)
        os.rename(filepath, new_path)
        msg = f"Renamed: {filename} -> {new_filename}"
        print(msg)
        log.append(msg)
    else:
        msg = f"No rename needed for {filename}"
        print(msg)
        log.append(msg)
    return new_filename

def find_files(root, exts):
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if any(f.endswith(ext) for ext in exts):
                yield os.path.join(dirpath, f)

def replace_in_file(filepath, replacements, backup_dir, log):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    new_content = content
    for old, new in replacements.items():
        new_content = new_content.replace(old, new)
    if new_content != content:
        backup_path, msg = backup_file(filepath, backup_dir)
        log.append(msg)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        msg2 = f"Updated references in {filepath}"
        print(msg2)
        log.append(msg2)

def main(root='.'):
    js_css_files = list(find_files(root, ['.js', '.css']))
    html_files = list(find_files(root, ['.html']))

    replacements = {}
    log = []

    rename_dir = os.path.join(root, '.rename')
    os.makedirs(rename_dir, exist_ok=True)

    for filepath in js_css_files:
        filename = os.path.basename(filepath)
        actual_hash = sha1_8(filepath)
        file_hash = extract_hash_from_filename(filename)

        if file_hash == actual_hash:
            msg = f"Skipped (hash match): {filename}"
            print(msg)
            log.append(msg)
            new_name = filename
        else:
            new_name = rename_with_hash(filepath, actual_hash, log, rename_dir)
        replacements[filename] = new_name

    for html_path in html_files:
        replace_in_file(html_path, replacements, rename_dir, log)

    log_path = os.path.join(rename_dir, 'log.txt')
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"Run at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        for line in log:
            f.write(line + '\n')
        f.write('\n')

    print(f"Process complete. Log saved to {log_path}")

if __name__ == '__main__':
    root_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    main(root_dir)