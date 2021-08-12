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

# import bpy.props
from bpy.props import BoolProperty, EnumProperty, StringProperty
# from bpy.utils import register_class, unregister_class
from bpy.types import WindowManager

from rigified.utils.fs import try_get_or_init_meta_rigs_root, try_get_or_init_rigs_root, try_get_or_init_feature_sets_root


def _meta_rig_folder_items(self, context):
    result = []
    feature_set = getattr(context.window_manager, 'rigified_feature_sets')
    if not feature_set:
        return
    root = try_get_or_init_meta_rigs_root(feature_set)
    result.append(('ROOT', 'Root', root))
    for folder in os.listdir(root):
        candidate = os.path.join(root, folder)
        if os.path.isdir(candidate) and not folder == '__pycache__':
            path = os.path.abspath(candidate)
            result.append((folder, folder, path))
    return result


def _rig_folder_items(self, context):
    result = []
    feature_set = getattr(context.window_manager, 'rigified_feature_sets')
    if not feature_set:
        return
    root = try_get_or_init_rigs_root(feature_set)
    result.append(('ROOT', 'Root', root))
    # recursively collect all subfolders first
    candidates = []
    folders = list(os.listdir(root))
    while len(folders):
        folder = folders.pop()
        folder_path = os.path.join(root, folder)
        if folder.endswith('__pycache__') or folder.endswith('_lib') or not os.path.isdir(folder_path):
            continue
        candidates.append(folder)
        for subfolder in os.listdir(os.path.join(root, folder)):
            folders.append(os.path.join(folder, subfolder))

    for candidate in candidates:
        candidate_name = candidate.replace(os.path.sep, '.')
        candidate_path = os.path.join(root, folder)
        result.append((candidate_name, candidate_name, candidate_path))

    return result


def _feature_set_items(self, context):
    result = []
    # self is window manager aka id_store
    # context is current context
    root = try_get_or_init_feature_sets_root()
    # FIXME: hard coded default feature set
    seen = set()
    default_feature_set = context.preferences.addons[__package__].preferences.default_feature_set
    result.append((default_feature_set, default_feature_set, root))
    seen.add(default_feature_set)
    for folder in os.listdir(root):
        if folder not in seen:
            candidate = os.path.join(root, folder)
            if os.path.isdir(candidate) and not folder == '__pycache__':
                path = os.path.abspath(candidate)
                result.append((folder, folder, path))
                seen.add(folder)
    return result



class RigStateWrapper:
    """

    """

    def __init__(self, wm, is_meta, parent):
        self._parent = parent
        self._wm = wm
        self._is_meta = is_meta

    @property
    def parent(self):
        return self._parent

    @property
    def wm(self):
        return self._wm

    def _get_prefix(self):
        return 'rigified_' + ('meta_' if self._is_meta else '') + 'rig'

    @property
    def name(self):
        return getattr(self._wm, self._get_prefix() + '_name')

    @name.setter
    def name(self, value):
        setattr(self._wm, self._get_prefix() + '_name', value)

    @property
    def categories(self):
        return getattr(self._wm, self._get_prefix() + '_categories')

    @categories.setter
    def categories(self, value):
        setattr(self._wm, self._get_prefix() + '_categories', value)

    @property
    def effective_categories(self):
        return '' if self.categories == 'ROOT' else self.categories

    @property
    def add_category(self):
        return getattr(self._wm, self._get_prefix() + '_add_category')

    @add_category.setter
    def add_category(self, value):
        setattr(self._wm, self._get_prefix() + '_add_category', value)

    @property
    def category(self):
        return getattr(self._wm, self._get_prefix() + '_category')

    @category.setter
    def category(self, value):
        setattr(self._wm, self._get_prefix() + '_category', value)

    @property
    def creation_mode(self):
        return getattr(self._wm, self._get_prefix() + '_creation_mode')

    @creation_mode.setter
    def creation_mode(self, value):
        setattr(self._wm, self._get_prefix() + '_creation_mode', value)

    @property
    def is_overwrite(self):
        return self.creation_mode == 'OVERWRITE'

    @property
    def is_meta(self):
        return self._is_meta


class StateWrapper:
    """ Wrapper around bpy.types.WindowManager to make things easier when accessing properties
    associated with the addon.
    """

    def __init__(self, wm):
        self._wm = wm
        self._meta_rig_state_wrapper = RigStateWrapper(wm, True, self)
        self._rig_state_wrapper = RigStateWrapper(wm, False, self)

    def get_rig_state_wrapper(self):
        return self._meta_rig_state_wrapper if self.is_meta else self._rig_state_wrapper

    @property
    def wm(self):
        return self._wm

    @property
    def feature_sets(self):
        return getattr(self._wm, 'rigified_feature_sets')

    @feature_sets.setter
    def feature_sets(self, value):
        setattr(self._wm, 'rigified_feature_sets', value)

    @property
    def add_feature_set(self):
        return getattr(self._wm, 'rigified_add_feature_set')

    @add_feature_set.setter
    def add_feature_set(self, value):
        setattr(self._wm, 'rigified_add_feature_set', value)

    @property
    def feature_set(self):
        return getattr(self._wm, 'rigified_feature_set')

    @feature_set.setter
    def feature_set(self, value):
        setattr(self._wm, 'rigified_feature_set', value)

    @property
    def export_mode(self):
        return getattr(self._wm, 'rigified_export_mode')

    @export_mode.setter
    def export_mode(self, value):
        setattr(self._wm, 'rigified_export_mode', value)

    @property
    def is_meta(self):
        return self.export_mode == 'META'


def register():
    WM = WindowManager

    # register_class(RigifiedFeatureSetPropertyGroup)
    # register_class(RigifiedMetaRigCategoryPropertyGroup)
    # register_class(RigifiedRigCategoryPropertyGroup)
    # register_class(RigifiedPropertyGroup)

    # WM.rigified = PointerProperty(type=RigifiedPropertyGroup)

    # RIGIFIED_SIDEBAR_PT_Export
    WM.rigified_feature_sets = EnumProperty(
        name="Feature Sets",
        description="Set the feature set to export to",
        items=_feature_set_items)

    WM.rigified_add_feature_set = BoolProperty(
        name="Add Feature Set",
        description="Add new feature set",
        default=False)

    WM.rigified_feature_set = StringProperty(
        name='Feature Set',
        description='Feature set name',
        default='')

    WM.rigified_export_mode = EnumProperty(
        name="Export Mode",
        description=(
            'Set the export mode. When in rig export mode, \n'
            + 'a default rig class will be included in the \n'
            + 'exported file'
        ),
        items=(('META', 'Meta Rig', 'Export Meta Rig'),
               ('SAMPLE', 'Rig', 'Export Rig')))

    WM.rigified_meta_rig_name = StringProperty(
        name='Name',
        description='Meta rig name',
        default='')

    WM.rigified_meta_rig_add_category = BoolProperty(
        name="Add Category",
        description="Add new meta rigs category",
        default=False)

    WM.rigified_meta_rig_categories = EnumProperty(
        items=_meta_rig_folder_items,
        name="Meta Rig Categories",
        description="Choose category")

    WM.rigified_meta_rig_category = StringProperty(
        name='Category',
        description='New category name',
        default='')

    WM.rigified_meta_rig_creation_mode = EnumProperty(
        name='Creation Mode',
        description="Set the creation mode",
        items=(('NEW', 'New', 'Create new rig'),
               ('OVERWRITE', 'Overwrite', 'Overwrite existing rig')))

    WM.rigified_rig_name = StringProperty(
        name='Name',
        description='Rig name',
        default='')

    WM.rigified_rig_add_category = BoolProperty(
        name="Add Category",
        description="Add new rigs category",
        default=False)

    WM.rigified_rig_categories = EnumProperty(
        items=_rig_folder_items,
        name="Rig Categories",
        description="Choose category")

    WM.rigified_rig_category = StringProperty(
        name='Category',
        description='New category name',
        default='')

    WM.rigified_rig_creation_mode = EnumProperty(
        name='Creation Mode',
        description="Set the creation mode",
        items=(('NEW', 'New', 'Create new rig'),
               ('OVERWRITE', 'Overwrite', 'Overwrite existing rig')))


def unregister():
    WM = WindowManager

    delattr(WM, 'rigified_feature_sets')
    delattr(WM, 'rigified_feature_set')
    delattr(WM, 'rigified_add_feature_set')

    delattr(WM, 'rigified_export_mode')

    delattr(WM, 'rigified_meta_rig_name')
    delattr(WM, 'rigified_meta_rig_categories')
    delattr(WM, 'rigified_meta_rig_add_category')
    delattr(WM, 'rigified_meta_rig_category')
    delattr(WM, 'rigified_meta_rig_creation_mode')

    delattr(WM, 'rigified_rig_name')
    delattr(WM, 'rigified_rig_categories')
    delattr(WM, 'rigified_rig_add_category')
    delattr(WM, 'rigified_rig_category')
    delattr(WM, 'rigified_rig_creation_mode')

    # unregister_class(RigifiedFeatureSetPropertyGroup)
