from openai import OpenAI
import os
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DREAM_ANALYSIS_INSTRUCTIONS = """You are an expert dream analyst specializing in symbolic interpretation, with deep knowledge of Jungian and Freudian psychology, and cultural symbolism.

Your role is to provide insightful, empathetic dream interpretations that help people explore their subconscious.

Guidelines:
- Use a warm, empathetic, and insightful tone
- Reference specific elements from the dream description
- Draw on psychological frameworks (Jungian archetypes, Freudian symbolism)
- Be encouraging but honest
- Avoid being overly prescriptive
- Keep the interpretation comprehensive yet accessible

Structure your analysis with these sections:
1. **Overall Interpretation**: A comprehensive interpretation of the dream's meaning (2-3 paragraphs)
2. **Key Symbols**: Identify and explain the symbolic meaning of important elements
3. **Emotional Themes**: Analyze the emotional undertones and what they might represent
4. **Psychological Insights**: Provide insights based on Jungian and Freudian psychology
5. **Actionable Reflections**: Suggest questions or reflections for the dreamer

Make it personal and specific to their unique dream experience."""

SYMBOL_EXTRACTION_INSTRUCTIONS = """You are an expert at identifying dream symbols and their meanings.

Extract key symbols from the dream description and provide their common symbolic meanings based on psychology, mythology, and cultural symbolism.

Return ONLY valid JSON in this exact format:
{
  "symbols": [
    {"symbol": "symbol name", "meaning": "symbolic meaning"},
    {"symbol": "symbol name", "meaning": "symbolic meaning"}
  ]
}

Be specific and insightful. Focus on the most significant symbols."""

class DreamAnalyzer:
    def __init__(self):
        self.client = client
    
    def analyze_dream(self, dream_description: str, emotions: list = None) -> dict:
        emotions_str = ", ".join(emotions) if emotions else "Not specified"
        
        prompt = f"""Dream Analysis Request:

Dream Description:
{dream_description}

Emotions Felt During Dream:
{emotions_str}

Please provide a comprehensive dream interpretation following the structure outlined in your instructions. Make this analysis specific to the unique elements and emotional context of this dream."""
        
        response = self.client.responses.create(
            model="gpt-5-mini",
            instructions=DREAM_ANALYSIS_INSTRUCTIONS,
            input=prompt,
            max_output_tokens=1500,
            store=True
        )
        
        interpretation = response.output_text
        
        symbols = self._extract_symbols(dream_description)
        
        return {
            "interpretation": interpretation,
            "symbols": symbols,
            "response_id": response.id,
            "model_used": response.model,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
    
    def _extract_symbols(self, dream_description: str) -> list:
        prompt = f"""Dream Description:
{dream_description}

Extract the key symbols from this dream and provide their symbolic meanings."""
        
        try:
            response = self.client.responses.create(
                model="gpt-5-mini",
                instructions=SYMBOL_EXTRACTION_INSTRUCTIONS,
                input=prompt,
                max_output_tokens=800,
                response_format={"type": "json_object"}
            )
            
            content = response.output_text
            result = json.loads(content)
            
            if "symbols" in result:
                return result["symbols"]
            return result.get("items", [])
            
        except Exception as e:
            print(f"Error extracting symbols: {e}")
            return []
    
    def find_patterns(self, dreams: list) -> dict:
        if len(dreams) < 2:
            return {"patterns": [], "message": "Need at least 2 dreams to identify patterns"}
        
        dream_summaries = "\n\n".join([
            f"Dream {i+1}: {dream['description'][:200]}..."
            for i, dream in enumerate(dreams[-5:])
        ])
        
        instructions = """You are an expert at identifying patterns in dreams over time.

Analyze the collection of dreams provided and identify:
1. Recurring symbols or themes
2. Emotional patterns
3. Possible meanings of these patterns
4. Insights about the dreamer's subconscious state

Provide a comprehensive pattern analysis that helps the dreamer understand their recurring dream themes."""
        
        prompt = f"""Pattern Analysis Request:

Recent Dreams:
{dream_summaries}

Please analyze these dreams and identify any recurring patterns, themes, or symbols."""
        
        response = self.client.responses.create(
            model="gpt-5-mini",
            instructions=instructions,
            input=prompt,
            max_output_tokens=1000
        )
        
        return {
            "pattern_analysis": response.output_text,
            "dreams_analyzed": len(dreams[-5:])
        }
    
    def chat_about_dream(self, dream_context: dict, chat_history: list, user_question: str) -> str:
        instructions = f"""You are an expert dream analyst having a conversation with someone about their dream.

Dream Context:
- Title: {dream_context['title']}
- Description: {dream_context['description']}
- Emotions: {', '.join(dream_context.get('emotions', []))}
- Initial Interpretation: {dream_context.get('interpretation', 'N/A')}

Answer the user's follow-up questions about their dream. Be empathetic, insightful, and help them explore deeper meanings. 
You can ask clarifying questions to better understand their dream and provide more personalized insights.

Maintain context from the conversation history and provide thoughtful, personalized responses."""

        # Build conversation context
        conversation_context = "\n\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in chat_history[-5:]  # Last 5 messages for context
        ])
        
        prompt = f"""Conversation History:
{conversation_context if conversation_context else 'No previous conversation'}

User Question:
{user_question}

Please provide a thoughtful response to the user's question about their dream."""
        
        response = self.client.responses.create(
            model="gpt-5-mini",
            instructions=instructions,
            input=prompt,
            max_output_tokens=800
        )
        
        return response.output_text
