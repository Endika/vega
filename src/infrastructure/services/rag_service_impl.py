from typing import Any

from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from src.domain.entities.conversation import Conversation
from src.domain.services.rag_service import RAGService
from src.infrastructure.cache.conversation_cache import ConversationCacheService
from src.shared.config.settings import settings


class RAGServiceImpl(RAGService):
    def __init__(self, cache_service: ConversationCacheService | None = None) -> None:
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=0.7,
            api_key=settings.openai_api_key,  # type: ignore[arg-type]
        )

        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            api_key=settings.openai_api_key,  # type: ignore[arg-type]
        )

        # Initialize vector store
        self.vector_store = Chroma(
            persist_directory=settings.knowledge_base_path,
            embedding_function=self.embeddings,
        )

        # Initialize LangGraph
        self.memory = MemorySaver()
        self.graph = self._build_graph()

        # Initialize cache service
        self.cache_service = cache_service

    def _build_graph(self) -> StateGraph:
        def retrieve_documents(state: dict[str, Any]) -> dict[str, Any]:
            query = state["query"]
            docs = self.vector_store.similarity_search(query, k=5)
            state["retrieved_docs"] = docs
            return state

        def generate_response(state: dict[str, Any]) -> dict[str, Any]:
            query = state["query"]
            docs = state["retrieved_docs"]
            conversation_history = state.get("conversation_history", [])

            # Build context from retrieved documents
            context = "\n".join([doc.page_content for doc in docs])

            # Build conversation history
            history_text = ""
            for msg in conversation_history[-10:]:  # Last 10 messages
                history_text += f"{msg['sender']}: {msg['content']}\n"

            # Create prompt
            prompt = f"""
            You are a helpful customer support assistant. Use the following context to answer the user's question.
            
            Context:
            {context}
            
            Conversation History:
            {history_text}
            
            User Question: {query}
            
            Please provide a helpful, accurate, and friendly response. If you need more information, ask clarifying questions.
            """

            response = self.llm.invoke(prompt)
            state["response"] = response.content
            return state

        # Build the graph
        workflow = StateGraph(dict)  # type: ignore[type-var]
        workflow.add_node("retrieve", retrieve_documents)  # type: ignore[type-var]
        workflow.add_node("generate", generate_response)  # type: ignore[type-var]

        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)

        return workflow.compile(checkpointer=self.memory)  # type: ignore[return-value]

    async def generate_response(
        self, conversation: Conversation, user_message: str
    ) -> str:
        # Check cache first
        if self.cache_service:
            cached_response = await self.cache_service.get_cached_rag_response(
                user_message
            )
            if cached_response:
                return str(cached_response["response"])

        # Prepare conversation history
        conversation_history = [
            {
                "sender": msg.sender,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
            }
            for msg in conversation.messages[-10:]  # Last 10 messages
        ]

        # Run the graph
        result = await self.graph.ainvoke(  # type: ignore[attr-defined]
            {"query": user_message, "conversation_history": conversation_history},
            config={"configurable": {"thread_id": "default"}},
        )

        response = result["response"]

        # Cache the response
        if self.cache_service:
            await self.cache_service.cache_rag_response(user_message, response, {})

        return str(response)

    async def generate_summary(self, conversation: Conversation) -> dict[str, Any]:
        # Prepare conversation text
        conversation_text = "\n".join(
            [f"{msg.sender}: {msg.content}" for msg in conversation.messages]
        )

        # Create summary prompt
        prompt = f"""
        Please provide a comprehensive summary of the following customer support conversation:
        
        {conversation_text}
        
        The summary should include:
        1. The main issue or problem discussed
        2. Key points and details mentioned
        3. Any solutions or next steps discussed
        4. The overall tone and sentiment of the conversation
        
        Please provide a clear, concise summary that captures the essence of the conversation.
        """

        response = await self.llm.ainvoke(prompt)

        return {
            "summary": response.content,
            "conversation_length": len(conversation.messages),
            "duration_minutes": self._calculate_duration(conversation),
        }

    async def extract_key_points(self, conversation: Conversation) -> list[str]:
        # Prepare conversation text
        conversation_text = "\n".join(
            [f"{msg.sender}: {msg.content}" for msg in conversation.messages]
        )

        # Create key points extraction prompt
        prompt = f"""
        Extract the key points from the following customer support conversation:
        
        {conversation_text}
        
        Please provide a list of 3-5 key points that summarize the most important aspects of this conversation.
        Each point should be a single, clear sentence.
        """

        response = await self.llm.ainvoke(prompt)

        # Parse response into list
        key_points = [
            point.strip()
            for point in str(response.content).split("\n")
            if point.strip()
        ]
        return key_points[:5]  # Limit to 5 key points

    async def search_knowledge_base(self, query: str) -> list[dict[str, Any]]:
        docs = self.vector_store.similarity_search_with_score(query, k=5)

        return [
            {"content": doc.page_content, "metadata": doc.metadata, "score": score}
            for doc, score in docs
        ]

    def _calculate_duration(self, conversation: Conversation) -> float:
        if not conversation.messages:
            return 0.0

        first_message = conversation.messages[0]
        last_message = conversation.messages[-1]

        duration = last_message.timestamp - first_message.timestamp
        return duration.total_seconds() / 60.0
