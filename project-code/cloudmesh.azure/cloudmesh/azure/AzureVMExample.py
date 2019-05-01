from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import DiskCreateOption

# ServicePrincipalCredentials related Variables
CLIENT_ID = '<Application ID from Azure Active Directory App Registration Process>'
SECRET = '<Secret Key from Application configured in Azure>'
TENANT = '<Directory ID from Azure Active Directory section>'

credentials = ServicePrincipalCredentials(
    client_id = CLIENT_ID,
    secret = SECRET,
    tenant = TENANT
    )

SUBSCRIPTION_ID = '<Subscription ID from Azure>'

# Management Clients
resource_client = ResourceManagementClient(credentials, SUBSCRIPTION_ID)
network_client  = NetworkManagementClient(credentials, SUBSCRIPTION_ID)
compute_client  = ComputeManagementClient(credentials, SUBSCRIPTION_ID)

# ResourceManagementClient related Variables
GROUP_NAME = 'Cloudmesh-Group'
LOCATION = 'EastUS'

resource_client.resource_groups.create_or_update(GROUP_NAME, {'location': LOCATION})

# NetworkManagementClient related Variables
VNET_NAME       = 'azure-cloudmesh-vnet'
SUBNET_NAME     = 'azure-cloudmesh-subnet'
IP_CONFIG_NAME  = 'azure-cloudmesh-ip-config'
NIC_NAME        = 'azure-cloudmesh-nic'

# Create Network Interface for Virtual Machine
# Virtual Network
async_vnet_creation = network_client.virtual_networks.create_or_update(

    GROUP_NAME,
    VNET_NAME,
    {
        'location': LOCATION,
        'address_space': {
            'address_prefixes': ['10.0.0.0/16']
        }
    }
)
async_vnet_creation.wait()

# Subnet
async_subnet_creation = network_client.subnets.create_or_update(
    GROUP_NAME,
    VNET_NAME,
    SUBNET_NAME,
    {'address_prefix': '10.0.0.0/24'}
)
subnet_info = async_subnet_creation.result()

# Create Network Interface
async_nic_creation = network_client.network_interfaces.create_or_update(
    GROUP_NAME,
    NIC_NAME,
    {
        'location': LOCATION,
        'ip_configurations': [{
            'name': IP_CONFIG_NAME,
            'subnet': {
                'id': subnet_info.id
            }
        }]
    }
)
nic = async_nic_creation.result()

# Virtual Machine Parameters
VM_NAME = 'Cloudmesh-Virtual-Machine'
USERNAME = 'cloudmesh'
PASSWORD = 'Cms2019'
NIC_ID = nic.id

VM_PARAMETERS={
        'location': LOCATION,
        'os_profile': {
            'computer_name': VM_NAME,
            'admin_username': USERNAME,
            'admin_password': PASSWORD
        },
        'hardware_profile': {
            'vm_size': 'Standard_DS1_v2'
        },
        'storage_profile': {
            'image_reference': {
                'publisher': 'Canonical',
                'offer': 'UbuntuServer',
                'sku': '16.04.0-LTS',
                'version': 'latest'
            },
        },
        'network_profile': {
            'network_interfaces': [{
                'id': NIC_ID,
            }]
        },
    }

# Create Virtual Machine using the VM_PARAMETERS defined above
async_vm_creation = compute_client.virtual_machines.create_or_update(GROUP_NAME, VM_NAME, VM_PARAMETERS)
async_vm_creation.wait()

# Creating a Managed Data Disk
async_disk_creation = compute_client.disks.create_or_update(
    GROUP_NAME,
    'cloudmesh-datadisk1',
    {
        'location': LOCATION,
        'disk_size_gb': 1,
        'creation_data': {
            'create_option': DiskCreateOption.empty
        }
    }
)
data_disk = async_disk_creation.result()

# Get the virtual machine by name
virtual_machine = compute_client.virtual_machines.get(
    GROUP_NAME,
    VM_NAME
)

# Attaching Data Disk to a Virtual Machine
virtual_machine.storage_profile.data_disks.append({
    'lun': 12,
    'name': 'cloudmesh-datadisk1',
    'create_option': DiskCreateOption.attach,
    'managed_disk': {
        'id': data_disk.id
    }
})
async_disk_attach = compute_client.virtual_machines.create_or_update(
    GROUP_NAME,
    virtual_machine.name,
    virtual_machine
)
async_disk_attach.wait()

# Detaching a Data Disk
data_disks = virtual_machine.storage_profile.data_disks
data_disks[:] = [disk for disk in data_disks if disk.name != 'cloudmesh-datadisk1']
async_vm_update = compute_client.virtual_machines.create_or_update(
    GROUP_NAME,
    VM_NAME,
    virtual_machine
)
virtual_machine = async_vm_update.result()

# Deallocating the Virtual Machine (in preparation for a disk resize)
async_vm_deallocate = compute_client.virtual_machines.deallocate(GROUP_NAME, VM_NAME)
async_vm_deallocate.wait()

# Increasing the OS disk size
os_disk_name = virtual_machine.storage_profile.os_disk.name
os_disk = compute_client.disks.get(GROUP_NAME, os_disk_name)
if not os_disk.disk_size_gb:
    os_disk.disk_size_gb = 30

os_disk.disk_size_gb += 10

# Updating disk
async_disk_update = compute_client.disks.create_or_update(
    GROUP_NAME,
    os_disk.name,
    os_disk
)
async_disk_update.wait()