# =================================================================
#
# Terms and Conditions of Use
#
# Unless otherwise noted, computer program source code of this
# distribution # is covered under Crown Copyright, Government of
# Canada, and is distributed under the MIT License.
#
# The Canada wordmark and related graphics associated with this
# distribution are protected under trademark law and copyright law.
# No permission is granted to use them outside the parameters of
# the Government of Canada's corporate identity program. For
# more information, see
# http://www.tbs-sct.gc.ca/fip-pcim/index-eng.asp
#
# Copyright title to all 3rd party software distributed with this
# software is held by the respective copyright holders as noted in
# those files. Users are asked to read the 3rd Party Licenses
# referenced with those assets.
#
# Copyright (c) 2025 Tom Kralidis
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

import importlib
import logging
import os

from typing import Dict, Type
from pygeometa.schemas.base import BaseOutputSchema

LOGGER = logging.getLogger(__name__)
THISDIR = os.path.dirname(os.path.realpath(__file__))

# runtime mapping: schema_key -> class object
_DISCOVERED_SCHEMAS: Dict[str, Type[BaseOutputSchema]] = {}
_DISCOVERY_DONE = False


def _discover_schemas():
    """Discover local schema packages (folders with __init__.py) in ./schemas.

    For each discovered package module, import it and choose the first class
    that is a subclass of BaseOutputSchema (excluding BaseOutputSchema itself).
    The mapping key will be:
      - module attribute SCHEMA_NAME if defined, else
      - the package (folder) name.

    This function is idempotent and caches results in _DISCOVERED_SCHEMAS.
    """
    global _DISCOVERY_DONE, _DISCOVERED_SCHEMAS  # noqa
    if _DISCOVERY_DONE:
        return

    LOGGER.debug("Discovering schema packages in %s", THISDIR)
    pkg_name = __name__  # 'pygeometa.schemas'

    try:
        entries = sorted(os.listdir(THISDIR))
    except OSError:
        entries = []

    for entry in entries:
        path = os.path.join(THISDIR, entry)
        # look for directories with __init__.py only
        if not os.path.isdir(path):
            continue
        init_py = os.path.join(path, "__init__.py")
        if not os.path.isfile(init_py):
            continue

        module_name = f"{pkg_name}.{entry}"
        try:
            # import normally so package semantics and relative imports work
            module = importlib.import_module(module_name)
        except Exception as exc:
            LOGGER.exception(f"Failed to import schema package {module_name}: {exc}") # noqa
            continue

        # Key selection: prefer explicit module-provided `name`,
        # else use dotted name
        schema_key = getattr(module, "name", None) or module.__name__

        # Collect candidate classes in module that are subclasses
        # of BaseOutputSchema
        candidates = []
        for attr_name in dir(module):
            try:
                attr = getattr(module, attr_name)
            except Exception:
                # some modules raise on attribute access; skip those
                continue
            if not isinstance(attr, type):
                continue
            # Exclude BaseOutputSchema itself
            if attr is BaseOutputSchema:
                continue
            try:
                if issubclass(attr, BaseOutputSchema):
                    candidates.append(attr)
            except TypeError:
                # issubclass can raise if attr is not a class; ignore
                continue

        if not candidates:
            LOGGER.warning(f"No BaseOutputSchema subclass found in {module_name}; skipping" ) # noqa
            continue

        # pick the most concrete subclass (leaf in the inheritance chain)
        # the class with the longest method-resolution order (MRO)
        chosen_cls = sorted(candidates, key=lambda c: len(getattr(c, "__mro__", ())), reverse=True)[0] # noqa

        # Ensure uniqueness of keys
        if schema_key in _DISCOVERED_SCHEMAS:
            existing = _DISCOVERED_SCHEMAS[schema_key]
            if existing is chosen_cls:
                LOGGER.debug("Schema key {schema_key} already registered with same class; skipping") # noqa
                continue
            LOGGER.warning(f"""Duplicate schema key '{schema_key}' (module {module_name}, class {chosen_cls.__name__}). # noqa 
                           Keeping first discovered: {existing.__module__}.{existing.__name__}""") # noqa
            continue

        _DISCOVERED_SCHEMAS[schema_key] = chosen_cls
        LOGGER.info(f"Discovered schema '{schema_key}' -> {chosen_cls.__module__}.{chosen_cls.__name__}") # noqa

    _DISCOVERY_DONE = True


def get_supported_schemas(details: bool = False,
                          include_autodetect: bool = False) -> list:
    """
    Get supported schemas.

    :param details: provide read/write details
    :param include_autodetect: include magic auto detection mode

    :returns: list of supported schemas (strings) or details matrix
    """
    _discover_schemas()

    def has_mode(plugin: BaseOutputSchema, mode: str) -> bool:
        enabled = False

        try:
            _ = getattr(plugin, mode)('test')
        except NotImplementedError:
            pass
        except Exception:
            enabled = True

        return enabled

    LOGGER.debug('Generating list of supported schemas')

    if not details:
        schema_names = []
        for cls in _DISCOVERED_SCHEMAS.values():
            try:
                schema_names.append(cls().name)
            except Exception:
                continue
        if include_autodetect:
            schema_names.append("autodetect")
        return schema_names

    schema_matrix = []
    for key, cls in _DISCOVERED_SCHEMAS.items():
        nm = key
        try:
            schema_inst = cls()
            nm = schema_inst.name
            can_read = has_mode(schema_inst, "import_")
            can_write = has_mode(schema_inst, "write")
            description = getattr(schema_inst, "description", "")
        except Exception:
            LOGGER.exception(f"Error instantiating schema class for key {key}") # noqa
            can_read = False
            can_write = False
            description = ""

        schema_matrix.append({
            "id": nm,
            "description": description,
            "read": can_read,
            "write": can_write
        })

    if include_autodetect:
        schema_matrix.append({
            "id": "autodetect",
            "description": "Auto schema detection",
            "read": True,
            "write": False
        })

    return schema_matrix


def load_schema(schema_name: str) -> BaseOutputSchema:
    """
    loads schema plugin by name

    :param schema_name: shortname of schema

    :returns: plugin object
    """
    _discover_schemas()
    LOGGER.debug("Available schemas: %s", list(_DISCOVERED_SCHEMAS.keys()))

    # allow 'autodetect' to be handled elsewhere (kept for parity)
    if schema_name == "autodetect":
        raise InvalidSchemaError("Autodetect is not a concrete schema")

    cls = None
    for v in _DISCOVERED_SCHEMAS.values():
        if v().name == schema_name:
            cls = v
            break

    if not cls:
        msg = f"Schema {schema_name} not found"
        LOGGER.exception(msg)
        raise InvalidSchemaError(msg)

    try:
        return cls()
    except Exception as exc:
        msg = f"Failed to instantiate schema {schema_name}: {exc}"
        LOGGER.exception(msg)
        raise InvalidSchemaError(msg)


class InvalidSchemaError(Exception):
    """Invalid plugin"""
    pass
