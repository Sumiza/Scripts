import os
import hashlib

allfiles = set()


def hashme(file, hashtype=None):
    hashhold = hashtype or hashlib.sha256()
    with open(file, 'rb') as f:
        hashhold.update(f.read())
        return hashhold.hexdigest()


def find_duplicate(folder, delete=False):
    for root, _, files in os.walk(folder):
        for file in files:
            fileloc = os.path.abspath(root + "/" + file)
            hashhold = hashme(fileloc)
            if hashhold in allfiles:
                if delete:
                    print('[Deleting]', fileloc)
                    os.remove(fileloc)
                else:
                    print('[duplicate]', fileloc)
            else:
                allfiles.add(hashhold)


find_duplicate(os.getcwd(), False)
