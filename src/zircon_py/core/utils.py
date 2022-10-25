from typing import Any, Dict

__author__ = "kancherj"
__copyright__ = "kancherj"
__license__ = "MIT"


def generate_artifact_id(project: str, path: str, version: int) -> str:
    """Generate ArtifactDB Resource ID

    Args:
        project (str): project id
        path (str): path to the resource
        version (int): version to access

    Returns:
        str: artifactdb identifier
    """
    return f"{project}:{path}@{str(version)}"


def unpack_artifactdb_id(artifact_id: str) -> Dict[str, Any]:
    """split an artifactdb id into project, path and version

    Args:
        artifact_id (str): artifact id

    Raises:
        Exception: when artifact_id is not properly formatted

    Returns:
        Dict[str, Any]: return project, path and version
    """
    id1 = artifact_id.index(":")
    if id1 < 0:
        raise Exception("could not identify project from 'id'")
    elif id1 == 0:
        raise Exception(f"'id' should not have an empty project")

    id2 = artifact_id.rindex("@")
    if id2 < 0:
        raise Exception("could not identify version from 'id'")
    elif id2 == len(artifact_id) - 1:
        raise Exception("'id' should not have an empty version")

    if id2 < id1:
        raise Exception("could not identify version from 'id'")
    elif id1 + 1 == id2:
        raise Exception("'id' should not have an empty path")

    return {
        "project": artifact_id[0:id1],
        "path": artifact_id[id1 + 1 : id2],
        "version": artifact_id[id2 + 1 :],
    }


def extract_entities_by_name_or_index(
    x: list,
    index: Any,
    name: str = "name",
    type: str = "entry",
    context: str = "array",
):
    """Given an array of objects with a name-like property, extract an entry by its name or index.

    Args:
        x (list): an array of resources or entities
        index (Any): Index or String of the entity of interest
        name (str): Name of the name-like property across all objects in `x`.
        entry (str): Type represented by each object in `x`, used for error messages only.
        context (str): Context of the array in `x`, used for error messages only.

    Returns:
        Dict: the specific object in x
    """
    if isinstance(index, str):
        for i in x:
            if i[name] == index:
                return i
        raise Exception(f"no {index} named {name} in {context}")

    if isinstance(index, int) and (index <= len(x) or index > 0):
        return x[index]

    raise Exception(f"no {index} named {name} in {context}")
