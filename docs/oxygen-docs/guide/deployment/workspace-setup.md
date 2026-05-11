> ## Documentation Index
> Fetch the complete documentation index at: https://oxy.tech/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Set Up Workspace & Repository

> Setting up your Oxy workspace and configuring your repository

After setting up the server infrastructure, you need to create or copy your Oxy workspace directory and configure your repository.

<Steps>
  <Step title="Create Workspace Directory">
    Create a directory for your Oxy workspace on the server:

    ```bash theme={null}
    mkdir -p ~/oxy-workspace
    cd ~/oxy-workspace
    ```
  </Step>

  <Step title="Configure Repository">
    Depending on your setup, you can either use Git to manage your Oxy files or manually set up your workspace.

    <Tabs>
      <Tab title="Using Git">
        If you're using Git to manage your workspace:

        1. Install Git and configure credentials:

        ```bash theme={null}
        apt-get update && apt-get install -y git
        ```

        2. Set up SSH keys for Git access:

        ```bash theme={null}
        # Generate SSH key
        ssh-keygen -t ed25519 -C "your-email@example.com"

        # Add GitHub to known hosts
        ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts

        # Print public key to add to GitHub
        cat ~/.ssh/id_ed25519.pub
        ```

        3. Add the public key to your GitHub account settings.

        4. Clone your Oxy repository:

        ```bash theme={null}
        git clone git@github.com:your-org/your-oxy-repo.git
        cd your-oxy-repo
        ```
      </Tab>

      <Tab title="Manual Setup">
        If you're not using Git:

        1. Manually copy your workspace files to the server using tools like SCP or SFTP:

        ```bash theme={null}
        # Example: Using scp to copy files from local to server
        # Run this command from your local machine
        scp -r /path/to/local/oxy-project user@server:/path/on/server
        ```

        2. Navigate to your workspace directory:

        ```bash theme={null}
        cd /path/on/server/oxy-project
        ```
      </Tab>
    </Tabs>
  </Step>

  <Step title="Verify Workspace Structure">
    Ensure your workspace has the necessary structure and files:

    ```bash theme={null}
    # List files in your workspace
    ls -la

    # Check if you have a config.yml file
    if [ -f "config.yml" ]; then
      echo "Config file found"
    else
      echo "Config file missing"
    fi
    ```

    A typical Oxy workspace should include:

    * `config.yml` - Main configuration file
    * Agent definitions (`.agent.yml` files)
    * Workflow definitions (`.workflow.yml` files)
    * SQL queries (`.sql` files)
    * Semantic models (`.schema.yml` files)
  </Step>

  <Step title="Update systemd Service Configuration">
    If you've already set up Oxy as a systemd service, update the service file to point to your actual workspace path:

    ```bash theme={null}
    sudo sed -i "s|/home/ubuntu/your-oxy-project|$(pwd)|g" /etc/systemd/system/oxy.service
    sudo systemctl daemon-reload
    ```
  </Step>
</Steps>

Now that your workspace is set up, proceed to configure the environment variables and secrets.

<div className="mt-8">
  <Cards>
    <Card title="Next: Configure Environment" icon="arrow-right" href="/deployment/environment">
      Set up environment variables and secrets management
    </Card>
  </Cards>
</div>
