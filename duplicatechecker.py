import os
import hashlib

def hashme(file: str) -> str:
    with open(file, 'rb') as f:
        hashdata = hashlib.sha512()
        while chunk := f.read(1_000_000):
            hashdata.update(chunk)
        return hashdata.hexdigest()

def isdupe(hash: str, allhash: set[str] = set()) -> bool:
    if hash in allhash:
        return True
    allhash.add(hash)
    return False

def find_duplicate(folder: str, delete: bool = False) -> None:
    for root, _, files in os.walk(folder):
        for file in files:
            file = os.path.join(os.path.abspath(root), file)
            if isdupe(hashme(file)):
                if delete:
                    print('[Deleting]', file)
                    os.remove(file)
                else:
                    print('[Duplicate]', file)

find_duplicate(os.getcwd(), False)
