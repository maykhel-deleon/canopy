import os
from abc import ABC, abstractmethod
from typing import List, Optional

from canopy.context_engine.context_builder import StuffingContextBuilder
from canopy.context_engine.context_builder.base import ContextBuilder
from canopy.knowledge_base import KnowledgeBase
from canopy.knowledge_base.base import BaseKnowledgeBase
from canopy.models.data_models import Context, Query
from canopy.utils.config import ConfigurableMixin

CE_DEBUG_INFO = os.getenv("CE_DEBUG_INFO", "FALSE").lower() == "true"


class BaseContextEngine(ABC, ConfigurableMixin):

    @abstractmethod
    def query(self, queries: List[Query], max_context_tokens: int, ) -> Context:
        pass

    @abstractmethod
    async def aquery(self, queries: List[Query], max_context_tokens: int, ) -> Context:
        pass


class ContextEngine(BaseContextEngine):

    _DEFAULT_COMPONENTS = {
        'knowledge_base': KnowledgeBase,
        'context_builder': StuffingContextBuilder,
    }

    def __init__(self,
                 knowledge_base: BaseKnowledgeBase,
                 *,
                 context_builder: Optional[ContextBuilder] = None,
                 global_metadata_filter: Optional[dict] = None
                 ):

        if not isinstance(knowledge_base, BaseKnowledgeBase):
            raise TypeError("knowledge_base must be an instance of BaseKnowledgeBase, "
                            f"not {type(self.knowledge_base)}")
        self.knowledge_base = knowledge_base

        if context_builder:
            if not isinstance(context_builder, ContextBuilder):
                raise TypeError(
                    "context_builder must be an instance of ContextBuilder, "
                    f"not {type(context_builder)}"
                )
            self.context_builder = context_builder
        else:
            self.context_builder = self._DEFAULT_COMPONENTS['context_builder']()

        self.global_metadata_filter = global_metadata_filter

    def query(self, queries: List[Query], max_context_tokens: int, ) -> Context:
        query_results = self.knowledge_base.query(
            queries,
            global_metadata_filter=self.global_metadata_filter)
        context = self.context_builder.build(query_results, max_context_tokens)

        if CE_DEBUG_INFO:
            context.debug_info["query_results"] = [qr.dict() for qr in query_results]
        return context

    async def aquery(self, queries: List[Query], max_context_tokens: int, ) -> Context:
        raise NotImplementedError()