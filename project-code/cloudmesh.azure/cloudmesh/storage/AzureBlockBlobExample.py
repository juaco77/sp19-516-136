import os
from azure.storage.blob import BlockBlobService, PublicAccess

ACCOUNT_NAME = '<Account Name from Azure Storage Account>'
ACCOUNT_KEY = '<Access Key from Azure Storage Account>'

block_blob_service = BlockBlobService(account_name=ACCOUNT_NAME, account_key=ACCOUNT_KEY)

# Create a container in Azure, we will use the container name to interact with the service
container_name ='cloudmeshblobcontainer'
block_blob_service.create_container(container_name)

# The method set_container_acl allows us to set permissions to the container, in this case we will make the blobs public.
block_blob_service.set_container_acl(container_name, public_access=PublicAccess.Container)

# Declare the local path where our files will be created and downloaded
local_path=os.path.expanduser("~/Documents")

# Let's now create a list where we will add the files reference so we can delete the files after our test is completed.
local_file_list = []
i = 1
while i <= 5:
  local_file_name = "CloudmeshBlob_" + str(i) + ".txt"
  created_file_location = os.path.join(local_path, local_file_name)

  # Let's add some text to our file
  file = open(created_file_location, 'w')
  file.write("This is a Cloudmesh BlobContainer Test file # "+str(i))
  file.close()

  # For the purpose of this test we will print information about the file that will be uploaded to Azure's container
  print("\nCreated file: " + created_file_location)

  # Now we will upload the file to Azure's container using create_blob_from_path
  block_blob_service.create_blob_from_path(container_name, local_file_name, created_file_location)
  local_file_list.append(created_file_location)

  # Add 1 to our Integer so our file names are different
  i += 1

# Let's now make sure our blobs were uploaded successfully and download them.
# We will declare another list in order to remove the downloaded files once our test is complete.
downloaded_file_list = []

# list_blobs allows us to list all the blob files inside our container we will loop through them and download them next.
generator = block_blob_service.list_blobs(container_name)
for blob in generator:
    # As we loop through the files we will append downloaded_from_Azure to the name of the file so we can identify
    # the one created locally vs the one downloaded from Azure.
    downloaded_file_name =  str.replace(blob.name ,'.txt', '_downloaded_from_Azure.txt')
    downloaded_file_location = os.path.join(local_path, downloaded_file_name)

    # Now let's download the blobs.
    print("\nDownloading blob to: " + downloaded_file_location)
    block_blob_service.get_blob_to_path(container_name, blob.name, downloaded_file_location)
    downloaded_file_list.append(downloaded_file_location)

# Now we are going to delete the container in Azure and all the local files created and downloaded
# Delete Azure Container
print("\nDeleting container: " + container_name)
block_blob_service.delete_container(container_name)

# Delete Local Created Files
for localfilename in local_file_list:
    print("\nDeleting created file: "+localfilename)
    os.remove(localfilename)

# Delete Local Downloaded Files
for downloadedfilename in downloaded_file_list:
    print("\nDeleting downloaded file: "+downloadedfilename)
    os.remove(downloadedfilename)