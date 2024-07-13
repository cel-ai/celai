from aiogram import Bot
from loguru import logger as log
from cel.connectors.whatsapp.model.media_utils import query_media_url
from cel.gateway.model.attachment import FileAttachment, \
                                                LocationAttachment, \
                                                MessageAttachmentType

# class TelegramLocationAttachment(LocationAttachment):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)

sample_data = {
    "object": "whatsapp_business_account",
    "entry": [
        {
            "id": "103048736088448",
            "changes": [
                {
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "15550463673",
                            "phone_number_id": "105602452496989"
                        },
                        "contacts": [
                            {
                                "profile": {
                                    "name": "John Doe"
                                },
                                "wa_id": "134911669XXXXX"
                            }
                        ],
                        "messages": [
                            {
                                "from": "134911669XXXXX",
                                "id": "wamid.HBgNNTQ5MTE2NjkzNzg0OBUCABIYFDNBRkEzN0ZFMDXXXX==",
                                "timestamp": "1717858794",
                                "type": "image",
                                "image": {
                                    "caption": "Take a look",
                                    "mime_type": "image/jpeg",
                                    "sha256": "dEctuifbo+EGLhzh3H5KAuaS1b9fnn10LMpZBqiSmjA=",
                                    "id": "971782074594239"
                                }
                            }
                        ]
                    },
                    "field": "messages"
                }
            ]
        }
    ]
}


class WhatsappAttachment(FileAttachment):

    def __init__(self,  
                 type: MessageAttachmentType = None,
                 title: str = None,
                 description: str = None,
                 mimeType: str = None,
                 metadata: any = None,
                 fileSize: int = None,
                 width: int = None,
                 height: int = None,
                 file_url: str = None,
                 caption: str = None):
        
        super().__init__(title, description, mimeType=mimeType, metadata=metadata, type=type)
        self.fileSize: int = fileSize
        self.width: int = width
        self.height: int = height
        assert isinstance(file_url, str), "file_url must be a string"
        self.file_url = file_url
        # self.file_url: str = file_url,
        self.caption: str = caption
    
    def to_dict(self):
        data = super().to_dict()
        data['fileSize'] = self.fileSize
        data['width'] = self.width
        data['height'] = self.height
        data['file_url'] = self.file_url
        return data
    
    @classmethod
    def from_dict(cls, attachment_dict):
        return WhatsappAttachment(
            title=attachment_dict.get("title"),
            description=attachment_dict.get("description"),
            content=attachment_dict.get("content"),
            mimeType=attachment_dict.get("mimeType"),
            metadata=attachment_dict.get("metadata"),
            fileSize=attachment_dict.get("fileSize"),
            width=attachment_dict.get("width"),
            height=attachment_dict.get("height"),
            file_url=attachment_dict.get("file_url")
        )
    
    def __str__(self):
        return f"WhatsappAttachment: {self.title}"
    
    def __repr__(self):
        return f"WhatsappAttachment: {self.title}"
    
    
    @classmethod
    async def load_from_message(cls, data: dict, token: str, phone_number_id: str):
        assert isinstance(data, dict), "data must be a dictionary"
        msg = data.get("entry")[0].get("changes")[0].get("value").get("messages")[0]

        # check if the message has a photo
        if 'image' in msg:
            log.info("Loading image from message")
            return await cls.load_image_from_message(data, token, phone_number_id)
        # if 'voice' in msg:
        #     return await cls.load_audio_from_message(message, token)
        # if 'location' in msg:
        #     return await cls.load_location_from_message(message)
        
    @classmethod
    async def load_image_from_message(cls, data: dict, token: str, phone_number_id: str):
        
        msg = data.get("entry")[0].get("changes")[0].get("value").get("messages")[0]
        image = msg.get('image')
        
        caption = image['caption']
        mime_type = image['mime_type']
        file_id = image['id']
        sha256 = image['sha256']
        file_url = query_media_url(file_id, token)
        metadata = {
            'sha256': sha256,
            'file_id': file_id,
            'caption': caption,
            'phone_number_id': phone_number_id,
            'token': token
        }
        
        return WhatsappAttachment(
            type=MessageAttachmentType.IMAGE,
            title=caption,
            description="photo",
            file_url=file_url,
            mimeType=mime_type,
            metadata=metadata,
            fileSize=None,
            width=None,
            height=None
        )        
    
            
        
        
        
    # @classmethod
    # async def load_location_from_message(cls, message: dict):
    #     msg = message.get("message")
    #     location = msg.get('location')
    #     latitude = location['latitude']
    #     longitude = location['longitude']
    #     metadata = {}
    #     description = ""
    #     if 'venue' in msg:
    #         venue = msg['venue']
    #         metadata['title'] = venue.get('title')
    #         metadata['address'] = venue.get('address')
    #         metadata['foursquare_id'] = venue.get('foursquare_id')
    #         metadata['foursquare_type'] = venue.get('foursquare_type')  
    #         description = venue['title'] + " at " + venue['address'] + "(" + venue.get('foursquare_type') + ")"
        
    #     return TelegramLocationAttachment(latitude=latitude, 
    #                                       longitude=longitude,
    #                                       description=description,
    #                                       metadata=metadata)
        
    # @classmethod
    # async def load_audio_from_message(cls, message: dict, token: str):
        
    #     msg = message.get("message")
    #     audio = msg['voice']
    #     file_id = audio['file_id']
    #     file_unique_id = audio['file_unique_id']
    #     file_size = audio['file_size']
    #     duration = audio['duration']
    #     mime_type = audio['mime_type']
    #     metadata = {
    #         'file_id': file_id,
    #         'file_unique_id': file_unique_id,
    #         'file_size': file_size,
    #         'duration': duration,
    #         'mime_type': mime_type
    #     }
        
    #     # get file url
    #     file_url = "https://es.wikipedia.org/static/images/icons/wikipedia.png"
    #     if file_id != '123':
    #         bot = Bot(token=token)
    #         file = await bot.get_file(file_id)
    #         file_url = f"https://api.telegram.org/file/bot{token}/{file.file_path}" 
        
    #     return TelegramAttachment(
    #         type=MessageAttachmentType.VOICE,
    #         title="audio",
    #         description="audio",
    #         mimeType=mime_type,
    #         metadata=metadata,
    #         fileSize=file_size,
    #         width=None,
    #         height=None,
    #         file_url=file_url
    #     )


    # @classmethod
    # async def load_image_from_message(cls, message: dict, token: str):
        
    #     msg = message.get("message")
        
    #     photo = msg['photo'][-1]
    #     file_id = photo['file_id']
    #     file_unique_id = photo['file_unique_id']
    #     file_size = photo['file_size']
    #     width = photo['width']
    #     height = photo['height']
    #     metadata = {
    #         'file_id': file_id,
    #         'file_unique_id': file_unique_id,
    #         'file_size': file_size,
    #         'width': width,
    #         'height': height
    #     }
        
    #     # get file url
    #     file_url = f"https://es.wikipedia.org/static/images/icons/wikipedia.png"
    #     if file_id != '123':
    #         bot = Bot(token=token)
    #         file = await bot.get_file(file_id)
    #         file_url = file.file_path
        
    #     return TelegramAttachment(
    #         type=MessageAttachmentType.IMAGE,
    #         title="photo",
    #         description="photo",
    #         mimeType="image/jpeg",
    #         metadata=metadata,
    #         fileSize=file_size,
    #         width=width,
    #         height=height,
    #         file_url=file_url
    #     )        
    
    