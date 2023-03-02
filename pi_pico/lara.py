import machine
import microcontroller
import socket
import math
import utime
import network
import time

class stepper:
    def _init_(step_pin,direction_pin,rps,delay):
        self.step_pin=machine.Pin(step_pin,machine.Pin.OUT)
        self.direction_pin=machine.Pin(direction_pin,machine.Pin.OUT)
        self.rps=rps
        self.rpms=rps*1000
        self.delay=delay
    def rev(dir,rev):
        ticks=time.ticks_ms()
        while time.ticks_ms()-ticks<=math.floor(rev/rpms):
            if(dir):
                self.direction_pin.high()
            else:
                self.direction_pin.low()
            self.step_pin.high()
            time.sleep_ms(self.delay)
            self.step_pin.low()
            time.sleep_ms(self.delay)
        return 1

class HCSR04:
    def __init__(self, trigger_pin, echo_pin, echo_timeout_us=500*2*30):
        self.echo_timeout_us = echo_timeout_us
        self.trigger = Pin(trigger_pin, mode=Pin.OUT, pull=None)
        self.trigger.value(0)
        self.echo = Pin(echo_pin, mode=Pin.IN, pull=None)

    def _send_pulse_and_wait(self):
        self.trigger.value(0)
        time.sleep_us(5)
        self.trigger.value(1)
        time.sleep_us(10)
        self.trigger.value(0)
        try:
            pulse_time = machine.time_pulse_us(self.echo, 1, self.echo_timeout_us)
            return pulse_time
        except OSError as ex:
            if ex.args[0] == 110: 
                raise OSError('Out of range')
            raise ex

    def distance_mm(self):
        pulse_time = self._send_pulse_and_wait()
        mm = pulse_time * 100 // 582
        return mm

    def distance_cm(self):
        pulse_time = self._send_pulse_and_wait()
        cms = (pulse_time / 2) / 29.1
        return cms


class ADXL345:
    def __init__(self,i2c,addr=const(0x53)):
        self.device = device
        self.regAddress = const(0x32)
        self.TO_READ = 6
        self.buff = bytearray(6)
        self.addr = addr
        self.i2c = i2c
        b = bytearray(1)
        b[0] = 0
        self.i2c.writeto_mem(self.addr,0x2d,b)
        b[0] = 16
        self.i2c.writeto_mem(self.addr,0x2d,b)
        b[0] = 8
        self.i2c.writeto_mem(self.addr,0x2d,b)

    @property
    def xValue(self):
        self.buff = self.i2c.readfrom_mem(self.addr,self.regAddress,self.TO_READ)
        x = (int(buff[1]) << 8) | buff[0]
        if x > 32767:
            x -= 65536
        return x
   
    @property
    def yValue(self):
        self.buff = self.i2c.readfrom_mem(self.addr,self.regAddress,self.TO_READ)
        y = (int(self.buff[3]) << 8) | self.buff[2]
        if y > 32767:
            y -= 65536
        return y
     
    @property   
    def zValue(self): 
        self.buff = self.i2c.readfrom_mem(self.addr,self.regAddress,self.TO_READ)
        z = (int(self.buff[5]) << 8) | self.buff[4]
        if z > 32767:
            z -= 65536
        return z
           
    def RP_calculate(self,x,y,z):
        roll = math.atan2(y , z) * 57.3
        pitch = math.atan2((- x) , math.sqrt(y * y + z * z)) * 57.3
        return roll,pitch
