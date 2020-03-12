#!/usr/bin/python3
# !coding=utf-8
# __author__='Zhang Liangdong'
# Date:2020/3/5 16:05
# fileName:getSvrInfo.py
import os
import psutil


class sysExecuted:

    def __init__(self):
        self.args="get svrInformation From cmd by os.system()"


    @classmethod
    def get_cmd_info(cls,cmd):
        """
        :param cmd: 入参指令
        :return: 获取本地服务器指令执行的结果并转换为str类型
        """
        output = os.popen(cmd).read()
        return output


    # 查找输入的PID进程,保证指令查询出来的唯一性，如果不唯一返回第一个PID
    @classmethod
    def getpsauxPID(cls,cmd):
        """
        :param cmd:  需要查找进程的指令
        :return: 返回PID进程
        """
        try:
            output=os.popen("ps aux | grep %s |grep -v 'grep'|grep 'java'" %cmd).read()
            # outputt=os.popen("/usr/bin/jps|grep DfsWebMain|awk '{print $1}'" %cmd)

            # output=outputt.read()

            if output is not None:

                for line in output.splitlines():
                    if cmd in line:
                        pid=int(line.split()[1])
                        return pid
                    break
            else:
                print("未查询出对应的进程信息！")
                return 0

        except Exception as ex:
            print(">>>>>>>>>>>>>>>>>>出错!请查看原因：%s<<<<<<<<<<<<<<<<<<<<" %ex)
            # print(">>>>>>>>>>>>>>>>>>>>>>DEBUG:" %ex)
            return 0

class serverInfo(sysExecuted):


    def __init__(self):
        super().__init__()
        self.args="get svrInformation From psutil"


    @classmethod
    def get_network_name(cls,serverIP):
        """
        [snicaddr(family=<AddressFamily.AF_INET: 2>, address='172.16.10.29', netmask='255.255.255.0', broadcast='172.16.10.255', ptp=None),
        snicaddr(family=<AddressFamily.AF_INET6: 10>, address='fe80::ec4:7aff:feda:9985%enp5s0', netmask='ffff:ffff:ffff:ffff::', broadcast=None, ptp=None),
        snicaddr(family=<AddressFamily.AF_PACKET: 17>, address='0c:c4:7a:da:99:85', netmask=None, broadcast='ff:ff:ff:ff:ff:ff', ptp=None)]

        :param serverIP:对应IP
        :return:返回网卡名称，如果不存在网卡则返回None
        """

        netName=None
        getNetInfo=psutil.net_if_addrs()

        for ky,vl in getNetInfo.items():
            for i in range(len(vl)):
                if serverIP == vl[i][1]:

                    netName=ky
        return netName

    @classmethod
    def get_total_load_info(cls):
        """
        获取系统负载的总阈值，也可以直接查询CPU的个数
        :return:
        """
        # 获取负载总阈值,备用,暂时不用
        get_total_load=float(cls.get_cmd_info("cat /proc/cpuinfo |grep 'model name' -c"))

        return get_total_load


    @classmethod
    def get_net_io_trans_info(cls,svrIP):
        """
        sar -n DEV 1 1|grep ens160|awk '{print $1,$7,$11}',单位kb
        吞吐量:表示单位时间内成功传输的数据量，单位通常为 b/s（比特 / 秒）或者B/s（字节 / 秒）。
        吞吐量受带宽限制，而吞吐量 / 带宽，也就是该网络的使用率
        get_net_receiver: rxbyt/s：每秒钟接收到的字节数
        get_net_transfer: txbyt/s：每秒钟发送出去的字节数

        PPS：是 Packet Per Second（包 / 秒）的缩写，表示以网络包为单位的传输速率。
        PPS 通常用来评估网络的转发能力
        get_net_rpck rxpck/s：每秒钟接收到的包数目
        get_net_tpck txpck/s：每秒钟发送出去的包数目

        get_net_util: %ifutil 是网络接口的使用率
        :return:
        """
        try:
            netName=cls.get_network_name(svrIP)

            if netName is None:
                print(">>>>>>>>>>>>>>>>>>>>>get_net_io_trans_info get no Net Card!")

                return 0.0, 0.0, 0.0, 0.0, 0.0

            else:

                getInfo = cls.get_cmd_info("sar -n DEV 1 1|grep %s|awk '{print $3,$4,$5,$6,$7,$11}'" % netName)

                if getInfo != '':

                    get_net_rpck = float(getInfo.split("\n")[0].split(" ")[1])
                    get_net_tpck = float(getInfo.split("\n")[0].split(" ")[2])

                    get_net_receiver = float(getInfo.split("\n")[0].split(" ")[3])
                    get_net_transfer = float(getInfo.split("\n")[0].split(" ")[4])

                    get_net_util = float(getInfo.split("\n")[0].split(" ")[5])
                    return get_net_rpck, get_net_tpck, get_net_receiver, get_net_transfer, get_net_util
                else:
                    print(">>>>>>>>>>>>>>>>>>>get_net_io_trans_info no Network Information!")
                    return 0.0, 0.0, 0.0, 0.0, 0.0

        except Exception as ex:
            print(ex)




    @classmethod
    def get_server_load_from_psutil(cls):

        """
        本方法基于psutil==5.7.0,以下版本不确定是否存在该方法，慎用！
        :return:获取一分钟，五分钟，十五分钟的负载
        Return the average system load over the last 1, 5 and 15 minutes as a tuple
        """
        getInfo=psutil.getloadavg()
        get_oneMin_load=getInfo[0]
        get_fiveMins_load=getInfo[1]
        get_fifteenMins_load=getInfo[2]

        return get_oneMin_load,get_fiveMins_load,get_fifteenMins_load


    @classmethod
    def get_cpu_stats(cls):

        """
        查询CPU的状态，整体任务的上下文切换数，系统中断数据，软连接中断数
        :return:软连接暂时不用
        """
        #
        # ctx_s=psutil.cpu_stats().ctx_switches
        # in_count=psutil.cpu_stats().interrupts
        # soft_in=psutil.cpu_stats().soft_interrupts

        getInfo=cls.get_cmd_info("vmstat 1 2|awk '{print $1,$11,$12}'")

        return getInfo.split('\n')[-2].split(' ')[0],getInfo.split('\n')[-2].split(' ')[1],getInfo.split('\n')[-2].split(' ')[2]


    @classmethod
    def get_cpu_counts(cls):

        """
        查询CPU的个数，并非物理逻辑个数
        :return:
        """
        cpu_counts=psutil.cpu_count()
        return cpu_counts


    @classmethod
    def get_sys_io_throughout_info(cls):
        """

        :return: 获取系统IO的吞吐量，通过指令获取
        """

        getInfo=cls.get_cmd_info("iostat -d -x 1 2|grep sda|awk '{print $1,$6,$7}'")
        get_rkb=float(getInfo.split(" ")[3])
        get_wrkb=float(getInfo.split(" ")[4])

        return get_rkb,get_wrkb

    @classmethod
    def get_data_io_throughout_info(cls):
        """
        获取SDB所在的数据盘的信息，目前暂未看到有其他盘在服务器如有可适当修改下代码sdc
        代码兼容性可能存在某些问题
        :return: 获取数据盘（SDB）的IO的吞吐量，通过指令获取
        """
        getInfo=cls.get_cmd_info("iostat -d -x 1 2|grep sdb|awk '{print $1,$6,$7}'")
        if getInfo!='':
            get_rkb=float(getInfo.split(" ")[3])
            get_wrkb=float(getInfo.split(" ")[4])
        else:
            get_rkb='null'
            get_wrkb='null'

        return get_rkb,get_wrkb

    @classmethod
    def get_pid_io_info(cls,cmd):

        """
        暂不用
        :param cmd:  需要查找进程的指令
        :return:如果查询到进程，则返回如下参数，如果查询不到进程则返回0
        1、累加的读取操作次数，
        2、累加的写入操作次数
        3、累加读取的总量
        4、累加写入的总量
        """
        pid=cls.getpsauxPID(cmd)

        if pid==0:
            print(">>>>>>>>>>>>>>>>getSvrInfo.py can not Find The PID,cmd={}".format(cmd))
            return pid

        else:
            getInfo=psutil.Process(pid).io_counters()
            read_count=getInfo.read_count
            write_count=getInfo.write_count
            read_bytes=getInfo.read_bytes
            write_bytes=getInfo.write_bytes
            return read_count,read_bytes,write_count,write_bytes


    @classmethod
    def get_swap_si_so_info(cls):
        """
        获取swap的换进换出量值
        si：从内存写入SWAP的值
        so：从SWAP写入内存的值
        :return:
        """
        getInfo=cls.get_cmd_info("vmstat 1 2|awk '{print $7,$8}'")

        return getInfo.split('\n')[-2].split(' ')[0],getInfo.split('\n')[-2].split(' ')[1]

    @classmethod
    def get_sys_io_flow_info(cls):
        """

        :return: 获取IO的TPS，读取，写入的参数值
        """
        # getInfo=cls.get_cmd_info("iostat -d 1 2|grep sda|awk '{print $1,$2,$3,$4}'")
        getInfo = cls.get_cmd_info("iostat -d 1 2|grep sda|awk '{print $1,$2,$3,$4}'")
        get_tps_info = float(getInfo.split(" ")[4])
        get_readIO_info = float(getInfo.split(" ")[5])
        get_wrthIO_info = float(getInfo.split(" ")[6])

        return get_tps_info, get_readIO_info, get_wrthIO_info

    @classmethod
    def get_sys_io_response_info(cls):
        """
        :return: 获取IO响应值，svctm,util
        """
        getInfo = cls.get_cmd_info("iostat -d -x 1 2|grep sda|awk '{print $1,$10,$13,$14}'")
        get_await_info = float(getInfo.split(" ")[4])
        get_svctm_info = float(getInfo.split(" ")[5])
        get_util_info = float(getInfo.split(" ")[6])

        return get_await_info, get_svctm_info, get_util_info

    @classmethod
    def get_data1_io_flow_info(cls):
        """

        :return: 获取IO的TPS，读取，写入的参数值
        """
        getInfo = cls.get_cmd_info("iostat -d 1 2|grep sdb|awk '{print $1,$2,$3,$4}'")
        if getInfo != '':
            get_tps_info = float(getInfo.split(" ")[4])
            get_readIO_info = float(getInfo.split(" ")[5])
            get_wrthIO_info = float(getInfo.split(" ")[6])
        else:
            get_tps_info = 'null'
            get_readIO_info = 'null'
            get_wrthIO_info = 'null'

        return get_tps_info, get_readIO_info, get_wrthIO_info

    @classmethod
    def get_data1_io_response_info(cls):
        """
        :return: 获取IO响应值，svctm,util
        """
        getInfo = cls.get_cmd_info("iostat -d -x 1 2|grep sdb|awk '{print $1,$10,$13,$14}'")
        if getInfo != '':

            get_await_info = float(getInfo.split(" ")[4])
            get_svctm_info = float(getInfo.split(" ")[5])
            get_util_info = float(getInfo.split(" ")[6])
        else:
            get_await_info = 'null'
            get_svctm_info = 'null'
            get_util_info = 'null'

        return get_await_info, get_svctm_info, get_util_info


# if __name__ == '__main__':
#     get_pid=serverInfo.get_cmd_info("ps -aux --sort -pmem |head -n 11|awk {'print $2'}").split("\n")[1:-1]
#     # get_pid=[int(t[i]) for i in range(len(t[1:-1]))]
#
#     # get_pid=t[1:-1]
#
#     # tt=[int(get_pid[i]) for i in range(len(t))]
#
#
#
#     # print(tt)