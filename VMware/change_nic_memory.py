#!/usr/bin/evn python
# -*- encoding:utf-8 -*-
# function: connect exsi server api  for restart vm
# date:2020-9-09
# Arthor:Timbaland
'''
Example script to change the network of the Virtual Machine NIC

'''
import atexit
import codecs
import configparser
from vms_tools import VcTools
from pyVmomi import vim, vmodl
from con_mysql import Con_mysql

def get_obj(content, vimtype, name):
    """
     Get the vsphere object associated with a given text name
    """
    obj = None
    container = content.viewManager.CreateContainerView(content.rootFolder,vimtype, True)
    for view in container.view:
        if view.name == name:
            obj = view
            break
    return obj

def wait_for_tasks(service_instance, tasks):
    """Given the service instance si and tasks, it returns after all the
   tasks are complete
   """
    property_collector = service_instance.content.propertyCollector
    task_list = [str(task) for task in tasks]
    # Create filter
    obj_specs = [vmodl.query.PropertyCollector.ObjectSpec(obj=task)
                 for task in tasks]
    property_spec = vmodl.query.PropertyCollector.PropertySpec(type=vim.Task,
                                                               pathSet=[],
                                                               all=True)
    filter_spec = vmodl.query.PropertyCollector.FilterSpec()
    filter_spec.objectSet = obj_specs
    filter_spec.propSet = [property_spec]
    pcfilter = property_collector.CreateFilter(filter_spec, True)
    try:
        version, state = None, None
        # Loop looking for updates till the state moves to a completed state.
        while len(task_list):
            update = property_collector.WaitForUpdates(version)
            for filter_set in update.filterSet:
                for obj_set in filter_set.objectSet:
                    task = obj_set.obj
                    for change in obj_set.changeSet:
                        if change.name == 'info':
                            state = change.val.state
                        elif change.name == 'info.state':
                            state = change.val
                        else:
                            continue

                        if not str(task) in task_list:
                            continue

                        if state == vim.TaskInfo.State.success:
                            # Remove task from taskList
                            task_list.remove(str(task))
                        elif state == vim.TaskInfo.State.error:
                            raise task.info.error
            # Move to next version
            version = update.version
    finally:
        if pcfilter:
            pcfilter.Destroy()

if __name__ == '__main__':
    cf = configparser.ConfigParser()
    cf.read_file(codecs.open('config.ini', "r", "utf-8-sig"))
    # print(cf.get('vc1','vc_ip'),cf.get('vc1','vc_acount'),cf.get('vc1','vc_pwd'),int(cf.get('vc1','vc_port')))
    #查询对应教室的虚拟机
    vm_list_sql = """
                    SELECT c.vm_name,b.dg_name
                    from hj_classroom  a
                    INNER JOIN hj_dg b on a.classroom_tag=b.dg_name
                    INNER JOIN hj_vm c on c.dg_id =b.id
                    WHERE a.classroom_name = 'c504教室'
    """
    cn = Con_mysql(cf.get('hj_db','db_host'),
                  cf.get('hj_db','db_user'),
                  cf.get('hj_db','db_pwd'),
                  cf.get('hj_db','db'))
    vm_list = cn.query(vm_list_sql)

    vs = VcTools(host=cf.get('vc1','vc_ip'),
                user=cf.get('vc1','vc_acount'),
                pwd=cf.get('vc1','vc_pwd'),
                port=int(cf.get('vc1','vc_port')))

    si = vs.con()
    for i in vm_list:
        print(i[0])
        vm_uuid = vs.vm_uuid(si,f'{i[0]}')
        print(vm_uuid)

        # x修改vlan
        vs.change_nic(si,vm_uuid,'vlan3199')
        #
        # #修改内存 CPU
        # vs.change_memory(si,6,f'{i[0]}')