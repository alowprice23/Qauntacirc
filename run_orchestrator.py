import asyncio
import logging
from core.config_loader import load_config
from core.orchestrator import Orchestrator

async def main():
    """
    Main entry point to run the orchestrator as a standalone service.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    config = load_config()
    orchestrator = Orchestrator(config)

    try:
        await orchestrator.start()
        log.info("Orchestrator is running. Press Ctrl+C to stop.")
        # Keep the orchestrator running indefinitely
        await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        log.info("Orchestrator is shutting down.")
    finally:
        await orchestrator.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass