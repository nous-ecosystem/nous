from dependency_injector import containers, providers
from services.llm.manager import LLMManager
from services.llm.providers.openai import OpenAIProvider
from services.llm.providers.cohere import CohereProvider
from services.llm.providers.groq import GroqProvider
from core.config import Config
from utils.logging import LoggerResolver
from services.database import DatabaseService


class Container(containers.DeclarativeContainer):
    """Application container."""

    config = providers.Singleton(Config)

    # Initialize logger first
    _ = providers.Resource(
        LoggerResolver.get_logger,
        log_level=config.provided.logging.level,
        log_dir=config.provided.logging.directory,
    )

    # LLM Providers
    openai_provider = providers.Singleton(
        OpenAIProvider,
        api_key=config.openai.api_key,
    )

    cohere_provider = providers.Singleton(
        CohereProvider,
        api_key=config.cohere.api_key,
    )

    groq_provider = providers.Singleton(
        GroqProvider,
        api_key=config.groq.api_key,
    )

    # Main LLM Manager
    main_llm = providers.Singleton(
        LLMManager,
        name="default",
    )

    # Initialize providers in the manager
    main_llm.provided.register_provider.call_with(
        name="openai", provider=openai_provider
    )
    main_llm.provided.register_provider.call_with(
        name="cohere", provider=cohere_provider
    )
    main_llm.provided.register_provider.call_with(name="groq", provider=groq_provider)

    # Database service
    database = providers.Singleton(
        DatabaseService,
        db_url=f"mysql+aiomysql://{config.provided.database.user}:"
        f"{config.provided.database.password}@{config.provided.database.host}:"
        f"{config.provided.database.port}/{config.provided.database.name}",
        redis_url=f"redis://{config.provided.redis.host}:{config.provided.redis.port}",
    )
