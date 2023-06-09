from machine import ADC, Pin
from time import sleep


class RpiPico():
    INTEGRATED_TEMP_CORRECTION = 27  # Temperatura interna para corregir lecturas
    adc_voltage_correction = 0.706
    voltage_working = 3.3

    max = 0
    min = 0
    avg = 0
    current = 0
    locked = False

    def __init__(self, debug=False):

        self.DEBUG = debug

        self.TEMP_SENSOR = ADC(4)  # Sensor interno de raspberry pi pico.

        # Definición de GPIO
        self.LED_INTEGRATED = Pin(25, Pin.OUT)

        # 16bits factor de conversión, aunque la lectura real en raspberry pi pico es de 12bits.
        self.adc_conversion_factor = self.voltage_working / 65535

        # Realizo primera lectura de temperatura para inicializar variables y no comenzar a evaluar con 0 en estadísticas.
        sleep(0.100)
        self.resetStats()

    def resetStats(self, temp=None):
        """Reset Statistics"""

        temp = temp if temp else self.readSensorTemp()
        self.max = temp
        self.min = temp
        self.avg = temp
        self.current = temp

    def readSensorTemp(self):
        if self.locked:
            return self.current

        reading = (self.TEMP_SENSOR.read_u16() * self.adc_conversion_factor) - \
            self.adc_voltage_correction

        value = self.INTEGRATED_TEMP_CORRECTION - reading / 0.001721  # Formula given in RP2040 Datasheet

        cpu_temp = round(float(value), 1)
        self.current = cpu_temp

        # Estadísticas
        if cpu_temp > self.max:
            self.max = cpu_temp
        if cpu_temp < self.min:
            self.min = cpu_temp

        self.avg_cpu_temp = round(float((self.avg + cpu_temp) / 2), 1)

        return round(float(cpu_temp), 1)

    def getTemp(self):
        cpu_temp = self.readSensorTemp()

        return round(float(cpu_temp), 1)

    def ledOn(self):
        self.LED_INTEGRATED.on()

    def ledOff(self):
        self.LED_INTEGRATED.off()

    def getStats(self):
        """ Get Statistics formated as a dictionary"""

        return {
            'max': round(float(self.max), 1),
            'min': round(float(self.min), 1),
            'avg': round(float(self.avg), 1),
            'current': round(float(self.current), 1)
        }

    def readAnalogInput(self, pin):
        """
        Read analog value from pin
        Lectura del ADC a 16 bits (12bits en raspberry pi pico, traducido a 16bits)
        """

        reading = ADC(pin).read_u16()

        print("Lectura raw :", reading)

        #print("Lectura pin :" + str(pin))

        #readingParse = ((reading - self.adc_voltage_correction)
        #                * self.adc_conversion_factor)
        #print("Lectura pin :" + str(pin),
        #      (reading / 65535) * self.voltage_working)

        #print("Lectura parseada: " + str(readingParse))

        #print("raw: " + str(reading))
        #print("adc_voltage_correction: " + str(self.adc_voltage_correction))

        #print("voltaje: " + str(self.voltage_working -
        #                        ((reading / 65535) * self.voltage_working)))

        return self.voltage_working - ((reading / 65535) * self.voltage_working)
        # return (reading / 65535) * self.voltage_working
        
        ------------------------------------------- CODIGO 2 ----------------------------------------------------------
        
      rom Models.RpiPico import RpiPico
from time import sleep

from machine import Pin

controller = RpiPico(debug=True)
controller.ledOn()

WATER_PUMP = Pin(12, Pin.OUT)
WATER_SENSOR = Pin(8, Pin.IN)

TIMEOUT_WATER_IRRIGATION = 3 # Tiempo de riego en segundos.

def check_water():
    return bool(WATER_SENSOR.value())

def soil_moisture_correct():
    soil_read_1 = controller.readAnalogInput(28)
    #soil_read_2 = controller.readAnalogInput(26)
    #print(soil_read_1, soil_read_2)
    print(soil_read_1)

    if soil_read_1 < 2:
        return False

    return True

def water_pump():
    if check_water():
        print('REGANDO')
        WATER_PUMP.value(1)
        sleep(TIMEOUT_WATER_IRRIGATION)
        WATER_PUMP.value(0)
    else:
        print('NO HAY AGUA')


def loop():
    controller.ledOn()

    # Compruebo ambos sensores, en caso de uno faltarle agua activar motor.
    if not soil_moisture_correct():
        water_pump()

    sleep(1)
    controller.ledOff()
    sleep(1)


while True:
    try:
        loop()
    except Exception as e:
        print('Error en el loop', e)
        WATER_PUMP.value(0)  
