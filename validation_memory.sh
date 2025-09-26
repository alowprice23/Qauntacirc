#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "--- Running Constellation Memory Validation Test Suite ---"

# The qcli command might not be in the PATH, so we'll call it via `python -m cli.main`
QCLI="python -m cli.main"

# Clean up previous test runs
rm -rf ./.quantacirc_cli_storage

# --- Test 1: Fact Extraction and Storage ---
echo -e "\n\n--- Test 1: Fact Extraction and Storage ---"
echo "Adding a fact about JWT expiration..."
$QCLI memory add-fact "JWT tokens expire after 1 hour in production" --type "policy" --owner "security_team"

echo "Querying for token policies..."
$QCLI memory query "token expiration policies"
# Expected: The fact about JWT tokens should be returned.

# --- Test 2: Pattern Recognition ---
echo -e "\n\n--- Test 2: Pattern Recognition ---"
echo "Adding facts to create an authentication pattern..."
$QCLI memory learn-text "Project 'Phoenix' uses OAuth2 for authentication." --owner "phoenix_dev"
$QCLI memory learn-text "Project 'Griffin' uses OAuth2 for authentication." --owner "griffin_dev"
$QCLI memory learn-text "The 'Hydra' project uses SAML for authentication." --owner "hydra_dev"

echo "Analyzing authentication patterns..."
$QCLI memory analyze-patterns --domain "authentication"
# Expected: A pattern about OAuth2 being used for authentication should be identified.

# --- Test 3: Context-Aware Agent Execution ---
echo -e "\n\n--- Test 3: Context-Aware Agent Execution ---"
echo "Generating a secure API endpoint with memory..."
# This is a conceptual test. We check if the command runs and if memory is used.
# The `generate` command is not fully implemented in this test suite, but we can check if the `--use-memory` flag is accepted.
# In a real scenario, we would inspect the generated code for security patterns.
echo "Note: The 'generate' command is not part of this test suite. This test is conceptual."
# $QCLI generate "create a secure API endpoint" --use-memory

# --- Test 4: Temporal Reasoning ---
echo -e "\n\n--- Test 4: Temporal Reasoning ---"
echo "Adding historical facts for temporal analysis..."
# We need to create facts with past timestamps.
# Timestamps are in ISO 8601 format.
$QCLI memory add-fact "Legacy authentication used basic auth" --type "legacy_pattern" --owner "ops" --timestamp "2023-01-15T10:00:00"
$QCLI memory add-fact "SAML was introduced for enterprise SSO" --type "auth_standand" --owner "security_team" --timestamp "2023-06-20T14:00:00"
$QCLI memory add-fact "OAuth2 became the standard for new services" --type "auth_standard" --owner "security_team" --timestamp "2024-03-10T11:00:00"

echo "Running timeline analysis for 'authentication'..."
$QCLI memory timeline --query "authentication" --span 18
# Expected: A timeline showing the evolution of authentication approaches.

echo -e "\n\n--- Validation Test Suite Completed Successfully ---"
echo "Note: Manual inspection of the output is required to confirm correctness."