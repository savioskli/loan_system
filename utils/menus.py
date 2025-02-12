# utils/menu.py

def build_menu_hierarchy(modules):
    # Group modules by parent_id
    modules_by_parent = {}
    for module in modules:
        modules_by_parent.setdefault(module.parent_id, []).append(module)

    def build_hierarchy(parent_id):
        return [
            {
                'module': module,
                'children': build_hierarchy(module.id)
            }
            for module in modules_by_parent.get(parent_id, [])
        ]

    return build_hierarchy(None)
