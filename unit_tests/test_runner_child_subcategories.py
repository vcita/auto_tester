"""Regression tests for nested-subcategory recursion.

A mixed node (a subcategory that owns both direct tests and nested subcategories)
must run its nested children; before the fix they were silently skipped because the
boundary loop only reaches a boundary's direct children. ``_run_child_subcategories``
is the shared helper that both pure groups and mixed nodes use.
"""
import time
from pathlib import Path
from types import SimpleNamespace

from src.models import Category
from src.models import Test as CaseModel
from src.runner.runner import TestRunner as Runner


def _test(name: str) -> CaseModel:
    return CaseModel(id=name, name=name, path=Path(f"p/{name}"))


def _subcat(name: str, isolated: bool = False) -> Category:
    return Category(
        name=name,
        path=Path(f"p/{name}"),
        account_profile={"type": "isolated"} if isolated else None,
    )


def _run_children(runner: Runner, parent: Category):
    return runner._run_child_subcategories(
        parent=parent,
        page=object(),
        context={},
        result=SimpleNamespace(stopped_early=False),
        video_timestamps=[],
        video_start_time=0.0,
        time_module=time,
    )


def test_runs_every_nested_subcategory_and_skips_own_tests(monkeypatch):
    runner = Runner(Path("tests"))
    parent = Category(name="Invoices", path=Path("p"))
    parent.tests = [_test("create"), _test("edit")]
    parent.subcategories = [_subcat("late_fee"), _subcat("attach_document")]

    visited = []
    monkeypatch.setattr(
        runner, "_run_subcategory_inline",
        lambda subcategory, **kw: (visited.append(subcategory.name), (False, None))[1],
    )

    hard_failed, first_failed = _run_children(runner, parent)

    assert visited == ["late_fee", "attach_document"]  # nested only, not the 2 tests
    assert hard_failed is False
    assert first_failed is None


def test_isolated_child_failure_does_not_cascade_to_siblings(monkeypatch):
    runner = Runner(Path("tests"))
    parent = Category(name="grp", path=Path("p"))
    parent.subcategories = [_subcat("a", isolated=True), _subcat("b", isolated=True)]

    visited = []

    def fake_inline(subcategory, **kw):
        visited.append(subcategory.name)
        return (True, f"{subcategory.name}/t") if subcategory.name == "a" else (False, None)

    monkeypatch.setattr(runner, "_run_subcategory_inline", fake_inline)

    hard_failed, first_failed = _run_children(runner, parent)

    assert visited == ["a", "b"]          # sibling still ran after isolated failure
    assert hard_failed is False           # contained inside the throwaway account
    assert first_failed == "a/t"


def test_non_isolated_child_failure_cascades_and_stops(monkeypatch):
    runner = Runner(Path("tests"))
    parent = Category(name="grp", path=Path("p"))
    parent.subcategories = [_subcat("a"), _subcat("b")]

    visited = []

    def fake_inline(subcategory, **kw):
        visited.append(subcategory.name)
        return (True, f"{subcategory.name}/t") if subcategory.name == "a" else (False, None)

    monkeypatch.setattr(runner, "_run_subcategory_inline", fake_inline)

    hard_failed, first_failed = _run_children(runner, parent)

    assert visited == ["a"]               # cascade: sibling not reached
    assert hard_failed is True
    assert first_failed == "a/t"
