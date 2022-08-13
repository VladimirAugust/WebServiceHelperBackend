# Functions for working with trees, serializing trees etc


def serialize_tree(root, all_nodes, serializer_cls):
    result = serializer_cls(instance=root).data
    result['children'] = []
    for node in all_nodes:
        if node.parent == root:
            result['children'].append(serialize_tree(node, all_nodes, serializer_cls))
    return result