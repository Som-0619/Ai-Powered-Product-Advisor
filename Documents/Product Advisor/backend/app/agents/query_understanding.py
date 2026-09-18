"""Query Understanding Agent implementing LangGraph-compatible node design.

Extracts structured intent, constraints, technical specs, budget, and language from
English and Hinglish queries using ModelGateway (Qwen 4B).
"""

import re
import uuid
from typing import Any, Dict, Optional, Union

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from app.core.logging import logger
from app.schemas.query_analysis import (
    QueryAnalysis,
    QueryUnderstandingState,
    normalize_hinglish_shorthand,
)
from app.services.factory import get_model_gateway
from app.services.model_gateway import ModelGateway

SYSTEM_PROMPT = """You are the expert Query Understanding Agent for Product Advisor, an intelligent platform for consumer electronics (laptops, phones, audio) and electronic components (microcontrollers, sensors, relays, ICs).

Your task is to analyze user search queries in either English or Hinglish (Hindi written in English script) and extract structured intent, technical specifications, budget, and ambiguity.

Follow these strict extraction guidelines:
1. Category & Subcategory:
   - Accurately determine broad category (e.g. "Laptop", "Sensor", "Microcontroller", "Module", "Smartphone").
   - Extract specific subcategory if present (e.g. "Gaming Laptop", "Temperature Sensor", "Relay Module", "Development Board").
2. Budget & Currency:
   - Parse budget limits into numeric floats (e.g. "50k" or "50000" -> budget_max=50000.0, "under 80000" -> budget_max=80000.0).
   - For Indian colloquial queries ("50k", "80000", "rupees", "andar"), currency is "INR".
3. Use Case:
   - Capture intended workload (e.g. "Machine Learning / ML", "Gaming", "ESP32 IoT project", "Arduino automation").
4. Constraints:
   - hard_constraints: Strict specifications (e.g. "under 80000", "50k budget", "3.3V operating voltage", "5V logic", "Arduino compatible", "ESP32 compatible").
   - soft_preferences: Subjective wants (e.g. "best performance", "good battery", "lightweight").
   - brand_preferences / brand_exclusions: Mentioned brands.
5. Language:
   - Identify "en" for English, or "hinglish" for Hindi-English mix (e.g. "bhai", "chahiye", "ke andar", "ke liye", "kuch accha").
6. Ambiguity & Clarification:
   - When specific criteria are provided (e.g., specific category with budget or use case or voltage like 'best laptop under 80000 for ML', 'bhai 50k ke andar gaming laptop chahiye', 'ESP32 ke liye 3.3V temperature sensor chahiye', '5V relay module for Arduino'), the query is NOT ambiguous. You MUST set ambiguity=false and clarification_question=null.
   - Set ambiguity=true ONLY if the query is too vague, generic, or underspecified to begin searching (e.g. 'laptop', 'sensor', 'kuch accha dikhao', 'show me something good'). In that case, return exactly ONE helpful clarification question in clarification_question.

Return the result conforming strictly to the requested schema.
"""


class QueryUnderstandingAgent:
    """Agent responsible for parsing, understanding, and validating user queries."""

    def __init__(self, model_gateway: Optional[ModelGateway] = None):
        self._gateway = model_gateway or get_model_gateway()

    def _detect_language(self, text: str) -> str:
        """Detect whether text is predominantly English or Hinglish."""
        hinglish_markers = [
            r"\bchahiye\b", r"\bbhai\b", r"\bkuch\b", r"\baccha\b", r"\bacchi\b",
            r"\bandar\b", r"\bke liye\b", r"\bkaunsa\b", r"\bbatao\b", r"\bmera\b",
            r"\bmeri\b", r"\bmujhe\b", r"\bya\b", r"\bwala\b", r"\bwali\b", r"\bkaise\b",
        ]
        text_lower = text.lower()
        if any(re.search(pattern, text_lower) for pattern in hinglish_markers):
            return "hinglish"
        return "en"

    def _extract_heuristic_budget(self, text: str) -> Optional[float]:
        """Heuristic backup for budget extraction from Indian and international notation, including word numbers."""
        text_clean = text.strip()
        text_lower = text.lower()

        # Word-to-number mapping for English & Hinglish
        number_words = {
            "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
            "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
            "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
            "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
            "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
            # Hindi/Hinglish
            "ek": 1, "do": 2, "teen": 3, "chaar": 4, "char": 4, "paanch": 5, "panch": 5,
            "chhe": 6, "che": 6, "saat": 7, "aath": 8, "nau": 9, "das": 10,
            "gyarah": 11, "barah": 12, "terah": 13, "chaudah": 14, "pandrah": 15,
            "solah": 16, "satrah": 17, "atharah": 18, "unnis": 19, "bees": 20,
            "tees": 30, "chalis": 40, "chaalis": 40, "pachas": 50, "pachaas": 50,
            "saath": 60, "sattar": 70, "assi": 80, "nabbe": 90, "sau": 100,
        }

        multipliers = {
            "hundred": 100, "sau": 100,
            "thousand": 1000, "hazar": 1000, "hazaar": 1000, "k": 1000,
            "lakh": 100000, "lakhs": 100000, "lac": 100000, "lacs": 100000,
            "million": 1000000, "crore": 10000000, "cr": 10000000,
        }

        # 1. Numeric with explicit lakh/thousand multipliers (e.g., '1.5 lakh', '1 lakh', '70 thousand')
        num_mult_match = re.search(r"(\d+(?:\.\d+)?)\s*(lakhs?|lacs?|crores?|cr|thousand|hazar|hazaar|k)\b", text_lower)
        if num_mult_match:
            val = float(num_mult_match.group(1))
            mult = multipliers.get(num_mult_match.group(2), 1)
            return val * mult

        # 2. Spoken number words with multipliers (e.g., 'one lakh', 'seventy thousand', 'pachas hazar', 'two thousand')
        word_mult_match = re.search(r"\b([a-z]+(?:\s+[a-z]+)?)\s+(lakhs?|lacs?|crores?|cr|thousand|hazar|hazaar|k)\b", text_lower)
        if word_mult_match:
            base_words = word_mult_match.group(1).split()
            mult = multipliers.get(word_mult_match.group(2), 1)
            total = 0
            for w in base_words:
                if w in number_words:
                    total += number_words[w]
            if total > 0:
                return float(total * mult)

        # 3. Dollar amounts (e.g. 'under 10 dollars', '$50', 'under $500')
        dollar_match = re.search(r"(?:under|below|around|budget|upto|up to|max|\$)\s*[:=]?\s*(?:\$)?\s*(\d+(?:\.\d+)?)\s*(?:dollars?|usd)?\b", text_clean, re.IGNORECASE)
        if any(w in text_lower for w in ["dollar", "usd", "$"]) and dollar_match:
            val = float(dollar_match.group(1))
            if "k" in dollar_match.group(0).lower():
                val *= 1000
            return val

        # 4. Negation / upper bound: "no ... above 50000", "not above 50000", "not more than 50000"
        neg_match = re.search(r"(?:no\s+\w+\s+above|not\s+above|not\s+more\s+than|less\s+than|below|under|max|upto|up to)\s*[:=]?\s*[₹]?(?:rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*k?\b", text_clean, re.IGNORECASE)
        if neg_match:
            val = float(neg_match.group(1))
            if "k" in neg_match.group(0).lower() or val < 500:
                val *= 1000
            return val

        # 5. Rupee symbol: ₹50000, ₹80000
        rupee_match = re.search(r"[₹]\s*(\d+(?:\.\d+)?)\s*k?\b", text_clean)
        if rupee_match:
            val = float(rupee_match.group(1))
            if "k" in rupee_match.group(0).lower() or val < 500:
                val *= 1000
            return val

        # 6. Match Indian 'under 80000', '50k ke andar', '<= 50000'
        match = re.search(r"(?:under|below|around|andar|budget|upto|up to|max)\s*[:=]?\s*(?:rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*k?\b", text_clean, re.IGNORECASE)
        if match:
            val = float(match.group(1))
            if "k" in match.group(0).lower() or val < 500:
                val *= 1000
            return val
        
        # 7. Standalone e.g. "50k" or "80000"
        match_k = re.search(r"\b(\d+(?:\.\d+)?)\s*k\b", text_clean, re.IGNORECASE)
        if match_k:
            return float(match_k.group(1)) * 1000
        
        match_num = re.search(r"\b([1-9]\d{4,6})\b", text_clean)
        if match_num:
            return float(match_num.group(1))
            
        return None

    @staticmethod
    def _contains_currency_hint(text: str) -> bool:
        return bool(re.search(r"[₹]|(?:rs\.?|inr|rupees?|lakh|lac)\b|\b\d+(?:\.\d+)?\s*[kl]\b|\b(?:andar|ke andar)\b", text, re.IGNORECASE))

    @staticmethod
    def _append_constraint(analysis: QueryAnalysis, constraint: str) -> None:
        if not any(existing.lower() == constraint.lower() for existing in analysis.hard_constraints):
            analysis.hard_constraints.append(constraint)

    def _preserve_explicit_technical_constraints(
        self, analysis: QueryAnalysis, raw_query: str
    ) -> None:
        """Retain literal electrical/platform requirements if a small model omits them."""
        for voltage in re.findall(r"\b\d+(?:\.\d+)?\s*[vV]\b", raw_query):
            self._append_constraint(analysis, voltage.replace(" ", ""))
        for platform in ("ESP32", "Arduino", "Raspberry Pi", "I2C", "SPI", "UART"):
            if re.search(rf"\b{re.escape(platform)}\b", raw_query, re.IGNORECASE):
                self._append_constraint(analysis, platform)

    def _is_obviously_vague(self, text: str) -> bool:
        """Detect obvious single-word or generic queries requiring clarification."""
        clean = text.strip().lower()
        clean = re.sub(r"[^\w\s]", "", clean)
        words = clean.split()
        if not words:
            return True
        if len(words) <= 1 and words[0] in ("laptop", "phone", "sensor", "component", "parts", "chahiye"):
            return True
        if clean in (
            "kuch accha dikhao",
            "show me something good",
            "best products",
            "best laptop",
            "best sensor",
            "which component is compatible with this board",
            "which component is compatible with this board?",
            "is this compatible",
            "compatible with this board",
        ):
            return True
        return False

    async def analyze_query(
        self,
        raw_query: str,
        request_id: Optional[str] = None,
    ) -> QueryAnalysis:
        """Analyze raw query and extract structured QueryAnalysis via ModelGateway."""
        req_id = request_id or str(uuid.uuid4())
        normalized_text = normalize_hinglish_shorthand(raw_query)
        detected_lang = self._detect_language(raw_query)

        # Handle trivial vague queries immediately if obvious
        if self._is_obviously_vague(raw_query):
            if "board" in raw_query.lower() or "compatible" in raw_query.lower():
                clarification = "Could you specify which board or microcontroller model (such as ESP32, Arduino Uno, or Raspberry Pi) you are working with?"
            else:
                clarification = (
                    "Aapka budget kitna hai aur aap isse kis specific use case (jaise gaming, programming, ya general use) ke liye lena chahte hain?"
                    if detected_lang == "hinglish"
                    else "What is your approximate budget and primary use case for this product?"
                )
            return QueryAnalysis(
                language=detected_lang,
                ambiguity=True,
                clarification_question=clarification,
            )

        prompt = (
            f"Analyze this user query:\n"
            f"Raw query: \"{raw_query}\"\n"
            f"Preprocessed query: \"{normalized_text}\"\n"
            f"Detected dialect: {detected_lang}\n\n"
            f"Extract all constraints, budget limits, category, use cases, and ambiguity into the schema."
        )

        try:
            res = await self._gateway.generate_structured(
                prompt=prompt,
                schema=QueryAnalysis,
                system_prompt=SYSTEM_PROMPT,
                temperature=0.1,
                request_id=req_id,
            )
            analysis: QueryAnalysis = res.content

            # Post-validate and enrich language if missed
            if analysis.language == "en":
                analysis.language = detected_lang

            # Post-validate budget with heuristic fallback if model missed it
            if any(w in raw_query.lower() for w in ["dollar", "usd", "$"]):
                analysis.currency = "USD"
                heur_usd = self._extract_heuristic_budget(raw_query)
                if heur_usd is not None:
                    analysis.budget_max = heur_usd
            elif self._contains_currency_hint(raw_query):
                analysis.currency = "INR"
                heur_inr = self._extract_heuristic_budget(raw_query)
                if heur_inr is not None:
                    analysis.budget_max = heur_inr
            elif analysis.budget_max is None:
                heur_budget = self._extract_heuristic_budget(raw_query)
                if heur_budget is not None:
                    analysis.budget_max = heur_budget
                    analysis.currency = "INR" if self._contains_currency_hint(raw_query) else analysis.currency

            # Post-validate currency default for Indian queries
            if (analysis.budget_max is not None or analysis.budget_min is not None) and not analysis.currency:
                analysis.currency = "INR" if self._contains_currency_hint(raw_query) else "USD"

            self._preserve_explicit_technical_constraints(analysis, raw_query)

            # If the user provided specific criteria (category with budget, use case, or constraints), it is not ambiguous
            has_specific_specs = bool(
                analysis.category
                and (
                    analysis.budget_max is not None
                    or analysis.use_case
                    or len(analysis.hard_constraints) > 0
                    or analysis.subcategory
                )
            )
            if has_specific_specs:
                analysis.ambiguity = False
                analysis.clarification_question = None

            # Ensure clarification question exists if ambiguity is flagged
            if analysis.ambiguity and not analysis.clarification_question:
                analysis.clarification_question = (
                    "Could you specify your target budget and intended use case?"
                )


            logger.info(
                "Query analysis completed successfully",
                extra={
                    "request_id": req_id,
                    "category": analysis.category,
                    "budget_max": analysis.budget_max,
                    "ambiguity": analysis.ambiguity,
                    "language": analysis.language,
                },
            )
            return analysis

        except Exception as exc:
            logger.error(f"Error during query analysis: {exc}", extra={"request_id": req_id, "query": raw_query})
            # Graceful intelligent fallback when LLM gateway is offline
            heur_budget = self._extract_heuristic_budget(raw_query)
            q_lower = raw_query.lower()

            # Extract category & subcategory heuristically
            category = None
            subcategory = None
            use_case = None

            # Check Audio & Headphones first to prevent 'headphone' / 'earphone' matching 'phone'
            if any(w in q_lower for w in ["headphone", "headphones", "earphone", "earphones", "earbud", "earbuds", "headset", "airpod", "airpods", "audio", "boat", "bose", "rockerz", "sound", "jbl", "sennheiser"]):
                category = "Audio & Headphones"
                subcategory = "Noise-Cancelling Headphones"
                use_case = "Music & Media"
            elif bool(re.search(r"\b(phone|phones|smartphone|smartphones|mobile|mobiles|iphone|galaxy|pixel|oneplus|redmi|android)\b", q_lower)):
                category = "Smartphones"
                if any(w in q_lower for w in ["camera", "photo", "photography"]):
                    subcategory = "Camera Phones"
                    use_case = "Photography & Content Creation"
                elif any(w in q_lower for w in ["gaming", "game", "bgmi", "fps"]):
                    subcategory = "Gaming Phones"
                    use_case = "Mobile Gaming & High Performance"
                else:
                    subcategory = "All-Round Smartphones"
                    use_case = "Daily Driver & Media"
            elif any(w in q_lower for w in ["laptop", "laptops", "notebook", "notebooks", "macbook", "tuf", "legion", "vivobook", "victus", "nitro", "thinkpad", "xps", "gaming laptop", "ultrabook"]):
                category = "Laptops & Ultrabooks"
                if "gaming" in q_lower or "tuf" in q_lower or "rtx" in q_lower:
                    subcategory = "Gaming Laptops"
                    use_case = "Gaming & High Performance"
                elif any(w in q_lower for w in ["code", "coding", "programming", "ml", "dev"]):
                    subcategory = "Development & ML"
                    use_case = "Coding & Machine Learning"
                else:
                    subcategory = "All-Round Ultrabooks"
                    use_case = "Productivity & Multitasking"
            elif any(w in q_lower for w in ["esp32", "arduino", "mcu", "microcontroller", "pico", "raspberry", "pi 4", "rp2040"]):
                category = "Microcontrollers & SOCs"
                subcategory = "Development Boards"
                use_case = "IoT & Embedded Systems"
            elif any(w in q_lower for w in ["relay", "sensor", "shifter", "bme280", "capacitor", "ic", "module", "electronics", "electronic", "iot"]):
                category = "Electronic Components & Modules"
                subcategory = "Sensors & Actuators"
                use_case = "Electronics Prototyping"
            else:
                category = "Laptops & Ultrabooks"
                subcategory = "Consumer Tech"
                use_case = "General Use"

            # Ambiguity: only True if query has essentially no substantive words
            words = [w for w in re.findall(r"\w+", raw_query) if len(w) > 1]
            is_ambiguous = len(words) <= 1 and heur_budget is None and category == "Consumer Tech"

            return QueryAnalysis(
                category=category,
                subcategory=subcategory,
                use_case=use_case,
                budget_max=heur_budget,
                currency="INR" if (heur_budget or detected_lang == "hinglish") else "INR",
                language=detected_lang,
                ambiguity=is_ambiguous,
                clarification_question="What product category, budget, and use case do you have in mind?" if is_ambiguous else None,
            )


async def query_understanding_node(
    state: Union[QueryUnderstandingState, Dict[str, Any]],
    model_gateway: Optional[ModelGateway] = None,
) -> Dict[str, Any]:
    """LangGraph node function executing Query Understanding."""
    if isinstance(state, dict):
        raw_query = state.get("raw_query", "")
        req_id = state.get("request_id")
    else:
        raw_query = state.raw_query
        req_id = state.request_id

    agent = QueryUnderstandingAgent(model_gateway=model_gateway)
    analysis = await agent.analyze_query(raw_query=raw_query, request_id=req_id)

    return {
        "raw_query": raw_query,
        "parsed_query": analysis,
        "clarification_question": analysis.clarification_question if analysis.ambiguity else None,
        "error": None,
        "request_id": req_id,
        "metadata": {
            "ambiguity": analysis.ambiguity,
            "category": analysis.category,
            "language": analysis.language,
        },
    }


def build_query_understanding_graph(
    model_gateway: Optional[ModelGateway] = None,
) -> CompiledStateGraph:
    """Construct and compile a LangGraph workflow containing the query understanding node."""
    workflow = StateGraph(QueryUnderstandingState)

    async def _node_wrapper(state: QueryUnderstandingState) -> Dict[str, Any]:
        return await query_understanding_node(state, model_gateway=model_gateway)

    workflow.add_node("query_understanding", _node_wrapper)
    workflow.add_edge(START, "query_understanding")
    workflow.add_edge("query_understanding", END)

    return workflow.compile()
