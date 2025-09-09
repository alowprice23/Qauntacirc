---
generation_method: "This document is intended to be auto-generated from the Python docstrings in the `/messaging` directory using a tool like `mkdocstrings`. The content below is a manually-created placeholder."
---

# API Reference: `messaging`

This document provides a reference for the `messaging` module, which handles asynchronous communication within the QuantaCirc system. The system uses a NATS-based message bus for high-performance, reliable messaging.

## `Publisher`

**`messaging.publisher.Publisher`**

A class for publishing messages to a specific topic on the message bus.

### Methods

#### `publish(topic: str, message: dict) -> None`

Publishes a `message` to the specified `topic`.

- **Parameters**:
    - `topic` (`str`): The topic to publish the message to.
    - `message` (`dict`): The message payload, which must be a JSON-serializable dictionary.

### Usage

```python
from messaging.publisher import Publisher

# Assuming nats_client is already connected
publisher = Publisher(nats_client)
message = {"event": "state_updated", "state_id": "xyz-123"}
publisher.publish("system.events", message)
```

---

## `Subscriber`

**`messaging.subscriber.Subscriber`**

A class for subscribing to topics and receiving messages.

### Methods

#### `subscribe(topic: str, callback: callable) -> None`

Subscribes to a `topic` and registers a `callback` function to handle incoming messages.

- **Parameters**:
    - `topic` (`str`): The topic to subscribe to. Can include wildcards (e.g., `system.*`).
    - `callback` (`callable`): A function that will be called with the message payload when a message is received.

### Usage

```python
from messaging.subscriber import Subscriber

def handle_message(msg):
    print(f"Received message: {msg}")

# Assuming nats_client is already connected
subscriber = Subscriber(nats_client)
subscriber.subscribe("system.events", handle_message)

# The subscriber will now listen for messages in the background.
```

---

## `StreamManager`

**`messaging.stream_manager.StreamManager`**

A utility for managing NATS streams. Streams provide persistence for messages.

### Methods

#### `create_stream(stream_name: str, subjects: list[str]) -> None`

Creates a new persistent stream that captures messages from a list of subjects (topics).

- **Parameters**:
    - `stream_name` (`str`): The name of the stream to create.
    - `subjects` (`list[str]`): A list of subjects for the stream to capture.
