# TBD:LICENSE

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
