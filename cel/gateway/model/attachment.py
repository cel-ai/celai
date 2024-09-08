from abc import ABC

class MessageAttachmentType:
    IMAGE = "image"
    AUDIO = "audio"
    VOICE = "voice"
    VIDEO = "video"
    DOCUMENT = "document"
    LINK = "link"
    LOCATION = "location"
    CONTACT = "contact"
    CUSTOM = "custom"

class MessageAttachment(ABC):
    def __init__(self, type: MessageAttachmentType = None) -> None:
        self.type = type
        

class LocationAttachment(MessageAttachment):
    def __init__(self, 
                 latitude: float, 
                 longitude: float, 
                 description: str = None,
                 metadata: any = None):
        super().__init__(type=MessageAttachmentType.LOCATION)
        self.latitude: float = latitude
        self.longitude: float = longitude
        self.metadata: any = metadata
        self.description: str = description

    def to_dict(self):
        data = {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'metadata': self.metadata
        }
        return data

    @classmethod
    def from_dict(cls, attachment_dict):
        return LocationAttachment(
            latitude=attachment_dict.get("latitude"),
            longitude=attachment_dict.get("longitude"),
            metadata=attachment_dict.get("metadata")
        )

    def __str__(self):
        return f"LocationAttachment: {self.latitude}, {self.longitude}"
    
    def __repr__(self):
        return f"LocationAttachment: {self.latitude}, {self.longitude}"

class FileAttachment(MessageAttachment):
    def __init__(self, 
                 title: str = None, 
                 description: str = None, 
                 content: any = None, 
                 mimeType: str = None,
                 file_url: str = None,
                 metadata: any = None,
                 type: MessageAttachmentType = None):
        self.title: str = title
        self.description: str = description
        self.content: any = content
        self.mimeType: str = mimeType
        self.file_url: str = file_url
        self.metadata: any = metadata
        self.type = type

    def to_dict(self):
        data = {
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'mimeType': self.mimeType,
            'file_url': self.file_url,
            'metadata': self.metadata
        }
        return data

    @classmethod
    def from_dict(cls, attachment_dict):
        return FileAttachment(
            title=attachment_dict.get("title"),
            description=attachment_dict.get("description"),
            content=attachment_dict.get("content"),
            mimeType=attachment_dict.get("mimeType"),
            metadata=attachment_dict.get("metadata"),
            file_url=attachment_dict.get("file_url")
        )

    def __str__(self):
        return f"MessageAttachment: {self.title}"
    
    def __repr__(self):
        return f"MessageAttachment: {self.title}"
 