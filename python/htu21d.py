import Adafruit_GPIO.FT232H as FT232H
from time import sleep


class HTU21D():

    def __init__(self):
        # Temporarily disable FTDI serial drivers.
        FT232H.use_FT232H()
        # Find the first FT232H device.
        ft232h = FT232H.FT232H()
        self._i2c = FT232H.I2CDevice(ft232h, 0x40)

    def read_temperature(self):
        self._i2c.writeList(0xE3, [])
        sleep(0.05)
        response = self._i2c.readBytes(3)
        if not self.crc8check(response):
            return
        temphigh = response[0]
        templow = response[1]
        crc = response[2]
        _STATUS_LSBMASK     = 0b11111100
        temp = (temphigh << 8) | (templow & _STATUS_LSBMASK)
        temperature = -46.85 + (175.72 * temp) / 2**16
        return temperature

    def read_humidity(self):
        self._i2c.writeList(0xE5, [])
        sleep(0.05)
        response = self._i2c.readBytes(3)
        if not self.crc8check(response):
            return
        humidhigh = response[0]
        humidlow = response[1]
        crc = response[2]
        _STATUS_LSBMASK     = 0b11111100
        humid = (humidhigh << 8) | (humidlow & _STATUS_LSBMASK)
        humidity = -6 + (125.0 * humid) / 2**16
        return humidity

    def crc8check(self, value):
        """Calulate the CRC8 for the data received"""
        try:
            # Ported from Sparkfun Arduino HTU21D Library: https://github.com/sparkfun/HTU21D_Breakout
            remainder = ( ( value[0] << 8 ) + value[1] ) << 8
            remainder |= value[2]
        except:
            return False
        # POLYNOMIAL = 0x0131 = x^8 + x^5 + x^4 + 1
        # divsor = 0x988000 is the 0x0131 polynomial shifted to farthest left of three bytes
        divsor = 0x988000
        for i in range(0, 16):
            if( remainder & 1 << (23 - i) ):
                remainder ^= divsor
            divsor = divsor >> 1
        if remainder == 0:
            return True
        else:
            return False

if __name__ == "__main__":
    htu = HTU21D()
    print("Temperature: {} F".format(htu.read_temperature()))
    print("Humidity: {} %".format(htu.read_humidity()))
