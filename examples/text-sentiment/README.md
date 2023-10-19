# Text Sentiment Analysis Example

The example in this fork is modified to allow using either PyTorch or OpenVINO
Hugging Face models. It also adds inference duration to the output. To change
between PyTorch and OpenVINO, change the `backend` in
models/text\_sentiment/config.yml. By default GRPC is enabled, REST is disabled.

This is a proof-of-concept example. For OpenVINO inference, the model is
converted on-the-fly. For production use, it is recommended to load the
OpenVINO model directly.

By default it uses the [assemblyai/bert-large-uncased-sst2](https://huggingface.co/assemblyai/bert-large-uncased-sst2) AI model from the Hugging Face hub to perform text sentiment analysis. The model can be changed in the models/text\_sentiment/config.yml file. The Caikit runtime loads the model and serves it so that it can be inferred or called.

## Before Starting

The following tools are required:

- [python](https://www.python.org) (v3.8+)
- [pip](https://pypi.org/project/pip/) (v23.0+)

**Note: Before installing dependencies and to avoid conflicts in your environment, it is advisable to use a [virtual environment (venv)](https://docs.python.org/3/library/venv.html).**

Install the dependencies: `pip install -r requirements.txt`

## Running the Caikit runtime

In one terminal, start the runtime server:

```shell
python3 start_runtime.py
```

This should start the runtime server with grpc enabled.

You should see output similar to the following:

```command
$ python3 start_runtime.py   

<function register_backend_type at 0x7fce0064b5e0> is still in the BETA phase and subject to change!
{"channel": "COM-LIB-INIT", "exception": null, "level": "info", "log_code": "<RUN11997772I>", "message": "Loading service module: text_sentiment", "num_indent": 0, "thread_id": 8605140480, "timestamp": "2023-05-02T11:42:52.808812"}
{"channel": "COM-LIB-INIT", "exception": null, "level": "info", "log_code": "<RUN11997772I>", "message": "Loading service module: caikit.interfaces.common", "num_indent": 0, "thread_id": 8605140480, "timestamp": "2023-05-02T11:42:52.809406"}
{"channel": "COM-LIB-INIT", "exception": null, "level": "info", "log_code": "<RUN11997772I>", "message": "Loading service module: caikit.interfaces.runtime", "num_indent": 0, "thread_id": 8605140480, "timestamp": "2023-05-02T11:42:52.809565"}
[…]
{"channel": "MODEL-LOADER", "exception": null, "level": "info", "log_code": "<RUN89711114I>", "message": "Loading model 'text_sentiment'", "num_indent": 0, "thread_id": 8605140480, "timestamp": "2023-05-02T11:42:52.826657"}
{"channel": "MDLMNG", "exception": null, "level": "warning", "log_code": "<COR56759744W>", "message": "No backend configured! Trying to configure using default config file.", "num_indent": 0, "thread_id": 8605140480, "timestamp": "2023-05-02T11:42:52.827742"}
No model was supplied, defaulted to distilbert-base-uncased-finetuned-sst-2-english and revision af0f99b (https://huggingface.co/distilbert-base-uncased-finetuned-sst-2-english).
Using a pipeline without specifying a model name and revision in production is not recommended.
[…]
{"channel": "COM-LIB-INIT", "exception": null, "level": "info", "log_code": "<RUN11997772I>", "message": "Loading service module: text_sentiment", "num_indent": 0, "thread_id": 8605140480, "timestamp": "2023-05-02T11:42:53.929756"}
{"channel": "COM-LIB-INIT", "exception": null, "level": "info", "log_code": "<RUN11997772I>", "message": "Loading service module: caikit.interfaces.common", "num_indent": 0, "thread_id": 8605140480, "timestamp": "2023-05-02T11:42:53.929814"}
{"channel": "COM-LIB-INIT", "exception": null, "level": "info", "log_code": "<RUN11997772I>", "message": "Loading service module: caikit.interfaces.runtime", "num_indent": 0, "thread_id": 8605140480, "timestamp": "2023-05-02T11:42:53.929858"}
{"channel": "GP-SERVICR-I", "exception": null, "level": "info", "log_code": "<RUN76773778I>", "message": "Validated Caikit Library CDM successfully", "num_indent": 0, "thread_id": 8605140480, "timestamp": "2023-05-02T11:42:53.929942"}
{"channel": "GP-SERVICR-I", "exception": null, "level": "info", "log_code": "<RUN76884779I>", "message": "Constructed inference service for library: text_sentiment, version: unknown", "num_indent": 0, "thread_id": 8605140480, "timestamp": "2023-05-02T11:42:53.930734"}
{"channel": "SERVER-WRAPR", "exception": null, "level": "info", "log_code": "<RUN81194024I>", "message": "Intercepting RPC method /caikit.runtime.HfTextsentiment.HfTextsentimentService/HfBlockPredict", "num_indent": 0, "thread_id": 8605140480, "timestamp": "2023-05-02T11:42:53.930786"}
{"channel": "SERVER-WRAPR", "exception": null, "level": "info", "log_code": "<RUN33333123I>", "message": "Wrapping safe rpc for Predict", "num_indent": 0, "thread_id": 8605140480, "timestamp": "2023-05-02T11:42:53.931424"}
{"channel": "SERVER-WRAPR", "exception": null, "level": "info", "log_code": "<RUN30032825I>", "message": "Re-routing RPC /caikit.runtime.HfTextsentiment.HfTextsentimentService/HfBlockPredict from <function _ServiceBuilder._GenerateNonImplementedMethod.<locals>.<lambda> at 0x7fce01f660d0> to <function CaikitRuntimeServerWrapper.safe_rpc_wrapper.<locals>.safe_rpc_call at 0x7fce02144670>", "num_indent": 0, "thread_id": 8605140480, "timestamp": "2023-05-02T11:42:53.931479"}
{"channel": "SERVER-WRAPR", "exception": null, "level": "info", "log_code": "<RUN24924908I>", "message": "Interception of service caikit.runtime.HfTextsentiment.HfTextsentimentService complete", "num_indent": 0, "thread_id": 8605140480, "timestamp": "2023-05-02T11:42:53.931530"}
[…]

{"channel": "GRPC-SERVR", "exception": null, "level": "info", "log_code": "<RUN10001807I>", "message": "Running in insecure mode", "num_indent": 0, "thread_id": 8605140480, "timestamp": "2023-05-02T11:42:53.936511"}
{"channel": "GRPC-SERVR", "exception": null, "level": "info", "log_code": "<RUN10001001I>", "message": "Caikit Runtime is serving on port: 8085 with thread pool size: 5", "num_indent": 0, "thread_id": 8605140480, "timestamp": "2023-05-02T11:42:53.938054"}
```

## Inferring the Served Model

In another terminal, run the client code:

```shell
python3 client.py
```
The client code calls the model and queries it for sentiment analysis on 2 different pieces of text.

You should see output similar to the following:

```command
$ python client.py

Duration: 40.58
Text: I am not feeling well today!
RESPONSE from gRPC: classes {
  class_name: "LABEL_0"
  confidence: 0.97693902254104614
}

Duration: 36.58
Text: Today is a nice sunny day
RESPONSE from gRPC: classes {
  class_name: "LABEL_1"
  confidence: 0.99803906679153442
}

Duration: 36.63
Text: It's raining today
RESPONSE from gRPC: classes {
  class_name: "LABEL_0"
  confidence: 0.94041192531585693
}

```
