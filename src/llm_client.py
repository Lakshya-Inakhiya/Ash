"""
LLM Client Module for Ash Robot.

This module provides a simple wrapper around the Google Gemini API
for conversational AI functionality.
"""

import os
import google.generativeai as genai
from pathlib import Path


class LLMClient:
    """
    Client for interacting with Google's Gemini API.
    
    This class handles all communication with the Gemini API and provides
    a simple interface for asking questions and getting concise responses.
    """
    
    def __init__(self, config, api_key):
        """
        Initialize the Gemini API client.
        
        Args:
            config: Configuration dictionary with LLM settings
            api_key: Google Gemini API key
        """
        self.config = config
        self.model_name = config['llm']['model']
        self.system_instruction = config['llm']['system_instruction']
        self.max_tokens = config['llm']['max_tokens']
        
        # Configure the API
        genai.configure(api_key=api_key)
        
        # Initialize the model
        generation_config = {
            "max_output_tokens": self.max_tokens,
            "temperature": 0.7,  # Slightly creative but focused
        }
        
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=generation_config,
            system_instruction=self.system_instruction
        )
        
        # Start a chat session for context continuity
        self.chat = self.model.start_chat(history=[])
        
        print(f"LLM Client initialized with model: {self.model_name}")
    
    def ask(self, prompt):
        """
        Ask Gemini a question and get a concise response.
        
        Args:
            prompt: The user's question or statement
        
        Returns:
            str: Gemini's response, or error message if request fails
        """
        if not prompt or not prompt.strip():
            return "I didn't catch that. Could you repeat?"
        
        try:
            # Send message and get response
            response = self.chat.send_message(prompt)
            
            # Extract text from response
            answer = response.text.strip()
            
            # Ensure response isn't too long (safety check)
            if len(answer) > 500:
                # Truncate to first 2 sentences if too long
                sentences = answer.split('. ')
                answer = '. '.join(sentences[:2])
                if not answer.endswith('.'):
                    answer += '.'
            
            return answer
            
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return "Sorry, I had trouble thinking of a response."
    
    def reset_conversation(self):
        """
        Reset the conversation history.
        Useful if you want to start a fresh conversation.
        """
        self.chat = self.model.start_chat(history=[])
        print("Conversation history reset")
    
    def get_conversation_history(self):
        """
        Get the current conversation history.
        
        Returns:
            list: List of message dictionaries
        """
        return self.chat.history


# Standalone function for simple usage
def ask_gemini(prompt, api_key=None, system_instruction=None):
    """
    Simple standalone function to ask Gemini a question.
    
    This is a convenience function that doesn't require creating a client object.
    Use this for one-off queries. For conversation context, use the LLMClient class.
    
    Args:
        prompt: The question to ask
        api_key: Gemini API key (optional, reads from env if not provided)
        system_instruction: Custom system instruction (optional)
    
    Returns:
        str: Gemini's response
    """
    if api_key is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "Error: GEMINI_API_KEY not set"
    
    try:
        genai.configure(api_key=api_key)
        
        generation_config = {
            "max_output_tokens": 100,
            "temperature": 0.7,
        }
        
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
            system_instruction=system_instruction or "Give very concise answers in 1-2 sentences."
        )
        
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        print(f"Error: {e}")
        return f"Error calling Gemini API: {str(e)}"


def main():
    """
    Test function for the LLM client module.
    """
    import sys
    sys.path.append(str(Path(__file__).parent))
    from utils import load_config, load_env, get_api_key
    
    print("LLM Client Test")
    print("-" * 40)
    
    try:
        # Load configuration and API key
        load_env()
        config = load_config()
        api_key = get_api_key()
        
        # Create client
        client = LLMClient(config, api_key)
        
        # Test questions
        test_questions = [
            "What is your name?",
            "What can you do?",
            "Tell me a fun fact about robots.",
        ]
        
        print("\nTesting LLM with sample questions...\n")
        
        for question in test_questions:
            print(f"Q: {question}")
            answer = client.ask(question)
            print(f"A: {answer}\n")
        
        print("Test complete!")
        
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("\nPlease create a .env file with your GEMINI_API_KEY:")
        print("  GEMINI_API_KEY=your_actual_api_key_here")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

