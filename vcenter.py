#!/usr/bin/evn python
# -*- encoding:utf-8 -*-
# function: connect exsi server api  for restart vm
# date:2019-08-09
# Arthor:Timbaland
import sys

_Arthur_ = 'Timbaland'
import pysphere, pymysql
from pysphere import VIServer
import logging
import ssl
import datetime, os, time
import configparser, codecs

# 全局取消证书验证,忽略连接VSPHERE时提示证书验证
ssl._create_default_https_context = ssl._create_unverified_context

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class VcentTools():

    def __init__(self, host_ip, user, password):
        self.host_ip = host_ip
        self.user = user
        self.password = password
        # self.flag = flag
    # 可以连接esxi主机，也可以连接vcenter

    def _connect(self):

        server_obj = VIServer()

    def esxi_version(self):
        server_obj = VIServer()
        try:
            server_obj.connect(self.host_ip, self.user, self.password)
            servertype, version = server_obj.get_server_type(), server_obj.get_api_version()
            server_obj.disconnect()
            return servertype, version
        except Exception as  e:
            print (e)

    def vm_status(self, vm_name):

        server_obj = VIServer()
        try:
            server_obj.connect(self.host_ip, self.user, self.password)
            # servertype, version = server_obj.get_server_type(),server_obj.get_api_version()


        except Exception as  e:
            print (e)

        # 通过名称获取vm的实例
        try:
            vm = server_obj.get_vm_by_name(vm_name)
            if vm.is_powered_off() == False:
                server_obj.disconnect()
                return 1

            if vm.is_powered_off() == True:
                server_obj.disconnect()
                return 2

        except Exception as e:
            server_obj.disconnect()
            return 3

    def vmaction(self, vm_name):

        server_obj = VIServer()
        try:
            server_obj.connect(self.host_ip, self.user, self.password)
        except Exception as  e:
            print (e)

        # 通过名称获取vm的实例
        try:
            vm = server_obj.get_vm_by_name(vm_name)
        except Exception as e:
            print(e)
            return 0
        if vm.is_powered_off() == False:
            try:
                # vm.reset()
                vm.power_off()

                # print (type(int(vm_hz)))
                # for i in range(1, int(vm_hz)):
                #     print (f'虚拟机{vm_name} 正在重置中。。。。，请等待注册\n' )
                #     time.sleep(1)
                # print ('重置完成')
                server_obj.disconnect()

                return 1
            except Exception as e:
                print (e)

        if vm.is_powered_off() == True:
            try:
                # vm.power_on()
                # print (f'虚拟机{vm_name} 正在开机中。。。。')
                server_obj.disconnect()

            except Exception as e:
                return 2
    def del_datas(self,vm_name,guster_user,guster_pwd,del_dir):
        server_obj = VIServer()
        try:
            server_obj.connect(self.host_ip, self.user, self.password)
        except Exception as  e:
            print(e)
        # 通过名称获取vm的实例
        try:
            vm = server_obj.get_vm_by_name(vm_name)
        except Exception as e:
            # print(e)
            return 0
        print(vm.get_tools_status())
        if vm.get_tools_status() == 'RUNNING': #判断tools状态
            print(f'{vm_name} tools is  RUNING--------------------')
            try :
                vm.login_in_guest(guster_user,guster_pwd)
                # vm.delete_directory(del_dir, recursive=True)  # 清空数据盘
                path_list = vm.list_files(del_dir)
                new_list = []
                #排除目录或文件
                not_list = ['.','..','$RECYCLE.BIN','pagefile.sys','pvsvm', 'size','System Volume Information','vdiskdif.vhdx','desktop.ini']
                for list_ctent in path_list:
                    if list_ctent['path'] not in not_list:
                        new_list.append(list_ctent)
                if len(new_list) > 0:
                    for filter_list in new_list:
                        print(filter_list)
                        if filter_list['type'] == 'file':
                            try:
                                vm.delete_file(del_dir+filter_list['path'])
                            except Exception as e:
                                print(e)
                        if filter_list['type'] == 'directory':
                            try:
                                vm.delete_directory(del_dir + filter_list['path'],recursive=True)
                            except Exception as e:
                                print(e)


            except Exception as e:
                print(e)

            finally:

                print(f'{vm_name} 数据盘清空完毕！！！！！')
        else:
            print(f'{vm_name} tools is not RUNING--------------------')



