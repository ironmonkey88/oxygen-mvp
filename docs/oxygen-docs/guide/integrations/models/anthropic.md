> ## Documentation Index
> Fetch the complete documentation index at: https://oxy.tech/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Claude

> Oxy is the fastest way to build AI agents

<Warning>
  Note: Claude models currently have rate limits and may require careful
  configuration for optimal performance.
</Warning>

### Setup Guide

<Steps>
  <Step title="Set up Claude API key">
    ```sh theme={null}
      export CLAUDE_API_KEY=<your Claude API key>
    ```
  </Step>

  <Step title="Add model configuration">
    Add the model configuration to your `config.yml` file:

    ```yaml config.yml theme={null}
    ...
    models:
    - name: claude-3-7-sonnet
      key_var: ANTHROPIC_API_KEY # name of the environment variable containing the API key
      model_ref: claude-3-7-sonnet-20250219 # or model of your choice
      vendor: anthropic
    ...
    ```
  </Step>

  <Step title="Update agent's model configuration">
    Update the agent's model configuration:

    ```yaml agents/agent.yml theme={null}
    model: claude-3-7-sonnet
    ```
  </Step>
</Steps>
