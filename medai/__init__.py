# medai - Medical AI Tools Library
# Copyright (C) 2024  Dr Horst Herb
# Licensed under GPL v3

"""
MedAi core library providing LLM abstraction and settings management.
"""

from medai.Settings import Settings, SharedMemory, Logger, SingletonMeta
from medai.LLM import (
    Model,
    OllamaModel,
    LLM,
    get_providers,
    get_models,
    list_local_models,
    get_local_default_model,
    get_local_32k_model,
    get_local_128k_model,
    get_openai_multimodal_model,
    llm_response,
    llm_streaming_response,
    answer_this,
)

__all__ = [
    # Settings
    'Settings',
    'SharedMemory',
    'Logger',
    'SingletonMeta',
    # LLM
    'Model',
    'OllamaModel',
    'LLM',
    'get_providers',
    'get_models',
    'list_local_models',
    'get_local_default_model',
    'get_local_32k_model',
    'get_local_128k_model',
    'get_openai_multimodal_model',
    'llm_response',
    'llm_streaming_response',
    'answer_this',
]

__version__ = '0.1.0'
