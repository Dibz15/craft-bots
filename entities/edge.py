import math as m


class Edge:
    def __init__(self, world, node_a, node_b):
        self.node_a = node_a
        self.node_b = node_b
        self.world = world

        self.id = world.get_new_id()
        self.node_a.append_edge(self)
        self.node_b.append_edge(self)

        self.fields = {"node_a": self.node_a.id, "node_b": self.node_b.id, "id": self.id, "length": self.length(),
                       "get_other_node": self.get_other_node_id}

    def __eq__(self, other):
        if isinstance(other, Edge):
            if self.node_a == other.node_a and self.node_b == other.node_b or self.node_a == other.node_b and\
                    self.node_b == other.node_a:
                return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "Edge" + self.__str__()

    def __str__(self):
        return "(" + str(self.node_a) + ", " + str(self.node_b) + ", " + str(self.length()) + ")"

    def length(self):
        return m.ceil(m.dist((self.node_a.x, self.node_a.y), (self.node_b.x, self.node_b.y)))

    def connects(self, node):
        return node == self.node_a or node == self.node_b

    def get_other_node(self, node):
        if self.node_a == node:
            return self.node_b
        elif self.node_b == node:
            return self.node_a
        return None

    def get_other_node_id(self, node_id):
        node = self.world.get_by_id(node_id, entity_type="Node")
        if node is not None:
            other_node = self.get_other_node(node)
            if other_node is not None:
                return other_node.id
        return None