from .utils import generate_artifact_id
from .config import config
from typing import Any, Dict
from urllib.parse import quote
import requests
from pathlib import Path
from tempfile import mkdtemp
import hashlib

__author__ = "kancherj"
__copyright__ = "kancherj"
__license__ = "MIT"


class Resource:
    """Defines a File or a Resource in ArtifactDB.

    Raises:
        Exception: ARTIFACTDB_URL is not set in config
        Exception: Error accessing metadata or data
    """

    def __init__(
        self, project: str, path: str, version: str, metadata: dict = None
    ) -> None:
        self._project = project
        self._path = path
        self._version = version
        self._metadata = metadata

        if config["ARTIFACTDB_URL"] is None:
            raise Exception("ARTIFACTDB_URL is not set in config")

    @property
    def project(self):
        return self._project

    @property
    def path(self):
        return self._path

    @property
    def version(self):
        return self._version

    @property
    def metadata(self):
        if self._metadata is None:
            self._metadata = self.download_metadata(self.id)

        return self._metadata

    @property
    def id(self):
        return generate_artifact_id(self.project, self.path, self.version)

    @property
    def gprn(self):
        meta = self.metadata
        return meta["_extra"]["gprn"]

    def download(self, force_buffer=False):
        return self.download_file(self.id, force_buffer=force_buffer)

    # TODO: Cache resources as they are download : pyBiocFileCache
    def download_metadata(
        self,
        artifact_id: str,
        cache: bool = False,
        follow_link: bool = True,
    ) -> Dict:
        """Default method to access metadata from ArtifactDB instance

        Args:
            base_url (str): base url to artifactdb rest api
            artifact_id (str): artifact id
            cache (bool, optional): cache files ?. Defaults to False.
            follow_link (bool, optional): follow redirections ?. Defaults to True.

        Raises:
            Exception: accessing metadata fails

        Returns:
            Dict: resource's metadata
        """
        m_url = self.generate_metadata_url(
            artifact_id=artifact_id,
            follow_link=follow_link,
        )
        try:
            r = requests.get(m_url, verify=False)
        except Exception as e:
            raise Exception(f"Error accessing metadata for {m_url} from API: {str(e)}")

        if r.status_code != 200:
            raise Exception(
                f"Error accessing metadata for {m_url} from API, status code :{r.status_code}"
            )

        return r.json()

    # TODO: Cache using pyBiocFileCache
    # also implement buffer so someone just gets r.content
    def download_file(
        self,
        artifact_id: str,
        cache: bool = False,
        force_buffer: bool = False,
        path: str = None,
    ) -> str:
        """Download a file from ArtifactDB

        Args:
            base_url (str): artifact db instance
            artifact_id (str): artifact id
            cache (bool, optional): cache files ?. Defaults to False.
            force_buffer (bool, optional): access buffer instead of path ?. Defaults to False.
            path (str, Optional): path to store the file to, defaults to tmp directory

        Raises:
            Exception: failed to download resource

        Returns:
            str: path to file
        """
        f_url = self.generate_download_url(artifact_id=artifact_id)

        final_path = path
        if final_path is None:
            final_path = str(
                Path(mkdtemp(), hashlib.md5(f_url.encode("utf-8")).hexdigest())
            )

        try:
            with requests.get(f_url, stream=True, verify=False) as r:
                r.raise_for_status()
                with open(final_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        f.write(chunk)
        except Exception as e:
            raise Exception(f"Failed to download resoure {f_url} ::: {str(e)}")

        # if force_buffer:
        #     return r.content

        return final_path

    def generate_metadata_url(self, artifact_id: str, follow_link: bool = True) -> str:
        """generate url to access metadata from artifactdb rest api

        Args:
            base_url (str): base url to artifactdb rest api
            artifact_id (str): artifact id
            follow_link (bool, optional): follow redirections ?. Defaults to True.

        Returns:
            str: The URL to `GET` to obtain JSON-formatted metadata.
        """
        r_url = f"{config['ARTIFACTDB_URL']}/files/{quote(artifact_id)}/metadata"
        if follow_link:
            r_url = f"{r_url}?follow_link=true"
        return r_url

    def generate_download_url(self, artifact_id: str) -> str:
        """Construct the endpoint URL to download a resource from an ArtifactDB REST API.

        Args:
            base_url (str): base url to artifactdb rest api
            artifact_id (str): artifact id

        Returns:
            str: The URL to `GET` to download the file.
        """
        return f"{config['ARTIFACTDB_URL']}/files/{quote(artifact_id)}"
