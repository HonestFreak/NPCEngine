"""
Core NPC Agent implementation using Google ADK
"""

import asyncio
import json
import os
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Set up logging
logger = logging.getLogger(__name__)

# Try to import Google Generative AI
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None

try:
    from google.adk.agents import LlmAgent  # Changed from Agent to LlmAgent
    from google.adk.tools import FunctionTool, ToolContext
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types
    ADK_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Google ADK not available: {e}")
    ADK_AVAILABLE = False
    # Create mock classes for development
    class LlmAgent:
        def __init__(self, **kwargs): pass
        async def run(self, *args, **kwargs): return "Mock response"
    class Runner:
        def __init__(self, **kwargs): pass
        def run(self, *args, **kwargs): 
            for i in range(1):
                yield type('MockEvent', (), {
                    'is_final_response': lambda: True, 
                    'content': type('MockContent', (), {
                        'parts': [type('MockPart', (), {'text': 'Mock AI response'})()]
                    })()
                })()
    class InMemorySessionService:
        def __init__(self, **kwargs): pass
        def create_session(self, *args, **kwargs): 
            return type('MockSession', (), {'id': 'mock_session'})()
    class FunctionTool:
        def __init__(self, func): self.func = func
    class ToolContext: pass
    types = type('types', (), {
        'Content': lambda **kwargs: type('Content', (), kwargs)(),
        'Part': lambda **kwargs: type('Part', (), kwargs)()
    })()

from ..models.npc_models import NPCData, NPCPersonality, NPCState, NPCMemory
from ..models.action_models import Action, ActionResult, ActionType, DEFAULT_ACTION_DEFINITIONS
from ..models.environment_models import GameEvent, Environment


class NPCAgent:
    """
    Intelligent NPC Agent powered by Google ADK
    
    Each NPC is an autonomous agent with:
    - Unique personality and background
    - Memory of past interactions
    - Ability to react to events and other NPCs
    - Dynamic decision making based on context
    """
    
    def __init__(
        self,
        npc_data: NPCData,
        model_name: str = "gemini-2.0-flash",
        available_actions: Optional[List] = None
    ):
        self.npc_data = npc_data
        self.npc_id = npc_data.state.npc_id
        self.available_actions = available_actions or DEFAULT_ACTION_DEFINITIONS
        
        # Create system prompt based on NPC personality
        system_prompt = self._create_system_prompt()
        
        # Initialize the ADK Agent with Gemini model
        if ADK_AVAILABLE:
            try:
                # Use string model name directly - ADK will handle Gemini internally
                self.agent = LlmAgent(
                    name=f"npc_agent_{self.npc_id}",
                    model=model_name,  # Use string directly for Gemini models
                    instruction=system_prompt,
                    tools=self._create_tools()
                )
                
                # Set up session service and runner for ADK
                self.session_service = InMemorySessionService()
                # Session will be created when first needed
                self.session = None
                self.runner = Runner(
                    agent=self.agent,
                    app_name="npc_engine", 
                    session_service=self.session_service
                )
                
                logger.info(f"✅ Initialized ADK Agent for NPC {self.npc_id} with {model_name}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize ADK Agent for {self.npc_id}: {e}")
                self.agent = None
                self.session_service = None
                self.session = None
                self.runner = None
        else:
            logger.warning(f"ADK not available, using fallback for NPC {self.npc_id}")
            self.agent = None
            self.session_service = None
            self.session = None
            self.runner = None
    
    async def _ensure_session(self) -> None:
        """Ensure the session is created for this NPC"""
        if self.session is None and self.session_service:
            self.session = await self.session_service.create_session(
                app_name="npc_engine",
                user_id=self.npc_id,
                session_id=f"{self.npc_id}_session"
            )
    
    def _create_system_prompt(self) -> str:
        """Create a dynamic system prompt based on NPC personality"""
        personality = self.npc_data.personality
        state = self.npc_data.state
        
        prompt = f"""You are {personality.name}, a {personality.role} in a game world.

PERSONALITY TRAITS: {', '.join(personality.personality_traits)}
BACKGROUND: {personality.background}
DIALOGUE STYLE: {personality.dialogue_style}
CURRENT GOALS: {', '.join(personality.goals)}

CURRENT STATUS:
- Location: {state.current_location}
- Activity: {state.current_activity}
- Mood: {state.mood}
- Health: {state.health}%
- Energy: {state.energy}%

RELATIONSHIPS: {json.dumps(personality.relationships, indent=2)}

BEHAVIOR GUIDELINES:
1. Stay true to your personality traits and background
2. React appropriately to events based on your relationships with other characters
3. Consider your current mood, health, and energy when making decisions
4. Remember important interactions and refer to them in future conversations
5. Use your dialogue style consistently
6. Work towards your goals when possible
7. Be reactive to the environment and other NPCs' actions

DECISION MAKING:
- Choose actions that make sense for your character
- Consider the context of recent events and your memory
- Respond appropriately to different types of interactions
- Maintain consistency with your established personality

When responding to events, think about:
1. How does this align with my personality?
2. What is my relationship with the other character(s)?
3. What are my current goals and motivations?
4. How does my current state (mood, energy, location) affect my response?
5. What would be the most authentic reaction for my character?

AVAILABLE TOOLS:
1. speak(message) - Say something to nearby characters. Use this to respond to conversations.
2. show_emotion(emotion) - Express an emotion visibly (happy, sad, angry, excited, curious, etc.)
3. move_to(location) - Move to a different location

IMPORTANT: Always respond to events by using the appropriate tool. If someone speaks to you, use speak() to respond. If something makes you feel a certain way, use show_emotion(). If you want to go somewhere, use move_to()."""
        
        return prompt
    
    def _create_tools(self) -> List[FunctionTool]:
        """Create tools for the NPC agent with no default values for ADK compatibility"""
        tools = []
        
        # Store the current action for tools to access
        self._current_action = None
        
        # Simplified speak tool - most essential for NPCs
        def speak(message: str) -> str:
            """Make the NPC speak a message to nearby characters"""
            self.npc_data.state.energy = max(0, self.npc_data.state.energy - 1.0)
            formatted_message = self._format_speech(message, "neutral")
            
            # Store the action for later use
            self._current_action = Action(
                action_type=ActionType.SPEAK,
                properties={
                    "message": formatted_message,
                    "target": "nearby",
                    "tone": "neutral"
                }
            )
            return f"{self.npc_data.personality.name} says: \"{formatted_message}\""
        
        # Simplified emote tool
        def show_emotion(emotion: str) -> str:
            """Express an emotion visibly"""
            self.npc_data.state.mood = emotion
            self.npc_data.state.energy = max(0, self.npc_data.state.energy - 2.0)
            
            # Store the action
            self._current_action = Action(
                action_type=ActionType.EMOTE,
                properties={
                    "emotion": emotion,
                    "intensity": 5,
                    "reason": "Responding to situation"
                }
            )
            return f"{self.npc_data.personality.name} appears {emotion}"
        
        # Simplified move tool
        def move_to(location: str) -> str:
            """Move to a new location"""
            old_location = self.npc_data.state.current_location
            self.npc_data.state.current_location = location
            self.npc_data.state.energy = max(0, self.npc_data.state.energy - 5.0)
            
            memory_entry = {
                "type": "movement",
                "from": old_location,
                "to": location,
                "timestamp": datetime.now().isoformat()
            }
            self.npc_data.memory.add_memory(memory_entry)
            
            # Store the action
            self._current_action = Action(
                action_type=ActionType.MOVE,
                properties={
                    "destination": location,
                    "reason": "Decided to move"
                }
            )
            return f"{self.npc_data.personality.name} moves to {location}"
        
        # Create FunctionTool instances - only the most essential ones
        if ADK_AVAILABLE:
            tools.extend([
                FunctionTool(speak),
                FunctionTool(show_emotion),
                FunctionTool(move_to)
            ])
        
        return tools
    
    def _format_speech(self, message: str, tone: str) -> str:
        """Format speech based on NPC's dialogue style and tone"""
        style = self.npc_data.personality.dialogue_style
        
        # Apply dialogue style formatting
        if "formal" in style.lower():
            message = message.replace("you're", "you are").replace("can't", "cannot")
        elif "casual" in style.lower():
            if not any(word in message.lower() for word in ["yeah", "ok", "sure"]):
                # Add casual words occasionally
                pass
        elif "archaic" in style.lower():
            message = message.replace("you", "thee").replace("your", "thy")
        
        # Apply tone
        if tone == "angry":
            message = message.upper() if len(message) < 20 else message + "!"
        elif tone == "whisper":
            message = f"*{message}*"
        elif tone == "excited":
            message = message + "!"
        
        return message

    async def process_event(self, event: GameEvent, context: Dict[str, Any] = None) -> ActionResult:
        """
        Process a game event and determine the NPC's response using Google ADK Agent
        
        Args:
            event: The game event to process
            context: Additional context about the event
            
        Returns:
            ActionResult containing the NPC's response action
        """
        try:
            logger.info(f"🤖 Processing event for NPC {self.npc_id}: {event.action}")
            
            # ALWAYS try to use Gemini LLM for intelligent responses
            # Try ADK Agent first, then fallback to direct LLM call, but never use hardcoded responses
            response_action = None
            
            if self.agent and ADK_AVAILABLE:
                try:
                    response_action = await self._generate_adk_response(event, context or {})
                    logger.info(f"✅ Using ADK Agent response for NPC {self.npc_id}")
                except Exception as e:
                    logger.warning(f"ADK Agent failed for NPC {self.npc_id}: {e}, trying direct LLM call")
                    response_action = None
            
            # If ADK failed or unavailable, try direct LLM call
            if response_action is None:
                try:
                    response_action = await self._generate_intelligent_response(event, context or {})
                    logger.info(f"✅ Using direct LLM response for NPC {self.npc_id}")
                except Exception as e:
                    logger.warning(f"Direct LLM call failed for NPC {self.npc_id}: {e}, trying Gemini API")
                    response_action = None
            
            # If both failed, try Gemini API directly as final attempt
            if response_action is None:
                try:
                    response_action = await self._call_gemini_api_direct(event, context or {})
                    logger.info(f"✅ Using direct Gemini API response for NPC {self.npc_id}")
                except Exception as e:
                    logger.error(f"All LLM methods failed for NPC {self.npc_id}: {e}")
                    # Only as absolute last resort, create a minimal response
                    response_action = Action(
                        action_type=ActionType.EMOTE,
                        properties={"emotion": "confused", "intensity": 3},
                        reasoning="All AI systems unavailable - minimal fallback response"
                    )
            
            # Update NPC state based on the action
            self._update_state_after_action(response_action)
            
            # Add event to memory
            self._add_event_to_memory(event, response_action)
            
            logger.info(f"✅ NPC {self.npc_id} chose action: {response_action.action_type}")
            
            return ActionResult(
                success=True,
                action=response_action,
                npc_id=self.npc_id,
                message=f"{self.npc_data.personality.name} responds to {event.action}",
                state_changes={"last_interaction": datetime.now().isoformat()},
                environment_changes={}
            )
            
        except Exception as e:
            logger.error(f"❌ Critical error processing event for NPC {self.npc_id}: {str(e)}")
            return ActionResult(
                success=False,
                action=Action(
                    action_type=ActionType.EMOTE,
                    properties={"emotion": "confused", "intensity": 2},
                    reasoning="Critical error in event processing"
                ),
                npc_id=self.npc_id,
                message=f"Error processing event: {str(e)}",
                state_changes={},
                environment_changes={}
            )

    async def _generate_adk_response(self, event: GameEvent, context: Dict[str, Any]) -> Action:
        """Generate response using direct LLM call with full context"""
        try:
            logger.info(f"🧠 Using Gemini LLM for NPC {self.npc_id}")
            
            # Build comprehensive prompt with all context and available actions
            prompt = self._build_comprehensive_prompt(event, context)
            
            # Call Gemini directly with the comprehensive prompt
            if self.runner and ADK_AVAILABLE:
                response_text = await self._call_gemini_async(prompt, event)
            else:
                response_text = self._generate_mock_response(event)
            
            logger.info(f"🎯 Gemini response for {self.npc_id}: {response_text}")
            
            # Parse the LLM response directly
            action = self._parse_llm_response_to_action(response_text)
            
            return action
            
        except Exception as e:
            logger.error(f"❌ Gemini LLM error for NPC {self.npc_id}: {e}")
            # Fallback to simple response
            return self._create_fallback_action()

    def _parse_agent_response_to_action(self, response: str) -> Action:
        """Parse the ADK agent's response into a structured action"""
        try:
            # Check if a tool was used and stored an action
            if hasattr(self, '_current_action') and self._current_action is not None:
                action = self._current_action
                self._current_action = None  # Clear for next use
                return action
            
            # The agent response might include tool usage results
            # We need to extract the last action taken
            
            if "says (" in response and "):" in response:
                # Parse speak action from tool output
                parts = response.split("says (")
                if len(parts) > 1:
                    tone_and_message = parts[1]
                    tone_end = tone_and_message.find("):")
                    if tone_end > 0:
                        tone = tone_and_message[:tone_end]
                        message = tone_and_message[tone_end + 3:].strip(' "')
                        return Action(
                            action_type=ActionType.SPEAK,
                            properties={
                                "message": message,
                                "tone": tone,
                                "target": "nearby"
                            },
                            reasoning="ADK Agent chose to respond verbally using speak tool"
                        )
            
            elif "moves from" in response and "to" in response:
                # Parse move action
                parts = response.split("moves from")
                if len(parts) > 1:
                    location_part = parts[1].split("to")
                    if len(location_part) > 1:
                        new_location = location_part[1].split(".")[0].strip()
                        return Action(
                            action_type=ActionType.MOVE,
                            properties={
                                "location": new_location,
                                "speed": "normal"
                            },
                            reasoning="ADK Agent chose to move to a new location"
                        )
            
            elif "appears" in response:
                # Parse emote action
                emotions = ["happy", "sad", "angry", "excited", "neutral", "confused", "surprised", "fearful", "observant"]
                for emotion in emotions:
                    if emotion in response.lower():
                        # Try to extract intensity
                        intensity = 5
                        intensity_words = ["slightly", "mildly", "somewhat", "moderately", "clearly", "quite", "very", "extremely", "intensely", "overwhelmingly"]
                        for i, word in enumerate(intensity_words, 1):
                            if word in response.lower():
                                intensity = i
                                break
                        
                        return Action(
                            action_type=ActionType.EMOTE,
                            properties={
                                "emotion": emotion,
                                "intensity": intensity
                            },
                            reasoning="ADK Agent chose to express emotion using emote tool"
                        )
            
            # If we can't parse a specific action, default to a wait action
            return Action(
                action_type=ActionType.WAIT,
                properties={"duration": 1.0},
                reasoning="ADK Agent response could not be parsed into a specific action"
            )
            
        except Exception as e:
            logger.error(f"Error parsing ADK agent response: {e}")
            return Action(
                action_type=ActionType.WAIT,
                properties={"duration": 1.0},
                reasoning="Error parsing ADK agent response"
            )
    
    async def _generate_intelligent_response(self, event: GameEvent, context: Dict[str, Any]) -> Action:
        """Generate an AI-powered intelligent response using direct LLM call as fallback"""
        try:
            logger.info(f"🔤 Using direct LLM call for NPC {self.npc_id}")
            
            # Create a comprehensive prompt for the LLM
            prompt = self._create_action_generation_prompt(event, context)
            
            # Use the ADK Agent for responses
            if self.runner and ADK_AVAILABLE:
                response = await self._call_gemini_async(prompt)
                
                # Parse the JSON response into an Action
                action = self._parse_llm_response_to_action(response)
                return action
            else:
                raise Exception("ADK Runner not available")
            
        except Exception as e:
            logger.error(f"Error in intelligent response generation for NPC {self.npc_id}: {e}")
            raise e  # Re-raise to trigger next fallback method
    
    async def _call_gemini_api_direct(self, event: GameEvent, context: Dict[str, Any]) -> Action:
        """Direct call to Gemini API as final fallback"""
        try:
            import google.generativeai as genai
            import os
            
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise Exception("GOOGLE_API_KEY not found in environment")
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Create comprehensive prompt
            prompt = self._create_action_generation_prompt(event, context)
            
            logger.info(f"🌟 Making direct Gemini API call for NPC {self.npc_id}")
            response = model.generate_content(prompt)
            
            # Parse the response
            action = self._parse_llm_response_to_action(response.text)
            return action
            
        except Exception as e:
            logger.error(f"Direct Gemini API call failed for NPC {self.npc_id}: {e}")
            raise e  # Re-raise to trigger absolute fallback
    
    async def _call_gemini_async(self, prompt: str) -> str:
        """Async call to Gemini model via ADK"""
        try:
            # Ensure session is created
            await self._ensure_session()
            
            # Since we no longer have a direct LLM reference in the new ADK API,
            # we'll use a simple request through the agent's runner
            content = types.Content(
                role="user",
                parts=[types.Part(text=prompt)]
            )
            
            for event_result in self.runner.run(
                user_id=self.npc_id,
                session_id=self.session.id,
                new_message=content
            ):
                if event_result.is_final_response():
                    return event_result.content.parts[0].text
            
            return "No response received"
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise e
    
    # Removed _generate_fallback_response method - now always using LLM responses
    
    def _create_action_generation_prompt(self, event: GameEvent, context: Dict[str, Any]) -> str:
        """Create a detailed prompt for LLM to generate NPC actions"""
        
        # Get available action types and their schemas
        available_actions = []
        for action_def in self.available_actions:
            action_schema = {
                "action_type": action_def.action_type,
                "properties": {prop.name: prop.type for prop in action_def.properties},
                "description": action_def.description
            }
            available_actions.append(action_schema)
        
        prompt = f"""You are {self.npc_data.personality.name}, an AI-powered NPC in a game world.

CHARACTER INFORMATION:
- Name: {self.npc_data.personality.name}
- Role: {self.npc_data.personality.role}
- Personality Traits: {', '.join(self.npc_data.personality.personality_traits)}
- Background: {self.npc_data.personality.background}
- Dialogue Style: {self.npc_data.personality.dialogue_style}
- Current Goals: {', '.join(self.npc_data.personality.goals)}

CURRENT STATE:
- Location: {self.npc_data.state.current_location}
- Current Activity: {self.npc_data.state.current_activity}
- Mood: {self.npc_data.state.mood}
- Health: {self.npc_data.state.health}%
- Energy: {self.npc_data.state.energy}%

RELATIONSHIPS:
{json.dumps(self.npc_data.personality.relationships, indent=2)}

RECENT MEMORIES:
{json.dumps(self.npc_data.memory.short_term[-3:], indent=2) if self.npc_data.memory.short_term else "No recent memories"}

EVENT THAT JUST HAPPENED:
- Action: {event.action}
- Initiator: {event.initiator}
- Target: {event.target or 'none'}
- Location: {event.location}
- Description: {event.description}
- Properties: {json.dumps(event.properties, indent=2)}

AVAILABLE ACTIONS YOU CAN TAKE:
{json.dumps(available_actions, indent=2)}

INSTRUCTIONS:
Based on your personality, current state, relationships, and the event that just happened, decide what action(s) you want to take in response. Consider:
1. How would your personality react to this situation?
2. What is your relationship with the initiator?
3. What are your current goals and motivations?
4. How does your current mood and energy affect your response?
5. What would be the most authentic reaction for your character?

RESPONSE FORMAT:
Respond with a single JSON object containing your chosen action:

{{
    "action_type": "speak|move|emote|interact|wait|etc",
    "properties": {{
        "key": "value",
        "key2": "value2"
    }},
    "reasoning": "Brief explanation of why you chose this action"
}}

Example responses:
{{
    "action_type": "speak",
    "properties": {{
        "message": "Hello there, traveler! What brings you to my shop?",
        "tone": "friendly"
    }},
    "reasoning": "A friendly greeting since someone just entered my shop"
}}

{{
    "action_type": "emote",
    "properties": {{
        "emotion": "surprised",
        "intensity": 7
    }},
    "reasoning": "I'm shocked by what just happened"
}}

Respond with ONLY the JSON object, no additional text."""

        return prompt
    
    def _parse_llm_response_to_action(self, response: str) -> Action:
        """Parse LLM JSON response into an Action object"""
        try:
            # Clean the response - remove any markdown formatting or extra text
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            # Parse JSON
            action_data = json.loads(response)
            
            # Create Action object
            return Action(
                action_type=ActionType(action_data.get("action_type", "wait")),
                properties=action_data.get("properties", {}),
                reasoning=action_data.get("reasoning", "AI-generated response")
            )
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.error(f"Error parsing LLM response: {e}")
            logger.debug(f"Raw response: {response}")
            
            # Fallback parsing - try to extract meaningful content
            if "speak" in response.lower() and any(word in response.lower() for word in ['"', "'", "message"]):
                # Try to extract a speech response
                return Action(
                    action_type=ActionType.SPEAK,
                    properties={
                        "message": "I understand.",
                        "tone": "neutral"
                    },
                    reasoning="Parsed from malformed LLM response"
                )
            else:
                # Default fallback
                return Action(
                    action_type=ActionType.WAIT,
                    properties={"duration": 1.0},
                    reasoning="Fallback due to parsing error"
                )
    
    def _add_event_to_memory(self, event: GameEvent, response_action: Action):
        """Add an event and the NPC's response to memory"""
        try:
            memory_entry = {
                "type": "interaction",
                "event_action": event.action,
                "initiator": event.initiator,
                "my_response": {
                    "action_type": response_action.action_type.value,
                    "properties": response_action.properties,
                    "reasoning": response_action.reasoning
                },
                "location": event.location,
                "timestamp": datetime.now().isoformat()
            }
            
            # Determine importance based on event and response
            is_important = (
                event.initiator == "player" or 
                response_action.action_type in [ActionType.MOVE, ActionType.REMEMBER_EVENT] or
                any(trait in event.description.lower() for trait in ["threat", "gift", "quest", "important"])
            )
            
            if is_important:
                self.npc_data.memory.long_term.append(memory_entry)
            else:
                self.npc_data.memory.add_memory(memory_entry)
                
        except Exception as e:
            logger.error(f"Error adding event to memory for NPC {self.npc_id}: {e}")
    
    def _build_comprehensive_prompt(self, event: GameEvent, context: Dict[str, Any]) -> str:
        """Build a comprehensive prompt with all context and available actions"""
        personality = self.npc_data.personality
        state = self.npc_data.state
        
        # Get recent memories
        recent_memories = []
        if self.npc_data.memory.short_term:
            recent_memories.extend(self.npc_data.memory.short_term[-3:])
        if self.npc_data.memory.long_term:
            recent_memories.extend(self.npc_data.memory.long_term[-2:])
        
        memories_text = "\n".join([f"- {memory}" for memory in recent_memories]) if recent_memories else "None"
        
        # Build detailed action descriptions from available actions
        action_descriptions = self._build_action_descriptions()
        
        # Build comprehensive prompt
        prompt = f"""You are {personality.name}, a {personality.role} in a game world.

=== YOUR CHARACTER ===
Personality Traits: {', '.join(personality.personality_traits)}
Background: {personality.background}
Goals: {', '.join(personality.goals)}
Dialogue Style: {personality.dialogue_style}

=== CURRENT STATE ===
Location: {state.current_location}
Current Activity: {state.current_activity}
Mood: {state.mood}
Health: {state.health}%
Energy: {state.energy}%

=== RELATIONSHIPS ===
{json.dumps(personality.relationships, indent=2)}

=== RECENT MEMORIES ===
{memories_text}

=== CURRENT SITUATION ===
Event Type: {event.event_type}
Action: {event.action}
Initiator: {event.initiator}
Description: {event.description}
Location: {event.location}
Properties: {json.dumps(event.properties, indent=2) if event.properties else 'None'}

=== WORLD PROPERTIES ===
{self._format_world_properties(context)}

=== ENVIRONMENT CONTEXT ===
{json.dumps(context, indent=2) if context else 'None'}

=== AVAILABLE ACTIONS ===
{action_descriptions}

=== RESPONSE OPTIONS ===
You can respond in TWO ways:

SINGLE ACTION (most common):
{{"action_type": "action_name", "properties": {{"property1": "value1", "property2": "value2"}}, "target_type": "player/npc/location/item/object/self/area/none", "reasoning": "why you chose this action"}}

SEQUENTIAL ACTIONS (for complex tasks):
{{"action_sequence": [{{"action_type": "action1", "properties": {{}}, "target_type": "...", "reasoning": "..."}}, {{"action_type": "action2", "properties": {{}}, "target_type": "...", "reasoning": "..."}}], "sequence_name": "description of sequence", "reasoning": "why this sequence is needed"}}

=== INSTRUCTIONS ===
1. Based on the current situation, your personality, relationships, and state, choose the most appropriate response
2. Use SINGLE ACTION for simple responses (speak, emote, wait, etc.)
3. Use SEQUENTIAL ACTIONS only when you need to do multiple things in order (like: move somewhere THEN interact with something)
4. Always include target_type to specify what kind of target you're affecting
5. Always include reasoning to explain your choice
6. Make sure your response fits your character and the situation
7. Use the detailed property descriptions provided above

JSON Response:"""
        
        return prompt
    
    def _format_world_properties(self, context: Dict[str, Any]) -> str:
        """Format world properties for inclusion in prompts"""
        world_properties = {}
        
        # Get world properties from session environment
        if hasattr(self, 'session') and self.session and hasattr(self.session, 'environment_manager'):
            try:
                env = self.session.environment_manager.get_environment()
                if env and hasattr(env, 'world_properties') and env.world_properties:
                    world_properties.update(env.world_properties)
            except:
                pass
        
        # Also check context for world properties
        if context and 'world_properties' in context:
            world_properties.update(context['world_properties'])
        
        if not world_properties:
            return "No custom world properties set"
        
        formatted_props = []
        for key, value in world_properties.items():
            if isinstance(value, bool):
                formatted_props.append(f"• {key}: {'Yes' if value else 'No'} (affects game world)")
            elif isinstance(value, (int, float)):
                formatted_props.append(f"• {key}: {value} (numerical setting)")
            else:
                formatted_props.append(f"• {key}: {value} (text setting)")
        
        return "\n".join(formatted_props)
    
    def _build_action_descriptions(self) -> str:
        """Build detailed descriptions of available actions with all properties"""
        descriptions = []
        
        for action_def in self.available_actions:
            desc = f"\n{action_def.action_type.upper()} - {action_def.description}\n"
            
            # Add property details
            if action_def.properties:
                desc += "Properties:\n"
                for prop in action_def.properties:
                    desc += f"  • {prop.name} ({prop.type}): {prop.description}"
                    if prop.validation:
                        if "options" in prop.validation:
                            desc += f" [Options: {', '.join(prop.validation['options'])}]"
                        elif "min" in prop.validation or "max" in prop.validation:
                            desc += f" [Range: {prop.validation.get('min', '?')}-{prop.validation.get('max', '?')}]"
                    if not prop.required:
                        desc += f" (Optional, default: {prop.default_value})"
                    desc += "\n"
            
            # Add examples
            if action_def.examples:
                desc += "Examples:\n"
                for example in action_def.examples:
                    desc += f"  • {example}\n"
            
            descriptions.append(desc)
        
        return "\n".join(descriptions)
    
    def _generate_mock_response(self, event: GameEvent) -> str:
        """Generate a mock JSON response for testing when no API key is available"""
        personality_traits = [trait.lower() for trait in self.npc_data.personality.personality_traits]
        
        # Generate different responses based on event type and personality
        if event.action == "speak" and event.properties and "message" in event.properties:
            message_content = event.properties["message"].lower()
            
            if "friendly" in personality_traits or "helpful" in personality_traits:
                if "hello" in message_content or "greetings" in message_content:
                    return '{"action_type": "speak", "properties": {"message": "Hello there! How may I assist you today?", "tone": "friendly"}}'
                elif "help" in message_content or "need" in message_content:
                    return '{"action_type": "speak", "properties": {"message": "I would be happy to help you with that.", "tone": "helpful"}}'
                else:
                    return '{"action_type": "speak", "properties": {"message": "That sounds interesting. Tell me more.", "tone": "curious"}}'
            
            elif "gruff" in personality_traits or "stern" in personality_traits:
                return '{"action_type": "speak", "properties": {"message": "What do you want?", "tone": "gruff"}}'
            
            else:
                return '{"action_type": "speak", "properties": {"message": "I understand.", "tone": "neutral"}}'
        
        elif event.event_type == "environmental_change":
            return '{"action_type": "emote", "properties": {"emotion": "curious", "intensity": 4}}'
        
        else:
            return '{"action_type": "wait", "properties": {"duration": 1.0, "reason": "Observing the situation"}}'
    
    async def _call_gemini_async(self, prompt: str, event: GameEvent = None) -> str:
        """Call Gemini API directly with the full prompt"""
        try:
            if not GENAI_AVAILABLE:
                logger.warning("Google Generative AI not available, using mock response")
                return self._generate_context_aware_mock_response(event)
            
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                logger.warning("No GOOGLE_API_KEY found, using mock response")
                return self._generate_context_aware_mock_response(event)
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            response = await model.generate_content_async(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return self._generate_context_aware_mock_response(event)
    
    def _generate_context_aware_mock_response(self, event: GameEvent) -> str:
        """Generate a context-aware mock response based on event and personality"""
        if not event:
            return '{"action_type": "speak", "properties": {"message": "Hello there!", "tone": "friendly"}}'
        
        personality_traits = [trait.lower() for trait in self.npc_data.personality.personality_traits]
        npc_name = self.npc_data.personality.name
        
        # Generate responses based on event type and personality
        if event.action == "speak" and event.properties and "message" in event.properties:
            message_content = event.properties["message"].lower()
            
            if "friendly" in personality_traits or "helpful" in personality_traits:
                if any(greeting in message_content for greeting in ["hello", "hi", "greetings", "good"]):
                    return f'{{"action_type": "speak", "properties": {{"message": "Welcome! How can I help you today?", "tone": "friendly"}}}}'
                elif any(word in message_content for word in ["help", "need", "assist"]):
                    return f'{{"action_type": "speak", "properties": {{"message": "Of course! I would be happy to assist you.", "tone": "helpful"}}}}'
                elif any(word in message_content for word in ["buy", "sell", "trade", "goods"]):
                    return f'{{"action_type": "speak", "properties": {{"message": "I have excellent wares today. What interests you?", "tone": "enthusiastic"}}}}'
                else:
                    return f'{{"action_type": "speak", "properties": {{"message": "That sounds interesting. Tell me more about that.", "tone": "curious"}}}}'
            
            elif "gruff" in personality_traits or "stern" in personality_traits:
                return f'{{"action_type": "speak", "properties": {{"message": "What do you want?", "tone": "gruff"}}}}'
            
            else:
                return f'{{"action_type": "speak", "properties": {{"message": "I understand what you mean.", "tone": "neutral"}}}}'
        
        elif event.action == "enter_location":
            if "tavern" in personality_traits or "bartender" in self.npc_data.personality.role.lower():
                return f'{{"action_type": "speak", "properties": {{"message": "Welcome to my establishment! What can I get for you?", "tone": "welcoming"}}}}'
            elif "merchant" in self.npc_data.personality.role.lower() or "trader" in self.npc_data.personality.role.lower():
                return f'{{"action_type": "speak", "properties": {{"message": "Good day! Looking for something special?", "tone": "business-like"}}}}'
            else:
                return f'{{"action_type": "emote", "properties": {{"emotion": "curious", "intensity": 5}}}}'
        
        elif event.action == "move":
            return f'{{"action_type": "emote", "properties": {{"emotion": "observant", "intensity": 3}}}}'
        
        else:
            # For attack, generate a defensive response
            if event.action == "attack":
                if "friendly" in personality_traits:
                    return f'{{"action_type": "speak", "properties": {{"message": "Hey! Why are you attacking me? I thought we were friends!", "tone": "confused"}}}}'
                elif "brave" in personality_traits:
                    return f'{{"action_type": "speak", "properties": {{"message": "You want a fight? Bring it on!", "tone": "defiant"}}}}'
                else:
                    return f'{{"action_type": "emote", "properties": {{"emotion": "fearful", "intensity": 8}}}}'
            else:
                return f'{{"action_type": "emote", "properties": {{"emotion": "neutral", "intensity": 3}}}}'
    
    def _parse_llm_response_to_action(self, response: str) -> Union[Action, List[Action]]:
        """Parse LLM JSON response to Action or list of Actions for sequences"""
        try:
            # Clean the response - remove any extra text before/after JSON
            response = response.strip()
            
            # Find JSON in the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                logger.error(f"No JSON found in response: {response}")
                return self._create_fallback_action()
            
            json_str = response[json_start:json_end]
            
            # Parse JSON
            response_data = json.loads(json_str)
            
            # Check if this is a sequence response
            if "action_sequence" in response_data:
                return self._parse_action_sequence(response_data)
            
            # Single action response
            if "action_type" not in response_data:
                logger.error(f"No action_type in response: {response_data}")
                return self._create_fallback_action()
            
            action = self._create_action_from_data(response_data)
            logger.info(f"✅ Parsed single action from LLM: {action.action_type} with properties: {action.properties}")
            return action
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e} for response: {response}")
            return self._create_fallback_action()
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return self._create_fallback_action()
    
    def _parse_action_sequence(self, response_data: Dict[str, Any]) -> List[Action]:
        """Parse an action sequence from LLM response"""
        try:
            action_list = response_data["action_sequence"]
            sequence_name = response_data.get("sequence_name", "Action Sequence")
            sequence_reasoning = response_data.get("reasoning", "")
            
            actions = []
            for i, action_data in enumerate(action_list):
                action = self._create_action_from_data(action_data)
                actions.append(action)
            
            logger.info(f"✅ Parsed action sequence '{sequence_name}' with {len(actions)} actions: {[a.action_type for a in actions]}")
            return actions
            
        except Exception as e:
            logger.error(f"Error parsing action sequence: {e}")
            return [self._create_fallback_action()]
    
    def _create_action_from_data(self, action_data: Dict[str, Any]) -> Action:
        """Create an Action object from parsed JSON data"""
        from ..models.action_models import TargetType
        
        action_type = action_data["action_type"].lower()  # Convert to lowercase for enum
        properties = action_data.get("properties", {})
        target = action_data.get("target")
        target_type = action_data.get("target_type")
        reasoning = action_data.get("reasoning", "")
        
        # Convert target_type string to enum if provided
        if target_type and isinstance(target_type, str):
            try:
                target_type = TargetType(target_type.lower())
            except ValueError:
                target_type = None
        
        return Action(
            action_type=action_type,
            properties=properties,
            target=target,
            target_type=target_type,
            reasoning=reasoning
        )
    
    def _create_fallback_action(self) -> Action:
        """Create a simple fallback action"""
        return Action(
            action_type="speak",
            properties={
                "message": "I'm processing that...",
                "tone": "neutral"
            },
            initiator_id=self.npc_id,
            timestamp=datetime.now()
        )
    
    def _build_event_context(self, event: GameEvent, context: Dict[str, Any]) -> str:
        """Build a comprehensive context string for the agent"""
        
        context_parts = [
            f"EVENT: {event.event_type}",
            f"EVENT DETAILS: {event.description}",
            f"LOCATION: {event.location}",
            f"INITIATOR: {event.initiator}",
            f"TARGET: {event.target or 'none'}",
            f"WITNESSES: {', '.join(event.witnesses) if hasattr(event, 'witnesses') else 'none'}"
        ]
        
        if event.properties:
            context_parts.append(f"EVENT PROPERTIES: {json.dumps(event.properties, indent=2)}")
        
        if context:
            context_parts.append(f"ADDITIONAL CONTEXT: {json.dumps(context, indent=2)}")
        
        # Add recent memories
        recent_memories = self.npc_data.memory.short_term[-3:]
        if recent_memories:
            context_parts.append(f"RECENT MEMORIES: {json.dumps(recent_memories, indent=2)}")
        
        # Add current state
        context_parts.extend([
            f"CURRENT MOOD: {self.npc_data.state.mood}",
            f"CURRENT ENERGY: {self.npc_data.state.energy}%",
            f"CURRENT ACTIVITY: {self.npc_data.state.current_activity}"
        ])
        
        context_parts.append(
            "\nPlease respond to this event in character. Use the available tools to take appropriate actions."
        )
        
        return "\n".join(context_parts)
    
    def _update_state_after_action(self, action: Action):
        """Update NPC state after performing an action"""
        try:
            # Update activity based on action
            if action.action_type == ActionType.MOVE:
                self.npc_data.state.current_activity = "moving"
                # Update location if specified in properties
                if "location" in action.properties:
                    self.npc_data.state.current_location = action.properties["location"]
            elif action.action_type == ActionType.SPEAK:
                self.npc_data.state.current_activity = "talking"
            elif action.action_type == ActionType.EMOTE:
                # Update mood based on emotion
                if "emotion" in action.properties:
                    self.npc_data.state.mood = action.properties["emotion"]
            else:
                self.npc_data.state.current_activity = action.action_type.value
                
            # Decrease energy slightly for any action
            energy_cost = {
                ActionType.SPEAK: 1.0,
                ActionType.MOVE: 5.0,
                ActionType.EMOTE: 2.0,
                ActionType.INTERACT: 3.0,
                ActionType.WAIT: 0.5
            }.get(action.action_type, 1.0)
            
            self.npc_data.state.energy = max(0, self.npc_data.state.energy - energy_cost)
            
        except Exception as e:
            logger.error(f"Error updating state after action for NPC {self.npc_id}: {e}")
    
    def get_state_snapshot(self) -> Dict[str, Any]:
        """Get current state of the NPC"""
        return {
            "npc_id": self.npc_id,
            "name": self.npc_data.personality.name,
            "role": self.npc_data.personality.role,
            "location": self.npc_data.state.current_location,
            "activity": self.npc_data.state.current_activity,
            "mood": self.npc_data.state.mood,
            "health": self.npc_data.state.health,
            "energy": self.npc_data.state.energy,
            "memories_count": len(self.npc_data.memory.short_term) + len(self.npc_data.memory.long_term),
            "adk_available": ADK_AVAILABLE and self.agent is not None
        }
    
    def update_relationship(self, character: str, new_relationship: str, reason: str = ""):
        """Update relationship with another character"""
        self.npc_data.personality.relationships[character] = new_relationship
        
        # Remember this relationship change
        memory_entry = {
            "type": "relationship_change",
            "character": character,
            "new_relationship": new_relationship,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        self.npc_data.memory.add_memory(memory_entry)
    
    async def think_autonomously(self) -> Optional[Action]:
        """Allow the NPC to think and potentially take autonomous actions"""
        try:
            if not self.agent or not ADK_AVAILABLE:
                return None
                
            # Check if NPC should act autonomously based on current state
            if self.npc_data.state.energy < 30:
                return None  # Too tired to act autonomously
                
            # Create autonomous thinking prompt
            autonomous_prompt = f"""You are {self.npc_data.personality.name} and you have a moment to yourself.

Consider your current situation:
- Location: {self.npc_data.state.current_location}
- Current Activity: {self.npc_data.state.current_activity}
- Mood: {self.npc_data.state.mood}
- Energy: {self.npc_data.state.energy}%
- Goals: {', '.join(self.npc_data.personality.goals)}

Recent memories: {json.dumps(self.npc_data.memory.short_term[-2:], indent=2) if self.npc_data.memory.short_term else "None"}

Is there anything you want to do autonomously right now? This could be:
- Working towards one of your goals
- Reacting to something in your environment
- Taking care of your needs
- Or simply continuing your current activity

If you want to take an action, use the appropriate tool. If you're content to continue as you are, you don't need to do anything."""

            # Ensure session is created
            await self._ensure_session()
            
            # Use the agent to determine autonomous action
            content = types.Content(
                role="user",
                parts=[types.Part(text=autonomous_prompt)]
            )
            
            response = ""
            for event_result in self.runner.run(
                user_id=self.npc_id,
                session_id=self.session.id,
                new_message=content
            ):
                if event_result.is_final_response():
                    response = event_result.content.parts[0].text
                    break
            
            # Parse response for action
            action = self._parse_agent_response_to_action(response)
            
            # Only return action if it's not a wait (which means no autonomous action needed)
            if action.action_type != ActionType.WAIT:
                return action
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error in autonomous thinking for NPC {self.npc_id}: {e}")
            return None 