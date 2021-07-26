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
