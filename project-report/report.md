## Virtual Machines and Storage Management using Azure's Python Libraries
| **Joaquin Avila Eggleton**
| javilaeg@iu.edu
| *Indiana University*
| hid: sp19-516-136
| github: [:cloud:] (https://github.com/cloudmesh-community/sp19-516-136/project-report/report.md)

---

**Keywords:** Cloud, Azure, Python Libraries, Virtual Machines and Storage Management

---

## Project Documentation

The purpose of this project is to learn about features available in Azure's Python libraries to manage Virtual Machines
as well as Storage using Cloudmesh.

:o: the project is not just about learning, but about developing a multicloud interface to clouds which includes azure and is located at cloudmesh.cloud. This report is not needed and should be integrated in most aspects into cloudmesh-manaual.

However the document is a good example on how to take notes and document how to do certain things with the azure library.

:o: cloudmesh Config() is not used in the examples The inclusion of credetials in the examples must be avoided and replaced with Config() using cloudmesh4.yaml

## Scope

This document will walk you through every step needed to leverage Azure's Python Libraries
to interact with 2 of their Services:
1) Virtual Machines Management
2) Storage - How to store files in a highly available and scalable cloud storage service.

Once we have a good understanding on how to use Azure's Python libraries, we will use that code to write Cloudmesh
`Provider classes` for Virtual Machines (VM) and Storage.

## Python Version

The information provided in this document considers the use of `Python 3.7.2`
 
# Virtual Machines 

Let's get started with Azure Virtual Machine Management using Python.

## Azure Service Principal Credentials

The first step before you are able to interact with Azure's API is to have your own set of credentials. 
You can get a free Azure Account if your goal is to learn Azure.
Once you have configured an Azure account you will need to follow a few steps to get the credentials that we will use 
in our next section.
 
The steps to create your credentials can be followed from Microsoft's documentation:
<https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service -principal-portal>.

Please note that you will need to activate your account within the first 30 days of creation, otherwise you will lose 
access.

### Azure Python Libraries for Managing Virtual Machines

In order to manage Azure Virtual Machines the following libraries will need to be imported.
* ServicePrincipalCredentials
* ResourceManagementClient
* NetworkManagementClient
* ComputeManagementClient
* DiskCreateOption

### Managing credentials in Cloudmesh

Cloudmesh uses a yaml file called from which various clouds settings can be managed.

Credentials should be set in the yaml file and should never be included as part of the code.
The following yaml sample depicts the Cloud section for Azure's compute configuration, which will be used by our python
code related to Virtual Machines Management.

```yaml
   cloudmesh:
     ...
     cloud:
       ...
       azure:
         cm:
           active: True
           heading: Azure
           host: azure.microsoft.com
           label: Azure
           kind: azure
           version: 'latest'
           service: compute
         default:
           image: 'linux:Canonical:UbuntuServer:16.04-LTS:latest'
           image2: 'windows:MicrosoftWindowsServer:WindowsServer:2016-Datacenter:latest'
           size: 'Basic_A0'
           resource_group: 'cloudmesh'
           storage_account: 'cmdrive'
           network: 'cmnetwork' 
           subnet: 'cmsubnet'
           blob_container: 'vhds'
           AZURE_VM_IP_CONFIG: 'cloudmesh-ip-config'
           AZURE_VM_NIC: 'cloudmesh-nic'
           AZURE_VM_DISK_NAME: 'cloudmesh-os-disk'
           AZURE_VM_USER: TBD
           AZURE_VM_PASSWORD: TBD
           AZURE_VM_NAME: 'cloudmeshVM'
         credentials:
           AZURE_TENANT_ID: 'xxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
           AZURE_SUBSCRIPTION_ID: 'xxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
           AZURE_APPLICATION_ID: 'xxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
           AZURE_SECRET_KEY: TBD
           AZURE_REGION: 'eastus'           
```

> **_NOTE:_** 
> 
> Please note that the parameter names used in Azure's documentation do not match how Azure labels them while you are 
> setting up your Azure credentials. 

The following table maps the credential labels from Azure VS the 
`ServicePrincipalCredentials class` parameters and the Parameter Value in Cloudmesh's YAML file.

|ServicePrincipalCredentials parameters|Azure Label|Cloudmesh YAML|
|--------------------|-------------|-------------|
|client_id|Application ID|AZURE_APPLICATION_ID|
|secret|Key|AZURE_SECRET_KEY|
|tenant|Directory ID|AZURE_TENANT_ID|

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




A more detailed information about cloudmesh's configuration yaml file [can be found here](https://cloudmesh.github.io/cloudmesh-manual/configuration/configuration.html)




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

##### ServicePrincipalCredentials Code Sample 1

```python
from azure.common.credentials import ServicePrincipalCredentials
from cloudmesh.management.configuration.config import Config

configuration = "~/.cloudmesh/cloudmesh4.yaml"

conf = Config(configuration)["cloudmesh"]
spec = conf["cloud"]["azure"]
cred = spec["credentials"]

# ServicePrincipalCredentials related Variables to configure in cloudmesh4.yaml file
# AZURE_APPLICATION_ID = '<Application ID from Azure Active Directory App Registration Process>'
# AZURE_SECRET_KEY = '<Secret Key from Application configured in Azure>'
# AZURE_TENANT_ID = '<Directory ID from Azure Active Directory section>'

credentials = ServicePrincipalCredentials(
    client_id = cred['AZURE_APPLICATION_ID'],
    secret = cred['AZURE_SECRET_KEY'],
    tenant = cred['AZURE_TENANT_ID']
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
from cloudmesh.management.configuration.config import Config

configuration = "~/.cloudmesh/cloudmesh4.yaml"

conf = Config(configuration)["cloudmesh"]
spec = conf["cloud"]["azure"]
cred = spec["credentials"]

# ServicePrincipalCredentials related Variables to configure in cloudmesh4.yaml file
# AZURE_APPLICATION_ID = '<Application ID from Azure Active Directory App Registration Process>'
# AZURE_SECRET_KEY = '<Secret Key from Application configured in Azure>'
# AZURE_TENANT_ID = '<Directory ID from Azure Active Directory section>'

credentials = ServicePrincipalCredentials(
    client_id = cred['AZURE_APPLICATION_ID'],
    secret = cred['AZURE_SECRET_KEY'],
    tenant = cred['AZURE_TENANT_ID'],
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

###### Optional parameters are

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
from cloudmesh.management.configuration.config import Config

configuration = "~/.cloudmesh/cloudmesh4.yaml"

conf = Config(configuration)["cloudmesh"]
spec = conf["cloud"]["azure"]
cred = spec["credentials"]
default = spec["default"]

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

# Azure Resource Group
GROUP_NAME      = default["resource_group"]

# Azure Datacenter Region
LOCATION        = cred["AZURE_REGION"]

resource_client.resource_groups.create_or_update(GROUP_NAME, {'location': LOCATION})
```

##### ResourceManagementClient Code Sample 2 - `ResourceGroupsOperations` - `check_existence`

```python
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from cloudmesh.management.configuration.config import Config

configuration = "~/.cloudmesh/cloudmesh4.yaml"

conf = Config(configuration)["cloudmesh"]
spec = conf["cloud"]["azure"]
cred = spec["credentials"]
default = spec["default"]

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

# Azure Resource Group
GROUP_NAME      = default["resource_group"]

# Azure Datacenter Region
LOCATION        = cred["AZURE_REGION"]

resource_client.resource_groups.create_or_update(GROUP_NAME, {'location': LOCATION})

# groupExists is a Boolean; will return true if resource group exists and false if it does not.
groupExists = resource_client.resource_groups.check_existence(GROUP_NAME)
```

##### ResourceManagementClient Code Sample 3 - `ResourceGroupsOperations` - `delete`

```python
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from cloudmesh.management.configuration.config import Config

configuration = "~/.cloudmesh/cloudmesh4.yaml"

conf = Config(configuration)["cloudmesh"]
spec = conf["cloud"]["azure"]
cred = spec["credentials"]
default = spec["default"]

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

# Azure Resource Group
GROUP_NAME      = default["resource_group"]

# Azure Datacenter Region
LOCATION        = cred["AZURE_REGION"]

resource_client.resource_groups.create_or_update(GROUP_NAME, {'location': LOCATION})

# If Resource Group exists - Delete Resource Group
if(resource_client.resource_groups.check_existence(GROUP_NAME))
    resource_client.resource_groups.delete(GROUP_NAME)
```

##### ResourceManagementClient Code Sample 4 - `ResourceGroupsOperations` - `get`

```python
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from cloudmesh.management.configuration.config import Config

configuration = "~/.cloudmesh/cloudmesh4.yaml"

conf = Config(configuration)["cloudmesh"]
spec = conf["cloud"]["azure"]
cred = spec["credentials"]
default = spec["default"]

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

# Azure Resource Group
GROUP_NAME      = default["resource_group"]

# Azure Datacenter Region
LOCATION        = cred["AZURE_REGION"]

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
from cloudmesh.management.configuration.config import Config

configuration = "~/.cloudmesh/cloudmesh4.yaml"

conf = Config(configuration)["cloudmesh"]
spec = conf["cloud"]["azure"]
cred = spec["credentials"]
default = spec["default"]

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

# Azure Resource Group
GROUP_NAME      = default["resource_group"]

# Azure Datacenter Region
LOCATION        = cred["AZURE_REGION"]

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
from cloudmesh.management.configuration.config import Config

configuration = "~/.cloudmesh/cloudmesh4.yaml"

conf = Config(configuration)["cloudmesh"]
spec = conf["cloud"]["azure"]
cred = spec["credentials"]
default = spec["default"]

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
network_client  = NetworkManagementClient(credentials, SUBSCRIPTION_ID)

# Azure Resource Group
GROUP_NAME      = default["resource_group"]

# Azure Datacenter Region
LOCATION        = cred["AZURE_REGION"]

resource_client.resource_groups.create_or_update(GROUP_NAME, {'location': LOCATION})

# NetworkManagementClient related Variables pulled from Cloudmesh YAML file
VNET_NAME       = default["network"]
SUBNET_NAME     = default["subnet"]
IP_CONFIG_NAME  = default["AZURE_VM_IP_CONFIG"]
NIC_NAME        = default["AZURE_VM_NIC"]

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

> **_NOTE:_**  
> 
> When setting up the Virtual Machine Password please take into consideration the following guidelines.
> 
> The supplied password must be between 6-72 characters long and must satisfy at least 3 of password complexity 
> requirements from the following: 
> 1) Contains an uppercase character
> 2) Contains a lowercase character
> 3) Contains a numeric digit
> 4) Contains a special character
> 5) Control characters are not allowed
>
> Another important thing to consider is that the Virtual Machine Name **should not** contain spaces.


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
from cloudmesh.management.configuration.config import Config

configuration = "~/.cloudmesh/cloudmesh4.yaml"

conf = Config(configuration)["cloudmesh"]
spec = conf["cloud"]["azure"]
cred = spec["credentials"]
default = spec["default"]

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
network_client  = NetworkManagementClient(credentials, SUBSCRIPTION_ID)
compute_client  = ComputeManagementClient(credentials, SUBSCRIPTION_ID)

# Azure Resource Group
GROUP_NAME      = default["resource_group"]

# Azure Datacenter Region
LOCATION        = cred["AZURE_REGION"]

resource_client.resource_groups.create_or_update(GROUP_NAME, {'location': LOCATION})

# NetworkManagementClient related Variables pulled from Cloudmesh YAML file
VNET_NAME       = default["network"]
SUBNET_NAME     = default["subnet"]
IP_CONFIG_NAME  = default["AZURE_VM_IP_CONFIG"]
NIC_NAME        = default["AZURE_VM_NIC"]

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

# Azure VM Storage details
OS_DISK_NAME    = default["AZURE_VM_DISK_NAME"]
USERNAME        = default["AZURE_VM_USER"]
PASSWORD        = default["AZURE_VM_PASSWORD"]
VM_NAME         = default["AZURE_VM_NAME"]
NIC_ID          = nic.id

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

So far we have covered all the steps to be able to Manage Virtual Machines.
The following example assumes that you have completed all the steps until creating a Virtual Machine.
Now you will be able to perform the following operations:

* Starting a Virtual Machine
* Restarting a Virtual Machine 
* Stopping (Turning Off) a Virtual Machine
* Obtaining a List of all Virtual Machines in your Azure Subscription
* Obtaining a List of Virtual Machines in a Resource Group
* Deleting a Virtual Machine

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
### DiskCreateOption Class

```python
from azure.mgmt.compute.models import DiskCreateOption
```
This class is used for disk Management. This helps with security and scalability. By leveraging Azure Managed Disks 
you are able to scale without worrying about limitations associated with storage accounts.

##### DiskCreateOption Sample - Use case 1: Managed Disks in Virtual Machines

Creation of Managed Disks in Virtual Machines is simplified with implicit creation without specifying all disk details. 
This happens when creating a VM from an OS image in Azure. The storage_profile parameter has an optional setting 
"os_disk" so you don't have to create a storage account as a precondition to create a Virtual Machine.

> **_NOTE:_** 
> 
> Please note that in order to use `DiskCreateOption` for VMs we will need to first set up a `ComputeManagementClient`.

The following sample will depict how to perform multiple operations combining `ComputeManagementClient` and 
`DiskCreateOption`:
* Creating a Managed Data Disk
* Attaching Data Disk to a Virtual Machine
* Detaching a Data Disk
* Deallocating the Virtual Machine (in preparation for a disk resize)
* Increasing the OS disk size

```python
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import DiskCreateOption
from cloudmesh.management.configuration.config import Config

configuration = "~/.cloudmesh/cloudmesh4.yaml"

conf = Config(configuration)["cloudmesh"]
spec = conf["cloud"]["azure"]
cred = spec["credentials"]
default = spec["default"]

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
network_client  = NetworkManagementClient(credentials, SUBSCRIPTION_ID)
compute_client  = ComputeManagementClient(credentials, SUBSCRIPTION_ID)

# Azure Resource Group
GROUP_NAME      = default["resource_group"]

# Azure Datacenter Region
LOCATION        = cred["AZURE_REGION"]

resource_client.resource_groups.create_or_update(GROUP_NAME, {'location': LOCATION})

# NetworkManagementClient related Variables pulled from Cloudmesh YAML file
VNET_NAME       = default["network"]
SUBNET_NAME     = default["subnet"]
IP_CONFIG_NAME  = default["AZURE_VM_IP_CONFIG"]
NIC_NAME        = default["AZURE_VM_NIC"]

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

# Azure VM Storage details
OS_DISK_NAME    = default["AZURE_VM_DISK_NAME"]
USERNAME        = default["AZURE_VM_USER"]
PASSWORD        = default["AZURE_VM_PASSWORD"]
VM_NAME         = default["AZURE_VM_NAME"]
NIC_ID          = nic.id

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
```

# Storage

Let's get started with Azure Storage Service using Python.

## Azure Credentials for Storage

In order to use Storage we will need to create a specific storage account within your Azure portal.
For detailed steps on how to create your storage account please use the link below from Microsoft's documentation:
<https://docs.microsoft.com/en-us/azure/storage/common/storage-quickstart-create-account?tabs=azure-portal>.

### Storage Account

We will be using a general purpose v1 storage account, which provides access to the following Azure Storage services: 
* blobs
* files
* queues
* tables

The only service not provided under v1 storage account is "disks", however we will not be using it. That one is 
available using a general purpose v2 storage account.

### Scope of this document 

We will be covering 2 Storage Services in this document (blob and files). 


### Installing Azure Storage Blob

Let's start with "Blobs".
Installation is pretty straightforward using pip. In your terminal or command line type the following:
```bash
pip install azure-storage-blob
```

### BlockBlobService Class

```python
from azure.storage.blob import BlockBlobService
```

The following is an extract from Microsoft's documentation regarding Block Blobs

> **_Extract from Microsoft's documentation_** 
> 
> Block blobs let you upload large blobs efficiently.
> Block blobs are comprised of blocks, each of which is identified by a block ID. 
> You create or modify a block blob by writing a set of blocks and committing them by their block IDs. 
> Each block can be a different size, up to a maximum of 100 MB, and a block blob can include up to 50,000 blocks. 
> The maximum size of a block blob is therefore approximately 4.75 TB (100 MB X 50,000 blocks). 
> If you are writing a block blob that is no more than 64 MB in size, you can upload it in its entirety with a single 
> write operation.
>
> [Reference link to Microsoft's documentation source ](https://docs.microsoft.com/en-us/python/api/azure-storage-blob/azure.storage.blob.blockblobservice.blockblobservice?view=azure-python)

In order to interact with this service you will need two parameters from your azure storage account:
* Account Name
* Account Key 

Make sure to store your access keys securely. Keys can be regenerated regularly for security. Azure actually provides 
2 keys per storage account which makes it convenient for keeping uninterrupted service while regenerating keys.

##### Storage Connection Configuration Sample

The following script is the first step to connect and start interacting with the Storage Service.

:o: rewrite the example using cloudmesh Config()

```python
from azure.storage.blob import BlockBlobService

ACCOUNT_NAME = '<Account Name from Azure Storage Account>'
ACCOUNT_KEY = '<Access Key from Azure Storage Account>'

block_blob_service = BlockBlobService(account_name=ACCOUNT_NAME, account_key=ACCOUNT_KEY)
```

The following example will perform the following tasks.

1. Create a Container
2. Set Permissions to the Container
3. Create a file (This is using python's `os` class not `BlockBlobService`. This is the file we will use to upload to Azure Storage Service)
4. Add text to the file.
5. Upload the file to the Container we just created using Azure's Storage Service
6. List the blob files inside the container.
7. Download the files from the server.
8. Delete Container (This will also delete all files inside the container).
9. Delete local files (Also using Python's `os` class).

:o: rewrite the example using cloudmesh Config()

```python
import os
from azure.storage.blob import BlockBlobService, PublicAccess

ACCOUNT_NAME = '<Account Name from Azure Storage Account>'
ACCOUNT_KEY = '<Access Key from Azure Storage Account>'

block_blob_service = BlockBlobService(account_name=ACCOUNT_NAME, account_key=ACCOUNT_KEY)

# 1. Create a container in Azure, we will use the container name to interact with the service
container_name ='cloudmeshblobcontainer'
block_blob_service.create_container(container_name)

# 2. The method set_container_acl allows us to set permissions to the container, in this case we will make the blobs public.
block_blob_service.set_container_acl(container_name, public_access=PublicAccess.Container)

# Declare the local path where our files will be created and downloaded
local_path=os.path.expanduser("~/Documents")

# Let's now create a list where we will add the files reference so we can delete the files after our test is completed.
local_file_list = []
i = 1
while i <= 5:
  local_file_name = "CloudmeshBlob_" + str(i) + ".txt"
  # 3. Create file
  created_file_location = os.path.join(local_path, local_file_name)

  # 4. Let's add some text to our file
  file = open(created_file_location, 'w')
  file.write("This is a Cloudmesh BlobContainer Test file # "+str(i))
  file.close()

  # For the purpose of this test we will print information about the file that will be uploaded to Azure's container
  print("\nCreated file: " + created_file_location)

  # 5. Now we will upload the file to Azure's container using create_blob_from_path
  block_blob_service.create_blob_from_path(container_name, local_file_name, created_file_location)
  local_file_list.append(created_file_location)

  # Add 1 to our Integer so our file names are different
  i += 1

# Let's now make sure our blobs were uploaded successfully and download them.
# We will declare another list in order to remove the downloaded files once our test is complete.
downloaded_file_list = []

# 6. list_blobs allows us to list all the blob files inside our container we will loop through them and download them next.
generator = block_blob_service.list_blobs(container_name)
for blob in generator:
    # As we loop through the files we will append downloaded_from_Azure to the name of the file so we can identify
    # the one created locally vs the one downloaded from Azure.
    downloaded_file_name =  str.replace(blob.name ,'.txt', '_downloaded_from_Azure.txt')
    downloaded_file_location = os.path.join(local_path, downloaded_file_name)

    # 7. Now let's download the blobs.
    print("\nDownloading blob to: " + downloaded_file_location)
    block_blob_service.get_blob_to_path(container_name, blob.name, downloaded_file_location)
    downloaded_file_list.append(downloaded_file_location)

# Now we are going to delete the container in Azure and all the local files created and downloaded
# 8. Delete Azure Container
print("\nDeleting container: " + container_name)
block_blob_service.delete_container(container_name)

# 9A. Delete Local Created Files
for localfilename in local_file_list:
    print("\nDeleting created file: "+localfilename)
    os.remove(localfilename)

# 9B. Delete Local Downloaded Files
for downloadedfilename in downloaded_file_list:
    print("\nDeleting downloaded file: "+downloadedfilename)
    os.remove(downloadedfilename)
```


