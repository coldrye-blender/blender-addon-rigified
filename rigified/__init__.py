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


bl_info = {
    'name': 'Rigified',
    'author': 'Carsten Klein',
    'description': '',
    'support': 'COMMUNITY',
    'location': 'View3D > Sidebar > Rigify',
    'wiki_url': 'https://github.com/coldrye-solutions/blender-addon-rigified',
    'tracker_url': 'https://github.com/coldrye-solutions/blender-addon-rigified',
    'category': 'Rigging',
    'version': (1, 0, 0, 1, 1, 2, 93, 0, 0),
    'warning': '',
    'blender': (2, 93, 0),
}


if 'bpy' in locals():
    import sys
    import importlib
    # order is important here
    modules = [
        'rigified.utils.rigify',
        'rigified.utils.fs',
        'rigified.utils.feature_set',
        'rigified.commons.versioning',
        'rigified.state',
        'rigified.operators',
        'rigified.ui',
        'rigified.preferences'
    ]
    for key in modules:
        importlib.reload(sys.modules[key])
    del importlib
    del sys
else:
    # do not remove, used as a canary for above dynamic reload
    from . import state
    from . import operators
    from . import ui
    from . import preferences


def register():
    state.register()
    operators.register()
    ui.register()
    preferences.register()


def unregister():
    preferences.unregister()
    ui.unregister()
    operators.unregister()
    state.unregister()
