# Copyright The Caikit Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Tests for the caikit HTTP server
"""
# Standard
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Optional
import json
import os
import tempfile

# Third Party
import pytest
import requests
import tls_test_tools

# First Party
import aconfig

# Local
from caikit.runtime import http_server
from tests.conftest import temp_config

## Helpers #####################################################################


def save_key_cert_pair(prefix, workdir, key=None, cert=None):
    crtfile, keyfile = None, None
    if key is not None:
        keyfile = os.path.join(workdir, f"{prefix}.key")
        with open(keyfile, "w") as handle:
            handle.write(key)
    if cert is not None:
        crtfile = os.path.join(workdir, f"{prefix}.crt")
        with open(crtfile, "w") as handle:
            handle.write(cert)
    return crtfile, keyfile


@dataclass
class SampleServer:
    server: http_server.RuntimeHTTPServer
    port: int
    ca_certfile: Optional[str]
    client_keyfile: Optional[str]
    client_certfile: Optional[str]


@dataclass
class KeyPair:
    cert: str
    key: str


@dataclass
class TLSConfig:
    server: KeyPair
    client: KeyPair


@contextmanager
def generate_tls_configs(
    tls: bool = False, mtls: bool = False, **http_config_overrides
):
    """Helper to generate tls configs"""
    with tempfile.TemporaryDirectory() as workdir:
        config_overrides = {}
        client_keyfile, client_certfile, ca_certfile = None, None, None
        if mtls or tls:
            ca_key = tls_test_tools.generate_key()[0]
            ca_cert = tls_test_tools.generate_ca_cert(ca_key)
            ca_certfile, _ = save_key_cert_pair("ca", workdir, cert=ca_cert)
            server_certfile, server_keyfile = save_key_cert_pair(
                "server",
                workdir,
                *tls_test_tools.generate_derived_key_cert_pair(ca_key=ca_key),
            )

            tls_config = TLSConfig(
                server=KeyPair(cert=server_certfile, key=server_keyfile),
                client=KeyPair(cert="", key=""),
            )
            # need to save this ca_certfile in config_overrides so the tls tests below can access it from client side
            config_overrides["use_in_test"] = {"ca_cert": ca_certfile}
            if mtls:
                client_certfile, client_keyfile = save_key_cert_pair(
                    "client",
                    workdir,
                    *tls_test_tools.generate_derived_key_cert_pair(ca_key=ca_key),
                )
                tls_config.client = KeyPair(cert=ca_certfile, key="")
                # need to save the client cert and key in config_overrides so the mtls test below can access it
                config_overrides["use_in_test"]["client_cert"] = client_certfile
                config_overrides["use_in_test"]["client_key"] = client_keyfile

            config_overrides["runtime"] = {"tls": tls_config}
        port = http_server.RuntimeServerBase._find_port()
        config_overrides.setdefault("runtime", {})["http"] = {
            "port": port,
            **http_config_overrides,
        }

        with temp_config(config_overrides, "merge"):
            yield config_overrides


@pytest.fixture(scope="session")
def insecure_http_server():
    with generate_tls_configs():
        insecure_http_server = http_server.RuntimeHTTPServer()
        yield insecure_http_server


def test_insecure_server(insecure_http_server):
    with insecure_http_server.run_in_thread():
        resp = requests.get(f"http://localhost:{insecure_http_server.port}/docs")
        resp.raise_for_status()
        # TODO: how do I kill this thread?


def test_basic_tls_server():
    with generate_tls_configs(
        tls=True, mtls=False, http_config_overrides={}
    ) as config_overrides:
        http_server_with_tls = http_server.RuntimeHTTPServer(
            tls_config_override=config_overrides["runtime"]["tls"]
        )
        with http_server_with_tls.run_in_thread():
            resp = requests.get(
                f"https://localhost:{http_server_with_tls.port}/docs",
                verify=config_overrides["use_in_test"]["ca_cert"],
            )
            resp.raise_for_status()
            # TODO: how do I kill this thread?


def test_mutual_tls_server():
    with generate_tls_configs(
        tls=True, mtls=True, http_config_overrides={}
    ) as config_overrides:
        http_server_with_mtls = http_server.RuntimeHTTPServer(
            tls_config_override=config_overrides["runtime"]["tls"]
        )
        with http_server_with_mtls.run_in_thread():
            print(
                "client_cert_file is: ", config_overrides["use_in_test"]["client_cert"]
            )
            print("client key file is: ", config_overrides["use_in_test"]["client_key"])
            print("ca cert is: ", config_overrides["use_in_test"]["ca_cert"])
            resp = requests.get(
                f"https://localhost:{http_server_with_mtls.port}/docs",
                verify=config_overrides["use_in_test"]["ca_cert"],
                cert=(
                    config_overrides["use_in_test"]["client_cert"],
                    config_overrides["use_in_test"]["client_key"],
                ),
            )
            resp.raise_for_status()
            # TODO: how do I kill this thread?


# Third Party
## Tests #######################################################################
from fastapi.testclient import TestClient

# def test_simple():
#     server = http_server.RuntimeHTTPServer()


def test_docs():
    """Simple check that pinging /docs returns 200"""
    server = http_server.RuntimeHTTPServer()
    with TestClient(server.app) as client:
        response = client.get("/docs")
        assert response.status_code == 200


def test_inference(sample_task_model_id):
    """Simple check that we can ping a model"""
    server = http_server.RuntimeHTTPServer()
    with TestClient(server.app) as client:
        json_input = {"inputs": {"sample_input": {"name": "world"}}}
        response = client.post(
            f"/api/v1/{sample_task_model_id}/task/sample",
            json=json_input,
        )
        assert response.status_code == 200
        json_response = json.loads(response.content.decode(response.default_encoding))
        assert json_response["greeting"] == "Hello world"


def test_inference_optional_field(sample_task_model_id):
    """Simple check for optional fields"""
    server = http_server.RuntimeHTTPServer()
    with TestClient(server.app) as client:
        json_input = {
            "inputs": {"sample_input": {"name": "world"}},
            "parameters": {"throw": True},
        }
        response = client.post(
            f"/api/v1/{sample_task_model_id}/task/sample",
            json=json_input,
        )
        # this is 500 because we explicitly pass in `throw` as True, which
        # raises an internal error in the module
        assert response.status_code == 500


def test_inference_other_task(other_task_model_id):
    """Simple check that we can ping a model"""
    server = http_server.RuntimeHTTPServer()
    with TestClient(server.app) as client:
        json_input = {"inputs": {"sample_input": {"name": "world"}}}
        response = client.post(
            f"/api/v1/{other_task_model_id}/task/other",
            json=json_input,
        )
        assert response.status_code == 200
        json_response = json.loads(response.content.decode(response.default_encoding))
        assert json_response["farewell"] == "goodbye: world 42 times"


def test_model_not_found():
    """Simple check that we can ping a model"""
    server = http_server.RuntimeHTTPServer()
    with TestClient(server.app) as client:
        response = client.post(
            f"/api/v1/this_is_not_a_model/task/sample",
            json={"inputs": {"name": "world"}},
        )
        assert response.status_code == 404


# TODO: uncomment later
# def test_train():
#     server = http_server.RuntimeHTTPServer()
#     with TestClient(server.app) as client:
#         json_input = {
#             "inputs": {
#                 "model_name": "sample_task_train",
#                 "training_data": {"jsondata": {"number": 1}},
#             }
#         }
#         response = client.post(
#             f"/api/v1/asdf/SampleTaskSampleModuleTrain",
#             json=json_input,
#         )
#         assert response.status_code == 200
#         json_response = json.loads(response.content.decode(response.default_encoding))
#         assert json_response["greeting"] == "Hello world"
