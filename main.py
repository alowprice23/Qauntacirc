import json
from src.nlp_processor.processor import NLProcessor

def pretty_print(data):
    """Helper function to print dictionaries in a readable format."""
    print(json.dumps(data, indent=2, default=str))

def main():
    """
    Main function to demonstrate the NLProcessor's capabilities.
    """
    print("Initializing Advanced NLP Processor...")
    processor = NLProcessor()

    print("\n" + "="*50)
    print("STEP 1: Processing a complex, multi-step command.")
    print("="*50)

    complex_command = "Build microservices with auth and rate limiting, then generate comprehensive tests, and finally set up deployment automation."
    print(f"INPUT COMMAND: \"{complex_command}\"")

    result = processor.process_command(complex_command)

    print("\n--- COMMAND ANALYSIS RESULT ---")
    pretty_print(result)

    print("\n" + "="*50)
    print("STEP 2: Processing more commands to build history.")
    print("="*50)

    processor.process_command("Build a new feature and run tests.")
    processor.process_command("Build and deploy the login service.")
    # Process the first command again to increase its frequency for auto-completion
    processor.process_command(complex_command)

    print("History has been populated with a few commands.")

    print("\n" + "="*50)
    print("STEP 3: Demonstrating intelligent auto-completion.")
    print("="*50)

    partial_input = "Build micro"
    print(f"INPUT PARTIAL: \"{partial_input}\"")

    suggestions = processor.get_completion_suggestions(partial_input)

    print("\n--- AUTO-COMPLETION SUGGESTIONS ---")
    pretty_print(suggestions)

    partial_input_2 = "Build and"
    print(f"\nINPUT PARTIAL: \"{partial_input_2}\"")
    suggestions_2 = processor.get_completion_suggestions(partial_input_2)
    print("\n--- AUTO-COMPLETION SUGGESTIONS ---")
    pretty_print(suggestions_2)


if __name__ == "__main__":
    main()
