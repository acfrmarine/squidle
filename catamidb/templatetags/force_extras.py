import os
import Image
from django.template import Library
from urlparse import urlparse
import httplib

register = Library()

def exists(site, path):
    conn = httplib.HTTPConnection(site)
    conn.request('HEAD', path)
    response = conn.getresponse()
    conn.close()
    return response.status == 200

def websafe_image(image_url):
    """@brief Returns equivalent PNG/JPEG url if file is TIFF format


    Examples:
    <img src="object.src.url" alt="original image" />
    <img src="object.image.src|websafe_image" alt="PNG version of image" />


    """
    if image_url:
        url_data = urlparse(image_url)

        basepath, _format = url_data.path.rsplit('.', 1)

        new_url_png = url_data.scheme + '://' + url_data.netloc + basepath + '.png'
        if exists(url_data.netloc, basepath + '.png'):
            return new_url_png
        
        new_url_jpg = url_data.scheme + '://' + url_data.netloc + basepath + '.jpg'
        if exists(url_data.netloc, basepath + '.jpg'):
            return new_url_jpg

        # png_url = urlparse(new_url_png)
        # url_address = png_url.scheme + '://' + png_url.netloc

        # if exists(url_address, png_url.path):
        #     return new_url_png

    return image_url

register.filter(websafe_image)