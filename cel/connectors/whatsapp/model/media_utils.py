from loguru import logger as log
import requests
import os
import mimetypes
from requests_toolbelt.multipart.encoder import MultipartEncoder
from typing import Union, Dict, Any
from cel.connectors.whatsapp.constants import BASE_URL
from cel.connectors.whatsapp.utils import build_headers


def upload_media(media: str, token: str, phone_number_id: str) -> Union[Dict[Any, Any], None]:
    """
    Uploads a media to the cloud api and returns the id of the media

    Args:
        media[str]: Path of the media to be uploaded
        token[str]: The Meta Access Token
        phone_number_id[str]: The Meta Phone Number Id

    ref: https://developers.facebook.com/docs/whatsapp/cloud-api/reference/media#
    """
    assert token is not None, "Token not provided"
    assert phone_number_id is not None, "Phone number id not provided"
    assert media is not None, "Media not provided"

    form_data = {
        "file": (
            media,
            open(os.path.realpath(media), "rb"),
            mimetypes.guess_type(media)[0],
        ),
        "messaging_product": "whatsapp",
        "type": mimetypes.guess_type(media)[0],
    }
    form_data = MultipartEncoder(fields=form_data)
    headers = build_headers(token)
    headers["Content-Type"] = form_data.content_type
    log.info(f"Content-Type: {form_data.content_type}")
    log.info(f"Uploading media {media}")
    r = requests.post(
        f"{BASE_URL}/{phone_number_id}/media",
        headers=headers,
        data=form_data,
    )
    if r.status_code == 200:
        log.info(f"Media {media} uploaded")
        return r.json()
    log.info(f"Error uploading media {media}")
    log.info(f"Status code: {r.status_code}")
    log.info(f"Response: {r.json()}")
    return None


def delete_media(media_id: str, token: str) -> Union[Dict[Any, Any], None]:
    """
    Deletes a media from the cloud api

    Args:
        media_id[str]: Id of the media to be deleted
        token[str]: The Meta Access Token
    """
    assert token is not None, "Token not provided"
    assert media_id is not None, "Media id not provided"
    
    log.info(f"Deleting media {media_id}")
    r = requests.delete(
        f"{BASE_URL}/{media_id}", headers=build_headers(token))
    if r.status_code == 200:
        log.info(f"Media {media_id} deleted")
        return r.json()
    log.info(f"Error deleting media {media_id}")
    log.info(f"Status code: {r.status_code}")
    log.info(f"Response: {r.json()}")
    return None


def query_media_url(media_id: str, token: str) -> Union[str, None]:
    """
    Query media url from media id obtained either by manually uploading media or received media

    Args:
        media_id[str]: Media id of the media
        token[str]: The Meta Access Token

    Returns:
        str: Media url
    """
    assert media_id is not None, "Media id not provided"
    assert BASE_URL is not None, "Base url not provided"
    assert token is not None, "Token not provided"

    log.info(f"Querying media url for {media_id}")
    r = requests.get(f"{BASE_URL}/{media_id}", headers=build_headers(token))
    if r.status_code == 200:
        log.info(f"Media url queried for {media_id}")
        url = r.json()["url"]
        return url
    log.info(f"Media url not queried for {media_id}")
    log.info(f"Status code: {r.status_code}")
    log.info(f"Response: {r.json()}")
    return None


def download_media(media_url: str, 
                   mime_type: str, 
                   token: str, 
                   file_path: str = "temp"
                  ) -> Union[str, None]:
    """
    Download media from media url obtained either by manually uploading media or received media

    Args:
        media_url[str]: Media url of the media
        mime_type[str]: Mime type of the media
        file_path[str]: Path of the file to be downloaded to. Default is "temp"
                        Do not include the file extension. It will be added automatically.
        token[str]: The Meta Access Token
        
    Returns:
        str: Media url
    """
    assert media_url is not None, "Media url not provided"
    assert mime_type is not None, "Mime type not provided"
    assert token is not None, "Token not provided"
    
    r = requests.get(media_url, headers=build_headers(token))
    content = r.content
    extension = mime_type.split("/")[1]
    save_file_here = None
    # create a temporary file
    try:

        save_file_here = (
            f"{file_path}.{extension}" if file_path else f"temp.{extension}"
        )
        with open(save_file_here, "wb") as f:
            f.write(content)
        log.info(f"Media downloaded to {save_file_here}")
        return f.name
    except Exception as e:
        log.info(e)
        log.error(f"Error downloading media to {save_file_here}")
        return None
