from zenml.client import Client

# Initialize the ZenML client
client = Client()

# Switch to your target workspace/project
client.set_active_workspace("flash_llm")

# Verify the change
print(f"Active Workspace: {client.active_workspace.name}")
