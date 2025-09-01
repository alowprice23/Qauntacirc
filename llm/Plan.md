# Plan for the `llm` Directory - Complete Implementation Guide

## 1. Architecture Overview & Philosophy

The `llm` directory provides the Large Language Model integration layer for QuantaCirc, enabling natural language processing capabilities while maintaining mathematical rigor and formal verification standards. This package abstracts LLM interactions behind a consistent interface, supports multiple providers, and ensures all AI-generated content is validated against system constraints.

### Core Design Principles

1. **Provider Abstraction**: Unified interface supporting multiple LLM providers (OpenAI, Anthropic, Groq, Gemini)
2. **Rate Limiting & Cost Control**: Built-in rate limiting and cost tracking for all LLM operations
3. **Prompt Versioning**: All prompts are versioned, checksummed, and validated for integrity
4. **Response Validation**: AI responses undergo strict validation before system integration
5. **Retry & Resilience**: Robust retry mechanisms with exponential backoff for reliability
6. **Tool Integration**: Support for function calling and structured output generation

### Mathematical Integration

The LLM layer operates within QuantaCirc's quantum-mechanical framework:
- **Energy-Aware Processing**: LLM operations contribute to E_dynamic energy component
- **Closure Rule Compliance**: All generated content must satisfy Δ closure rules
- **Formal Verification**: Generated code/proofs undergo automatic verification
- **Bounded Uncertainty**: Confidence scoring and uncertainty quantification for AI outputs

---

## 2. Core Infrastructure Files

### File: `llm/__init__.py` (5 LOC)

**Purpose**: Package initializer exposing main LLM client interface and key abstractions.

**Implementation**:
```python
"""
QuantaCirc LLM Integration Package
=================================

Provides Large Language Model integration with multiple provider support,
rate limiting, validation, and quantum-state-aware processing.
"""

from .client import LLMClient
from .prompt_registry import PromptRegistry
from .validators import ResponseValidator

__all__ = ["LLMClient", "PromptRegistry", "ResponseValidator"]
```

**Integration Points**:
- Imported by all agents requiring LLM capabilities
- Used by CLI commands for direct LLM interaction
- Referenced by configuration system for provider setup

---

### File: `llm/client.py` (150 LOC)

**Purpose**: Abstract base client defining unified interface for all LLM providers with quantum-state integration.

**Core Functionality**:
- Abstract LLM client interface with provider-agnostic methods
- Quantum state context integration for energy-aware processing
- Structured input/output validation and type safety
- Built-in metrics collection and cost tracking
- Response caching and request deduplication

**Implementation Strategy**:
```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, AsyncIterator
from dataclasses import dataclass
import asyncio
import time

from core.types import QCState, EnergyComponents
from .schemas import LLMRequest, LLMResponse, ToolCall, CompletionConfig
from .rate_limiter import RateLimiter
from .validators import ResponseValidator

@dataclass
class LLMUsageMetrics:
    """Tracks LLM usage for cost and performance monitoring."""
    tokens_used: int
    cost_estimate: float
    latency_ms: float
    provider: str
    model: str

class LLMClient(ABC):
    """
    Abstract base class for all LLM provider clients.
    
    Provides quantum-state-aware LLM processing with energy considerations,
    formal validation, and mathematical constraint compliance.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.rate_limiter = RateLimiter(config.get('rate_limits', {}))
        self.validator = ResponseValidator()
        self.usage_metrics: List[LLMUsageMetrics] = []
        self._cache: Dict[str, LLMResponse] = {}
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the LLM provider."""
        pass
    
    @property
    @abstractmethod
    def supported_models(self) -> List[str]:
        """List of models supported by this provider."""
        pass
    
    @abstractmethod
    async def complete(
        self,
        request: LLMRequest,
        quantum_context: Optional[QCState] = None
    ) -> LLMResponse:
        """
        Generate completion with quantum state awareness.
        
        Args:
            request: Structured LLM request with prompt and parameters
            quantum_context: Current quantum state for energy-aware processing
            
        Returns:
            Validated LLM response with energy impact assessment
        """
        pass
    
    @abstractmethod
    async def stream_complete(
        self,
        request: LLMRequest,
        quantum_context: Optional[QCState] = None
    ) -> AsyncIterator[str]:
        """Stream completion tokens with real-time validation."""
        pass
    
    @abstractmethod
    async def tool_call(
        self,
        request: LLMRequest,
        available_tools: List[ToolCall],
        quantum_context: Optional[QCState] = None
    ) -> LLMResponse:
        """Execute tool-calling with function schema validation."""
        pass
    
    async def quantum_aware_complete(
        self,
        request: LLMRequest,
        quantum_context: QCState
    ) -> LLMResponse:
        """
        Complete with full quantum state integration.
        
        Considers current energy state, Lyapunov potential, and closure rules
        when processing the request and validating responses.
        """
        # Pre-process request with quantum context
        enhanced_request = self._enhance_with_quantum_context(request, quantum_context)
        
        # Apply rate limiting
        await self.rate_limiter.acquire()
        
        # Check cache first
        cache_key = self._compute_cache_key(enhanced_request)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Execute completion
        start_time = time.time()
        response = await self.complete(enhanced_request, quantum_context)
        
        # Validate response against quantum constraints
        validation_result = self.validator.validate_quantum_compliance(
            response, quantum_context
        )
        
        if not validation_result.is_valid:
            raise ValueError(f"Response violates quantum constraints: {validation_result.violations}")
        
        # Record metrics
        usage = LLMUsageMetrics(
            tokens_used=response.usage.total_tokens,
            cost_estimate=self._estimate_cost(response.usage),
            latency_ms=(time.time() - start_time) * 1000,
            provider=self.provider_name,
            model=response.model
        )
        self.usage_metrics.append(usage)
        
        # Cache and return
        self._cache[cache_key] = response
        return response
    
    def _enhance_with_quantum_context(self, request: LLMRequest, context: QCState) -> LLMRequest:
        """Enhance request with quantum state information."""
        # Add energy state and constraints to the request context
        quantum_info = {
            "current_energy": context.energy,
            "lyapunov_potential": context.lyapunov_potential,
            "phase": context.optimization_phase,
            "closure_obligations": context.closure_obligations
        }
        
        enhanced_request = request.copy()
        enhanced_request.context.update(quantum_info)
        return enhanced_request
    
    def _compute_cache_key(self, request: LLMRequest) -> str:
        """Compute cache key for request deduplication."""
        # Implementation for request hashing
        pass
    
    def _estimate_cost(self, usage: Any) -> float:
        """Estimate cost based on token usage and provider pricing."""
        # Implementation for cost estimation
        pass
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get usage summary for monitoring and cost tracking."""
        if not self.usage_metrics:
            return {"total_cost": 0, "total_tokens": 0, "average_latency": 0}
        
        return {
            "total_cost": sum(m.cost_estimate for m in self.usage_metrics),
            "total_tokens": sum(m.tokens_used for m in self.usage_metrics),
            "average_latency": sum(m.latency_ms for m in self.usage_metrics) / len(self.usage_metrics),
            "request_count": len(self.usage_metrics)
        }
```

**Integration Points**:
- Inherited by all provider-specific clients
- Uses `core/types.py` for quantum state integration
- Integrates with `monitoring/metrics.py` for usage tracking
- Used by all agents for LLM-based operations

---

### File: `llm/providers/__init__.py` (5 LOC)

**Purpose**: Providers package initializer exposing all LLM provider implementations.

**Implementation**:
```python
"""
LLM Provider Implementations
===========================

Contains concrete implementations of the LLMClient interface for
various LLM providers including OpenAI, Anthropic, Groq, and Gemini.
"""

from .openai_client import OpenAIClient
from .anthropic_client import AnthropicClient
from .groq_client import GroqClient
from .gemini_client import GeminiClient

__all__ = ["OpenAIClient", "AnthropicClient", "GroqClient", "GeminiClient"]
```

---

### File: `llm/providers/openai_client.py` (80 LOC)

**Purpose**: OpenAI provider implementation with GPT model support and function calling capabilities.

**Core Functionality**:
- OpenAI API integration with proper authentication
- Support for GPT-3.5, GPT-4, and GPT-4 Turbo models
- Function calling for tool integration
- Streaming completion support
- Cost tracking for OpenAI pricing tiers

**Implementation Strategy**:
```python
import openai
from typing import List, AsyncIterator, Optional
import json

from ..client import LLMClient
from ..schemas import LLMRequest, LLMResponse, TokenUsage, ToolCall
from core.types import QCState

class OpenAIClient(LLMClient):
    """OpenAI provider implementation with quantum state awareness."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config['api_key']
        self.organization = config.get('organization')
        self.client = openai.AsyncOpenAI(
            api_key=self.api_key,
            organization=self.organization
        )
        self.default_model = config.get('default_model', 'gpt-4-turbo')
    
    @property
    def provider_name(self) -> str:
        return "openai"
    
    @property
    def supported_models(self) -> List[str]:
        return [
            "gpt-3.5-turbo",
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4-turbo-preview",
            "gpt-4-vision-preview"
        ]
    
    async def complete(
        self,
        request: LLMRequest,
        quantum_context: Optional[QCState] = None
    ) -> LLMResponse:
        """Generate completion using OpenAI's chat completion API."""
        
        # Build OpenAI-specific request
        openai_request = {
            "model": request.model or self.default_model,
            "messages": self._format_messages(request),
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "top_p": request.top_p,
            "frequency_penalty": request.frequency_penalty,
            "presence_penalty": request.presence_penalty
        }
        
        # Add quantum context as system message if provided
        if quantum_context:
            quantum_message = self._create_quantum_context_message(quantum_context)
            openai_request["messages"].insert(0, quantum_message)
        
        # Execute API call
        response = await self.client.chat.completions.create(**openai_request)
        
        # Convert to standard response format
        return LLMResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage=TokenUsage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens
            ),
            finish_reason=response.choices[0].finish_reason,
            provider="openai"
        )
    
    async def stream_complete(
        self,
        request: LLMRequest,
        quantum_context: Optional[QCState] = None
    ) -> AsyncIterator[str]:
        """Stream completion tokens from OpenAI."""
        
        openai_request = self._build_request(request, quantum_context)
        openai_request["stream"] = True
        
        async for chunk in await self.client.chat.completions.create(**openai_request):
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def tool_call(
        self,
        request: LLMRequest,
        available_tools: List[ToolCall],
        quantum_context: Optional[QCState] = None
    ) -> LLMResponse:
        """Execute function calling with OpenAI."""
        
        openai_request = self._build_request(request, quantum_context)
        openai_request["tools"] = [self._format_tool(tool) for tool in available_tools]
        openai_request["tool_choice"] = "auto"
        
        response = await self.client.chat.completions.create(**openai_request)
        
        # Handle tool calls in response
        if response.choices[0].message.tool_calls:
            return self._process_tool_calls(response)
        
        return self._format_standard_response(response)
    
    def _format_messages(self, request: LLMRequest) -> List[Dict[str, str]]:
        """Format messages for OpenAI API."""
        messages = []
        
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        
        messages.append({"role": "user", "content": request.prompt})
        
        return messages
    
    def _create_quantum_context_message(self, context: QCState) -> Dict[str, str]:
        """Create system message with quantum state context."""
        quantum_info = f"""
        Current Quantum State Context:
        - Energy (E_approx): {context.energy:.6f}
        - Lyapunov Potential (Φ): {context.lyapunov_potential:.6f}
        - Optimization Phase: {context.optimization_phase}
        - Active Closure Obligations: {len(context.closure_obligations)}
        
        Consider these constraints when generating responses.
        """
        return {"role": "system", "content": quantum_info}
```

**Integration Points**:
- Implements LLMClient abstract interface
- Uses OpenAI Python SDK for API communication
- Integrates quantum context into system messages
- Supports function calling for agent tool integration

---

### File: `llm/providers/anthropic_client.py` (80 LOC)

**Purpose**: Anthropic Claude provider implementation with Constitutional AI integration.

**Key Features**:
- Claude 3 (Haiku, Sonnet, Opus) model support
- Constitutional AI principles for safety
- Message-based conversation format
- Large context window utilization
- Safety filtering and content moderation

**Implementation Strategy**: Similar to OpenAI client but adapted for Anthropic's API format, with emphasis on Constitutional AI principles and quantum state integration through conversation context.

---

### File: `llm/providers/groq_client.py` (80 LOC)

**Purpose**: Groq provider implementation optimized for high-speed inference.

**Key Features**:
- Ultra-fast inference with Groq's LPU architecture
- Support for Mixtral and Llama models
- Optimized for real-time agent interactions
- Cost-effective processing for high-volume operations
- Integration with QuantaCirc's performance monitoring

**Implementation Strategy**: Focuses on speed optimization while maintaining quantum state awareness and validation requirements.

---

### File: `llm/providers/gemini_client.py` (80 LOC)

**Purpose**: Google Gemini provider implementation with multimodal capabilities.

**Key Features**:
- Gemini Pro and Ultra model support
- Multimodal input processing (text, images, code)
- Google AI safety filters integration
- Advanced reasoning capabilities for complex quantum calculations
- Code understanding and generation optimization

**Implementation Strategy**: Leverages Gemini's advanced reasoning for quantum-mechanical calculations and code analysis tasks.

---

## 3. Supporting Infrastructure Files

### File: `llm/rate_limiter.py` (100 LOC)

**Purpose**: Comprehensive rate limiting for all LLM providers with quantum-aware throttling.

**Core Functionality**:
- Token bucket algorithm for rate limiting
- Provider-specific rate limit configuration
- Cost-based throttling to prevent budget overruns
- Energy-aware limiting based on system state
- Adaptive limiting based on response quality

**Implementation Strategy**:
```python
import asyncio
import time
from typing import Dict, Any
from dataclasses import dataclass
from enum import Enum

from core.types import QCState

class LimitType(Enum):
    REQUESTS_PER_MINUTE = "requests_per_minute"
    TOKENS_PER_MINUTE = "tokens_per_minute"
    COST_PER_HOUR = "cost_per_hour"
    ENERGY_BUDGET = "energy_budget"

@dataclass
class RateLimit:
    limit_type: LimitType
    value: float
    window_seconds: int
    current_usage: float = 0
    window_start: float = 0

class QuantumAwareRateLimiter:
    """
    Rate limiter with quantum state awareness for energy-efficient LLM usage.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.limits = self._parse_limits(config)
        self.lock = asyncio.Lock()
        self.usage_history: List[Dict[str, Any]] = []
    
    async def acquire(self, 
                     estimated_tokens: int = 100,
                     estimated_cost: float = 0.01,
                     quantum_context: Optional[QCState] = None) -> bool:
        """
        Acquire permission for LLM request with quantum state consideration.
        """
        async with self.lock:
            current_time = time.time()
            
            # Check all rate limits
            for limit in self.limits:
                if not self._check_limit(limit, estimated_tokens, estimated_cost, current_time):
                    # Calculate wait time
                    wait_time = self._calculate_wait_time(limit, current_time)
                    await asyncio.sleep(wait_time)
            
            # Apply quantum-aware throttling
            if quantum_context:
                quantum_delay = self._calculate_quantum_delay(quantum_context)
                if quantum_delay > 0:
                    await asyncio.sleep(quantum_delay)
            
            # Update usage tracking
            self._update_usage(estimated_tokens, estimated_cost, current_time)
            return True
    
    def _calculate_quantum_delay(self, context: QCState) -> float:
        """
        Calculate additional delay based on quantum state.
        
        Higher energy states or Lyapunov instability may require
        throttling to prevent system destabilization.
        """
        base_delay = 0.0
        
        # Energy-based throttling
        if context.energy > context.energy_threshold * 0.8:
            base_delay += 0.5  # 500ms delay for high energy
        
        # Lyapunov-based throttling
        if context.lyapunov_potential > context.stability_threshold:
            base_delay += 1.0  # 1s delay for instability
        
        return base_delay
```

**Integration Points**:
- Used by all LLM clients for request throttling
- Integrates with quantum state for adaptive limiting
- Connects to cost tracking and budget management
- Provides metrics for monitoring and alerting

---

### File: `llm/validators.py` (90 LOC)

**Purpose**: Comprehensive validation framework for LLM inputs and outputs with quantum constraint checking.

**Core Functionality**:
- Response content validation and sanitization
- Quantum constraint compliance checking
- Mathematical formula validation
- Code syntax and semantic validation
- Safety and content filtering

**Implementation Strategy**:
```python
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re
import ast
import json

from core.types import QCState
from .schemas import LLMResponse

@dataclass
class ValidationResult:
    is_valid: bool
    violations: List[str]
    confidence_score: float
    sanitized_content: Optional[str] = None

class ResponseValidator:
    """
    Comprehensive validator for LLM responses with quantum awareness.
    """
    
    def __init__(self):
        self.safety_patterns = self._load_safety_patterns()
        self.quantum_validators = self._initialize_quantum_validators()
    
    def validate_response(self, response: LLMResponse, context: Optional[QCState] = None) -> ValidationResult:
        """
        Validate LLM response for safety, correctness, and quantum compliance.
        """
        violations = []
        confidence_score = 1.0
        
        # Content safety validation
        safety_result = self._validate_safety(response.content)
        if not safety_result.is_valid:
            violations.extend(safety_result.violations)
            confidence_score *= 0.5
        
        # Code validation if response contains code
        if self._contains_code(response.content):
            code_result = self._validate_code(response.content)
            if not code_result.is_valid:
                violations.extend(code_result.violations)
                confidence_score *= 0.7
        
        # Mathematical formula validation
        if self._contains_math(response.content):
            math_result = self._validate_mathematics(response.content)
            if not math_result.is_valid:
                violations.extend(math_result.violations)
                confidence_score *= 0.8
        
        # Quantum constraint validation
        if context:
            quantum_result = self.validate_quantum_compliance(response, context)
            if not quantum_result.is_valid:
                violations.extend(quantum_result.violations)
                confidence_score *= 0.6
        
        # Sanitize content if needed
        sanitized_content = self._sanitize_content(response.content) if violations else None
        
        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations,
            confidence_score=confidence_score,
            sanitized_content=sanitized_content
        )
    
    def validate_quantum_compliance(self, response: LLMResponse, context: QCState) -> ValidationResult:
        """
        Validate response compliance with quantum mechanical constraints.
        """
        violations = []
        
        # Check energy conservation
        if self._violates_energy_conservation(response, context):
            violations.append("Response violates energy conservation principles")
        
        # Check Lyapunov stability
        if self._destabilizes_lyapunov(response, context):
            violations.append("Response may destabilize Lyapunov potential")
        
        # Check closure rule compliance
        if self._violates_closure_rules(response, context):
            violations.append("Response violates active closure rules")
        
        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations,
            confidence_score=1.0 if not violations else 0.3
        )
    
    def _validate_code(self, content: str) -> ValidationResult:
        """Validate code syntax and basic semantic correctness."""
        violations = []
        
        # Extract code blocks
        code_blocks = self._extract_code_blocks(content)
        
        for code_block in code_blocks:
            try:
                # Basic syntax validation
                ast.parse(code_block)
            except SyntaxError as e:
                violations.append(f"Syntax error in code: {str(e)}")
            
            # Check for dangerous operations
            if self._contains_dangerous_operations(code_block):
                violations.append("Code contains potentially dangerous operations")
        
        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations,
            confidence_score=1.0 if not violations else 0.4
        )
```

**Integration Points**:
- Used by all LLM clients for response validation
- Integrates with quantum state for constraint checking
- Connects to safety and security frameworks
- Provides feedback for prompt optimization

---

### File: `llm/retry.py` (70 LOC)

**Purpose**: Robust retry logic with exponential backoff for LLM API reliability.

**Core Functionality**:
- Exponential backoff with jitter
- Provider-specific error handling
- Circuit breaker pattern for failing providers
- Retry budget management
- Context-aware retry strategies

**Implementation Strategy**: Implements advanced retry patterns with quantum state consideration, provider failover, and intelligent error classification for optimal retry strategies.

---

### File: `llm/schemas.py` (120 LOC)

**Purpose**: Pydantic schemas for structured LLM data exchange with quantum integration.

**Core Functionality**:
- Request/Response data models
- Tool calling schemas
- Quantum context integration models
- Validation rules and constraints
- Serialization/deserialization support

**Implementation Strategy**: Comprehensive Pydantic models ensuring type safety and validation for all LLM interactions, with special consideration for quantum state data.

---

### File: `llm/prompt_registry.py` (100 LOC)

**Purpose**: Version-controlled registry for prompt management with integrity checking.

**Core Functionality**:
- Prompt versioning and checksumming
- Template parameter validation
- A/B testing support for prompt optimization
- Performance tracking per prompt version
- Automated prompt quality assessment

**Implementation Strategy**: Centralized prompt management system with version control, performance tracking, and automated optimization based on response quality and quantum compliance.

---

### File: `llm/response_parser.py` (80 LOC)

**Purpose**: Intelligent parsing and extraction from LLM responses with structured output support.

**Core Functionality**:
- JSON/YAML extraction from mixed content
- Code block extraction and validation
- Mathematical formula parsing
- Structured data extraction
- Content classification and routing

**Implementation Strategy**: Advanced parsing capabilities using regex patterns, AST analysis, and machine learning for intelligent content extraction and validation.

---

### File: `llm/tool_calls.py` (110 LOC)

**Purpose**: Function calling interface management with quantum-aware tool integration.

**Core Functionality**:
- Tool schema definition and validation
- Function call orchestration
- Parameter validation and sanitization
- Quantum context propagation to tools
- Result validation and integration

**Implementation Strategy**: Comprehensive function calling framework that integrates with QuantaCirc's agent system while maintaining quantum state awareness and formal verification requirements.

---

## 4. Integration Architecture

### Quantum State Integration
All LLM operations are integrated with QuantaCirc's quantum state representation, ensuring that AI-generated content aligns with the system's mathematical constraints and energy optimization goals.

### Agent Collaboration
The LLM layer provides a unified interface for all agents to leverage language models while maintaining the system's rigor classification and verification requirements.

### Cost & Performance Management
Comprehensive cost tracking, rate limiting, and performance monitoring ensure efficient and sustainable LLM usage across the entire system.

### Safety & Compliance
Multi-layered validation ensures all LLM outputs meet safety, security, and quantum compliance requirements before integration into the system state.

This LLM integration layer provides the foundation for QuantaCirc's agentic capabilities while maintaining the mathematical rigor and formal verification standards that define the system's approach to software engineering.
