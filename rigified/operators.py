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
from bpy.props import BoolProperty, StringProperty
from bpy.utils import register_class, unregister_class

from rigify.utils.rig import write_metarig

from rigified.utils.fs import normalize_filename, try_get_or_init_meta_rigs_root, try_get_or_init_rigs_root
from rigified.utils.rigify import update_external_rigs


class OBJECT_OT_update_external_rigs(bpy.types.Operator):
    """ Force update all external rigs.
    """
    bl_idname = 'object.update_external_rigs'
    bl_label = 'Update External Rigs'

    def execute(self, context):
        # TODO: This might fail due to https://developer.blender.org/T90081
        update_external_rigs(context)
        return {'FINISHED'}


class RIGIFIED_OT_explore_feature_set(bpy.types.Operator):
    """ Explore feature set in file browser.
    """
    bl_idname = 'rigified.explore_feature_set'
    bl_label = 'Explore Feature Set'

    filepath: StringProperty('File path')

    def execute(self, context):
        bpy.ops.wm.path_open(filepath=self.filepath)
        return {'FINISHED'}


class RIGIFIED_OT_export_rig(bpy.types.Operator):
    """ Export meta rig.
    """
    bl_idname = 'rigified.export_rig'
    bl_label = 'Export Rig'

    name: StringProperty(name='Name')
    feature_set: StringProperty(name='Feature Set')
    category: StringProperty(name='Category')
    overwrite: BoolProperty(name='Overwrite')
    as_sample: BoolProperty(name='Export as Sample', default=False)

    def execute(self, context):
        filename = normalize_filename(self.name)
        if filename != self.name:
            self.report({'ERROR_INVALID_INPUT'}, 'name was adjusted to ' + filename)
            return {'CANCELLED'}

        category = normalize_filename(self.category, is_category=True)
        if category != self.category:
            self.report({'ERROR_INVALID_INPUT'}, 'Category name was adjusted to ' + category)
            return {'CANCELLED'}

        if not self.as_sample and len(re.sub('[^.]', '', category)) > 0:
            self.report({'ERROR_INVALID_INPUT'}, 'Category names for meta rigs must not include any dots ' + category)
            return {'CANCELLED'}
        category_path = category.replace('.', os.path.sep)

        if not self.feature_set:
            self.report({'ERROR_INVALID_INPUT'}, 'No feature set given')
            return {'CANCELLED'}

        feature_set = normalize_filename(self.feature_set, is_category=True)
        if feature_set != self.feature_set:
            self.report({'ERROR_INVALID_INPUT'}, 'Feature set was adjusted to ' + feature_set)
            return {'CANCELLED'}

        if self.as_sample:
            root = try_get_or_init_rigs_root(feature_set, category_path)
        else:
            root = try_get_or_init_meta_rigs_root(feature_set, category_path)
        file_path = os.path.join(root, filename + '.py')
        is_file_path_exists = os.path.exists(file_path)

        result = {'CANCELLED'}
        if not filename:
            self.report({'ERROR_INVALID_INPUT'}, 'No name given')
        elif is_file_path_exists and not self.overwrite:
            self.report({'ERROR_INVALID_INPUT'}, 'Rig already exists')
        else:
            try:
                bpy.ops.object.mode_set(mode='EDIT')
                func_name = 'create_sample' if self.as_sample else 'create'
                data = write_metarig(context.active_object, layers=True, func_name=func_name, groups=True)

                if self.as_sample:
                    parts = data.split('def create_sample(obj):\n')
                    code = []
                    code.append(parts[0])
                    code.append('class Rig:')
                    code.append('    pass')
                    code.append('')
                    code.append('def create_sample(obj):')
                    code.append(parts[1])
                    data = '\n'.join(code)

                f = open(file_path, 'w')
                f.write(data)
                f.close()
                update_external_rigs(context)
                result = {'FINISHED'}
            except Exception as ex:
                # TODO: include exception message and log trace
                self.report({'ERROR'}, 'Failed to export rig')
                print(ex)
            finally:
                # reset ui
                WM = context.window_manager
                setattr(WM, 'rigified_feature_sets', feature_set)
                setattr(WM, 'rigified_add_feature_set', False)
                setattr(WM, 'rigified_feature_set', '')
                if self.as_sample:
                    setattr(WM, 'rigified_rig_categories', 'ROOT' if category == '' else category)
                    setattr(WM, 'rigified_rig_add_category', False)
                    setattr(WM, 'rigified_rig_creation_mode', 'NEW')
                    setattr(WM, 'rigified_rig_category', '')
                else:
                    setattr(WM, 'rigified_meta_rig_categories', 'ROOT' if category == '' else category)
                    setattr(WM, 'rigified_meta_rig_add_category', False)
                    setattr(WM, 'rigified_meta_rig_creation_mode', 'NEW')
                    setattr(WM, 'rigified_meta_rig_category', '')
                bpy.ops.object.mode_set(mode='OBJECT')

        return result


_classes = [
    RIGIFIED_OT_export_rig,
    RIGIFIED_OT_explore_feature_set,
    OBJECT_OT_update_external_rigs
]


def register():
    for klass in _classes:
        register_class(klass)


def unregister():
    for klass in _classes:
        unregister_class(klass)
