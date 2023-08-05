class NotEncryptedDeviceType(Exception):
    "Error to raise when trying to provide a passphrase for devices that are not encrypted"

    def __init__(self, device_id):
        self.message = f'The device with id {device_id} is not encrypted! You cannot enter a passphrase.'
