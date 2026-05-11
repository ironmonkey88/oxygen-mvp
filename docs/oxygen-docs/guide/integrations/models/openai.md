> ## Documentation Index
> Fetch the complete documentation index at: https://oxy.tech/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# OpenAI

By default, Oxy uses `gpt-4.1` from OpenAI.

If you want to use a different model, you can update the model config in `config.yml` file.

<Steps>
  <Step title="Add model config">
    Add model config into `config.yml` file

    Below is an example of how to add `gpt-4.1` model to the global config.

    ```yaml config.yml theme={null}
    ...
    models:
      - name: openai-4.1
        vendor: openai
        key_var: # your openai api key goes here
        model_ref: gpt-4.1
    ...
    ```
  </Step>

  <Step title="Update agent's model config">
    Update agent's model config:

    ```yaml agents/agent.yml theme={null}
    model: openai-4.1
    ```
  </Step>
</Steps>
