> ## Documentation Index
> Fetch the complete documentation index at: https://oxy.tech/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Quickstart

> Let's learn how to start using oxy

export const DownloadLink = () => {
  if (typeof window === "undefined") {
    return null;
  } else {
    setTimeout(() => {
      const platform = window.navigator.platform.toLowerCase();
      const userAgent = window.navigator.userAgent.toLowerCase();
      let os = "";
      let arch = "";
      if (platform.includes("win")) {
        os = "windows";
        arch = "x64";
      } else if (platform.includes("mac")) {
        os = "macos";
        if (userAgent.match(/OS X 10_([789]|1[01234])/)) {
          arch = "x64";
        } else {
          const w = document.createElement("canvas").getContext("webgl");
          const d = w.getExtension('WEBGL_debug_renderer_info');
          const g = d && w.getParameter(d.UNMASKED_RENDERER_WEBGL) || "";
          if (g.match(/Apple/) && !g.match(/Apple GPU/)) {
            arch = "arm";
          } else {
            arch = w.getSupportedExtensions().indexOf("WEBGL_compressed_texture_s3tc_srgb") === -1 ? "arm" : "x64";
          }
        }
      } else {
        os = "unsupported";
      }
      const linkMap = {
        "windows_x64": "https://github.com/oxy-hq/oxy/releases/latest/download/oxy_x64.zip",
        "macos_x64": "https://github.com/oxy-hq/oxy/releases/latest/download/oxy_x64.dmg",
        "macos_arm": "https://github.com/oxy-hq/oxy/releases/latest/download/oxy_aarch64.dmg"
      };
      const key = `${os}_${arch}`;
      const container = document.getElementById("download-link-container");
      if (linkMap[key]) {
        container.innerHTML = `<a href="${linkMap[key]}">Download latest version for ${os} (${arch})</a>`;
      } else {
        container.innerHTML = `Your operating system ${os} and architecture ${arch} is currently not supported.`;
      }
    }, 3);
  }
  return <div id="download-link-container"></div>;
};

## Overview

Install Oxy, scaffold a project, and launch the web interface. You'll need an OpenAI API key and a terminal (on Windows, use [WSL 2](/prerequisites#windows-wsl)).

<Steps>
  <Step title="Install Oxy">
    ```bash theme={null}
    bash <(curl --proto '=https' --tlsv1.2 -LsSf https://get.oxy.tech)
    ```

    You may need to restart your terminal for the `oxy` command to be recognized.

    <Accordion title="Edge builds & specific versions">
      ```bash theme={null}
      # Edge build (latest from main)
      bash <(curl --proto '=https' --tlsv1.2 -LsSf https://nightly.oxy.tech)

      # Specific stable version
      OXY_VERSION="0.5.20" bash <(curl --proto '=https' --tlsv1.2 -LsSf https://get.oxy.tech)
      ```

      Browse all releases at [oxy-hq/oxygen-nightly](https://github.com/oxy-hq/oxygen-nightly/releases).
    </Accordion>
  </Step>

  <Step title="Create a project">
    Run in an empty directory:

    ```bash theme={null}
    oxy init
    ```

    This generates a `config.yml`, a sample agent, workflow, data, and semantic layer file.
  </Step>

  <Step title="Set your API keys">
    The sample project is configured to use `OPENAI_API_KEY` and `ANTHROPIC_API_KEY`. Create a `.env` file following `.env.example`:

    ```bash theme={null}
    cp .env.example .env
    ```

    Then fill in your API keys. For alternative models, see [integrations](/integrations/overview).
  </Step>

  <Step title="Launch the web interface">
    ```bash theme={null}
    oxy start
    ```

    This starts PostgreSQL in Docker and launches the Oxy web UI.

    <Info>
      **Requires Docker.** See the [prerequisites guide](/prerequisites) if you
      don't have a container runtime installed.
    </Info>

    <Accordion title="Using your own PostgreSQL instead">
      ```bash theme={null}
      export OXY_DATABASE_URL="postgresql://user:pass@host:port/database"
      oxy serve
      ```

      Use `oxy serve` for production deployments or environments where Docker is not available.
    </Accordion>
  </Step>
</Steps>
