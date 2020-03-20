#!/usr/bin/env python

"""Tests for `openapi_to_markdown` package."""

import json
import textwrap

import pytest


@pytest.fixture()
def simple_property():
    return json.loads(r"""
    {
      "result": {
        "type": "string",
        "enum": [
          "ok",
          "failed"
        ],
        "description": "API result",
        "example": "ok"
      },
      "message": {
        "type": "string",
        "description": "detailed message",
        "example": "success"
      }
    }
    """)


def test_simple_property(simple_property):
    from openapi_to_markdown.openapi_to_markdown import _property_str

    r = _property_str(simple_property)
    assert r == textwrap.dedent("""
    {
      "result | API result": "string | ['ok', 'failed']",
      "message | detailed message": "string"
    }
    """).strip()


@pytest.fixture()
def array_property():
    return json.loads(r"""
    {
      "analysis": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "description of string array"
      }
    }
    """)


def test_array_property(array_property):
    from openapi_to_markdown.openapi_to_markdown import _property_str

    r = _property_str(array_property)
    assert r == textwrap.dedent("""
    {
      "analysis | description of string array": [
        "string"
      ]
    }
    """).strip()


@pytest.fixture()
def array_object_property():
    return json.loads(r"""
    {
      "results": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "id": {
              "type": "string",
              "description": "object's id"
            },
            "items": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "token": {
                    "type": "string"
                  }
                }
              },
              "description": "items' token list"
            }
          }
        },
        "description": "results bra bra"
      },
      "message": {
        "type": "string",
        "description": "Additional message",
        "example": "success"
      }
    }
    """)


def test_array_object_property(array_object_property):
    from openapi_to_markdown.openapi_to_markdown import _property_str

    r = _property_str(array_object_property)
    assert r == textwrap.dedent("""
    {
      "results | results bra bra": [
        {
          "id | object's id": "string",
          "items | items' token list": [
            {
              "token": "string"
            }
          ]
        }
      ],
      "message | Additional message": "string"
    }
    """).strip()


@pytest.fixture()
def allOf_property():
    return json.loads(r"""
    {
      "message": {
        "allOf": [
          {
            "type": "object",
            "description": "detailed message 1",
            "properties": {
                "p1": {"type": "string"}
            }
          },
          {
            "type": "object",
            "description": "detailed message 2",
            "properties": {
                "p2": {"type": "string"}
            }
          }
        ]
      }
    }
    """)


def test_allOf_property(allOf_property):
    from openapi_to_markdown.openapi_to_markdown import _property_str

    r = _property_str(allOf_property)
    assert r == textwrap.dedent("""
    {
      "message | detailed message 1 | detailed message 2": {
        "p1": "string",
        "p2": "string"
      }
    }
    """).strip()
