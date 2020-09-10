#!/usr/bin/env python
"""
get vc vname
"""
import re
import sys
import atexit
import time

from pyVmomi import vim, vmodl
from pyVim.connect import SmartConnectNoSSL, Disconnect
from pyVim import connect
from pyVim.task import WaitForTask
# from tools import cli

__author__ = 'Timbaland'

class VcTools():
    def __init__(self,host,user,pwd,port):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.port = port

    def con(self):
        try:
            si = SmartConnectNoSSL(host=self.host,
                                   user=self.user,
                                   pwd=self.pwd,
                                   port=self.port)

        except Exception as e:
            print(e)
        return si

    @staticmethod
    def get_obj(si, root, vim_type):
        container = si.content.viewManager.CreateContainerView(root, vim_type,True)
        view = container.view
        container.Destroy()
        return view


    def create_filter_spec(self,pc, vms, prop):
        objSpecs = []
        for vm in vms:
            objSpec = vmodl.query.PropertyCollector.ObjectSpec(obj=vm)
            objSpecs.append(objSpec)
        filterSpec = vmodl.query.PropertyCollector.FilterSpec()
        filterSpec.objectSet = objSpecs
        propSet = vmodl.query.PropertyCollector.PropertySpec(all=False)
        propSet.type = vim.VirtualMachine
        propSet.pathSet = [prop]
        filterSpec.propSet = [propSet]
        return filterSpec


    def filter_results(result, value):
        vms = []
        for o in result.objects:
            if o.propSet[0].val == value:
                vms.append(o.obj)
        return vms


    def vm_uuid(self,si,vmname):
        # args = setup_args()
        #获取vm UUID

        # Start with all the VMs from container, which is easier to write than
        # PropertyCollector to retrieve them.
        vms = VcTools.get_obj(si = si, root= si.content.rootFolder,vim_type = [vim.VirtualMachine])

        # pc = si.content.propertyCollector
        # filter_spec = create_filter_spec(pc, vms, 'runtime.powerState')
        # options = vmodl.query.PropertyCollector.RetrieveOptions()
        # result = pc.RetrievePropertiesEx([filter_spec], options)
        # # vms = filter_results(result, 'poweredOn')
        # print("VMs with %s = %s" % ('runtime.powerState', 'poweredOn'))
        for vm in vms:
            if vm.name == vmname:
                # print(vm.config.uuid)
                # Disconnect(si)
                return vm.config.uuid


    @classmethod
    def wait_for_tasks(cls,service_instance, tasks):
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
    def change_nic(self,si,vm_uuid,vlan):
        try:
            # print(11111)
            atexit.register(connect.Disconnect, si)

            content = si.RetrieveContent()
            # print(content)

            # for child in content.rootFolder.childEntity:
            #     print(child)
            #     if hasattr(child, 'vmFolder'):
            #         datacenter = child
            #         vmfolder = datacenter.vmFolder
            #         vmlist = vmfolder.childEntity
            #         for vm in vmlist:
            #             summary = vm.summary
            #             print(summary.config.name)
            # print(dir(content.searchIndex))
            #  ynlm71-1.guptsx.net
            # print(dir(content.searchIndex))
            vm = content.searchIndex.FindByUuid(None, vm_uuid, True)
            # print(vm.summary.config.uuid)
            # vm = content.searchIndex.FindByDnsName(None,'TVA5UR-1',True)
            # print(vm.config.hardware.device)
            # print(vm.storage)
            # print(vm.name)
            # for i in  dir(vm):
            #     print(i)
            device_change = []
            for device in vm.config.hardware.device:
                if isinstance(device, vim.vm.device.VirtualEthernetCard):
                    nicspec = vim.vm.device.VirtualDeviceSpec()
                    nicspec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
                    nicspec.device = device
                    nicspec.device.wakeOnLanEnabled = True
                    nicspec.device.backing = vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
                    nicspec.device.backing.network = VcTools.get_nicview(content, [vim.Network], vlan)
                    nicspec.device.backing.deviceName = vlan
                    nicspec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
                    nicspec.device.connectable.startConnected = True
                    nicspec.device.connectable.allowGuestControl = True
                    device_change.append(nicspec)
                    break
            config_spec = vim.vm.ConfigSpec(deviceChange=device_change)
            task = vm.ReconfigVM_Task(config_spec)
            VcTools.wait_for_tasks(si, [task])
            print("Successfully changed network")
        except vmodl.MethodFault as error:
            print("Caught vmodl fault : " + error.msg)
    def change_memory(self,si:object,memory_size:int,vm_name:str) -> str:
        atexit.register(connect.Disconnect, si)
        content = si.RetrieveContent()
        container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
        # 更改虚拟机配置
        cspec = vim.vm.ConfigSpec()
        # print(cspec)
        cspec.memoryMB = 1024 * memory_size
        # 开启热插拔
        cspec.memoryHotAddEnabled = True
        i = 0
        for c in container.view:
            # print(c.name)
            result = re.findall(vm_name, c.name)

            if len(result) > 0:
                i += 1
                print(c.name)
                task = c.Reconfigure(cspec)
                while task.info.state == "running" or task.info.state == "queued":
                    time.sleep(1)

                if task.info.state == "success":
                    print("success")
            # if c.name == 'C319-061':
            #     # obj.Reconfigure(cspec)
            #     print(1)
        print(i)
        container.Destroy()
    @classmethod
    def get_nicview(cls,content , vimtype, name):
        """
            Get the vsphere object associated with a given text name
           """
        obj = None
        container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
        for view in container.view:
            if view.name == name:
                obj = view
                break
        return obj
# if __name__ == '__main__':
#     main()