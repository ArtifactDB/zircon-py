from .Resource import Resource

__author__ = "kancherj"
__copyright__ = "kancherj"
__license__ = "MIT"


class Artifact:
    def __init__(self, resource: "Resource") -> None:
        self._resource = resource

    @property
    def resource(self):
        return self._resource

    @property
    def project(self):
        return self._resource.project

    @property
    def path(self):
        return self._resource.path

    @property
    def version(self):
        return self._resource.version

    @property
    def metadata(self):
        return self._resource.metadata

    @property
    def id(self):
        return self._resource.id
