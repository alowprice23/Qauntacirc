# Getting Started: Your First QuantaCirc Project

This guide will walk you through the process of creating and running your first QuantaCirc project in 5 minutes.

## Prerequisites

- Python 3.11+ installed
- QuantaCirc installed (`pip install quantacirc`)

## Step 1: Create a New Project

First, use the `qc` CLI to initialize a new project.

```bash
qc init --name "HelloWorld"
```

This command creates a new directory called `HelloWorld` and populates it with the basic project structure.

```bash
cd HelloWorld
```

## Step 2: Generate an Agent

Next, generate a simple "hello world" agent.

```bash
qc generate agent --name "HelloWorldAgent"
```

This creates a new file `agents/hello_world_agent.py`. For this tutorial, we don't need to edit the file. The default agent will simply print a message.

## Step 3: Run the System

Now, you are ready to run the system. Use the `run` command:

```bash
qc run
```

You should see output from the QuantaCirc engine, indicating that the system is initializing, running, and then converging. You should also see a "Hello World" message from the agent you generated.

```
...
INFO:ConvergenceEngine: Starting convergence process...
INFO:HelloWorldAgent: Hello, World!
INFO:LyapunovMonitor: System has reached a stable state.
INFO:ConvergenceEngine: Convergence reached in 10 steps.
...
```

## Next Steps

Congratulations! You have successfully created and run your first QuantaCirc project.

From here, you can explore the following resources:
- **[User Guide](./user_guide.md)**: For a more detailed explanation of how to use the system.
- **[Developer Guide](./dev_guide.md)**: If you want to contribute to QuantaCirc itself.
- **[Examples](../examples/)**: For more complex examples and tutorials.
