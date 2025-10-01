import contextlib
from datetime import UTC, datetime
import json
import logging
import re
from typing import Any

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from src.domain.entities.conversation import Conversation
from src.domain.entities.extracted_data import ExtractedData
from src.domain.services.data_extraction_service import DataExtractionService
from src.domain.value_objects.order_number import OrderNumber
from src.domain.value_objects.problem_category import (
    ProblemCategory,
)
from src.domain.value_objects.urgency_level import UrgencyLevel
from src.infrastructure.cache.conversation_cache import ConversationCacheService
from src.shared.config.settings import settings

logger = logging.getLogger(__name__)


class ExtractedDataSchema(BaseModel):
    order_number: str | None = Field(None, description="Order number if found")
    problem_category: str | None = Field(
        None,
        description="Problem category: technical, billing, shipping, product, account, general",
    )
    problem_description: str | None = Field(
        None, description="Description of the problem"
    )
    urgency_level: str | None = Field(
        None, description="Urgency level: low, medium, high, critical"
    )
    confidence_score: float = Field(
        0.0, description="Confidence score between 0.0 and 1.0"
    )


class DataExtractionServiceImpl(DataExtractionService):
    def __init__(self, cache_service: ConversationCacheService | None = None) -> None:
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=0.1,  # Low temperature for consistent extraction
            api_key=settings.openai_api_key,  # type: ignore[arg-type]
        )
        self.cache_service = cache_service

    async def extract_data(self, conversation: Conversation) -> ExtractedData:
        # Prepare conversation text
        conversation_text = "\n".join(
            [f"{msg.sender}: {msg.content}" for msg in conversation.messages]
        )

        # Check cache first
        if self.cache_service:
            cached_data = await self.cache_service.get_cached_extraction_data(
                conversation_text
            )
            if cached_data:
                extracted_data = cached_data["extracted_data"]

                # Create value objects from cached data
                order_number = None
                if extracted_data.get("order_number"):
                    with contextlib.suppress(ValueError):
                        order_number = OrderNumber(extracted_data["order_number"])

                problem_category = None
                if extracted_data.get("problem_category"):
                    with contextlib.suppress(ValueError):
                        problem_category = ProblemCategory.from_string(
                            extracted_data["problem_category"]
                        )

                urgency_level = None
                if extracted_data.get("urgency_level"):
                    with contextlib.suppress(ValueError):
                        urgency_level = UrgencyLevel.from_string(
                            extracted_data["urgency_level"]
                        )

                return ExtractedData(
                    conversation_id=conversation.id,
                    order_number=order_number,
                    problem_category=problem_category,
                    problem_description=extracted_data.get("problem_description"),
                    urgency_level=urgency_level,
                    extracted_at=datetime.now(UTC),
                    confidence_score=extracted_data.get("confidence_score", 0.0),
                )

        # Create extraction prompt
        prompt = f"""
        Analyze this customer support conversation and extract structured information.
        
        CONVERSATION:
        {conversation_text}
        
        EXTRACTION REQUIREMENTS:
        1. ORDER NUMBER: Look for patterns like:
           - ORD123456, ORD789012 (most common)
           - order: ABC123, order-123, #123456
           - pedido: ABC123 (Spanish)
           - Any alphanumeric code that looks like an order reference
        
        2. PROBLEM CATEGORY: Choose from:
           - technical (bugs, errors, not working)
           - billing (payment, charges, refunds)
           - shipping (delivery, tracking, packages)
           - product (quality, defective items)
           - account (login, access issues)
           - general (questions, information)
        
        3. PROBLEM DESCRIPTION: Clear description of the issue
        
        4. URGENCY LEVEL: Choose from:
           - low (minor issues, no rush)
           - medium (normal priority)
           - high (important, needs attention soon)
           - critical (urgent, immediate attention needed)
        
        5. CONFIDENCE SCORE: 0.0 to 1.0 based on clarity of information
        
        IMPORTANT: If you find an order number like "ORD123456", extract it exactly as "ORD123456", not just "123456".
        
        RESPONSE FORMAT: Return ONLY a valid JSON object with this exact structure:
        {{
            "order_number": "ORD123456",
            "problem_category": "shipping",
            "problem_description": "The user's orders have not arrived",
            "urgency_level": "high",
            "confidence_score": 0.8
        }}
        
        If information is not found, use null for that field. Be conservative with confidence scores.
        """

        try:
            # Use structured output with Pydantic
            response = await self.llm.ainvoke(prompt)

            # Parse the response (in a real implementation, you'd use structured output)
            logger.info("DEBUG: LLM response content: %s", response.content)
            logger.info("DEBUG: Conversation text: %s", conversation_text)
            extracted_data = self._parse_extraction_response(
                str(response.content), conversation_text
            )
            logger.info("DEBUG: Parsed extracted_data: %s", extracted_data)

            # Create value objects
            order_number = None
            if extracted_data.get("order_number"):
                with contextlib.suppress(ValueError):
                    order_number = OrderNumber(extracted_data["order_number"])

            problem_category = None
            if extracted_data.get("problem_category"):
                with contextlib.suppress(ValueError):
                    problem_category = ProblemCategory.from_string(
                        extracted_data["problem_category"]
                    )

            urgency_level = None
            if extracted_data.get("urgency_level"):
                with contextlib.suppress(ValueError):
                    urgency_level = UrgencyLevel.from_string(
                        extracted_data["urgency_level"]
                    )

            result = ExtractedData(
                conversation_id=conversation.id,
                order_number=order_number,
                problem_category=problem_category,
                problem_description=extracted_data.get("problem_description"),
                urgency_level=urgency_level,
                extracted_at=datetime.now(UTC),
                confidence_score=extracted_data.get("confidence_score", 0.0),
            )

            # Cache the extracted data
            if self.cache_service:
                await self.cache_service.cache_extraction_data(
                    conversation_text, extracted_data
                )

        except Exception as e:
            # Return empty extracted data on error
            return ExtractedData(
                conversation_id=conversation.id,
                order_number=None,
                problem_category=None,
                problem_description=None,
                urgency_level=None,
                extracted_at=datetime.now(UTC),
                confidence_score=0.0,
                metadata={"error": str(e)},
            )
        else:
            return result

    async def validate_extracted_data(self, extracted_data: ExtractedData) -> bool:
        # Check if all required fields are present
        if not extracted_data.order_number:
            return False

        if not extracted_data.problem_category:
            return False

        if (
            not extracted_data.problem_description
            or not extracted_data.problem_description.strip()
        ):
            return False

        if not extracted_data.urgency_level:
            return False

        # Check confidence score
        return not extracted_data.confidence_score < 0.5

    async def get_extraction_confidence(self, extracted_data: ExtractedData) -> float:
        return extracted_data.confidence_score

    def _parse_extraction_response(
        self, response: str, conversation_text: str = ""
    ) -> dict[str, Any]:
        result = {
            "order_number": None,
            "problem_category": None,
            "problem_description": None,
            "urgency_level": None,
            "confidence_score": 0.0,
        }

        try:
            # Try to parse as JSON first

            # Clean the response - remove any markdown formatting
            clean_response = response.strip()
            clean_response = clean_response.removeprefix("```json")
            clean_response = clean_response.removesuffix("```")
            clean_response = clean_response.strip()

            # Parse JSON
            parsed_data = json.loads(clean_response)

            # Extract data from JSON
            result["order_number"] = parsed_data.get("order_number")
            result["problem_category"] = parsed_data.get("problem_category")
            result["problem_description"] = parsed_data.get("problem_description")
            result["urgency_level"] = parsed_data.get("urgency_level")
            result["confidence_score"] = parsed_data.get("confidence_score", 0.0)

            logger.info("DEBUG: Successfully parsed JSON response: %s", result)

        except json.JSONDecodeError as e:
            logger.warning("DEBUG: Failed to parse JSON response: %s", e)
            logger.warning("DEBUG: Raw response: %s", response)

            # Fallback to regex parsing if JSON fails
            result = self._fallback_regex_parsing(response, conversation_text)

        return result

    def _fallback_regex_parsing(
        self, response: str, conversation_text: str = ""
    ) -> dict[str, Any]:
        result: dict[str, Any] = {
            "order_number": None,
            "problem_category": None,
            "problem_description": None,
            "urgency_level": None,
            "confidence_score": 0.0,
        }

        # Extract order number from conversation text (not LLM response)
        text_to_search = conversation_text if conversation_text else response

        # Improved order number patterns - capture full order number
        order_patterns = [
            r"(ORD\d{6,})",  # ORD123456 - capture full number
            r"(order[:\s#-]*[A-Z0-9-]{3,20})",  # order: ABC123, order-123
            r"(#[A-Z0-9-]{3,20})",  # #ABC123
            r"(pedido[:\s]*[A-Z0-9-]{3,20})",  # pedido: ABC123 (Spanish)
            r"(order\s+[A-Z0-9-]{3,20})",  # order ABC123
            r"([A-Z]{2,4}\d{4,})",  # Generic pattern like ABC1234
        ]

        for pattern in order_patterns:
            match = re.search(pattern, text_to_search, re.IGNORECASE)
            if match:
                # Clean up the extracted order number
                order_num = match.group(1).strip()
                # Remove common prefixes/suffixes
                order_num = re.sub(
                    r"^(order[:\s#-]*|pedido[:\s]*|#)",
                    "",
                    order_num,
                    flags=re.IGNORECASE,
                )
                result["order_number"] = order_num
                break

        # Extract problem category
        category_keywords = {
            "technical": [
                "technical",
                "bug",
                "error",
                "crash",
                "not working",
                "broken",
            ],
            "billing": ["billing", "payment", "charge", "refund", "invoice", "cost"],
            "shipping": [
                "shipping",
                "delivery",
                "shipped",
                "tracking",
                "package",
                "pedido",
                "llegado",
            ],
            "product": ["product", "item", "quality", "defective", "damaged"],
            "account": ["account", "login", "password", "access", "profile"],
            "general": ["general", "question", "help", "information"],
        }

        response_lower = response.lower()
        for category, keywords in category_keywords.items():
            if any(keyword in response_lower for keyword in keywords):
                result["problem_category"] = category
                break

        # Extract problem description
        if "problem" in response_lower or "issue" in response_lower:
            # Simple extraction - take text after "problem" or "issue"
            desc_patterns = [
                r"problem[:\s]+(.+?)(?=\n|urgency|category|$)",
                r"issue[:\s]+(.+?)(?=\n|urgency|category|$)",
            ]
            for pattern in desc_patterns:
                match = re.search(pattern, response, re.IGNORECASE | re.DOTALL)
                if match:
                    result["problem_description"] = match.group(1).strip()
                    break

        # Extract urgency level
        urgency_keywords = {
            "critical": [
                "critical",
                "urgent",
                "emergency",
                "asap",
                "immediately",
                "urgente",
            ],
            "high": ["high", "important", "soon", "quickly", "alta"],
            "medium": ["medium", "moderate", "normal", "media"],
            "low": ["low", "minor", "when possible", "low priority", "baja"],
        }

        for urgency, keywords in urgency_keywords.items():
            if any(keyword in response_lower for keyword in keywords):
                result["urgency_level"] = urgency
                break

        # Calculate confidence score based on extracted fields
        confidence = 0.0
        if result["order_number"]:
            confidence += 0.3
        if result["problem_category"]:
            confidence += 0.3
        if result["problem_description"]:
            confidence += 0.2
        if result["urgency_level"]:
            confidence += 0.2

        result["confidence_score"] = confidence

        logger.info("DEBUG: Fallback regex parsing result: %s", result)
        return result
