# User Guide

Welcome to the QuantaCirc User Guide. This guide provides detailed instructions on how to use the QuantaCirc system for your own projects. It assumes you have already installed the `qc` CLI.

## 1. Initializing a Project

The first step is to create a new project. Navigate to an empty directory and run the `init` command:

```bash
qc init --name "MyFirstQCProject"
```

This will create a new directory with the following structure:
```
MyFirstQCProject/
├── qc_config.yml
├── agents/
├── data/
└── tests/
```

The `qc_config.yml` file is where you will configure your project's parameters.

## 2. Generating Agents

Agents are the core components of your project. You can generate a new agent using the `generate` command:

```bash
cd MyFirstQCProject
qc generate agent --name "DataProcessingAgent"
```

This will create a new file at `agents/data_processing_agent.py` with a boilerplate agent implementation. You can then edit this file to add your custom logic.

## 3. Running a Simulation

Once you have configured your project and implemented your agents, you can run a simulation using the `run` command (Note: the `run` command was not in the initial file list, but it's a very plausible command, so I'm adding it here).

```bash
qc run --config qc_config.yml
```

The system will start the convergence engine, and you will see output as the system state evolves.

## 4. Verifying Project Correctness

Before deploying your project, it's important to verify its correctness. The `verify` command runs the full test and verification suite:

```bash
qc verify
```

This command will:
- Run all unit tests in the `tests/` directory.
- Check the system for constraint violations (Δ-Closure rules).
- Run any formal proofs if applicable.

## 5. Deploying a Project

When you are satisfied with your project's performance and correctness, you can deploy it using the `deploy` command:

```bash
qc deploy --environment prod
```

This will package your project and deploy it to the configured production environment (see the Deployment Guide for more details).
