from .config import config
from .Resource import Resource
import requests
from urllib.parse import quote
from pathlib import Path
import os

__author__ = "kancherj"
__copyright__ = "kancherj"
__license__ = "MIT"


class Project:
    """Interface to interact with projects in ArtifactDB"""

    def __init__(self, project: str, version: str = None) -> None:
        self._project = project
        self._version = version

        if config["ARTIFACTDB_URL"] is None:
            raise Exception("ARTIFACTDB_URL is not set in config")

    @property
    def project(self):
        return self._project

    @property
    def version(self):
        return self._version

    @property
    def metadata(self):
        if self._metadata is None:
            self._metadata = self.download_metadata()

        return self._metadata

    # TODO: Cache resources as they are download : pyBiocFileCache
    def download_metadata(self) -> dict:
        """Default method to access metadata from ArtifactDB instance

        Raises:
            Exception: accessing metadata fails

        Returns:
            dict: projects's metadata
        """

        m_url = self._generate_entity_url("metadata")

        try:
            r = requests.get(m_url, verify=False)
        except Exception as e:
            raise Exception(f"Error accessing metadata for {m_url} from API: {str(e)}")

        if r.status_code != 200:
            raise Exception(
                f"Error accessing metadata for {m_url} from API, status code :{r.status_code}"
            )

        return r.json()

    def clone(
        self,
        dir: str,
        link_only: bool = True,
        cache: bool = False,
    ):
        """Clone a project to the local file system

        Args:
            dir (str): Directory on local file system to clone to
            link_only (bool, optional): All non-metdata files are replaced by placeholders
            cache (bool, optional): cache files ?. Defaults to False.
        """

        if not Path(dir).exists():
            os.makedir(dir)

        meta = self.metadata

        for m in meta:
            fm_path = f"{dir}/{m['path']}"
            if not Path(fm_path).exists():
                os.makedir(fm_path)

            meta_path = m["path"]

            if not meta_path.endsWith(".json"):
                meta_path = f"{meta_path}.json"

            rsy = Resource(
                self._project,
                meta_path,
                self._version,
            )

            rsy.download_metadata(path=meta_path)

            # TODO: deal with link_only later
            if not link_only:
                rsy.download_file(path=m["path"])

    def get_permissions(self) -> dict:
        """Get Permissions for a project

        Returns:
            dict: Projects's permissions
        """

        p_url = self._generate_entity_url("permissions")

        try:
            r = requests.get(p_url, verify=False)
        except Exception as e:
            raise Exception(
                f"Error accessing permissions for {p_url} from API: {str(e)}"
            )

        if r.status_code != 200:
            raise Exception(
                f"Error accessing permissions for {p_url} from API, status code :{r.status_code}"
            )

        return r.json()

    def _generate_entity_url(self, entity: str):
        """Generate a url for each endpoint in projects

        Args:
            entity (str): entity to access
        """
        m_url = f"{config['ARTIFACTDB_URL']}/projects/{quote(self._project)}"

        if self._version is not None:
            m_url = f"{m_url}/version/{self._version}"

        m_url = f"{m_url}/{entity}"
