## Azure Virtal Machines and Storage Management using Azure Libraries
| **Joaquin Avila Eggleton**
| javilaeg@iu.edu
| *Indiana University*
| hid: sp19-516-136
| github: [:cloud:] (https://github.com/cloudmesh-community/sp19-516-136/project-report/report.md)

---

**Keywords:** Cloud, Azure, Libraries, Virtual Machines and Storage Management

---

## Project Documentation
The purpose of this project is to learn about features available in Azure's Python libraries to manage Virtual Machines
as well as Storage.

## Scope
This document will walk you through every step needed to leverage Azure's Python Libraries
to interact with 2 of their Services:
1) Virtual Machines Management
2) Storage - How to store files in a highly available and scalable cloud storage service.

Once we have a good understanding on how to use Azure's Python libraries, we will use that code to write Cloudmesh
`Provider classes` for Virtual Machines (VM) and Storage.

## Python Version
The information provided in this document considers the use of `Python 3.7.2`
 
## Azure Credentials
The first step before you are able to interact with Azure's API is to have your own set of credentials. 
You can get a free Azure Account if your goal is to learn Azure. 
The steps to create your credentials can be followed from Microsoft's documentation:
<https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service -principal-portal>.

Please note that you will need to activate your account within the first 30 days of creation, otherwise you will lose 
access.

# Virtual Machines 
Let's get started with Azure Virtual Machine Management using Python.

### Azure Python Libraries 
In order to manage Azure Virtual Machines the following libraries will need to be imported.
* ServicePrincipalCredentials
* ResourceManagementClient
* NetworkManagementClient
* ComputeManagementClient

The following sections will dive deeper into each library's capabilities.

### ServicePrincipalCredentials Class
```python
from azure.common.credentials import ServicePrincipalCredentials
```

The concept of Service Principal in Azure allows us to store credentials securely in a configuration file, the registry, 
or Azure KeyVault. 
This helps automated tools that will use Azure Services (like **Cloudmesh**) interact as applications and not a fully 
privileged user. This is where the Credentials created in the previous step will be used.

The `ServicePrincipalCredentials` class has two constructors:

##### ServicePrincipalCredentials Constructor 1
The first one receives the following parameters `(client_id, secret, tenant)`

> **_NOTE:_** 
> 
> Please note that the parameter names used in Azure's documentation do not match how Azure labels them while you are 
> setting up your Azure credentials. 

The following table maps the credential labels from Azure VS the 
`ServicePrincipalCredentials class` parameters.

|ServicePrincipalCredentials parameters|Azure Label|
|--------------------|-------------|
|client_id|Application ID| 
|secret|Key|
|tenant|Directory ID|

##### Application ID
This value is generated during the App registrations process in Azure AD while setting up your Azure Credentials.

##### Directory ID
While setting up your Azure Credentials you will have an Active Directory in your account.
The Directory ID can be located in Azure Portal by clicking on the "Azure Active Directory" tab. 

The right hand side of the screen will load a page with a new menu where you will need to click "Properties" to load 
the Directory Properties page where you will be able to locate the Directory ID. 

> **_NOTE:_** 
> 
> You may need to scroll down a bit to find the "Properties" submenu under the "Manage" section.

##### Key
During the Azure Credentials process you will be registering an Application. 
Part of this registration process will guide you to generate a Key. 
After you enter the description of the Key, the key value will be displayed. 
This is the value that you will need to store securely since you will no longer be able to retrieve it later. 
That Key is used as `Secret` in the `ServicePrincipalCredentials class`.

##### ServicePrincipalCredentials Code Sample 1

```python
from azure.common.credentials import ServicePrincipalCredentials

CLIENT_ID = '<Application ID from Azure Active Directory App Registration Process>'
SECRET = '<Secret Key from Application configured in Azure>'
TENANT = '<Directory ID from Azure Active Directory section>'

credentials = ServicePrincipalCredentials(
    client_id = CLIENT_ID,
    secret = SECRET,
    tenant = TENANT
)
```

##### ServicePrincipalCredentials Constructor 2
The second one includes a cloud environment `(client_id, secret, tenant, cloud_environment)`

The `cloud_environment` represents an Azure Cloud instance.
The current available `cloud_environment` options are:
* `AZURE_PUBLIC_CLOUD` 
* `AZURE_CHINA_CLOUD`
* `AZURE_US_GOV_CLOUD` 
* `AZURE_GERMAN_CLOUD` 

##### ServicePrincipalCredentials Code Sample 2
```python
from azure.common.credentials import ServicePrincipalCredentials
from msrestazure.azure_cloud import AZURE_PUBLIC_CLOUD

CLIENT_ID = '<Application ID from Azure Active Directory App Registration Process>'
SECRET = '<Secret Key from Application configured in Azure>'
TENANT = '<Directory ID from Azure Active Directory section>'

credentials = ServicePrincipalCredentials(
    client_id = CLIENT_ID,
    secret = SECRET,
    tenant = TENANT,
    cloud_environment = AZURE_PUBLIC_CLOUD
)
```

##### Subscription ID
The "Subscription ID" variable is not needed as part of ServicePrincipalCredentials however it will be required 
by all Management Classes, which we will be reviewing next `(ResourceManagementClient, NetworkManagementClient
and ComputeManagementClient)`.

The Subscription ID can be located in Azure's control panel by clicking the "All Services" menu. 
It will load a page with links to different services including one called "Subscriptions". 
After clicking on Subscriptions, you will be able to locate your current subscription along with the "Subscription ID". 

> **_NOTE:_** 
> 
> Please note that Free Trial Subscriptions expire after 30 days, however you will still be able to use some services 
> for free during the next 12 months.

Here are some of the services that will continue to be available after the 30 days, which are of interest to 
our cloudmesh project.

|PRODUCT|PERIOD OF FREE AVAILABILITY
|-------|----------------------------
|750 hours of Azure B1S General Purpose Virtual Machines for Microsoft Windows Server|12 months
|750 hours of Azure B1S General Purpose Virtual Machines for Linux|12 months
|128 GB of Managed Disks as a combination of two 64 GB (P6) SSD storage, plus 1 GB snapshot and 2 million I/O operations|12 months
|5 GB of LRS-Hot Blob Storage with 2 million read, 2 million write, and 2 million write/list operations|12 months
|5 GB of LRS File Storage with 2 million read, 2 million list, and 2 million other file operations|12 months 

### Management Clients
3 management clients will need to be initiated in order to create and manage resources. These Management Clients are:

* ResourceManagementClient
* NetworkManagementClient
* ComputeManagementClient

### ResourceManagementClient Class
```python
from azure.mgmt.resource import ResourceManagementClient
```

Provides operations for working with resources and resource groups.
To instantiate a ResourceManagementClient you will need two mandatory parameters. 
* **Credentials** - Refer to ServicePrincipalCredentials section for more details
* **Subscription ID** - Refer to Subscription ID section for more details

###### Optional parameters are:
* **API Version** - API version to use if no profile is provided, or if missing in profile.
* **Base URL** - Service URL
* **Profile** - A profile definition, from KnownProfiles to dict.

##### ResourceManagementClient Code Samples
We will extend the code from `ServicePrincipalCredentials` and incorporate `ResourceManagementClient` to create a resource
group. 

In this example we will declare 2 new variables:
* **GROUP_NAME** - To identify the resource we are creating. This variable can be used in the future to get a resource 
by name.
* **LOCATION** - To indicate the preferred Azure Location.
The following table shows all available Location values that can be used in Azure.

|Azure Locations|       |       | -       
|-----|-----|-----|-----
|AustraliaCentral|AustraliaCentral2|AustraliaEast|AustraliaSoutheast
|BrazilSouth|CanadaCentral|CanadaEast|CentralIndia|CentralUS
|CentralUSEUAP|ChinaEast|ChinaEast2|ChinaNorth
|ChinaNorth2|EastAsia|EastUS|EastUS2
|EastUS2EUAP|FranceCentral|FranceSouth|GermanyCentral
|GermanyNortheast|JapanEast|JapanWest|KoreaCentral
|KoreaSouth|NorthCentralUS|NorthEurope|SouthAfricaNorth
|SouthAfricaWest|SouthCentralUS|SoutheastAsia|SouthIndia
|UAECentral|UAENorth|UKSouth|UKWest
|USDoDCentral|USDoDEast|USGovArizona|USGovTexas
|USGovVirginia|USNatEast|USNatWest|USSecEast
|USSecWest|WestCentralUS|WestEurope|WestIndia
|WestUS|WestUS2||

From `ResourceManagementClient` we will leverage `ResourceGroupsOperations` class, which can be used as follows:
`resource_client.resource_groups.`+ _method_

The `ResourceGroupsOperations` methods available to manage resources are:

|ResourceGroupsOperations Method|Description
|------|-----------
|`check_existence(resource_group_name, custom_headers=None, raw=False, **operation_config)`|Checks whether a resource group exists.
|`create_or_update(resource_group_name, parameters, custom_headers=None, raw=False, **operation_config)`|Creates or updates a resource group.
|`delete(resource_group_name, custom_headers=None, raw=False, polling=True, **operation_config)`|Deletes a resource group.  When you delete a resource group, all of its resources are also deleted. Deleting a resource group deletes all of its template deployments and currently stored operations.
|`export_template(resource_group_name, resources=None, options=None, custom_headers=None, raw=False, **operation_config)`|Captures the specified resource group as a template.
|`get(resource_group_name, custom_headers=None, raw=False, **operation_config)`|Gets a resource group
|`list(filter=None, top=None, custom_headers=None, raw=False, **operation_config)`|Gets all the resource groups for a subscription.
|`update(resource_group_name, parameters, custom_headers=None, raw=False, **operation_config)`|Updates a resource group. Resource groups can be updated through a simple PATCH operation to a group address. The format of the request is the same as that for creating a resource group. If a field is unspecified, the current value is retained.

##### ResourceManagementClient Code Sample 1 - `ResourceGroupsOperations` - `create_or_update`
```python
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient

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

GROUP_NAME = 'Cloudmesh Group' 
LOCATION = 'EastUS'
resource_client.resource_groups.create_or_update(GROUP_NAME, {'location': LOCATION})
```

##### ResourceManagementClient Code Sample 2 - `ResourceGroupsOperations` - `check_existence`
```python
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient

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

GROUP_NAME = 'Cloudmesh Group' 
LOCATION = 'EastUS'
resource_client.resource_groups.create_or_update(GROUP_NAME, {'location': LOCATION})

# groupExists is a Boolean; will return true if resource group exists and false if it does not.
groupExists = resource_client.resource_groups.check_existence(GROUP_NAME)
```

##### ResourceManagementClient Code Sample 3 - `ResourceGroupsOperations` - `delete`
```python
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient

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

GROUP_NAME = 'Cloudmesh Group' 
LOCATION = 'EastUS'
resource_client.resource_groups.create_or_update(GROUP_NAME, {'location': LOCATION})

# If Resource Group exists - Delete Resource Group
if(resource_client.resource_groups.check_existence(GROUP_NAME))
    resource_client.resource_groups.delete(GROUP_NAME)
```

##### ResourceManagementClient Code Sample 4 - `ResourceGroupsOperations` - `get`
```python
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient

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

GROUP_NAME = 'Cloudmesh Group' 
LOCATION = 'EastUS'
resource_client.resource_groups.create_or_update(GROUP_NAME, {'location': LOCATION})

# If Resource Group exists - Get Resource Group
if(resource_client.resource_groups.check_existence(GROUP_NAME)):
    delete_async_operation = resource_client.resource_groups.get(GROUP_NAME)
    delete_async_operation.wait()
```

##### ResourceManagementClient Code Sample 5 - `ResourceGroupsOperations` - `list`
```python
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient

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

GROUP_NAME = 'Cloudmesh Group' 
LOCATION = 'EastUS'
resource_client.resource_groups.create_or_update(GROUP_NAME, {'location': LOCATION})

# List Resource Groups
for resource in resource_client.resource_groups.list():
    print("\tName: {}".format(resource.name))
    print("\tId: {}".format(resource.id))
    print("\tLocation: {}".format(resource.location))
    print("\tTags: {}".format(resource.tags))
```

### NetworkManagementClient Class
```python
from azure.mgmt.network import NetworkManagementClient
```
Unlike other Azure python APIs, the networking APIs are explicitly versioned into separage packages. You do not need to import them individually since the package information is specified in the client constructor.

To install the management package with pip use the following:
```bash
pip install azure-mgmt-network
```

To instantiate a NetworkManagementClient you will need two mandatory parameters. 
* **Credentials** - Refer to ServicePrincipalCredentials section for more details
* **Subscription ID** - Refer to Subscription ID section for more details

In order to manage a Virtual Machine using the `ComputeManagementClient` you will first need to have a Network Interface.
The following Code Sample will create a Network Interface using the `NetworkManagementClient`
The steps to create a Network Interface are as follows:

1. Create a Virtual Network - Once declaring a `NetworkManagementClient` use `virtual_networks.create_or_update` 
2. Create a Subnet - Once declaring a `NetworkManagementClient` use `subnets.create_or_update` 
3. Create Network Interface - Once declaring a `NetworkManagementClient` use `network_interfaces.create_or_update` 

> **_NOTE:_** 
> 
> Some of NetworkManagementClient operations execute asynchronously such as `create_or_update`. 
> An asynchronous operation returns an AzureOperationPoller. 
> We will use result() or wait() while using asynchronous operations.

##### NetworkManagementClient Code Sample  
```python
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient

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

# Group Variables
GROUP_NAME = 'Cloudmesh Group' 
LOCATION = 'EastUS'
resource_client.resource_groups.create_or_update(GROUP_NAME, {'location': LOCATION})

# Network Variables
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

# Nic = NetworkInterface Class - Nic.id will be needed when using ComputeManagementClient

```

> **_NOTE:_** 
> 
> Some of ComputeManagementClient operations execute asynchronously such as `create_or_update`. 
> An asynchronous operation returns an AzureOperationPoller. 
> We will use result() or wait() while using asynchronous operations.

### ComputeManagementClient Class
```python
from azure.mgmt.compute import ComputeManagementClient
```

Provides operations for working with virtual machines.
To instantiate a ComputeManagementClient you will need two mandatory parameters. 
* **Credentials** - Refer to ServicePrincipalCredentials section for more details
* **Subscription ID** - Refer to Subscription ID section for more details

From `ComputeManagementClient` we will leverage `VirtualMachinesOperations` class, which can be used as follows:
`compute_client.virtual_machines.`+ _method_

The `VirtualMachinesOperations` methods available to manage resources are:

|VirtualMachinesOperations Method|Description
|------|-----------
|`capture(resource_group_name, vm_name, parameters, custom_headers=None, raw=False, polling=True, **operation_config)`|Captures the VM by copying virtual hard disks of the VM and outputs a template that can be used to create similar VMs.
|`convert_to_managed_disks(resource_group_name, vm_name, custom_headers=None, raw=False, polling=True, **operation_config)`|Converts virtual machine disks from blob-based to managed disks. Virtual machine must be stop-deallocated before invoking this operation.
|`create_or_update(resource_group_name, vm_name, parameters, custom_headers=None, raw=False, polling=True, **operation_config)`|The operation to create or update a virtual machine.
|`deallocate(resource_group_name, vm_name, custom_headers=None, raw=False, polling=True, **operation_config)`|Shuts down the virtual machine and releases the compute resources. You are not billed for the compute resources that this virtual machine uses.
|`delete(resource_group_name, vm_name, custom_headers=None, raw=False, polling=True, **operation_config)`|The operation to delete a virtual machine.
|`generalize(resource_group_name, vm_name, custom_headers=None, raw=False, **operation_config)`|Sets the state of the virtual machine to generalized.
|`get(resource_group_name, vm_name, expand=None, custom_headers=None, raw=False, **operation_config)`|Retrieves information about the model view or the instance view of a virtual machine.
|`instance_view(resource_group_name, vm_name, custom_headers=None, raw=False, **operation_config)`|Retrieves information about the run-time state of a virtual machine.
|`list(resource_group_name, custom_headers=None, raw=False, **operation_config)`|Lists all of the virtual machines in the specified resource group. Use the nextLink property in the response to get the next page of virtual machines.
|`list_all(custom_headers=None, raw=False, **operation_config)`|Lists all of the virtual machines in the specified subscription. Use the nextLink property in the response to get the next page of virtual machines.
|`list_available_sizes(resource_group_name, vm_name, custom_headers=None, raw=False, **operation_config)`|Lists all available virtual machine sizes to which the specified virtual machine can be resized.
|`list_by_location(location, custom_headers=None, raw=False, **operation_config)`|Gets all the virtual machines under the specified subscription for the specified location.
|`perform_maintenance(resource_group_name, vm_name, custom_headers=None, raw=False, polling=True, **operation_config)`|The operation to perform maintenance on a virtual machine.
|`power_off(resource_group_name, vm_name, skip_shutdown=False, custom_headers=None, raw=False, polling=True, **operation_config)`|The operation to power off (stop)|
|`redeploy(resource_group_name, vm_name, custom_headers=None, raw=False, polling=True, **operation_config)`|The operation to redeploy a virtual machine.
|`reimage(resource_group_name, vm_name, temp_disk=None, custom_headers=None, raw=False, polling=True, **operation_config)`|Reimages the virtual machine which has an ephemeral OS disk back to its initial state.
|`restart(resource_group_name, vm_name, custom_headers=None, raw=False, polling=True, **operation_config)`|The operation to restart a virtual machine.
|`run_command(resource_group_name, vm_name, parameters, custom_headers=None, raw=False, polling=True, **operation_config)`|Run command on the VM.
|`start(resource_group_name, vm_name, custom_headers=None, raw=False, polling=True, **operation_config)`|The operation to start a virtual machine.
|`update(resource_group_name, vm_name, parameters, custom_headers=None, raw=False, polling=True, **operation_config)`|The operation to update a virtual machine.

Most methods only need 3 parameters:
* **Resource Group Name** - Which was covered in the ResourceManagementClient section.
* **Virtual Machine Name** - A String which refers to the VM Name (similar to Resource Group Name but for VMs).
* **Parameters** - This item expects a JSON String with 5 main Objects.

1. **Location** - Azure Location as explained in ResourceManagementClient Section.
2. **OS_Profile** - This Object expects the Virtual Machine Name along with it's User and Password. 
3. **Hardware_Profile** - Here you will specify the Virtual Machine Size. There are several options which
specify th Number of CPUs, Memory, Storage, Base and Max CPU Performance and Credits banked per hour.
We will use 'Standard_DS1_v2' for these examples. 
A full list of vm_size values can be found here: 

   <https://docs.microsoft.com/en-us/azure/virtual-machines/windows/sizes-general>

4. **Storage_Profile** - This Parameter defines the type of Image to be used for that Virtual Machine. The Image Class
takes 4 parameters: publisher, offer, sku and version.
5. **Network_Profile** - Specifies the list of resource Ids for the network interfaces associated with the 
Virtual Machine.

Here is a sample of a Virtual Machine Parameters variable that can be used as the "Parameters" when working with the
`VirtualMachinesOperations` Class, considering that LOCATION, VM_NAME, USERNAME, PASSWORD AND NIC_ID have been 
already defined.

```python
VM_PARAMETERS={
        'location': 'LOCATION',
        'os_profile': {
            'computer_name': 'VM_NAME',
            'admin_username': 'USERNAME',
            'admin_password': 'PASSWORD'
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
                'id': 'NIC_ID',
            }]
        },
    }
```

##### ComputeManagementClient Code Sample 1 - `VirtualMachinesOperations` - `create_or_update`
```python
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient

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
GROUP_NAME = 'Cloudmesh Group' 
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
VM_NAME = 'Cloudmesh Virtual Machine'
USERNAME = 'cloudmesh'
PASSWORD = 'cms2019'
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

```

##### ComputeManagementClient Sample 2 -`VirtualMachinesOperations`-`start, restart, power_off, list_all, list, delete`
```python
# Start Virtual Machine
async_vm_start = compute_client.virtual_machines.start(GROUP_NAME, VM_NAME)
async_vm_start.wait()

# Restart Virtual Machine
async_vm_restart = compute_client.virtual_machines.restart(GROUP_NAME, VM_NAME)
async_vm_restart.wait()

# Stop Virtual Machine
async_vm_stop = compute_client.virtual_machines.power_off(GROUP_NAME, VM_NAME)
async_vm_stop.wait()

# List Virtual Machines in Subscription
for vm in compute_client.virtual_machines.list_all():
    print("\tVirtualMachine: {}".format(vm.name))

# List Virtual Machines in Resource Group
for vm in compute_client.virtual_machines.list(GROUP_NAME):
    print("\tVirtualMachine: {}".format(vm.name))

# Delete Virtual Machine
async_vm_delete = compute_client.virtual_machines.delete(GROUP_NAME, VM_NAME)
async_vm_delete.wait()
```


