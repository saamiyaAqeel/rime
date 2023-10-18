"""
The name and friendly name of each provider. Placed here so that the generic provider may use them.
"""

ANDROID_CONTACTS = 'android-com.android.providers.contacts'
ANDROID_CONTACTS_FRIENDLY = 'Android Contacts'
ANDROID_GENERIC = 'android-generic'
ANDROID_GENERIC_FRIENDLY = 'Android Generic'
ANDROID_GENERIC_MEDIA = 'android-generic-media'
ANDROID_GENERIC_MEDIA_FRIENDLY = 'Android Generic Media'
ANDROID_TELEPHONY = "android-com.android.providers.telephony"
ANDROID_TELEPHONY_FRIENDLY = "Android Telephony"
ANDROID_WHATSAPP = 'android-com.whatsapp.android'
ANDROID_WHATSAPP_FRIENDLY = 'Android WhatsApp'
ANDROID_CAMERA = 'android-com.android.camera'
ANDROID_CAMERA_FRIENDLY = 'Android Camera'
ANDROID_CAMERA2_HMDGLOBAL = 'android-com.hmdglobal.camera2'
ANDROID_CAMERA2_HMDGLOBAL_FRIENDLY = 'Android Camera (HMD Global, Camera2)'
IOS_IMESSAGE = 'ios-com.apple.messages'
IOS_IMESSAGE_FRIENDLY = 'iOS Messages'
IOS_CONTACTS = 'ios-AddressBook'
IOS_CONTACTS_FRIENDLY = 'iOS Contacts'
IOS_WHATSAPP = 'ios-net.whatsapp.WhatsApp'
IOS_WHATSAPP_FRIENDLY = 'iOS WhatsApp'

FRIENDLY_NAMES = {
    ANDROID_CONTACTS: ANDROID_CONTACTS_FRIENDLY,
    ANDROID_GENERIC_MEDIA: ANDROID_GENERIC_MEDIA_FRIENDLY,
    ANDROID_GENERIC: ANDROID_GENERIC_FRIENDLY,
    ANDROID_TELEPHONY: ANDROID_TELEPHONY_FRIENDLY,
    ANDROID_WHATSAPP: ANDROID_WHATSAPP_FRIENDLY,
    ANDROID_CAMERA: ANDROID_CAMERA_FRIENDLY,
    ANDROID_CAMERA2_HMDGLOBAL: ANDROID_CAMERA2_HMDGLOBAL_FRIENDLY,
    IOS_IMESSAGE: IOS_IMESSAGE_FRIENDLY,
    IOS_CONTACTS: IOS_CONTACTS_FRIENDLY,
    IOS_WHATSAPP: IOS_WHATSAPP_FRIENDLY,
}


# Sanity check on import
def _check_friendlies():
    for name, value in globals().items():
        if (name.startswith('ANDROID_') or name.startswith('IOS_')) \
                and not name.endswith('FRIENDLY') \
                and value not in FRIENDLY_NAMES:
            raise ValueError(f'No friendly name for {name}')


_check_friendlies()
