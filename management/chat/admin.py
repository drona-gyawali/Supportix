from django.contrib import admin

from chat.models import (ChatGroup, FileAttachment, GroupMessage,
                         ImageAttachment)

admin.site.register(ChatGroup)
admin.site.register(GroupMessage)
admin.site.register(FileAttachment)
admin.site.register(ImageAttachment)
