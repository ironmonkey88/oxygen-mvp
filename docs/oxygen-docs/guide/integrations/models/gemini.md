> ## Documentation Index
> Fetch the complete documentation index at: https://oxy.tech/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Gemini

> Oxy is the fastest way to build AI agents

<Warning>
  Note: Gemini models currently have stability issues with function calling
  capabilities. Your agent may not be able to call tools as expected.
</Warning>

### Setup Guide

<Steps>
  <Step title="Set up Gemini API key">
    ```sh theme={null}
      export GEMINI_API_KEY=<your Gemini API key>
    ```
  </Step>

  <Step title="Add model configuration">
    Add the model configuration to your `config.yml` file:

    ```yaml config.yml theme={null}
    ...
    models:
    - name: gemini1.5pro
      key_var: GEMINI_API_KEY # name of the environment variable containing the API key
      model_ref: gemini-1.5-pro # or model of your choice
      vendor: gemini
    ...
    ```
  </Step>

  <Step title="Update agent's model configuration">
    Update the agent's model configuration:

    ```yaml agents/agent.yml theme={null}
    model: gemini1.5pro
    ```
  </Step>
</Steps>
