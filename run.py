from datetime import datetime
import os
import time

from config import app
from flask import render_template
import psutil
import socket
import platform
from common.getSvrInfo import serverInfo

global svrip
svrip="172.16.10.29"


@app.route('/sys/')
def sys():
    now_time= datetime.now()  # 现在时间
    start_time=datetime.fromtimestamp(psutil.boot_time()) # 开机时间
    syss={
    'system':platform.system(), #操作系统
    'version':platform.version(), #系统版本号
    'architecture':platform.architecture(), #位数
    'machine':platform.machine(), #类型
    'processor':platform.processor(), #处理器信息
    'run_time':str(now_time-start_time).split('.')[0]  #运行时间
    }
    # run_time=datetime.datetime.fromtimestamp(now_time-start_time)   #运行时间
    return render_template('sys.html',now_time=str(now_time).split('.')[0],start_time=start_time,
                           syss=syss)

@app.route('/cpu/')
def cpu():
    now_time = datetime.now()  # 现在时间
    running_pro,get_ctx_sw,get_inter=serverInfo.get_cpu_stats()
    cpu={
    'p_CPU':psutil.cpu_count(logical=False),
    'CPU':psutil.cpu_count(),
    'cpu_util':psutil.cpu_percent(interval=None),
    'averageload_1':psutil.getloadavg()[0],
    'averageload_5':psutil.getloadavg()[1],
    'averageload_15':psutil.getloadavg()[2],
    'user':psutil.cpu_times_percent().user,
    'system':psutil.cpu_times_percent().system,
    'iowait':psutil.cpu_times_percent().iowait,
    'running_pro':running_pro,
    'ctx_switch':get_ctx_sw,
    'interrupts':get_inter
    }
    # print(serverInfo.get_cpu_stats())
    return render_template('cpu.html',now_time=str(now_time).split('.')[0],cpu=cpu)

@app.route('/ram/')
def ram():
    now_time = datetime.now()  # 现在时间
    ram={
    'memmorySize':round(psutil.virtual_memory().total/(1024**3),3),
    'available':round(psutil.virtual_memory().available/(1024**3),3),
    'percent':psutil.virtual_memory().percent,
    'used':round(psutil.virtual_memory().used/(1024**3),3),
    'free':round(psutil.virtual_memory().free/(1024**3),3),
    'swap_total':round(psutil.swap_memory().total/(1024**3),3),
    'swap_used':round(psutil.swap_memory().used/(1024**3),3),
    'swap_free':round(psutil.swap_memory().free/(1024**3),3),
    'swap_percent':psutil.swap_memory().percent
    }
    return render_template('ram.html',now_time=str(now_time).split('.')[0],ram=ram)

@app.route('/disk/')
def disk():
    disks=psutil.disk_partitions()
    return render_template('disk.html',disks=disks)

@app.route('/sysio/')
def sysiodisk():
    now_time = datetime.now()  # 现在时间
    # 获取系统盘IO的流量信息
    get_sys_tps_info, get_sys_readIO_info, get_sys_wrthIO_info = serverInfo.get_sys_io_flow_info()

    # 吞吐量
    get_sys_read,get_sys_write=serverInfo.get_sys_io_throughout_info()
    # 获取系统盘IO的响应信息
    get_sys_await_info, get_sys_svctm_info, get_sys_util_info = serverInfo.get_sys_io_response_info()


    sysio={
        'sys_tps':get_sys_tps_info,
        'sys_read':get_sys_read,
        'sys_write':get_sys_write,
        'sys_await':get_sys_await_info,
        'sys_avctm':get_sys_svctm_info,
        'sys_util':get_sys_util_info
    }
    return render_template('sysio.html',now_time=str(now_time).split('.')[0],sysio=sysio)


@app.route('/dataio/')
def dataiodisk():
    now_time = datetime.now()  # 现在时间
    # 获取数据盘IO的流量信息
    get_data_tps_info, get_data_readIO_info, get_data_wrthIO_info = serverInfo.get_data1_io_flow_info()

    # 获取数据盘IO的响应信息
    get_data_await_info, get_data_svctm_info, get_data_util_info = serverInfo.get_data1_io_response_info()

    get_data_read,get_data_write=serverInfo.get_data_io_throughout_info()

    dataio={
        'data_tps':get_data_tps_info,
        'data_read':get_data_read,
        'data_write':get_data_write,
        'data_await':get_data_await_info,
        'data_avctm':get_data_svctm_info,
        'data_util':get_data_util_info
    }
    return render_template('dataio.html',now_time=str(now_time).split('.')[0],dataio=dataio)

@app.route('/netio/')
def networkio():
    now_time = datetime.now()  # 现在时间
    get_net_rpck, get_net_tpck, get_net_receiver, get_net_transfer, get_net_util = serverInfo.get_net_io_trans_info(
        svrip)
    print(get_net_rpck, get_net_tpck, get_net_receiver, get_net_transfer, get_net_util)
    netio={
        'net_rpck': get_net_rpck,
        'net_tpck': get_net_tpck,
        'net_receiver': get_net_receiver,
        'net_transfer': get_net_transfer,
        'net_util': get_net_util
    }
    return render_template('netio.html',now_time=str(now_time).split('.')[0],netio=netio)

@app.route('/process/')
def process():
     # pid=psutil.pids()[:20]
     processes=[]
     get_pid = serverInfo.get_cmd_info("ps -aux --sort -pmem |head -n 11|awk {'print $2'}").split("\n")[1:-1]

     for i in range(len(get_pid)):
         p=psutil.Process(int(get_pid[i]))

         processes.append((int(get_pid[i]),p.status(),round(p.memory_percent(),3),round(p.cpu_percent(interval=0.5),3),round(p.memory_info().rss/(1024**3),3)))
     return render_template('process.html',processes=processes)
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)
