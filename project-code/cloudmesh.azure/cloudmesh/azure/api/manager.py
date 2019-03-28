import cloudmesh.vm.provider.azure.Provider

class Manager(object):

    def __init__(self):
        print("init {name}".format(name=self.__class__.__name__))

    def list(self, service):
		provider = None
		self.service = self.service.lower()
		
		if self.service == "azure":
			provider = cloudmesh.vm.provider.azure.Provider.Provider()
		
		return provider
		
