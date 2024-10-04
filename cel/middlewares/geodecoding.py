import os
from typing import Optional
from loguru import logger as log
from cel.assistants.base_assistant import BaseAssistant
from cel.gateway.model.base_connector import BaseConnector
from cel.gateway.model.message import Message
from cel.gateway.model.attachment import LocationAttachment
from cel.decoders.gcp_geocoding import googlev3_decode_location


class GeodecodingMiddleware: 
    """ Middleware to decode meesages with 'location' attachments and add the address to the message text.
    It uses Google Geocoding API to decode the location. 
    """
    
    def __init__(self, location_prefix_msg: str = "My location: "):
        log.debug("GeodecodingMiddleware initialized")
        # Check if environment variables are set
        GOOGLE_GEOCODING_API_KEY = os.getenv("GOOGLE_GEOCODING_API_KEY")
        if not GOOGLE_GEOCODING_API_KEY:
            self.enabled = False
            log.critical("Google Geocoding API Key not set. GeodecodingMiddleware disabled.")
        else:
            self.enabled = True
            
        self.location_prefix_msg = location_prefix_msg
        
    async def __call__(self, 
                       message: Message, 
                       connector: BaseConnector, 
                       assistant: BaseAssistant) -> bool:
        assert isinstance(message, Message), "Message must be a Message object"
        
        if not self.enabled:
            log.error("GeodecodingMiddleware disabled. Google Geocoding API Key not set.")
            return False
        
        try:    
            attachments = message.attachments or []
            # has location attachment?
            location_attachment: Optional[LocationAttachment] = next((attachment for attachment in attachments if attachment.type == "location"), None)
            if location_attachment:
                # get the location
                latitude = location_attachment.latitude
                longitude = location_attachment.longitude
                location_coordinates = (latitude, longitude)
                log.debug(f"Location coordinates: {location_coordinates}")
                # get the address
                address = googlev3_decode_location(location_coordinates)
                
                if address:
                    location_attachment.metadata["address"] = address
                    desc = f"({location_attachment.description})" if location_attachment.description else ""
                    
                    # ------------------------------------------------------------------
                    message.text = f"{self.location_prefix_msg} {desc} {address}"
                    # ------------------------------------------------------------------
                    
                    log.debug(f"{self.location_prefix_msg}{location_attachment}")
            return True
        except ValueError as e:
            log.error(f"Error processing Geodecoding: {e}")
            message.text = f"{self.location_prefix_msg}: Error decoding location."
            return True