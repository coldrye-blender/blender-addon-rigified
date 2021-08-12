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

from bpy.props import BoolProperty, StringProperty
from bpy.types import AddonPreferences
from bpy.utils import register_class, unregister_class


class RigifiedAddonPreferences(AddonPreferences):
    bl_idname = __package__

    default_feature_set: StringProperty(
        name='Default Feature Set',
        description='The default feature set',
        default='rigified'
    )

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.prop(self, 'default_feature_set')


def register():
    register_class(RigifiedAddonPreferences)


def unregister():
    unregister_class(RigifiedAddonPreferences)
