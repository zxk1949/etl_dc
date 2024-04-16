import sys,os,ftplib,socket,hashlib
print("=====================FTP客户端=====================");
HOST = ''  # FTP主机地址
username = ''  # 用户名
password = ''  # 密码
buffer_size = 8192  # 缓冲区大小


# 连接登陆
class FtpUpload():
    def connect(self):
        try:
            ftp = ftplib.FTP(HOST)  # 实例化FTP对象
            ftp.login(username, password)  # 登录
            ftp.set_pasv(False)  # 如果被动模式由于某种原因失败，请尝试使用活动模式。
            print(ftp.getwelcome())
            print('已连接到： %s' % HOST)
            return ftp
        except (socket.error,socket.gaierror):
            print("FTP登陆失败，请检查主机号、用户名、密码是否正确")
            sys.exit(0)

    # 获取目录下文件或文件夹详细信息
    def dirInfo(ftp):
        ftp.dir()

    # 获取目录下文件或文件夹的列表信息，并清洗去除“. ..”
    def nlstListInfo(ftp):
        files_list = ftp.nlst()
        return [file for file in files_list if file != "." and file !=".."]

    # 判断文件与目录
    def checkFileDir(ftp,file_name):
        """
        判断当前目录下的文件与文件夹
        :param ftp: 实例化的FTP对象
        :param file_name: 文件名/文件夹名
        :return:返回字符串“File”为文件，“Dir”问文件夹，“Unknow”为无法识别
        """
        rec = ""
        try:
            rec = ftp.cwd(file_name)   # 需要判断的元素
            ftp.cwd("..")   # 如果能通过路劲打开必为文件夹，在此返回上一级
        except ftplib.error_perm as fe:
            rec = fe # 不能通过路劲打开必为文件，抓取其错误信息
        finally:
            if "Not a directory" in str(rec):
                return "File"
            elif "Current directory is" in str(rec):
                return "Dir"
            else:
                return "Unknow"
    # 获取当前路径
    def pwdinfo(ftp):
        pwd_path = ftp.pwd()
        print("FTP当前路径:", pwd_path)
        return ftp.pwd()
    # 上传文件
    def upload(ftp, filepath,file_name = None):
        """
        上传  文件
        :param ftp: 实例化的FTP对象
        :param filepath: 上传文件的本地路径
        :param file_name: 上传后的文件名（结合fileNameMD5()方法用）
        :return:
        """
        f = open(filepath, "rb")
        if file_name == None:
            file_name = os.path.split(filepath)[-1]

        if find(ftp, file_name) or file_name == "无后缀格式的文件":
            print("%s 已存在或识别为无后缀格式的文件,上传终止"%file_name) # 上传本地文件,同名文件会替换
            return False
        else:
            try:
                ftp.storbinary('STOR %s'%file_name, f, buffer_size)
                print('成功上传文件： "%s"' %file_name)
            except ftplib.error_perm:
                return False
        return True