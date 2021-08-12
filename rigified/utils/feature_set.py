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

from .fs import try_get_or_init_feature_root
from .rigify import update_external_rigs


def feature_set_init_or_update(context, feature_name):
    code = []
    code.append('rigify_info = {')
    code.append('    "name": "' + feature_name + '"')
    code.append('}')
    root = try_get_or_init_feature_root(feature_name)
    file_path = os.path.join(root, '__init__.py')
    file = open(file_path, 'w')
    file.write('\n'.join(code))
    file.close()
    update_external_rigs(context)


def feature_set_maintained_feature_set_list(context, root):
    update_external_rigs(context)
    maintained_feature_sets = context.preferences.addon['rigified'].preferences.maintained_feature_sets
    result = []
    for folder in os.listdir(root):
        candidate = os.path.join(root, folder)
        if candidate in maintained_feature_sets:
            result.append((folder, candidate))
    return result
