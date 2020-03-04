#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
プログラムの概要説明 (usage やオプション詳細は argparse で出るので、概要や実行例を）

pip install prance openapi-spec-validator
"""

import argparse
import json
import logging, logging.config
import os
import textwrap
from collections import defaultdict

from prance import ResolvingParser
import yaml

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
    # return str(endpoint.get("parameters", ""))
    header = DETAIL_REQUEST_HEADER
    param_str = [_detail_request_param(p) for p in endpoint.get("parameters", [])]
    return header + "\n".join(param_str)


def _detail_request_param(param: dict) -> str:
    return f"{param['name']} | {param['in']} | {param.get('required', False)} | {param.get('description', NO_DESC)} |" \
           f" {param.get('schema', NO_DESC)} "


def _detail_response_info(endpoint: dict) -> str:
    # return str(endpoint.get("responses", ""))
    result = ""
    for code, response in endpoint.get("responses", {}).items():
        result += f"#### {code}: {response['description']} "
