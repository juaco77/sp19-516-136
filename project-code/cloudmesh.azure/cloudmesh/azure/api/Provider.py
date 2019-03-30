from abc import ABCMeta, abstractmethod
import traceback

from cloudmesh.management.configuration.config import Config

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient

from msrestazure.azure_exceptions import CloudError

# noinspection PyUnusedLocal
class Provider(ComputeNodeABC):

    def __init__(self, name="azure_arm", configuration="~/Users/juaco/Dropbox/00 - MS in Data Science/SP19 516/cloudmesh4.yaml"):
        """
        Initializes the provider. The default parameters are read from the configutation
        file that is defined in yaml format.
        :param name: The name of the provider as defined in the yaml file
        :param configuration: The location of the yaml configuration file
        """
        self.config = Config()
        conf = Config(configuration)["cloudmesh"]

        self.user = conf["profile"]
        self.default = conf["default"]
        self.group = self.default["group"]
        self.experiment = self.default["experiment"]
        self.cloud = name
        self.spec = conf["cloud"][name]
        self.cm = self.spec["cm"]
        self.cloudtype = self.cm["kind"]
        self.default = self.spec["default"]
        cred = self.spec["credentials"]

        if self.cloudtype == 'azure':
            subscription_id = cred['AZURE_SUBSCRIPTION_ID']
            credentials = ServicePrincipalCredentials(
                client_id = cred['AZURE_APPLICATION_ID'],
                secret = cred['AZURE_SECRET_KEY'],
                tenant = cred['AZURE_TENANT_ID']
            )

        # Azure Datacenter Region
        LOCATION = cred["AZURE_REGION"]

        # Azure Resource Group
        GROUP_NAME = self.group

        # Azure Network
        VNET_NAME = cred["AZURE_VNET"]
        SUBNET_NAME = cred["AZURE_SUBNET"]

        # Azure VM Storage details
        OS_DISK_NAME = cred["AZURE_VM_DISK_NAME"]

        # Azure VM Network and Machine details
        IP_CONFIG_NAME = cred["AZURE_VM_IP_CONFIG"]
        NIC_NAME = cred["AZURE_VM_NIC"]
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

        resource_client = ResourceManagementClient(credentials, subscription_id)
        compute_client = ComputeManagementClient(credentials, subscription_id)
        network_client = NetworkManagementClient(credentials, subscription_id)

        # Create Resource group
        print('\nCreate Azure Virtual Machine Resource Group')
        resource_client.resource_groups.create_or_update(GROUP_NAME, {'location': LOCATION})

        try:
            nic = create_nic()
        except CloudError:
            print('A VM operation failed:\n{}'.format(traceback.format_exc()))

    # TODO Add dicts at the end of all functions
    def start(self, name=None):
        """
        start a node

        :param name: the unique node name
        :return:  The dict representing the node
        """
        # Start the VM
        print('\nStarting Azure VM')
        async_vm_start = self.compute_client.virtual_machines.start(self.GROUP_NAME, self.VM_NAME)
        async_vm_start.wait()

        raise NotImplementedError

    def restart(self, name=None):
        """

        :param name:
        :return:
        """
        # Restart the VM
        print('\nRestarting Azure VM')
        async_vm_restart = self.compute_client.virtual_machines.restart(self.GROUP_NAME, self.VM_NAME)
        async_vm_restart.wait()
        raise NotImplementedError

    def stop(self, name=None):
        """
        stops the node with the given name

        :param name:
        :return: The dict representing the node including updated status
        """
        # Stop the VM
        print('\nStopping Azure VM')
        async_vm_stop = self.compute_client.virtual_machines.power_off(self.GROUP_NAME, self.VM_NAME)
        async_vm_stop.wait()

        raise NotImplementedError


    def info(self, name=None):
        """
        gets the information of a node with a given name

        :param name:
        :return: The dict representing the node including updated status
        """
        # List VM in resource group
        print('\nList VMs in resource group')
        for vm in self.compute_client.virtual_machines.list(self.GROUP_NAME):
            print("\tVM: {}".format(vm.name))
        raise NotImplementedError

    
    def suspend(self, name=None):
        """
        suspends the node with the given name

        :param name: the name of the node
        :return: The dict representing the node
        """
        raise NotImplementedError


    def list(self):
        """
        list all nodes id

        :return: an array of dicts representing the nodes
        """
        # List all Azure Virtual Machines from my Account
        print('\nList all Azure Virtual Machines')
        for vm in self.compute_client.virtual_machines.list_all():
            print("\tVM: {}".format(vm.name))
        raise NotImplementedError

    def resume(self, name=None):
        """
        resume the named node

        :param name: the name of the node
        :return: the dict of the node
        """
        raise NotImplementedError


    def destroy(self, name=None):
        """
        Destroys the node
        :param name: the name of the node
        :return: the dict of the node
        """
        # Delete VM
        print('\nDeleteing Azure Virtual Machine')
        async_vm_delete = self.compute_client.virtual_machines.delete(self.GROUP_NAME, self.VM_NAME)
        async_vm_delete.wait()

        raise NotImplementedError


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
        raise NotImplementedError


    def rename(self, name=None, destination=None):
        """
        rename a node

        :param destination:
        :param name: the current name
        :return: the dict with the new name
        """
        # if destination is None, increase the name counter and use the new name
        raise NotImplementedError

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