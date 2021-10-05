import os

from typing import List
from pathlib import Path


def get_cirrus_lib_requirements() -> List[str]:
    '''
    Get the cirrus-lib dependency specified for this package.
    '''
    try:
        from importlib import metadata
    except ImportError:
        import importlib_metadata as metadata

    package_name = __package__.split('.')[0]

    reqs = []
    for req in metadata.requires(package_name):
        req, *others = req.split(';')
        if ' extra == "lib"' in others:
            reqs.append(req)

    return reqs


def relative_to_cwd(path: Path) -> Path:
    common_path = Path(os.getcwd())
    relative = ''
    path = path.resolve()
    result = path

    while True:
        try:
            result = path.relative_to(common_path)
        except ValueError:
            _common_path = common_path.parent
            relative += '../'
        else:
            if not relative:
                relative = './'
            return Path(relative + str(result))

        if _common_path == common_path:
            break

        common_path = _common_path

    return result
