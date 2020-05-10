# -*- coding: utf-8 -*-
# This is the code for the hangman game as an Alexa skill.  

import logging
import random
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

#allWords = ['hunter', 'positive', 'memory', 'depth', 'slope', 'border']
allWords = ['POSITIVE', 'DEPTH', 'SLOPE']

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        sessionAttributes = handler_input.attributes_manager.session_attributes
        sessionAttributes["chosenWord"] = None
        sessionAttributes["foundLetters"] = []
        sessionAttributes["foundLocations"] = []
        sessionAttributes["gamePlayingStatus"] = False
        
        speak_output = "Welcome to Hangman game. Say 'Let's play' to start the game or hear the insturctions by saying 'How to play'."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class GamePlayIntentHandler(AbstractRequestHandler):
    """Handler for GamePlay Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GamePlayIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        sessionAttributes = handler_input.attributes_manager.session_attributes
        sessionAttributes["gamePlayingStatus"] = True
        sessionAttributes["chosenWord"] = random.choice(allWords)
        
        speak_output = "The word is " + str(len(sessionAttributes["chosenWord"])) + " letters long."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class IdentifyLetterIntentHandler(AbstractRequestHandler):
    """Handler for IdentifyLetter Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("IdentifyLetterIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        sessionAttributes = handler_input.attributes_manager.session_attributes
        spokenLetterValue = ask_utils.request_util.get_slot(handler_input, "SpokenLetter").value
        
        if spokenLetterValue is not None:
            spokenLetterValue = spokenLetterValue[0]
        else:
            speak_output = "I did not get that. Could you repeat that?"
        
        if sessionAttributes["gamePlayingStatus"]:
            if spokenLetterValue not in sessionAttributes["foundLetters"]:
                if spokenLetterValue in sessionAttributes["chosenWord"]:
                    foundLocations = []
                    
                    locationValue = 1
                    for character in sessionAttributes["chosenWord"]:
                        if character == spokenLetterValue:
                            foundLocations.append(locationValue)
                            
                            sessionAttributes["foundLocations"].append(locationValue)
                            sessionAttributes["foundLetters"].append(spokenLetterValue)
                        locationValue += 1
                    
                    if(len(sessionAttributes["foundLocations"]) == len(sessionAttributes["chosenWord"])):
                        speak_output = "You have succesfully guessed the word and is it " + sessionAttributes["chosenWord"] + ". Say 'Let's play' to start again."
                        sessionAttributes["gamePlayingStatus"] = False
                    else:
                        speak_output = "The letter " + spokenLetterValue + " is present at locations - " + str(foundLocations) + "."
                else:
                    speak_output = "The letter " + spokenLetterValue + " is not present in the word." 
            else:
                speak_output = "The letter " + spokenLetterValue + " has already been said." 
        else:
            speak_output = "I did not get that. Could you repeat that?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())

# IntentHandlers for the custom added Intents
sb.add_request_handler(GamePlayIntentHandler())
sb.add_request_handler(IdentifyLetterIntentHandler())

sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_request_handler(IntentReflectorHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()