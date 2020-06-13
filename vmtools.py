#!/usr/bin/evn python
# -*- encoding:utf-8 -*-
# function: connect exsi server api  for restart vm
# date:2019-08-09
# Arthor:Timbaland
import sys

import logging
import ssl
import pymysql
import json
import configparser
import codecs
import time
import requests
import ctypes
requests.packages.urllib3.disable_warnings()
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import progressbar
from  vcenter import VcentTools
_Arthur_ = 'Timbaland'
# 全局取消证书验证,忽略连接VSPHERE时提示证书验证
ssl._create_default_https_context = ssl._create_unverified_context

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Class_VM(object):
    STD_INPUT_HANDLE = -10
    STD_OUTPUT_HANDLE = -11
    STD_ERROR_HANDLE = -12
    FOREGROUND_RED = 0x0c  # red.
    FOREGROUND_GREEN = 0x0a  # green.
    FOREGROUND_BLUE = 0x09  # blue.
    # get handle
    std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    def __init__(self, host, user, pwd, port, db, charset):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.port = port
        self.db = db
        self.charset = charset
    @staticmethod
    def vm_progess(vm_name:str,vm_hz:int):
        # 自定义
        widgets = [
            f'{vm_name}关机进度',
            progressbar.Percentage(),
            progressbar.Bar(marker='='),
        ]
        bar = progressbar.ProgressBar(widgets=widgets, max_value=100).start()
        for i in range(vm_hz*10):
            # do something
            time.sleep(0.1)
            bar.update(i + 1)
        bar.finish()

    # 获取教室里面的虚拟机信息
    def get_vmname(self, query_sql):
        try:
            # 连接mysql数据库参数字段
            con = None
            db = pymysql.connect(host=self.host, user=self.user, passwd=self.pwd, db=self.db, port=self.port,
                                 charset=self.charset)
            cursor = db.cursor()
            vmlist = []
            cursor.execute(query_sql)
            result = cursor.fetchall()
            # 获取教室云桌面数量
            vm_count = len(result)
            print (f'教室云桌面虚拟机数量共{vm_count}台')

            # print len(cursor.fetchall())
            # cursor.execute(query_vm)
            for vm_id in range(0, vm_count, 1):
                # print result[vm_id][0]
                # print result[vm_id][1]
                vmlist.append(result[vm_id])
                # print result[vm_id][0]

            # print type(cursor.fetchall()[0])

            db.commit()

        except ValueError:
            db.roolback
            print ('error')
        # 关闭游标和mysql数据库连接
        cursor.close()
        db.close()
        return vmlist

    def vm_action(self):

        cf = configparser.ConfigParser()
        cf.read_file(codecs.open('config.ini', "r", "utf-8-sig"))
        # 查询教室虚拟机
        query_vm = f''' SELECT vm.vm_name from hj_vm vm
                        INNER JOIN hj_dg dg on vm.dg_id=dg.id 
						INNER JOIN hj_classroom room on room.id=dg.classroom_id and room.del_flag='0'
                        WHERE vm.vm_type=1 and vm.del_flag='0' '''

        def vm_shutdown():
            vc = VcentTools(cf.get('vc', 'vc_ip'),cf.get('vc', 'vc_acount'),cf.get('vc', 'vc_pwd'))

            for vmname in self.get_vmname(query_vm):
                # for hz in range(1, int(cf.get('vm_hz', 'vm_hz'))):
                #     Class_VM.printDarkBlue(f'正在重置虚拟机ID:{vmname[0]} <<<<===========>>>> 虚拟机名称:{vmname[1]} \n', Class_VM.FOREGROUND_GREEN)
                #     time.sleep(1)

                k  = vc.vmaction(vmname[0])
                Class_VM.printDarkBlue(f'正在关闭虚拟机机 <<<<===========>>>> {vmname[0]} \n',
                                       Class_VM.FOREGROUND_GREEN)
                Class_VM.vm_progess(vmname[0],int(cf.get('vm_hz', 'vm_hz')))
                time.sleep(1)
        # 配置调度
        Class_VM.printDarkBlue(f"<<<<<<<<<---重启时间：{cf.get('time', 'hour')}时:{cf.get('time', 'minute')}分:{cf.get('time', 'second')}秒--->>>>>>>>>>  \n", Class_VM.FOREGROUND_BLUE)
        # print()
        scheduler = BlockingScheduler()
        # pd.class_vmreset()
        # scheduler.add_job(vmaction, 'cron', hour=int(cf.get('time', 'hour')), minute=int(cf.get('time', 'minute')))
        # scheduler.start()
        trigger = CronTrigger(day_of_week='mon-sun', hour=int(cf.get('time', 'hour')), minute=int(cf.get('time', 'minute')), second=int(cf.get('time', 'second')))
        # 查询虚拟机信息
        scheduler.add_job(vm_shutdown,trigger)
        scheduler.start()

    def vm_del_d(self,classroom):
        cf = configparser.ConfigParser()
        cf.read_file(codecs.open('config.ini', "r", "utf-8-sig"))
        vc = VcentTools(cf.get('vc', 'vc_ip'), cf.get('vc', 'vc_acount'), cf.get('vc', 'vc_pwd'))
        # 查询教室虚拟机
        query_vm = f''' SELECT vm.vm_name from hj_vm vm
                        INNER JOIN hj_dg dg on vm.dg_id=dg.id 
                        INNER JOIN hj_classroom room on room.id=dg.classroom_id and room.del_flag='0' and room.classroom_name='{classroom}'
                        WHERE vm.vm_type=1 and vm.del_flag='0' '''
        # print(query_vm)
        for vmname in self.get_vmname(query_vm):
            print(f'正在清理{classroom}教室：中虚拟机{vmname[0]}数据盘')
            vc.del_datas(vmname[0],cf.get('gust_vm','guster_user'),cf.get('gust_vm','guster_pwd'),cf.get('disk_path','disk_path'))

        # print(cf.get('gust_vm','guster_user'),cf.get('gust_vm','guster_pwd'),cf.get('disk_path','disk_path'))




    @staticmethod
    def set_cmd_text_color(color, handle=std_out_handle):
        Bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
        return Bool

    @staticmethod
    def resetColor(color):
        Class_VM.set_cmd_text_color(color)
    @staticmethod
    def printDarkBlue(mess,color):
        Class_VM.set_cmd_text_color(color)

        sys.stdout.write(mess)
        Class_VM.resetColor(color)