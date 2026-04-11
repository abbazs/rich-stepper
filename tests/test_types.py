"""Tests for StepNode and extended StepDefinition."""

from __future__ import annotations

import pytest

from stepper.node import StepNode
from stepper.types import StepDefinition, StepStatus


# ---------------------------------------------------------------------------
# StepDefinition extension tests
# ---------------------------------------------------------------------------


def test_step_definition_parallel_default() -> None:
    sd = StepDefinition(label="Build")
    assert sd.parallel is False


def test_step_definition_sub_steps_default() -> None:
    sd = StepDefinition(label="Build")
    assert sd.sub_steps is None


def test_step_definition_accepts_parallel_flag() -> None:
    sd = StepDefinition(label="Test Suite", parallel=True)
    assert sd.parallel is True


def test_step_definition_accepts_sub_steps() -> None:
    children = [StepDefinition(label="Unit"), StepDefinition(label="E2E")]
    sd = StepDefinition(label="Tests", sub_steps=children)
    assert sd.sub_steps == children


def test_step_definition_still_frozen() -> None:
    sd = StepDefinition(label="Build")
    with pytest.raises((AttributeError, TypeError)):
        sd.parallel = True  # type: ignore[misc]


# ---------------------------------------------------------------------------
# StepNode tests
# ---------------------------------------------------------------------------


def test_step_node_creation() -> None:
    node = StepNode(
        idx=0,
        label="Build",
        status=StepStatus.PENDING,
        description=None,
        logs=[],
        children=[],
        is_parallel=False,
        parent_idx=None,
        task_id=None,
    )
    assert node.idx == 0
    assert node.label == "Build"
    assert node.status is StepStatus.PENDING
    assert node.description is None
    assert node.logs == []
    assert node.children == []
    assert node.is_parallel is False
    assert node.parent_idx is None
    assert node.task_id is None


def test_step_node_is_mutable() -> None:
    node = StepNode(
        idx=0,
        label="Build",
        status=StepStatus.PENDING,
        description=None,
        logs=[],
        children=[],
        is_parallel=False,
        parent_idx=None,
        task_id=None,
    )
    node.status = StepStatus.COMPLETED
    assert node.status is StepStatus.COMPLETED


def test_step_node_logs_mutable() -> None:
    node = StepNode(
        idx=0,
        label="Build",
        status=StepStatus.PENDING,
        description=None,
        logs=[],
        children=[],
        is_parallel=False,
        parent_idx=None,
        task_id=None,
    )
    node.logs.append("line one")
    assert node.logs == ["line one"]


def test_step_node_children_mutable() -> None:
    parent = StepNode(
        idx=0,
        label="Parent",
        status=StepStatus.PENDING,
        description=None,
        logs=[],
        children=[],
        is_parallel=True,
        parent_idx=None,
        task_id=None,
    )
    child = StepNode(
        idx=1,
        label="Child",
        status=StepStatus.PENDING,
        description=None,
        logs=[],
        children=[],
        is_parallel=False,
        parent_idx=0,
        task_id=None,
    )
    parent.children.append(child)
    assert len(parent.children) == 1
    assert parent.children[0].label == "Child"
