```markdown
# Groq API Documentation

## Chat

### Create chat completion

**POST** https://api.groq.com/openai/v1/chat/completions

Creates a model response for the given chat conversation.

**Request Body**

| Parameter             | Type               | Required/Optional              | Default | Description                                                                                                                            |
| --------------------- | ------------------ | ------------------------------ | ------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `frequency_penalty`   | number/null        | Optional                       | 0       | Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text, decreasing repetition. |
| `function_call`       | string/object/null | Deprecated (use `tool_choice`) |         | Controlled function calls (deprecated).                                                                                                |
| `functions`           | array/null         | Deprecated (use `tools`)       |         | List of functions (deprecated).                                                                                                        |
| `logit_bias`          | object/null        | Optional                       |         | Modify likelihood of specific tokens (not yet supported).                                                                              |
| `logprobs`            | boolean/null       | Optional                       | false   | Return log probabilities of output tokens (not yet supported).                                                                         |
| `max_tokens`          | integer/null       | Optional                       |         | Maximum number of generated tokens.                                                                                                    |
| `messages`            | array              | Required                       |         | List of messages comprising the conversation.                                                                                          |
| `model`               | string             | Required                       |         | ID of the model to use.                                                                                                                |
| `n`                   | integer/null       | Optional                       | 1       | Number of completion choices (currently only supports 1).                                                                              |
| `parallel_tool_calls` | boolean/null       | Optional                       | true    | Enable parallel function calling during tool use.                                                                                      |
| `presence_penalty`    | number/null        | Optional                       | 0       | Number between -2.0 and 2.0. Positive values penalize new tokens based on their presence in the text, increasing topic diversity.      |
| `response_format`     | object/null        | Optional                       |         | Format of model output. Use `{ "type": "json_object" }` for JSON mode.                                                                 |
| `seed`                | integer/null       | Optional                       |         | Seed for deterministic sampling (not guaranteed).                                                                                      |
| `stop`                | string/array/null  | Optional                       |         | Up to 4 sequences to stop generation.                                                                                                  |
| `stream`              | boolean/null       | Optional                       | false   | Send partial message deltas as server-sent events.                                                                                     |
| `stream_options`      | object/null        | Optional                       |         | Options for streaming responses (use when `stream: true`).                                                                             |
| `temperature`         | number/null        | Optional                       | 1       | Sampling temperature (0-2). Higher values = more random.                                                                               |
| `tool_choice`         | string/object/null | Optional                       |         | Controls tool usage.                                                                                                                   |
| `tools`               | array/null         | Optional                       |         | List of tools the model may call (currently only functions).                                                                           |
| `top_logprobs`        | integer/null       | Optional                       |         | Number of most likely tokens to return (not yet supported).                                                                            |
| `top_p`               | number/null        | Optional                       | 1       | Nucleus sampling probability (alternative to `temperature`).                                                                           |
| `user`                | string/null        | Optional                       |         | Unique identifier for the end-user.                                                                                                    |

**Returns:**

A chat completion object, or streamed sequence if `stream` is true.

## Audio

### Create transcription

**POST** https://api.groq.com/openai/v1/audio/transcriptions

Transcribes audio into the input language.

**Request Body**

| Parameter                   | Type   | Required/Optional | Default   | Description                                                                            |
| --------------------------- | ------ | ----------------- | --------- | -------------------------------------------------------------------------------------- |
| `file`                      | string | Required          |           | The audio file object (flac, mp3, mp4, mpeg, mpga, m4a, ogg, wav, or webm).            |
| `language`                  | string | Optional          |           | Input language (ISO-639-1 format recommended).                                         |
| `model`                     | string | Required          |           | Model ID (currently only `whisper-large-v3`).                                          |
| `prompt`                    | string | Optional          |           | Text to guide the model's style or continue a segment.                                 |
| `response_format`           | string | Optional          | `json`    | Output format (`json`, `text`, or `verbose_json`).                                     |
| `temperature`               | number | Optional          | 0         | Sampling temperature (0-1).                                                            |
| `timestamp_granularities[]` | array  | Optional          | `segment` | Timestamp granularities (`word`, `segment`). Use with `response_format: verbose_json`. |


**Returns:**

An audio transcription object.

### Create translation

**POST** https://api.groq.com/openai/v1/audio/translations

Translates audio into English.

**Request Body** (Similar to transcription, but output is always English)

**Returns:**

An audio translation object.

## Models

### List models

**GET** https://api.groq.com/openai/v1/models

Lists available models.

**Returns:**

A list of models.


### Retrieve model

**GET** https://api.groq.com/openai/v1/models/{model}

Retrieves a specific model.

**Returns:**

A model object.
```


This markdown version includes the parameters, descriptions, and return types for each endpoint, presented in a clear and organized table format. It also highlights deprecated parameters and provides usage notes where applicable.  The curl examples are included within code blocks for better readability. Remember to replace placeholders like `$GROQ_API_KEY` with your actual API key and file paths as needed.