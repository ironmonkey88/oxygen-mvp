> ## Documentation Index
> Fetch the complete documentation index at: https://oxy.tech/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Ollama

> Oxy is the fastest way to build data agents

Ollama provides an easy way to host LLMs locally.

### Setup guide

<Steps>
  <Step title="Environment setup"> Start by downloading and installing [ollama](https://ollama.com/download) </Step>

  <Step title="Add model config">
    Add model config into `config.yml` file

    ```yaml config.yml theme={null}
    ...
    models:
      - name: llama3.2
        vendor: ollama
        model_ref: llama3.2:latest # or model of choice
        api_url: http://localhost:11434
        api_key: # your ollama api key goes here
    ...
    ```
  </Step>

  <Step title="Update agent's model config">
    Update agent's model config:

    ```yaml agents/agent.yml theme={null}
    model: llama3.2
    ```
  </Step>
</Steps>
