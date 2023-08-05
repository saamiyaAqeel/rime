class NotEncryptedDeviceType(Exception):
    "Error to raise when trying to provide a passphrase for devices that are not encrypted"

    def __init__(self, device_id):
        self.message = f'The device with id {device_id} is not encrypted! You cannot enter a passphrase.'


class DeviceNotFound(Exception):
    "Error to show when no device with device_id is being tracked by RIME."

    def __init__(self, device_id):
        self.message = f'Device with ID "{device_id}" not found in RIME.'
        super().__init__(self.message)
