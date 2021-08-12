# blender-addon-rigified
# Copyright (C) 2021 coldrye solutions, Carsten Klein and Contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import re

import bpy


# {___$2323123#@@#~\..+++=+-)_))(((././.. {.. .. }. . / ./ / . ./ .. ^ . .\'  \    '' @: : ; " > .,<___}
# expected rig name: ___2323123____
# expected category name: _2323123
def normalize_filename(filename, is_category=False):
    result = filename.lower()
    # remove all unwanted characters
    result = re.sub(r'[^a-zA-Z0-9_.\- ]', '', result)
    # keep user provided underscores for now
    # FIXME: replace by randomly generated id to prevent users from breaking the "algorithm"
    result = re.sub(r'_', 'RIGIFYKEEPUNDERSCORE', result)
    # eliminate all leading whitespace
    result = re.sub(r'^[ ]+', '', result)
    # eliminate all trailing whitespace
    result = re.sub(r'[ ]+$', '', result)
    # convert all whitespace and dashes into underscores
    result = re.sub(r'[ -]+', '_', result)
    # collapse all successive underscores
    result = re.sub(r'[_]+', '_', result)
    # restore user provided underscores
    # FIXME: replace by random id generated above
    result = re.sub(r'RIGIFYKEEPUNDERSCORE', '_', result)
    # remove all leading underscores as they will hide the rig since it will be considered private
    result = re.sub(r'^[_]+', '', result)
    # trailing underscores are just redundant
    result = re.sub(r'[_]+$', '', result)
    # FIXME: report an invalid input error in the operator instead
    # filenames starting with a number will be renamed to rig_* or cat_* depending on is_category
    # result = re.sub(r'^([0-9])(.+)$', r'cat_\1\2' if is_category else r'rig_\1\2', result)
    if is_category:
        # TODO: filter out _lib suffix as it is reserved
        result = re.sub(r'[.]+', '', result)
        result = re.sub(r'^[.]+', '', result)
        result = re.sub(r'[.]+$', '', result)
    else:
        result = re.sub(r'[.]+', '', result)
    return result


def try_init_folder(path):
    """ Try to create the folders along the specified path
    """
    exists = os.path.exists(path)
    if exists:
        if not os.path.isdir(path):
            raise Exception('not a folder ' + path)
    else:
        os.makedirs(path, exist_ok=True)


def try_get_or_init_meta_rigs_root(feature_name, category=''):
    """ Try to get the specified metarigs folder or initialize the folders along the specified path
    """
    feature_root = try_get_or_init_feature_root(feature_name)
    result = os.path.join(feature_root, 'metarigs', category)
    try_init_folder(result)
    return result


def try_get_or_init_rigs_root(feature_name, category=''):
    """ Try to get the specified rigs folder or initialize the folders along the specified path
    """
    feature_root = try_get_or_init_feature_root(feature_name)
    result = os.path.join(feature_root, 'rigs', category)
    try_init_folder(result)
    return result


def try_get_or_init_feature_root(feature_name):
    """ Try to get the specified feature or initialize the folders along the specified path from an existing
        scripts path that was configured in blender preferences.py.

        The so resolved path will be located in the rigify feature sets folder.

        The default base path being used is <blender_config>/<version>/scripts/rigify
        On windows this will resolve to <UserHomeDir>\<AppData>\Blender Foundation\<version>\scripts\rigify
    """
    root = try_get_or_init_feature_sets_root()
    result = os.path.join(root, feature_name)
    try_init_folder(result)
    initpy = os.path.join(result, '__init__.py')
    if not os.path.exists(initpy):
        code = []
        code.append('rigify_info = {')
        code.append('    "name": "' + feature_name + '",')
        code.append('    "created_by": "rigified",')
        code.append('}')
        f = open(initpy, 'w')
        f.write('\n'.join(code))
        f.close()
    return result


def try_get_or_init_feature_sets_root():
    """ Try to get the feature sets root or initialize the folders along the specified path from an existing
        scripts path that was configured in blender preferences.py.

        The so resolved path will be located in the rigify feature sets folder.

        The default base path being used is <blender_config>/<version>/scripts/rigify
        On windows this will resolve to <UserHomeDir>\<AppData>\Blender Foundation\<version>\scripts\rigify
    """
    result = None

    # FIXME make this simpler by using bpy.utils.user_resource('SCRIPTS', "rigify")

    # find provable candidates where there is either a scripts/rigify folder or where we can safely
    # create such a folder. existing candidates with a writable scripts/rigify folder will take
    # precedence over folders where there is no such folder
    # otherwise we will sort out these impossible candidates for later error reporting
    provable_candidates = []
    impossible_candidates = []
    for base_path in bpy.utils.script_paths():
        candidate = os.path.join(base_path, 'rigify')
        if os.path.exists(candidate):
            if os.path.isdir(candidate) and os.access(candidate, os.W_OK):
                provable_candidates.append((True, candidate))
            else:
                impossible_candidates.append(candidate)
        elif os.access(base_path, os.W_OK):
            provable_candidates.append((False, candidate))
        else:
            impossible_candidates.append(candidate)

    for provable_candidate in sorted(provable_candidates, key=lambda provable_candidate: provable_candidate[0]):
        # save to write to and also provides a script/rigify features folder?
        candidate = provable_candidate[1]
        if provable_candidate[0]:
            result = candidate
            break
        else:
            try:
                try_init_folder(candidate)
                result = candidate
                break
            except OSError:
                impossible_candidates.append(candidate)

    if result is None:
        raise Exception(
            'no writable rigify feature set storage found in possible candidates '
            + str(impossible_candidates))

    return result
