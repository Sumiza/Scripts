"""
Vanity SSH Generator
"""
import os
import subprocess
import time
import multiprocessing
import shutil

class SSHVanityGen():
    """
    A class for generating SSH keys with vanity patterns.

    Args:
    findlist (list): List of vanity patterns to search for in generated SSH keys.
    lettercase (bool, optional): Keep the case when searching for vanity patterns (default is False).
    findtoal (int, optional): Number of keys to find (default is 1).
    passphrase (str, optional): Passphrase for the SSH keys (default is None).
    comment (str, optional): Comment for the SSH keys (default is None).
    threads (int, optional): Number of CPU cores to use for key generation (default is None, uses all available cores).
    rounds (int, optional): Number of rounds to use for passphrase (default is 16).

    Methods:
    addfind(find: str) -> bool:
        Add a vanity pattern to the search list.

    removefind(remove: str) -> bool:
        Remove a vanity pattern from the search list.

    foundone(threadid, localcount, find, pubkey):
        Placeholder method to handle a found SSH key. Can be overridden in a subclass.

    start():
        Start the vanity SSH key generation process.

    status(sharedcount, foundcount):
        Placeholder method to display the current status. Can be overridden in a subclass.

    stop():
        Stop the vanity key generation process.

    """

    def __init__(self,
                 findlist: list,
                 lettercase: bool = False,
                 findtoal: int = 1,
                 passphrase: str = None,
                 comment: str = None,
                 threads: int = None,
                 rounds: int = 16) -> None:
        """
        Initialize the SSHVanityGen instance with specified parameters.

        Args:
        findlist (list): List of vanity patterns to search for in generated SSH keys.
        lettercase (bool, optional): Keep the case when searching for vanity patterns (default is False).
        findtoal (int, optional): Number of keys to find (default is 1).
        passphrase (str, optional): Passphrase for the SSH keys (default is None).
        comment (str, optional): Comment for the SSH keys (default is None).
        threads (int, optional): Number of CPU cores to use for key generation (default is None, uses all available cores).
        rounds (int, optional): Number of rounds to use for passphrase (default is 16).
        """

        self.multilist = []
        self.findlist = []
        self.lettercase = lettercase

        for find in findlist:
            self.addfind(find)

        self.rounds = rounds
        self.curcount = 0

        self.findtotal = findtoal
        self.comment = comment
        self.passphrase = passphrase

        if threads:
            self.threads = threads
        else:
            self.threads = os.cpu_count()

    def addfind(self, find: str) -> bool:
        """
        Add a vanity pattern to the search list.

        Args:
        find (str): Vanity pattern to be added to the search list.

        Returns:
        bool: True if the pattern was added successfully.
        """

        if self.lettercase is False:
            find = find.casefold()
        self.findlist.append(find)
        return True

    def removefind(self, remove: str) -> bool:
        """
        Remove a vanity pattern from the search list.

        Args:
        remove (str): Vanity pattern to be removed from the search list.

        Returns:
        bool: True if the pattern was removed successfully, False if not found.
        """

        try:
            self.findlist.remove(remove)
        except ValueError:
            return False

    def subrun(self, subcall):
        """
        Run a subprocess shell command.
        """

        subprocess.call(subcall, shell=True,
                        stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

    def _genkey(self, sharedcount, foundcount, threadid: int):
        """
        Generate SSH keys and search for vanity patterns in a separate process.
        """

        localcount = 0
        while True:

            if foundcount.value >= self.findtotal:
                break

            self.subrun(
                f'ssh-keygen -t ed25519 -f {threadid}-{localcount} -N "" -C ""')

            with open(f'{threadid}-{localcount}.pub', encoding="utf-8") as file:
                pubkey = file.read().strip()

            if self.lettercase is False:
                pubkey = pubkey.lower()

            for find in self.findlist:
                if find in pubkey:
                    with foundcount.get_lock():
                        foundcount.value += 1

                    if self.comment:
                        self.subrun(
                            f'ssh-keygen -c -f {threadid}-{localcount} -C {self.comment}')

                    if self.passphrase:
                        self.subrun(
                            f'ssh-keygen -p -a {self.rounds} -f {threadid}-{localcount} -N {self.passphrase}')
                    
                    shutil.copy(f'{threadid}-{localcount}.pub',
                              f'{threadid}-{localcount}-{find}.pub')
                    shutil.copy(f'{threadid}-{localcount}',
                              f'{threadid}-{localcount}-{find}')
                    
                    self.foundone(threadid, localcount, find, pubkey)

            os.remove(f'{threadid}-{localcount}.pub')
            os.remove(f'{threadid}-{localcount}')

            localcount += 1
            with sharedcount.get_lock():
                sharedcount.value += 1

    def foundone(self, threadid, localcount, find, pubkey):
        """
        Placeholder method to handle a found SSH key. Can be overridden in a subclass.

        Args:
        threadid: Identifier of the process.
        localcount: Local count of generated keys.
        find: The vanity pattern found.
        pubkey: The public key associated with the vanity pattern.
        """

    def start(self):
        """
        Start the vanity SSH key generation process.
        """
        if not self.findlist:
            raise ValueError('findlist is empty cant search for nothing')

        self.multilist = []
        sharedcount = multiprocessing.Value('i', 0)
        foundcount = multiprocessing.Value('i', 0)
        for threadid in range(self.threads):
            process = multiprocessing.Process(
                target=self._genkey, args=(sharedcount, foundcount, threadid))
            process.start()
            self.multilist.append(process)

        print(f'{len(self.multilist)} processes have started')
        self._waiting(sharedcount, foundcount)

    def status(self, sharedcount, foundcount):
        """
        Placeholder method to display the current status. Can be overridden in a subclass.

        Args:
        sharedcount: Shared counter for tracking key generation progress.
        foundcount: Shared counter for tracking the number of keys found.
        """

    def _waiting(self, sharedcount, foundcount):
        """
        Wait for the generation process to complete.
        """

        while foundcount.value < self.findtotal:
            self.status(sharedcount, foundcount)
            time.sleep(5)

        for process in self.multilist:
            process: multiprocessing.Process
            process.join()

        print('Done')

    def stop(self):
        """
        Stop the vanity key generation process.
        """

        self.findtotal = 0

if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("findstrings", help="String we are looking for", nargs='*')
    parser.add_argument('-l', help='Keep the case', action='store_true', default=False)
    parser.add_argument('-n', help='Number of keys to find', type=int, default=1)
    parser.add_argument('-p', help='Passphrase', type=str, default=None)
    parser.add_argument('-c', help='Comment', type=str, default=None)
    parser.add_argument('-t', help='Number of cores to use', type=int, default=None)
    parser.add_argument('-r', help='Number of rounds to use for passphrase', type=int, default=16)
    args = parser.parse_args()

    class LocalRun(SSHVanityGen):
        """
        Subclass of SSHVanityGen for local testing and customization.

        Methods:
        foundone(threadid, localcount, find, pubkey):
            Handle a found SSH key.

        status(sharedcount, foundcount):
            Display the current status.
        """

        def foundone(self, threadid, localcount, find, pubkey):
            """
            Handle a found SSH key.

            Args:
            threadid: Identifier of the process.
            localcount: Local count of generated keys.
            find: The vanity pattern found.
            pubkey: The public key associated with the vanity pattern.
            """

            print(threadid, localcount, find, pubkey,)

        def status(self, sharedcount, foundcount):
            """
            Display the current status.

            Args:
            sharedcount: Shared counter for tracking key generation progress.
            foundcount: Shared counter for tracking the number of keys found.
            """

            print(
                f'Keys Generated: {sharedcount.value}, Keys Found: {foundcount.value}')
    
    if args.findstrings:
        run = LocalRun(args.findstrings, args.l, args.n, args.p, args.c, args.t, args.r)
        run.start()
    else:
        print('Need at least one word to search for, please use --help for more information')
