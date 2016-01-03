#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" list.py


"""

import json
import optparse
import os
import sys

def main():
    parser = optparse.OptionParser()
    parser.add_option("-d", "--delete", action="store")
    parser.add_option("-D", "--delete_both", action="store_true")
    options, args = parser.parse_args()

    if len(args) == 0:
        sys.exit(0)

    filename = args[0]
    search = None
    if len(args) == 2:
        search = args[1].decode("utf-8")

    delete_recorded = False
    delete_encoded = False
    if search and options.delete_both:
        delete_recorded = True
        delete_encoded = True
    if search and options.delete == 'r':
        delete_recorded = True
    if search and options.delete == 'e':
        delete_encoded = True

    if delete_recorded or delete_encoded:
        delete_files(filename, search, delete_recorded, delete_encoded)
    else:
        list_files(filename, search)

def filter_files(filename, search):
    fp = open(filename, 'r')
    js = json.load(fp)
    fp.close()

    data = js
    if search:
        data = filter(
            lambda item: (
                item['title'].find(search) >= 0 or
                item['fullTitle'].find(search) >= 0 or
                item['recorded'].find(search) >= 0),
            js)
    return data
        
def delete_files(filename, search, delete_recorded, delete_encoded):
    data = filter_files(filename, search)
    total_count = 0
    total_size = 0

    for item in data:
        print("title: %s" % (item['fullTitle']))
        if delete_recorded:
            p = item['recorded']
            sz = get_filesize(p)
            print("recorded: %s (%s)" % (p, get_pretty_filesize(sz)))
            if sz:
                total_count += 1
            total_size += (sz or 0)
            
        if delete_encoded:
            p = item['encoded']
            sz = get_filesize(p)
            print("encoded: %s (%s)" % (p, get_pretty_filesize(sz)))
            if sz:
                total_count += 1
            total_size += (sz or 0)
        print("")

    sys.stdout.write("delete %d files (total: %s)? (yes/NO) " % (total_count, get_pretty_filesize(total_size)))
    ans = sys.stdin.readline()

    if ans.rstrip().lower() != "yes":
        print("canceled")
        sys.exit(0)

    for item in data:
        if delete_recorded:
            p = item['recorded']
            if os.path.exists(p):
                print("delete %s" % p)
                os.remove(p)
        if delete_encoded:
            p = item['encoded']
            if os.path.exists(p):
                print("delete %s" % p)
                os.remove(p)
    
        
    
def list_files(filename, search):
    data = filter_files(filename, search)
    
    for item in data:
        print("title: %s" % (item['fullTitle']))
        sz = get_filesize(item['recorded'])
        print("recorded: %s (%s)" %
              (item['recorded'], get_pretty_filesize(sz)))
        sz = get_filesize(item['encoded'])
        print("encoded: %s (%s)" % 
            (item['encoded'], get_pretty_filesize(sz)))
        print("")
        
def get_filesize(path):
    if not os.path.exists(path):
        return None
    else:
        return os.path.getsize(path)

def get_pretty_filesize(sz):
    if not sz:
        return "deleted"
    else:
        return "%d MB" % (sz / (1024 * 1024))
    
if __name__ == "__main__":
    main()
