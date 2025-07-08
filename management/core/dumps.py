"""
This module contains predefined response messages for various HTTP status codes
used in the Support System application.

Copyright (c) Supportix. All rights reserved.
Written in 2025 by Dorna Raj Gyawali <dronarajgyawali@gmail.com>
"""
# context that is used while building Restapi
SUCESS_SIGNUP = {"User created Successfully"}
CONTEXT_400 = {"Invalid credentials"}
CONTEXT_405 = {"Request method not allowed."}
CONTEXT_403 = "Unauthorized access."


# image configuration for this app: Can be changed acccording to the need.
ImageAttachmentExt = [
    ".jpeg",
    ".jpg",
    ".png",
    ".gif",
    ".bmp",
    ".tiff",
    ".tif",
    ".webp",
    ".svg",
    ".heic",
    ".ico",
]
FileAttachmentExt = [".pdf"]
FileAttachmentSize = 20 * 1024 * 1024  #20 mb
ImageAttachmentSize = 5 * 1024 * 1024 # 5 mb
OVERLOAD_THRESHOLD = 50
UNDERUTILIZED_THRESHOLD = 10
BATCH_SIZE = 100
