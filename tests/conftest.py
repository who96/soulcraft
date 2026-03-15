"""Shared pytest fixtures for SoulCraft tests."""

import json
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "schemas" / "soul_schema.json"
SOULS_DIR = ROOT / "souls"


@pytest.fixture(scope="session")
def schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)


@pytest.fixture(scope="session")
def soul_paths():
    return sorted(SOULS_DIR.glob("*/soul.yaml"))


@pytest.fixture(scope="session")
def all_souls(soul_paths):
    souls = {}
    for p in soul_paths:
        with open(p) as f:
            souls[p.parent.name] = yaml.safe_load(f)
    return souls


@pytest.fixture(scope="session")
def linus_soul(all_souls):
    return all_souls["linus-torvalds"]


@pytest.fixture(scope="session")
def buffett_soul(all_souls):
    return all_souls["warren-buffett"]
