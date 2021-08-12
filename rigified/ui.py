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

import bpy
from bpy.types import Panel
from bpy.utils import register_class, unregister_class

from .state import StateWrapper
from rigified.utils.fs import normalize_filename, try_get_or_init_feature_root


class SIDEBAR_PT_rigified_tools_panel(Panel):
    bl_label = "Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Rigify"

    # should be used from arbitrary contexts
    # @classmethod
    # def poll(cls, context):
    #     if not context.object:
    #         return False
    #     return (
    #         context.object.type == 'ARMATURE'
    #         and context.active_object.data.get("rig_id") is None
    #         and context.object.mode == 'OBJECT'
    #     )

    def draw(self, context):
        layout = self.layout
        id_store = context.window_manager

        row = layout.row(align=True)
        row.operator('object.update_external_rigs')


class SIDEBAR_PT_rigified_exports_panel(Panel):
    bl_label = "Export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Rigify"

    @classmethod
    def poll(cls, context):
        return (
            context.object
            and context.object.type == 'ARMATURE'
            and context.active_object.data.get("rig_id") is None
            and context.object.mode == 'OBJECT'
        )

    def draw(self, context):
        layout = self.layout
        state = StateWrapper(context.window_manager)
        state_ui = StateWrapperUi(context, state)

        state_ui.draw_feature_set_section(layout)
        state_ui.draw_export_mode_section(layout)
        rig_state_ui = state_ui.rig_state_ui
        rig_state_ui.draw_category_section(layout)
        rig_state_ui.draw_name_section(layout)
        rig_state_ui.draw_export_section(layout)


def popup(title, message):
    def draw_popup(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw_popup, title=title, icon='INFO')


class RigStateWrapperUi:

    def __init__(self, context, state):
        self._context = context
        self._state = state
        self._export_enabled = True

    @property
    def _prefix(self):
        return 'rigified_meta_rig_' if self._state.is_meta else 'rigified_rig_'

    def _enable_export(self):
        self._export_enabled = bool(
            (
                (not self._state.parent.add_feature_set and self._state.parent.feature_sets)
                or (self._state.parent.add_feature_set and self._state.parent.feature_set)
            )
            and (
                (not self._state.add_category and self._state.categories)
                # prevent nested meta rig categories as it is not supported by rigify
                or (self._state.is_meta and self._state.category and not self._state.category.count('.'))
                or (not self._state.is_meta and self._state.category)
            )
            and self._state.name
        )

    def _validate_categories(self):
        if not self._state.categories:
            self._state.categories = 'ROOT'

    def _validate_category(self):
        category = self._state.category
        normalized_category = normalize_filename(category, is_category=True)
        if category != normalized_category:
            self._state.category = normalized_category
            # FIXME: reject input for meta rigs containing multiple dots, prevent export
            self._export_enabled = False
            popup('Invalid Input', 'category was adjusted')

    def draw_category_section(self, layout):
        row = layout.row(align=True)
        split = row.split(factor=0.3)
        split.label(text='New Category:' if self._state.add_category else 'Category:')
        sub = split.row(align=True)
        if self._state.add_category:
            self._validate_category()
            row = sub.row(align=True)
            # FIXME: extend to also alert on invalid meta rig category or reserved _lib rig categories
            row.alert = not self._state.category
            row.prop(self._state.wm, self._prefix + 'category', text='')
        else:
            self._validate_categories()
            sub.prop(self._state.wm, self._prefix + 'categories', text='')
        sub.prop(self._state.wm, self._prefix + 'add_category', text='', icon='NEWFOLDER')

    def _validate_name(self):
        name = self._state.name
        normalized_name = normalize_filename(name)
        if name != normalized_name:
            self._state.name = normalized_name
            popup('Invalid Input', 'name was adjusted')

    def draw_name_section(self, layout):
        row = layout.row(align=True)
        split = row.split(factor=0.3)
        split.label(text='Name:')
        self._validate_name()
        row = split.row()
        row.alert = not self._state.name
        row.prop(self._state.wm, self._prefix + 'name', text='')

    def draw_export_section(self, layout):
        self._enable_export()
        col = layout.column(align=True)
        col.enabled = self._export_enabled
        row = col.row(align=True)
        row.prop(self._state.wm, self._prefix + 'creation_mode', expand=True)
        props = col.operator('rigified.export_rig')
        props.name = self._state.name
        if self._state.add_category:
            props.category = self._state.category
        else:
            props.category = self._state.effective_categories
        props.overwrite = self._state.is_overwrite
        props.as_sample = not self._state.is_meta
        if self._state.parent.add_feature_set:
            props.feature_set = self._state.parent.feature_set
        else:
            props.feature_set = self._state.parent.feature_sets


class StateWrapperUi:

    def __init__(self, context, state):
        self._context = context
        self._state = state
        self._rig_state_wrapper_ui = RigStateWrapperUi(context, state.get_rig_state_wrapper())

    @property
    def rig_state_ui(self):
        return self._rig_state_wrapper_ui

    def draw_export_mode_section(self, layout):
        row = layout.row(align=True)
        row.prop(self._state.wm, 'rigified_export_mode', expand=True)

    def draw_feature_set_section(self, layout):
        row = layout.row(align=True)
        split = row.split(align=True, factor=0.3)
        self._validate_feature_sets()
        if self._state.add_feature_set:
            self._validate_feature_set()
            split.label(text='New Feature Set:')
            sub = split.row(align=True)
            sub.alert = not self._state.feature_set
            sub.prop(self._state.wm, 'rigified_feature_set', text='')
        else:
            split.label(text='Feature Set:')
            sub = split.row(align=True)
            sub.prop(self._state.wm, 'rigified_feature_sets', text='')
            feature_set_root = try_get_or_init_feature_root(self._state.feature_sets)
            sub.operator('rigified.explore_feature_set', text='', icon='FILEBROWSER').filepath = feature_set_root
        sub.prop(self._state.wm, 'rigified_add_feature_set', text='', icon='NEWFOLDER')

    def _validate_feature_sets(self):
        # FIXME: refactor get from addon preferences wrapper
        default_feature_set = self._context.preferences.addons[__package__].preferences.default_feature_set
        if not self._state.feature_sets:
            # fix missing feature set by setting it to the default feature set
            self._state.feature_sets = default_feature_set
            popup('Invalid Input', 'feature set was adjusted to default feature set')

    def _validate_feature_set(self):
        feature_set = self._state.feature_set
        normalized_feature_set = normalize_filename(feature_set)
        if feature_set != normalized_feature_set:
            self._state.feature_set = normalized_feature_set
            popup('Invalid Input', 'new feature set was adjusted')


_classes = [
    SIDEBAR_PT_rigified_exports_panel,
    SIDEBAR_PT_rigified_tools_panel
]


def register():
    for klass in _classes:
        register_class(klass)


def unregister():
    for klass in _classes:
        unregister_class(klass)
