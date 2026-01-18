from openai import OpenAI
import os
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DREAM_ANALYSIS_PROMPT = """You are an expert dream analyst specializing in symbolic interpretation. 
Analyze the following dream and provide:

1. **Overall Interpretation**: A comprehensive interpretation of the dream's meaning
2. **Key Symbols**: Identify and explain the symbolic meaning of important elements
3. **Emotional Themes**: Analyze the emotional undertones and what they might represent
4. **Psychological Insights**: Provide insights based on Jungian and Freudian psychology
5. **Actionable Reflections**: Suggest questions or reflections for the dreamer

Be empathetic, insightful, and avoid being overly prescriptive. Focus on helping the dreamer explore their subconscious.

Dream Description: {dream_description}
Emotions Felt: {emotions}
"""

SYMBOL_EXTRACTION_PROMPT = """Extract key symbols from this dream description and provide their common symbolic meanings.
Return a JSON array of objects with 'symbol' and 'meaning' fields.

Dream: {dream_description}
"""

class DreamAnalyzer:
    def __init__(self):
        self.client = client
    
    def analyze_dream(self, dream_description: str, emotions: list = None) -> dict:
        emotions_str = ", ".join(emotions) if emotions else "Not specified"
        
        prompt = DREAM_ANALYSIS_PROMPT.format(
            dream_description=dream_description,
            emotions=emotions_str
        )
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert dream analyst with deep knowledge of symbolic interpretation, psychology, and cultural symbolism."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        interpretation = response.choices[0].message.content
        
        symbols = self._extract_symbols(dream_description)
        
        return {
            "interpretation": interpretation,
            "symbols": symbols,
            "model_used": response.model
        }
    
    def _extract_symbols(self, dream_description: str) -> list:
        prompt = SYMBOL_EXTRACTION_PROMPT.format(dream_description=dream_description)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert at identifying dream symbols. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=800,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
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
        
        prompt = f"""Analyze these recent dreams and identify recurring patterns, themes, or symbols:

{dream_summaries}

Provide:
1. Recurring symbols or themes
2. Emotional patterns
3. Possible meanings of these patterns
4. Insights about the dreamer's subconscious state
"""
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert at identifying patterns in dreams over time."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        return {
            "pattern_analysis": response.choices[0].message.content,
            "dreams_analyzed": len(dreams[-5:])
        }
    
    def chat_about_dream(self, dream_context: dict, chat_history: list, user_question: str) -> str:
        system_prompt = f"""You are an expert dream analyst having a conversation with someone about their dream.

Dream Title: {dream_context['title']}
Dream Description: {dream_context['description']}
Emotions: {', '.join(dream_context.get('emotions', []))}
Initial Interpretation: {dream_context.get('interpretation', 'N/A')}

Answer the user's follow-up questions about their dream. Be empathetic, insightful, and help them explore deeper meanings. 
You can ask clarifying questions to better understand their dream and provide more personalized insights."""

        messages = [{"role": "system", "content": system_prompt}]
        
        for msg in chat_history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        messages.append({"role": "user", "content": user_question})
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=800
        )
        
        return response.choices[0].message.content
