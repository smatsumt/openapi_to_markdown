#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
プログラムの概要説明 (usage やオプション詳細は argparse で出るので、概要や実行例を）

pip install prance openapi-spec-validator
"""

import json
import logging
from collections import defaultdict
from typing import Any

from prance import ResolvingParser

logger = logging.getLogger(__name__)


def retrieve_endpoint(api_data: dict) -> list:
    """
    OpenAPI を読んだ結果から、エンドポイント相当の情報を取得する
    @return [{"endname": "/hogehoge", "method": "POST", }]
    """
    result = []
    paths = api_data["paths"]
    for endname in paths:
        for method, value in paths[endname].items():
            value["endname"] = endname
            value["method"] = method.upper()
            result.append(value)
    return result


def group_endpoint(endpoints: list) -> dict:
    """ タグごとにグループ化する """
    result = defaultdict(list)
    for ep in endpoints:
        tags = ["(none)"]  # とりあえず (none) にあるとする
        for t in tags:
            result[t].append(ep)
    return result


SUMMARY_HEADER = """# 概要

API|概説|パラメータ
:---|:---|:---
"""
NO_PARAM = "(なし)"
NO_DESC = "-"


def get_summary_info(endpoints: list) -> str:
    """ サマリ情報の文字を返す """
    result = SUMMARY_HEADER
    for ep in endpoints:
        result += f"{ep['method']} {ep['endname']}|{ep.get('summary', NO_DESC)}|{_summary_param_str(ep)}\n"
    return result


def _summary_param_str(ep):
    """ サマリ情報のパラメータ部分の文字を返す """
    params = ep.get("parameters", [])
    req_body = ep.get("requestBody", {})
    if not params and not req_body:
        return NO_PARAM
    # params の文字列化
    param_str_list = [_each_param_str(p) for p in params]
    # requestBody の文字列化
    try:
        req_params = req_body["content"]["application/json"]["schema"]["properties"]
        req_body = {p: f"{req_params[p].get('description', NO_DESC)}" for p in req_params}
        req_str_list = [f"body: {json.dumps(req_body, ensure_ascii=False)}"]
    except KeyError:
        req_str_list = []

    return ", ".join(param_str_list + req_str_list)


def _each_param_str(param):
    if param["in"] == "path":
        return f"{{{param['name']}}}: {param.get('description', NO_DESC)}"
    else:
        return f"{param['name']}: {param.get('description', NO_DESC)}"


DETAIL_HEADER = """
# 詳細

"""


DETAIL_ENDPOINT_TEMPLATE = """
## {method} {endname}

{summary}

### request
{request_desc}

### response
{response_desc}

"""


def get_detail_info(endpoints: list) -> str:
    """ 詳細情報の文字を返す """
    result = DETAIL_HEADER
    for ep in endpoints:
        result += DETAIL_ENDPOINT_TEMPLATE.format(
            method=ep["method"], endname=ep["endname"], summary=ep["summary"],
            request_desc=_detail_request_info(ep), response_desc=_detail_response_info(ep)
        )
    return result


DETAIL_REQUEST_HEADER = """
name | in | required | description | schema
:---|:---|:---|:---|:---
"""


def _detail_request_info(endpoint: dict) -> str:
    """ Generate Request info in detail section """
    header = DETAIL_REQUEST_HEADER
    param_str = [_detail_request_param(p) for p in endpoint.get("parameters", [])]
    return header + "\n".join(param_str)


def _detail_request_param(param: dict) -> str:
    """ Generate Request parameter info in detail section """
    return f"{param['name']} | {param['in']} | {param.get('required', False)} | {param.get('description', NO_DESC)} |" \
           f" {param.get('schema', NO_DESC)} "


def _detail_response_info(endpoint: dict) -> str:
    """ Generate Response info in detail section """
    result = ""
    for code, response in endpoint.get("responses", {}).items():
        result += f"#### {code}: {response['description']} \n"
        try:
            res_props = response["content"]["application/json"]["schema"]["properties"]
            result += f"```\n{_property_str(res_props)}\n```\n"
        except KeyError:
            pass
    return result


def _property_str(properties: dict) -> str:
    """ Format "properties" object """
    new_dict = dict([_property_str_visitor(k, v) for k, v in properties.items()])
    return json.dumps(new_dict, ensure_ascii=False, indent=2)


def _property_str_visitor(name: str, node: dict) -> (str, Any):
    """ helper for _property_str """
    key_parts = [name]

    # allOf branch
    if "allOf" in node:
        parts = [_property_str_visitor("", x) for x in node["allOf"]]
        key = name
        value = {}
        for k, v in parts:
            key += k
            value.update(v)
        return key, value

    # object key creation
    if "description" in node:
        key_parts.append(node["description"])
    key = " | ".join(key_parts)

    # object body creation
    if node["type"] == "object":
        properties = node["properties"]
        value = dict([_property_str_visitor(k, v) for k, v in properties.items()])
        return key, value
    elif node["type"] == "array":
        items = node["items"]
        value = [_property_str_visitor("", items)[1]]
        return key, value
    else:
        value_parts = [node["type"]]
        if "enum" in node:
            value_parts.append(str(node["enum"]))
        value = " | ".join(value_parts)
        return key, value
