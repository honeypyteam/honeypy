"""
Context class.

The context acts like a global service provider.
"""

from honeypy.services.datagraph.data_graph import DataGraph
from honeypy.services.datagraph.node_factory import NodeFactory


class HoneyContext:
    """
    A service provider.

    Several services related to the state of the application are provided. They include
    1. The data graph. This is the DAG of the data nodes and their associated metadata.
    Manipulation of this DAG can be achieved via this object.
    2. A node factory. This utilizes the data graph in order to create concrete nodes
    in a way independent from the graph model itself.
    """

    data_graph: DataGraph
    node_factory: NodeFactory

    def __init__(self, data_graph: DataGraph):
        self.data_graph = data_graph
        self.node_factory = NodeFactory(data_graph)
