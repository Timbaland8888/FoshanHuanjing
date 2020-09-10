#!/usr/bin/evn python
# -*- encoding:utf-8 -*-
# function: restart system
# date:2020-09-09
# Arthor:Timbaland

import win32api
def initpc(flag):
    if flag == 1 :
        try:
            win32api.InitiateSystemShutdown('localhost', '即将重启云桌面，重启后打开计算机重新授权，选择完全允许读写', 5, True, True)
        except Exception as e:
            print(e)

if __name__ == '__main__':
    flag = win32api.MessageBox(None, "重启后记得打开计算机磁盘重新授权，选择完全允许读写", "重启云桌面", 1)
    print(flag)
    initpc(flag)










