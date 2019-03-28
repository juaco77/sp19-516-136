import cloudmesh.vm.provider.azure.Provider


class Manager(object):

    def __init__(self):
        print("init {name}".format(name=self.__class__.__name__))

	def _provider(self, service):
		provider = None

		service = service.lower()

		if service == "azure":
			provider = cloudmesh.vm.provider.azure.Provider.Provider()

		return provider