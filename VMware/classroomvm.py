#!/usr/bin/evn python
# -*- encoding:utf-8 -*-
# function: connect exsi server api  for restart vm
# date:2020-06-09
# Arthor:Timbaland

from tkinter import *
from tkinter import ttk
from tkinter.messagebox import  showwarning
from  con_mysql import Con_mysql
import ctypes,sys
import configparser
import codecs
from vmtools import Class_VM

class Wroot():

    STD_INPUT_HANDLE = -10
    STD_OUTPUT_HANDLE = -11
    STD_ERROR_HANDLE = -12
    FOREGROUND_RED = 0x0c  # red.
    FOREGROUND_GREEN = 0x0a  # green.
    FOREGROUND_BLUE = 0x09  # blue.
    # get handle
    std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    def __init__(self,title,pic,width,height,backgroud):
        cf = configparser.ConfigParser()
        cf.read_file(codecs.open('config.ini', "r", "utf-8-sig"))
        self.title = title
        self.pic = pic
        self.width = width
        self.height = height
        self.backgroud = backgroud
        # print(f"注意：1、确保本地电脑可以ping通vcenter ->>> {cf.get('vc1', 'vc_ip')} \n")
        Wroot.printDarkBlue(f"注意：1、程序所在classroom文件下的config.ini配置文件是否正确 ->>>  \n\n",Wroot.FOREGROUND_RED)
        # print(f"注意：2、确保本地电脑可以ping通汇捷 ->>>{cf.get('hj_db', 'db_host')} \n")
        Wroot.printDarkBlue(f"注意：2、确保本地电脑可以访问汇捷 ->>>{cf.get('hj_db', 'db_host')} \n\n",Wroot.FOREGROUND_RED)
        # print(os.popen('ping 192.168.93.2').read())
        # print(os.popen('ping 192.168.93.168').read())
        # print(f'注意：3、请选择对应的教室重启云桌面,清理桌面 \n')
        Wroot.printDarkBlue(f'注意：3、请选择教室重启云桌面,清理桌面 \n\n',Wroot.FOREGROUND_RED)
        # print(f'注意：4、技术问题请联系轩辕网络股份有限公司工程师\n')
        Wroot.printDarkBlue(f'注意：4、技术问题请联系轩辕网络股份有限公司工程师\n',Wroot.FOREGROUND_RED)
        Wroot.printDarkBlue('\n\n', Wroot.FOREGROUND_GREEN)
        self.setUI()

    #初始化窗口
    def setUI(self):

        def _selection1():
            button_yes.place(x=140, y=180)
            r1.config(bg='red')  # 让对象l显示括号里的内容
            show_help.config(text='提示:  ' + var.get(), fg='blue')
            r2.config(bg='#C0FF3E')


        def _selection2():
            button_yes.place(x=140, y=180)
            r2.config(bg='red')  # 让对象l显示括号里的内容
            show_help.config(text='提示:  ' + var.get(),fg='blue')
            r1.config(bg='#C0FF3E')
            # showwarning('警告','暂时不开放清空数据盘，有空再加')
        def run():  # 处理事件，*args表示可变参数

            # os.system(r'wscript .\rename.vbs %s\%s' % (sharedir, sname))
            # print(comboxlist.get())  # 打印选中的值
            classroom = comboxlist.get()
            # # classroom = 'c406-1 -->WIN7406
            classroom,pvs_vdisk = classroom.split('<-->')
            classroom = classroom.strip()
            #判断是该重置虚拟机还是清空数据盘
            if var.get() == '定时重置所有教室桌面' :
                root.withdraw()
                cf = configparser.ConfigParser()
                cf.read_file(codecs.open('config.ini', "r", "utf-8-sig"))
                p = Class_VM(cf.get('hj_db', 'db_host'), cf.get('hj_db', 'db_user'), cf.get('hj_db', 'db_pwd'),
                             cf.getint('hj_db', 'db_port'), cf.get('hj_db', 'db'), 'utf8')
                p.vm_action()
                # button_yes.destroy()





            elif var.get() == "清空虚拟机数据盘":
                root.withdraw()
                # button_yes.destroy()
                cf = configparser.ConfigParser()
                cf.read_file(codecs.open('config.ini', "r", "utf-8-sig"))
                p = Class_VM(cf.get('hj_db', 'db_host'), cf.get('hj_db', 'db_user'), cf.get('hj_db', 'db_pwd'),
                             cf.getint('hj_db', 'db_port'), cf.get('hj_db', 'db'), 'utf8')
                p.vm_del_d(classroom)
                # for vmname in p.get_vmname(query_vm):
                #     obj1.del_datas(vmname,cf.get('gust_vm','guster_user'),cf.get('gust_vm','guster_pwd'),cf.get('disk_path','disk_path'))

                    # print(cf.get('gust_vm','guster_user'),cf.get('gust_vm','guster_pwd'),cf.get('disk_path','disk_path'))
                    # logger.info(f'正在清理{vmname}数据盘')
                    # show_help.config(text=f'正在清理虚拟机{vmname}数据盘', fg='blue')
                    # show_help.update()
                    # time.sleep(1)
                    # show_help.config(text=f'清理虚拟机{vmname}完毕！！！！', fg='blue')
                    # show_help.update()
            else:
                showwarning('警告','未选择任何功能')

            root.destroy()
            root.quit()
        root = Tk()
        root.title(self.title)
        root.iconbitmap(self.pic)
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        # alignstr = f'{self.width}x{self.height}+{(screenwidth - self.width)/ 2}+{(screenheight - self.height)/ 2}'
        alignstr = '%dx%d+%d+%d' % (self.width, self.height, (screenwidth - self.width) / 2, (screenheight - self.height) / 2)
        root.geometry(alignstr)  # 居中对齐
        root.resizable(0, 0) #固定窗口
        root['background'] = self.backgroud
        comvalue = StringVar()  # 窗体自带的文本，新建一个值
        Label(bg='#C0FF3E', text='教 室:', font='Helvetica -16 bold ', fg='black').place(x=10, y=40)#创建lable标签
        comboxlist = ttk.Combobox(root, textvariable=comvalue,width=26)  # 初始化
        cf = configparser.ConfigParser()
        cf.read_file(codecs.open('config.ini', "r", "utf-8-sig"))
        l = Con_mysql(cf.get('hj_db', 'db_host'), cf.get('hj_db', 'db_user'), cf.get('hj_db', 'db_pwd'),
                      cf.get('hj_db', 'db'))
        listroom = l.query("""SELECT DISTINCT CONCAT(a.classroom_name,' <-->',d.template_name)
                                from hj_classroom  a
                                INNER JOIN hj_dg b on a.classroom_tag=b.dg_name
                                INNER JOIN hj_vm c on c.dg_id =b.id
                                INNER JOIN hj_template d on d.id = c.template_id
                                WHERE a.classroom_name = '教室203'
                                                            """)
        newlistroom = []
        for i in listroom:
            newlistroom.append(i[0])
        comboxlist["values"] = newlistroom
        comboxlist.current(2)  # 选择第一个
        comboxlist.bind("<<ComboboxSelected>>", )  # 绑定事件,(下拉列表框被选中时，绑定go()函数)
        comboxlist.place(x=60, y=40)
        var = StringVar()
        r1 = Radiobutton(root, text='定时重置所有教室桌面', bg='#C0FF3E', variable=var, value='定时重置所有教室桌面', command=_selection1)
        r1.select()
        r1.place(x=10, y=100)
        r2 = Radiobutton(root, text='清空数据盘', bg='#C0FF3E', variable=var, value='清空虚拟机数据盘', command=_selection2)
        r2.place(x=200, y=100)
        button_yes = Button(root, text='确定', fg='red', relief='raised', bd=3, font='Helvetica -14 bold ', command=run)
        # button_yes.place(x=140, y=180)
        show_help = Label(root, bg='#C0FF3E')
        show_help.place(x=90, y=210)
        root.mainloop()
    @staticmethod
    def set_cmd_text_color(color, handle=std_out_handle):
        Bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
        return Bool

    @staticmethod
    def resetColor(color):
        Wroot.set_cmd_text_color(color)
    @staticmethod
    def printDarkBlue(mess,color):
        Wroot.set_cmd_text_color(color)

        sys.stdout.write(mess)
        Wroot.resetColor(color)

if __name__ == '__main__':
    r = Wroot('重启桌面工具','1.ico', 320,240,'#C0FF3E')

