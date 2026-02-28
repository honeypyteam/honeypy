"""
Data graph of the application.

The application is represented as a labeled DAG, where the labels are the various
node types, and the DAG structure is represented by principal parent - child relations.

This module contains classes and routines related to reading, writing and managing
this application metadata.
"""

from __future__ import annotations

import json
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Iterator, List, Mapping, Set
from uuid import UUID

from honeypy.data_graph.meta.node_type import NodeType

if TYPE_CHECKING:
    from honeypy.data_graph.meta.honey_node import HoneyNode
    from honeypy.data_graph.meta.raw_metadata import RawMetadata


@dataclass
class DataGraphNode:
    """A single node in the data graph DAG."""

    uuid: UUID
    node_type: NodeType
    raw_metadata: RawMetadata
    principal_parent: UUID
    parents: Set[UUID] = field(default_factory=set)
    children: Set[UUID] = field(default_factory=set)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DataGraphNode):
            return NotImplemented

        return self.uuid == other.uuid

    def __hash__(self) -> int:
        return hash(self.uuid)

    def __str__(self) -> str:
        return f"<{self.uuid!s}: {self.node_type}>"

    @classmethod
    def from_honey_node(cls, node: "HoneyNode") -> "DataGraphNode":
        """Create a DataGraphNode from a HoneyNode object."""
        return cls(
            uuid=node.uuid,
            node_type=node.NODE_TYPE,
            raw_metadata=node._serialise_metadata(node.metadata),
            principal_parent=(
                node.principal_parent.uuid if node.principal_parent else node.uuid
            ),
            parents={node.principal_parent.uuid} if node.principal_parent else set(),
        )


class DataGraph(Mapping[UUID, DataGraphNode]):
    """
    A graph of the data available in the project.

    The data and their relationships are represented as a labeled DAG. The labels
    represent the type of HoneyNode (e.g., collection) and the DAG-structure enforces
    the principal parent - child semantics.
    """

    nodes: Dict[UUID, DataGraphNode]

    _root: UUID
    _root_meta_folder: Path

    def __init__(self, root_meta_folder: Path):
        self._root = UUID("00000000-0000-0000-0000-000000000000")
        self.nodes = {}
        self._root_meta_folder = root_meta_folder

        self.nodes[self._root] = DataGraphNode(
            uuid=self._root,
            node_type=NodeType.ROOT,
            principal_parent=self._root,
            raw_metadata={
                "class_uuid": "00000000-0000-0000-0000-000000000000",
                "node_type": NodeType.ROOT.value,
                "data": {},
            },
        )

        self._construct_dag(root_meta_folder)

    def add_node(self, node: DataGraphNode, overwrite: bool = False) -> None:
        """Add a node to the data graph."""
        # TODO: enforce parent-child relationships if overwriting
        if node.uuid in self and not overwrite:
            return

        self.nodes[node.uuid] = node

    def children_of(self, node: UUID | DataGraphNode) -> Set[DataGraphNode]:
        """Find children of a node."""
        if isinstance(node, UUID):
            return {
                node
                for node in (self.nodes.get(c, None) for c in self.nodes[node].children)
                if node is not None
            }

        return {
            node
            for node in (
                self.nodes.get(c, None) for c in self.nodes[node.uuid].children
            )
            if node is not None
        }

    def add_principal_parent(self, node_uuid: UUID, parent: HoneyNode) -> None:
        """
        Add a principal parent to a node.

        Updates the relationships between parents and children.
        """
        node = self[node_uuid]

        if node.principal_parent == parent.uuid:
            return

        # Remove old parent
        old_pp_uuid = node.principal_parent
        node.parents.remove(old_pp_uuid)
        self[old_pp_uuid].children.remove(node_uuid)

        # Add parent uuid data
        p_uuid = parent.uuid
        node.principal_parent = p_uuid
        node.parents.add(p_uuid)

        # Add parent node
        if p_uuid not in self:
            self.add_node(DataGraphNode.from_honey_node(parent), overwrite=True)
        self[p_uuid].children.add(node_uuid)

    def _construct_dag(self, root_meta_folder: Path) -> None:
        self._add_children(self.nodes[self._root], root_meta_folder)

    def _would_create_cycle(self, parent: UUID, child: UUID) -> bool:
        return False  # TODO: not implemented

    def _add_children(self, parent: DataGraphNode, parent_path: Path) -> None:
        children_meta_path = parent_path / "children"

        if not children_meta_path.exists():
            return  # is leaf

        children_folders = [f for f in children_meta_path.iterdir() if f.is_dir()]

        children = DataGraph._get_children(parent.uuid, children_folders)

        for c in children:
            self.nodes[c.uuid] = c
        parent.children = {c.uuid for c in children}

        # Don't try zip with children_folders as parent.children is an unordered set
        for child in parent.children:
            child_path = parent_path / "children" / str(child)
            self._add_children(self.nodes[child], child_path)

    @staticmethod
    def _get_children(
        parent: UUID,
        children_folders: List[Path],
    ) -> List["DataGraphNode"]:
        """
        Obtain children for the associated folder.

        If `is_file_collection` is true, treats the folder as a collection of files,
        which reads a slightly flatter layout chosen to avoid excessive nesting
        """
        result: List["DataGraphNode"] = []
        for dir in children_folders:
            uuid: UUID
            raw_metadata: RawMetadata
            node_type: NodeType
            try:
                uuid = UUID(dir.name)
                raw_metadata = DataGraph._read_raw_metadata(dir / "metadata.json")
                node_type = NodeType(raw_metadata["node_type"])

                result.append(
                    DataGraphNode(
                        uuid=uuid,
                        node_type=node_type,
                        principal_parent=parent,
                        raw_metadata=raw_metadata,
                        parents={parent},
                    )
                )
            except Exception:
                print(
                    f"Error during datagraph construction. Problem parsing '{dir!s}'. \
    Skipping child: {traceback.format_exc()}"
                )
                continue

        return result

    @staticmethod
    def _read_raw_metadata(metadata_json: Path) -> RawMetadata:
        all_metadata: RawMetadata
        with open(metadata_json, "r", encoding="utf-8") as fh:
            all_metadata = json.load(fh)

        return all_metadata

    @property
    def root(self) -> UUID:
        """Get the root UUID."""
        return self._root

    @property
    def root_meta_folder(self) -> Path:
        """Get the path of the root metafolder i.e., .honeypy directory."""
        return self._root_meta_folder.parent

    def __getitem__(self, key: UUID) -> DataGraphNode:
        if not isinstance(key, UUID):
            raise ValueError(f"{key} must be specified as UUID")

        node = self.nodes.get(key)

        if not node:
            raise KeyError(f"node {key!s} not in data graph")

        return node

    def __contains__(self, key: object) -> bool:
        return key in self.nodes

    def __len__(self) -> int:
        return len(self.nodes)

    def __iter__(self) -> Iterator[UUID]:
        return iter(self.nodes)
