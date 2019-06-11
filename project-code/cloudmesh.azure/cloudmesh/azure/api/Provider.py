import traceback

from cloudmesh.abstractclass.ComputeNodeABC import ComputeNodeABC
from cloudmesh.management.configuration.config import Config
from cloudmesh.common.dotdict import dotdict

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import DiskCreateOption

from msrestazure.azure_exceptions import CloudError

# noinspection PyUnusedLocal
class NativeProvider(ComputeNodeABC):

    def __init__(self, name="azure", configuration="~/.cloudmesh/cloudmesh4.yaml"):
        """
        Initializes the provider. The default parameters are read from the configutation
        file that is defined in yaml format.
        :param name: The name of the provider as defined in the yaml file
        :param configuration: The location of the yaml configuration file
        """
        self.config = Config()

        conf = Config(configuration)["cloudmesh"]

        self.user = conf["profile"]
        self.cloud = name
        self.spec = conf["cloud"][name]
        cred = self.spec["credentials"]
        self.default = self.spec["default"]

        # ServicePrincipalCredentials related Variables to configure in cloudmesh4.yaml file
        # AZURE_APPLICATION_ID = '<Application ID from Azure Active Directory App Registration Process>'
        # AZURE_SECRET_KEY = '<Secret Key from Application configured in Azure>'
        # AZURE_TENANT_ID = '<Directory ID from Azure Active Directory section>'

        credentials = ServicePrincipalCredentials(
            client_id = cred['AZURE_APPLICATION_ID'],
            secret = cred['AZURE_SECRET_KEY'],
            tenant = cred['AZURE_TENANT_ID']
            )

        SUBSCRIPTION_ID = cred['AZURE_SUBSCRIPTION_ID']

        # Management Clients
        resource_client = ResourceManagementClient(credentials, SUBSCRIPTION_ID)
        compute_client = ComputeManagementClient(credentials, SUBSCRIPTION_ID)
        network_client = NetworkManagementClient(credentials, SUBSCRIPTION_ID)

        # Azure Resource Group
        GROUP_NAME = self.default["resource_group"]

        # Azure Datacenter Region
        LOCATION = cred["AZURE_REGION"]

        # NetworkManagementClient related Variables
        VNET_NAME       = self.default["network"]
        SUBNET_NAME     = self.default["subnet"]
        IP_CONFIG_NAME  = 'azure-cloudmesh-ip-config'
        NIC_NAME        = 'azure-cloudmesh-nic'




        # Azure VM Storage details
        OS_DISK_NAME = cred["AZURE_VM_DISK_NAME"]

        USERNAME = cred["AZURE_VM_USER"]
        PASSWORD = cred["AZURE_VM_PASSWORD"]
        VM_NAME = cred["AZURE_VM_NAME"]

        # TODO - I need to be able to parse the image settings from the yaml file default setting to create the VM_REFERENCE
        VM_REFERENCE = {
            'linux': {
                'publisher': 'Canonical',
                'offer': 'UbuntuServer',
                'sku': '16.04.0-LTS',
                'version': self.cm["version"]
            },
            'windows': {
                'publisher': 'MicrosoftWindowsServer',
                'offer': 'WindowsServer',
                'sku': '2016-Datacenter',
                'version': self.cm["version"]
            }
        }



        # Create Resource group
        print('\nCreate Azure Virtual Machine Resource Group')
        resource_client.resource_groups.create_or_update(GROUP_NAME, {'location': LOCATION})

    try:
        nic = create_nic()
    except CloudError:
        print('A VM operation failed:\n{}'.format(traceback.format_exc()))

    def start(self, groupName=None, vmName=None):
        """
        start a node

        :param name: the unique node name
        :return:  The dict representing the node
        """
        if groupName is None:
            groupName = self.GROUP_NAME
        if vmName is None:
            vmName = self.VM_NAME

        node = dotdict()
        node.name = groupName
        node.vmName = vmName

        # Start the VM
        print('\nStarting Azure VM')
        async_vm_start = self.compute_client.virtual_machines.start(groupName, vmName)
        async_vm_start.wait()
        return node

    # TODO Restart does not exist in ComputeNodeABC is it the same as Resume?
    def restart(self, groupName=None, vmName=None):
        """
        restart a node

        :param name:
        :return: The dict representing the node
        """
        if groupName is None:
            groupName = self.GROUP_NAME
        if vmName is None:
            vmName = self.VM_NAME

        node = dotdict()
        node.name = groupName
        node.vmName = vmName

        # Restart the VM
        print('\nRestarting Azure VM')
        async_vm_restart = self.compute_client.virtual_machines.restart(groupName, vmName)
        async_vm_restart.wait()
        return node

    def stop(self, groupName=None, vmName=None):
        """
        stops the node with the given name

        :param name:
        :return: The dict representing the node including updated status
        """
        if groupName is None:
            groupName = self.GROUP_NAME
        if vmName is None:
            vmName = self.VM_NAME

        node = dotdict()
        node.name = groupName
        node.vmName = vmName

        # Stop the VM
        print('\nStopping Azure VM')
        async_vm_stop = self.compute_client.virtual_machines.power_off(groupName, vmName)
        async_vm_stop.wait()
        return node

    def info(self, groupName=None):
        """
        gets the information of a node with a given name

        :param name:
        :return: The dict representing the node including updated status
        """
        if groupName is None:
            groupName = self.GROUP_NAME

        node = dotdict()
        node.name = groupName

        list = []

        # List VM in resource group
        print('\nList VMs in resource group')
        for vm in self.compute_client.virtual_machines.list(groupName):
            print("\tVM: {}".format(vm.name))
            v = dotdict()
            v.cloud_id = vm.cloud_id
            v.cloud = vm.cloud
            v.name = vm.name
            v.region = vm.region
            v.size = vm.size
            v.state = vm.state
            v.public_ips = vm.public_ips
            v.private_ips = vm.private_ips
            list.append(v)
        return self.to_dict(list)

    def list(self):
        """
        list all nodes id

        :return: an array of dicts representing the nodes
        """
        # List all Azure Virtual Machines from my Account

        list = []

        print('\nList all Azure Virtual Machines')
        for vm in self.compute_client.virtual_machines.list_all():
            print("\tVM: {}".format(vm.name))
            v = dotdict()
            v.cloud_id = vm.cloud_id
            v.cloud = vm.cloud
            v.name = vm.name
            v.region = vm.region
            v.size = vm.size
            v.state = vm.state
            v.public_ips = vm.public_ips
            v.private_ips = vm.private_ips
            list.append(v)

        return self.to_dict(list)

    # TODO Implement Suspend Method
    def suspend(self, name=None):
        """
        suspends the node with the given name

        :param name: the name of the node
        :return: The dict representing the node
        """
        raise NotImplementedError
        # must return dict

    # TODO Implement Resume Method (is it the same as restart?)
    def resume(self, name=None):
        """
        resume the named node

        :param name: the name of the node
        :return: the dict of the node
        """
        raise NotImplementedError
        # must return dict

    def destroy(self, groupName=None, vmName=None):
        """
        Destroys the node
        :param name: the name of the node
        :return: the dict of the node
        """
        if groupName is None:
            groupName = self.GROUP_NAME
        if vmName is None:
            vmName = self.VM_NAME

        node = dotdict()
        node.name = groupName
        node.vmName = vmName

        # Delete VM
        print('\nDeleteing Azure Virtual Machine')
        async_vm_delete = self.compute_client.virtual_machines.delete(groupName, vmName)
        async_vm_delete.wait()
        return node

    # TODO Migrate code from Init that is meant for creating a Node
    def create(self, name=None, image=None, size=None, timeout=360, **kwargs):
        """
        creates a named node

        :param name: the name of the node
        :param image: the image used
        :param size: the size of the image
        :param timeout: a timeout in seconds that is invoked in case the image does not boot.
               The default is set to 3 minutes.
        :param kwargs: additional arguments passed along at time of boot
        :return:
        """
        """
        create one node
        """
        # must return dict

    # TODO Implement Rename Method
    def rename(self, name=None, destination=None):
        """
        rename a node

        :param destination:
        :param name: the current name
        :return: the dict with the new name
        """
        # if destination is None, increase the name counter and use the new name
        # must return dict

    def create_nic(self):
        """
            Create a Network Interface for a Virtual Machine

        :return:
        """
        # Create Virtual Network
        print('\nCreate Vnet')
        async_vnet_creation = self.network_client.virtual_networks.create_or_update(
            self.GROUP_NAME,
            self.VNET_NAME,
            {
                'location': self.LOCATION,
                'address_space': {
                    'address_prefixes': ['10.0.0.0/16']
                }
            }
        )
        async_vnet_creation.wait()

        # Create Subnet
        print('\nCreate Subnet')
        async_subnet_creation = self.network_client.subnets.create_or_update(
            self.GROUP_NAME,
            self.VNET_NAME,
            self.SUBNET_NAME,
            {'address_prefix': '10.0.0.0/24'}
        )
        subnet_info = async_subnet_creation.result()

        # Create NIC
        print('\nCreate NIC')
        async_nic_creation = self.network_client.network_interfaces.create_or_update(
            self.GROUP_NAME,
            self.NIC_NAME,
            {
                'location': self.LOCATION,
                'ip_configurations': [{
                    'name': self.IP_CONFIG_NAME,
                    'subnet': {
                        'id': subnet_info.id
                    }
                }]
            }
        )
        return async_nic_creation.result()
        # must return dict

    def create_vm_parameters(self):
        """
            Create the VM parameters structure.
        """
        return {
            'location': self.LOCATION,
            'os_profile': {
                'computer_name': self.VM_NAME,
                'admin_username': self.USERNAME,
                'admin_password': self.PASSWORD
            },
            'hardware_profile': {
                'vm_size': 'Standard_DS1_v2'
            },
            'storage_profile': {
                'image_reference': {
                    'publisher': self.vm_reference['publisher'],
                    'offer': self.vm_reference['offer'],
                    'sku': self.vm_reference['sku'],
                    'version': self.vm_reference['version']
                },
            },
            'network_profile': {
                'network_interfaces': [{
                    'id': self.nic_id,
                }]
            },
        }

    def to_dict(self, lst, id="name"):
        d = {}
        if lst is not None:
            for entry in lst:
                d[entry[id]] = entry
        return d


    def update_dict(self, elements, func=None):
        # this is an internal function for building dict object
        d = []
        for element in elements:
            entry = element.__dict__
            entry["cm"] = {
                "kind": "cloud",
                "cloud": self.cloud,
                "name": element.name
            }
            element.properties = element.properties.__dict__
            entry["cm"]["created"] = \
                element.properties["creation_time"].isoformat()[0]
            entry["cm"]["updated"] = \
                element.properties["last_modified"].isoformat()[0]
            entry["cm"]["size"] = element.properties["content_length"]
            del element.properties["copy"]
            del element.properties["lease"]
            del element.properties["content_settings"]
            del element.properties["creation_time"]
            del element.properties["last_modified"]
            if func == 'delete':
                entry["cm"]["status"] = "deleted"
            else:
                entry["cm"]["status"] = "exists"
            if element.properties["deleted_time"] is not None:
                entry["cm"]["deleted"] = element.properties[
                    "deleted_time"].isoformat()
                del element.properties["deleted_time"]
            d.append(entry)
        return d

