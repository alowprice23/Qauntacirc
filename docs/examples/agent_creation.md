# Tutorial: Creating a Custom Agent

This tutorial provides a step-by-step guide to creating a custom agent that performs a specific task. We will create an agent that scans a directory for files and proposes to add metadata to them.

## 1. Define the State

First, let's define what our part of the system state looks like. In `qc_config.yml`, we can define a custom state structure.

```yaml
# qc_config.yml
initial_state:
  files:
    - path: "/data/file1.txt"
      metadata: {}
    - path: "/data/file2.csv"
      metadata: {}
```

## 2. Generate the Agent

Use the CLI to generate the agent boilerplate:

```bash
qc generate agent --name "MetadataAgent"
```

This creates `agents/metadata_agent.py`.

## 3. Implement the Agent Logic

Now, let's edit `agents/metadata_agent.py` to implement the logic.

### `propose_transition`

The `propose_transition` method will scan the files in the state and, if a file has no metadata, propose a transition to add some.

```python
# agents/metadata_agent.py
import os
from agents.base.agent import BaseAgent
from core.types import State, Transition, Operation

class MetadataAgent(BaseAgent):

    def propose_transition(self, state: State) -> Transition:
        """
        Proposes to add metadata to files that don't have any.
        """
        operations = []
        for file_info in state.get("files", []):
            if not file_info.get("metadata"):
                # Propose an operation to add metadata
                op = Operation(
                    op_type="ADD_METADATA",
                    path=file_info["path"],
                    payload={"size": os.path.getsize(file_info["path"]), "processed": False}
                )
                operations.append(op)

        return Transition(operations=operations)
```

### `execute_transition`

The `execute_transition` method is not strictly needed for this agent if another agent (or the core engine) is responsible for applying the operations. However, a full-fledged agent would also be able to execute its own proposed operations.

## 4. Activate the Agent

Finally, make sure the agent is enabled in your `qc_config.yml`:

```yaml
# qc_config.yml
agents:
  - name: "MetadataAgent"
    enabled: true
```

Now, when you run `qc run`, the `MetadataAgent` will be active. It will scan the state and propose operations to add metadata to the files. These operations will then be validated by the constraint solver and, if valid, applied to the state, causing the system to evolve.
