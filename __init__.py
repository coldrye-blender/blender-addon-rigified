# TBD:LICENSE

bl_info = {
    'name': 'Rigified',
    'version': (1, 0, 0, 0, 0),
    # major-minor-patch[-state-increment]
    # state: 0 - stable, 1 - alpha, 2 - beta, 3 - rc
    # increment: 0 - for stable releases, 0..N for alpha, beta, rc
    # stable releases omit both state and increment as they are always 0
    'warning': 'This is an alpha release.',
    # 'warning': 'This is a beta release.'
    # 'warning': 'This is a release candidate release.'
    'author': 'Carsten Klein',
    'blender': (2, 93, 0),
    'description': '',
    'support': 'COMMUNITY',
    'location': 'View3D > Sidebar > Rigify',
    'wiki_url': 'https://github.com/coldrye-solutions/blender-addon-rigified',
    'tracker_url': 'https://github.com/coldrye-solutions/blender-addon-rigified',
    'category': 'Rigging'
}


if 'bpy' in locals():
    import importlib
    # FIXME: find all rigified modules and reload everything not just the top level modules
    importlib.reload(state)
    importlib.reload(operators)
    importlib.reload(ui)
    importlib.reload(preferences)
else:
    from . import state
    from . import operators
    from . import ui
    from . import preferences


# do not remove, used as a canary for above dynamic reload
import bpy


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
