#!/usr/bin/env python3
# !coding=utf-8
import paramiko

import os
import stat
import traceback


class connectServer:
    # global ip, user, passwd, port
    # ip = rc.get_localService("host")
    # user = rc.get_localService("username")
    # passwd = rc.get_localService("password")
    # port = rc.get_localService("port")

    def __init__(self):
        pass

    def connect_ssh(self,ip,user,passwd,command):
        # 创建SSH对象
        ssh=paramiko.SSHClient()
        # 允许连接不在unknown的主机
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        # 连接ssh服务
        ssh.connect(hostname=ip,port=22,username=user,password=passwd)
        # stdin为输入的命令
        # stdout为命令返回的结果
        # stderr为命令错误时返回的结果
        cmd="echo %s | sudo -S %s" %(passwd,command)
        stdin,stdout,stderr=ssh.exec_command(command=cmd,timeout=300,bufsize=100)
        res,err=stdout.read(),stderr.readlines()
        if len(err) >0 and err[0] =="[sudo] password for install":
            print("connect_ssh ERROR ——>>"+err[0])

        ssh.close()
        return res

    def connect_sshNoRes(self,ip,user,passwd,command):
        # 创建SSH对象
        ssh=paramiko.SSHClient()
        # 允许连接不在unknown的主机
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        # 连接ssh服务
        ssh.connect(hostname=ip,port=22,username=user,password=passwd)
        # stdin为输入的命令
        # stdout为命令返回的结果
        # stderr为命令错误时返回的结果
        cmd="echo %s | sudo -S %s" %(passwd,command)
        ssh.exec_command(command=cmd,timeout=300,bufsize=100)

        ssh.close()

    # 将本地的文件上传到 远端服务器
    def sftp_put(self,ip,user,passwd,localfile,remoteFile):

        try:
            scp=paramiko.Transport(ip,22)
            scp.connect(username=user,password=passwd)
            sftp=paramiko.SFTPClient.from_transport(scp)
            sftp.put(localfile,remoteFile)
            scp.close()
        except Exception as e:
            print("sftp_put ERROR ——>>%s" %e)

    # 将远端的文件拉取到本地服务器
    def sftp_get(self,ip,user,passwd,localfile,remoteFile):
        try:
            scp=paramiko.Transport(ip,22)
            scp.connect(username=user,password=passwd)
            sftp=paramiko.SFTPClient.from_transport(scp)
            sftp.get(localfile,remoteFile)
            scp.close()
        except Exception as e:
            print("sftp_get ERROR ——>>%s" %e)

    def _get_all_files_in_remoteDir(self,sftp,remoteDir):
        all_files=list()
        if remoteDir[-1] == "/":
            remoteDir = remoteDir[0:-1]
        files=sftp.listdir_attr(remoteDir)

        for file in files:
            filename=remoteDir+'/'+file.filename

            if stat.S_ISDIR(file.st_mode):
                all_files.extend(self._get_all_files_in_remoteDir(sftp,filename))
            else:
                all_files.append(filename)
        return all_files

    # 代码暂未调用到，需调试
    def getFilesByDir(self,ip,user,passwd,remoteDir,localDir):
        try:
            scp=paramiko.Transport(ip,22)
            scp.connect(username=user,password=passwd)
            sftp=paramiko.SFTPClient.from_transport(scp)
            allFiles=self._get_all_files_in_remoteDir(sftp,remoteDir)
            for file in allFiles:
                local_filename=file.replace(remoteDir,localDir)
                local_path=os.path.dirname(local_filename)
                if not os.path.exists(local_path):
                    os.makedirs(local_path)

                sftp.get(file,local_filename)
        except:
            print(traceback.format_exc())


    def _get_all_files_in_localDir(self,localdir):
        all_files = list()

        for root, dirs, files in os.walk(localdir, topdown=True):
            for file in files:
                filename = os.path.join(root, file)
                all_files.append(filename)




        return all_files

    # 暂未调用到
    def putFilesByDir(self,ip,user,passwd,remoteDir,localDir):
        try:
            scp = paramiko.Transport(ip, 22)
            scp.connect(username=user, password=passwd)
            sftp = paramiko.SFTPClient.from_transport(scp)

            if remoteDir[-1] == "/":
                remoteDir = remoteDir[0:-1]

            all_files = self._get_all_files_in_localDir(localDir)


            for file in all_files:

                remote_filename=file.replace(localDir,remoteDir)
                remote_filepath=os.path.dirname(remote_filename)
                try:
                    sftp.stat(remote_filepath)
                except:
                    # os.popen('mkdir -p %s' % remote_filepath)
                    self.connect_ssh(ip,user,passwd,'mkdir -p {remotePath};chown -R install {remotePath};chgrp -R install {remotePath}'.format(remotePath=remote_filepath))

                sftp.put(file, remote_filename)
            # sftp.put("/data1/tools/newAutoTest/waiter/sql/DW_AI_PROCESS_MEM.sql", "/data1/tools/newTest/waiter/sql/DW_AI_PROCESS_MEM.sql")
            scp.close()
        except:
            print(traceback.format_exc())



