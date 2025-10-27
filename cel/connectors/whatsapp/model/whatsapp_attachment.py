from aiogram import Bot
from loguru import logger as log
from cel.connectors.whatsapp.model.media_utils import query_media_url
from cel.gateway.model.attachment import FileAttachment, \
                                        LocationAttachment, \
                                        MessageAttachmentType, \
                                        ContactAttachment


sample_data = {
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "11232312744885411",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "15553453411",
              "phone_number_id": "16563546234234211"
            },
            "contacts": [
              {
                "profile": { "name": "Ruben Sarasa" },
                "wa_id": "52161231257911"
              }
            ],
            "messages": [
              {
                "from": "52161231257911",
                "id": "wamid.SDFAASDASDSADS==",
                "timestamp": "1746830741",
                "type": "contacts",
                "contacts": [
                  {
                    "name": {
                      "first_name": "Jonathan",
                      "last_name": "Doe",
                      "formatted_name": "Jonathan Doe"
                    },
                    "phones": [
                      {
                        "phone": "+1 123 205 1111",
                        "wa_id": "5216621111",
                        "type": "CELL"
                      }
                    ]
                  }
                ]
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
        if 'contacts' in msg:
            log.info("Loading contact from message")
            return await cls.load_contact_from_message(data)
            
        # if 'voice' in msg:
        #     return await cls.load_audio_from_message(message, token)
        # if 'location' in msg:
        #     return await cls.load_location_from_message(message)
        
    @classmethod
    async def load_image_from_message(cls, data: dict, token: str, phone_number_id: str):
        
        msg = data.get("entry")[0].get("changes")[0].get("value").get("messages")[0]
        image = msg.get('image')
        
        caption = image.get('caption', '')
        mime_type = image.get('mime_type', 'image/jpeg')
        file_id = image.get('id')
        sha256 = image.get('sha256')
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
    

    @classmethod
    async def load_contact_from_message(cls, data: dict):
        msg = data.get("entry")[0].get("changes")[0].get("value").get("messages")[0]
        contact = msg.get('contacts')[0]
        name = contact.get('name', {}).get('formatted_name', '')
        metadata = contact        

        return ContactAttachment(
            name=name,
            metadata=metadata
        )