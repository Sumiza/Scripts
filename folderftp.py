import ftplib
import os

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
        ftps.prot_p()
        print(ftps.getwelcome())
        return ftps
    
    def upload(self):
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
        os.chdir(root)
        for file in files:
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
                folder_file_abs = os.path.abspath(self.local_folder + file_folder_tree)
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
