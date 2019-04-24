# Azure VM Management

| Joaquin Avila Eggleton
| javilaeg@iu.edu
| Indiana University
| hid: sp19-516-136
| github: [:cloud:](https://github.com/cloudmesh-community/sp19-516-136/project-report/report.md)

## Project Documentation
The purpose of this project is to learn about features available in Azure's Python libraries to manage Virtual Machines.

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

#Virtual Machines 

Let's get started with Azure Virtual Machine Management using Python.

###Azure Python Libraries 
In order to manage Azure Virtual Machines the following libraries will need to be imported.
* ServicePrincipalCredentials
* ResourceManagementClient
* ComputeManagementClient
* NetworkManagementClient

The following sections will dive deeper into each library's capabilities.

###ServicePrincipalCredentials Class

```python
from azure.common.credentials import ServicePrincipalCredentials
```

The concept of Service Principal in Azure allows us to store credentials securely in a configuration file, the registry, 
or Azure KeyVault. 
This helps automated tools that will use Azure Services (like Cloudmesh) interact as applications and not a fully 
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
* AZURE_PUBLIC_CLOUD 
* AZURE_CHINA_CLOUD 
* AZURE_US_GOV_CLOUD 
* AZURE_GERMAN_CLOUD 

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
by all Management Classes, which we will be reviewing next `(ResourceManagementClient, ComputeManagementClient and 
NetworkManagementClient)`.

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
* ComputeManagementClient
* NetworkManagementClient

##### Resource Management
Provides operations for working with resources and resource groups.
To instantiate a ResourceManagementClient you will need two mandatory parameters. 
* **Credentials** - Refer to ServicePrincipalCredentials section for more details
* **Subscription ID** - Refer to Subscription ID section for more details

######Optional parameters are:
* **API Version** - API version to use if no profile is provided, or if missing in profile.
* **Base URL** - Service URL
* **Profile** - A profile definition, from KnownProfiles to dict.

##### ResourceManagementClient Code Sample

We will extend the code from ServicePrincipalCredentials and incorporate ResourceManagementClient to create a resource
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
resource_client = ResourceManagementClient(credentials, SUBSCRIPTION_ID)

GROUP_NAME = 'Cloudmesh Group' 
LOCATION = 'EastUS'
resource_client.resource_groups.create_or_update(GROUP_NAME, {'location': LOCATION})

```







Use case 1: Setup for Key Vault samples, such as creating rest clients, creating a sample resource group if needed, and ensuring proper access for the service principal.
self.resource_mgmt_client = ResourceManagementClient(self.mgmt_creds, self.config.subscription_id)

# ensure the service principle has key vault as a valid provider
self.resource_mgmt_client.providers.register('Microsoft.KeyVault')

# ensure the intended resource group exists
self.resource_mgmt_client.resource_groups.create_or_update(self.config.group_name, {'location': self.config.location})

 

Use case 2:
self._resource_client = ResourceManagementClient(self._credentials, self._subscription_id)
self._network_client = NetworkManagementClient(self._credentials, self._subscription_id)
self._monitor_client = MonitorClient(self._credentials, self._subscription_id)

self._resource_groups = []
for resource_group in self._resource_client.resource_groups.list():
	self._resource_groups.append(resource_group.name)
 
Use Case 3:
def check_resource_existence(client, resource_group):
    """Create if resource group exists in Azure or not

    :param client: Azure object using ResourceManagementClient
    :param resource_group: string, name of Azure resource group
    :return: True if exists, otherwise False
    :rtype: boolean
    """
    response = client.resource_groups.check_existence(resource_group)
    return response

Use Case 4 - Create or Update Resource Group:
def create_resource_group(client, resource_group, region):
    """Create resource group in Azure

    :param client: Azure object using ResourceManagementClient
    :param resource_group: string, name of Azure resource group
    :param region: string, name of Azure region
    """
    response = client.resource_groups.create_or_update(
        resource_group, {'location': region})
    LOG.debug("resource_group response: {0}".format(response))
    LOG.debug("Created Resource Group '{0}' in Azure".format(resource_group)) 
	
Use Case 5 - Create Resource Group:



from azure.mgmt.resource import ResourceManagementClient
resource_group_client = ResourceManagementClient(
    credentials, 
    SUBSCRIPTION_ID
)


##### Compute Management
Provides operations for working with resources and resource groups.
To instantiate a ComputeManagementClient you will need two mandatory parameters. 
1) Credentials
2) Subscription ID 

https://www.programcreek.com/python/example/97119/azure.mgmt.compute.ComputeManagementClient

Methods
- list(location, custom_headers=None, raw=False, **operation_config)
Gets, for the specified location, the current compute resource usage information as well as the limits for compute resources under the subscription.

Use Case 1 - Usage 
    from azure.mgmt.compute import ComputeManagementClient

    compute_client = ComputeManagementClient(creds)

    usage_paged=compute_client.usage.list(location).usages
    core_usage=[usage for usage in usage_paged if usage.name.value == 'cores' ]
    available_cores=core_usage[0].limit-core_usage[0].current_value

    print "Current Cores %d Current Limit %d Available Cores %d Requested Cores %d" %(core_usage[0].current_value,core_usage[0].limit,available_cores,numofcores)

    print "###QUOTACHECK###"
    if numofcores > available_cores:
        print "CRITICAL Insufficient Quota, PCF will NOT deploy"
        sys.exit(0)
    else:
        print "Subscription Has Enough Quota"


SnapshotsOperations class
https://docs.microsoft.com/en-us/python/api/azure-mgmt-compute/azure.mgmt.compute.v2018_09_30.operations.snapshotsoperations?view=azure-python
Methods
create_or_update(resource_group_name, snapshot_name, snapshot, custom_headers=None, raw=False, polling=True, **operation_config)	
Creates or updates a snapshot.

delete(resource_group_name, snapshot_name, custom_headers=None, raw=False, polling=True, **operation_config)	
Deletes a snapshot.

get(resource_group_name, snapshot_name, custom_headers=None, raw=False, **operation_config)	
Gets information about a snapshot.

grant_access(resource_group_name, snapshot_name, access, duration_in_seconds, custom_headers=None, raw=False, polling=True, **operation_config)	
Grants access to a snapshot.

list(custom_headers=None, raw=False, **operation_config)	
Lists snapshots under a subscription.

list_by_resource_group(resource_group_name, custom_headers=None, raw=False, **operation_config)	
Lists snapshots under a resource group.

revoke_access(resource_group_name, snapshot_name, custom_headers=None, raw=False, polling=True, **operation_config)	
Revokes access to a snapshot.

update(resource_group_name, snapshot_name, snapshot, custom_headers=None, raw=False, polling=True, **operation_config)	
Updates (patches) a snapshot.

		
Use Case 2 - Get Resource by Name



def _get_node_by_name(self, node_name):
        """Get node instance by name

        We need to use expand param to get full instance info from InstanceView (e.g. power state).
        More details in this issue: https://github.com/Azure/azure-rest-api-specs/issues/117
        """
        config = self.load_config()

        compute_client = self.get_management_service(ComputeManagementClient, config=config)

        try:
            return compute_client.virtual_machines.get(config['resource_group_name'], node_name, expand='InstanceView')
        except CloudError, error:
            if not isinstance(error.inner_exception, CloudErrorData) or \
                              error.inner_exception.error != 'ResourceNotFound' or 'not found' not in error.message:
                raise error

		
from azure.mgmt.compute import ComputeManagementClient
resource_group_client = ResourceManagementClient(
    credentials, 
    SUBSCRIPTION_ID
)

##### Network Management
Provides operations for working with resources and resource groups.
To instantiate a NetworkManagementClient you will need two mandatory parameters. 
1) Credentials
2) Subscription ID 


def _get_or_create_subnet(self, config=None):
        LOG.info("***** Calling _get_or_create_subnet *******************")
        config = config or self.load_config()

        network_client = self.get_management_service(NetworkManagementClient, config=config)

        # Try get existing storage by name
        try:
            return network_client.subnets.get(config['resource_group_name'], config['vnet_name'], config['subnet_name'])
        except CloudError, error:
            if error.inner_exception.error != 'NotFound':
                raise error

        # Create new one
        async_subnet_creation = network_client.subnets.create_or_update(
            config['resource_group_name'],
            config['vnet_name'],
            config['subnet_name'],
            {'address_prefix': '10.0.1.0/24'}
        )
        async_subnet_creation.wait()
        return async_subnet_creation.result() 
		
		
		

from azure.mgmt.network import NetworkManagementClient

network_client = NetworkManagementClient(
    credentials, 
    SUBSCRIPTION_ID
)


##### DiskCreateOption

This class is used for disk Management. This helps with security and scalability. By leveraging Azure Managed Disks you are able to scale without worrying about limitations associated with storage accounts.

Use case 1: Creating an empty Managed Disk:
from azure.mgmt.compute.models import DiskCreateOption

        async_creation = compute_client.disks.create_or_update(
            'my_resource_group',
            'my_disk_name',
            {
                'location': 'westus',
                'disk_size_gb': 20,
                'creation_data': {
                    'create_option': DiskCreateOption.empty
                }
            }
        )
        disk_resource = async_creation.result()

Use case 2: Creating a Managed Disk from Blob Storage:

from azure.mgmt.compute.models import DiskCreateOption

        async_creation = compute_client.disks.create_or_update(
            'my_resource_group',
            'my_disk_name',
            {
                'location': 'westus',
                'creation_data': {
                    'create_option': DiskCreateOption.import_enum,
                    'source_uri': 'https://bg09.blob.core.windows.net/vm-images/non-existent.vhd'
                }
            }
        )
        disk_resource = async_creation.result()

Use case 3: Managed Disks in Virtual Machines
Creation of Managed Disks in Virtual Machines is simplified with implicit creation without specifying all disk details. This happens when creating a VM from an OS image in Azure. The storage_profile parameter has an optional setting "os_disk" so you don't have to create a storage account as a precondition to create a Virtual Machine.

Here's a sample of how to attach a previously provisioned Managed Disk to a Virtual Machine.

			vm = compute.virtual_machines.get(
                'my_resource_group',
                'my_vm'
            )
            managed_disk = compute_client.disks.get('my_resource_group', 'myDisk')
            vm.storage_profile.data_disks.append({
                'lun': 12, # You choose the value, depending of what is available for you
                'name': managed_disk.name,
                'create_option': DiskCreateOptionTypes.attach,
                'managed_disk': {
                    'id': managed_disk.id
                }
            })
            async_update = compute_client.virtual_machines.create_or_update(
                'my_resource_group',
                vm.name,
                vm,
            )
            async_update.wait()
		
		
		
from azure.mgmt.compute.models import DiskCreateOption
 # Create managed data disk
        print('\nCreate (empty) managed Data Disk')
        async_disk_creation = compute_client.disks.create_or_update(
            GROUP_NAME,
            'mydatadisk1',
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
        print('\nGet Virtual Machine by Name')
        virtual_machine = compute_client.virtual_machines.get(
            GROUP_NAME,
            VM_NAME
        )

        # Attach data disk
        print('\nAttach Data Disk')
        virtual_machine.storage_profile.data_disks.append({
            'lun': 12,
            'name': 'mydatadisk1',
            'create_option': DiskCreateOption.attach,
            'managed_disk': {
                'id': data_disk.id
            }
        })
        
        
        
SUBSCRIPTION_ID = 'subscription-id'
GROUP_NAME = 'myResourceGroup'
LOCATION = 'westus'
VM_NAME = 'myVM
