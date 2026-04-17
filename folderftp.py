import ftplib
import os
import ssl

class FolderFtps():

    def __init__(self,url:str, port:int,username:str,password:str,local_folder:str=None,remote_folder:str='',timeout:int=20):
        self.url = url
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.local_folder = local_folder or os.getcwd()
        self.remote_folder = remote_folder
        self.ftp = None

    def ftps_connect(self) -> ftplib.FTP_TLS:
        ftps = ftplib.FTP_TLS(timeout=self.timeout)
        ftps.connect(self.url,self.port)
        ftps.login(self.username,self.password)
        setprot= ftps.prot_p()
        print(setprot)

        assert setprot.startswith('200')
        assert isinstance(ftps.sock, ssl.SSLSocket)

        with ftps.transfercmd("LIST") as conn:
            assert isinstance(conn,ssl.SSLSocket)
            while conn.recv(5000):
                pass
        ftps.voidresp()

        print(ftps.getwelcome())
        return ftps
    
    def upload(self):
        # if self.ftp.sock is None 
        self.ftp = self.ftps_connect()

        for root,dirs,files in os.walk(self.local_folder):
            os.chdir(self.local_folder)
            self.ftp.cwd('/'+ self.remote_folder)
            working_remote_folder = root.removeprefix(self.local_folder).replace('\\','/').removeprefix('/')
            self.ftp.cwd(working_remote_folder)
            self.make_remote_folder(dirs)
            self.upload_file(files,root)

        self.ftp.quit()
    

    def upload_file(self,files:list,root:str):
        def get_remote_file_size(file:str):
            try:
                return self.ftp.size(file)
            except ftplib.error_perm:
                return None
            
        os.chdir(root)
        for file in files:
            if os.path.getsize(file) == get_remote_file_size(file):
                print(f"Duplicate file {file}")
                continue
            with open(file,'rb') as f:
                self.ftp.storbinary(f'STOR {file}',f)
                print(f'Uploaded {file}')

    def make_remote_folder(self,folders:list):
        for folder in folders:
            try:
                self.ftp.mkd(folder)
                print(f'Made folder {folder}')
            except ftplib.error_perm: 
                    print(f'Folder {folder} already exists')

    def download(self):
        self.ftp = self.ftps_connect()

        def recursive_folders(folder:str):
            for file_folder, data in self.ftp.mlsd(folder):
                file_folder_tree = folder + '/' + file_folder
                folder_file_abs = os.path.abspath(
                    (self.local_folder + file_folder_tree).replace(self.remote_folder,''))
                os.makedirs(os.path.dirname(folder_file_abs),exist_ok=True)
                if data['type'] == 'dir':
                    recursive_folders(file_folder_tree)
                if data['type'] == 'file':
                    if os.path.exists(folder_file_abs) and os.path.getsize(folder_file_abs) == int(data['size']):
                        print(f"Duplicate file {folder_file_abs}")
                    else:
                        with open(folder_file_abs,'wb') as f:
                            self.ftp.retrbinary(f'RETR {file_folder_tree}',lambda data: f.write(data))
                            print(f'Wrote file {folder_file_abs}')
        recursive_folders(self.remote_folder)

        self.ftp.quit()
    
    def remove_from_remote(self):
        self.ftp = self.ftps_connect()
        folderlist = []
        def recursive_folders(folder:str):
            for file_folder, data in self.ftp.mlsd(folder):
                file_folder_tree = folder + '/' + file_folder
                folder_file_abs = os.path.abspath(
                    (self.local_folder + file_folder_tree).replace(self.remote_folder,''))
                if data['type'] == 'dir':
                    if not os.path.exists(folder_file_abs):
                        print('deleting', file_folder_tree)
                        folderlist.append(file_folder_tree)
                    recursive_folders(file_folder_tree)
                if data['type'] == 'file':
                    if not os.path.exists(folder_file_abs):
                        print('deleting', file_folder_tree)
                        self.ftp.delete(file_folder_tree)
        recursive_folders(self.remote_folder)

        for folder in folderlist[::-1]:
            self.ftp.rmd(folder)
        self.ftp.quit()

    def remove_from_local(self):
        # if self.ftp.sock is None 
        self.ftp = self.ftps_connect()

        folderlist = []

        for root,_,files in os.walk(self.local_folder):
            os.chdir(self.local_folder)
            os.chdir(root)
            self.ftp.cwd('/'+ self.remote_folder)
            working_remote_folder = root.removeprefix(self.local_folder).replace('\\','/').removeprefix('/')
            
            try:
                self.ftp.cwd(working_remote_folder)
            except ftplib.error_perm as e:
                if 'No such file or directory' in str(e):
                    print('deleting dir', working_remote_folder)
                    folderlist.append(working_remote_folder)

            for file in files:
                try:
                    self.ftp.size(file)
                except ftplib.error_perm as e:
                    if 'No such file or directory' in str(e):
                        print(f"deleting file {file}")
                        os.remove(file)

        os.chdir(self.local_folder)
        for folder in folderlist[::-1]:
            os.rmdir(os.path.abspath(self.local_folder + '/' + folder))

        self.ftp.quit()

if __name__ == '__main__':
    ftp = FolderFtps(
        'ftp.server.com',
        990,
        'username',
        'password',
        '/home/user/',
        'userfolder',
        30
    )
