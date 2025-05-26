"""
This module contains predefined response messages for various HTTP status codes
used in the Support System application.

Copyright (c) Supportix. All rights reserved.
Written in 2025 by Dorna Raj Gyawali <dronarajgyawali@gmail.com>
"""

SUCESS_SIGNUP = {"User created Successfully"}
CONTEXT_400 = {"Invalid credentials"}
CONTEXT_405 = {"Request method not allowed."}
CONTEXT_403 = "Unauthorized access."
ImageAttachementExt = [
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
FileAttachementExt = [".pdf"]
FileAttachemenSize = 20 * 1024 * 1024
ImageAttachemenSize = 5 * 1024 * 1024
