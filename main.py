#!/usr/bin/python
# -*- coding:utf-8 -*-
# code for balloon package
# atsclct  11.2023
import uasyncio as asyncio
import time
import MPU925x #Gyroscope/Acceleration/Magnetometer
import BME280   #Atmospheric Pressure/Temperature and humidity
import LTR390   #UV
import TSL2591  #LIGHT
import SGP40
import VOC_Algorithm
import math, time, uos
import ozone, gas_gmxx, sdcard, sdc4x, sds011, gnss
from ssd1306 import SSD1306_I2C
from rylr import RYLR
from machine import Pin, I2C, UART, SPI
uart = UART(1, baudrate=115200, rx=Pin(5), tx=Pin(4))
rylr = RYLR(uart)
i2c = I2C(0, scl=Pin(21), sda=Pin(20), freq=400000)
i2c1 = I2C(1, scl=Pin(27), sda=Pin(26), freq=400000)

oled = SSD1306_I2C(128, 64, i2c1)
oled.fill(0)
oled.text('starting',8,20)
oled.show()

print(i2c.scan())
print(i2c1.scan())
led=Pin(25,Pin.OUT)
gps = gnss.DFRobot_GNSS_I2C(i2c1, gnss.GNSS_DEVICE_ADDR)
bme280 = BME280.BME280()
bme280.get_calib_param()
light = TSL2591.TSL2591()
sgp = SGP40.SGP40()
voc_sgp = VOC_Algorithm.VOC_Algorithm()
uv = LTR390.LTR390()
mpu = MPU925x.MPU925x()
o3 = ozone.DFRobot_Ozone_IIC(i2c1 ,ozone.OZONE_ADDRESS_3)
o3.set_mode(ozone.MEASURE_MODE_AUTOMATIC)
gas = gas_gmxx.GAS_GMXXX (i2c1 ,0x08)
gas.preheat()
scd4x = sdc4x.SCD4X(i2c_bus=i2c1,address=0x62)
scd4x.temperature_offset = 5.4
scd4x.altitude = 15
scd4x.self_calibration_enabled = True
scd4x.persist_settings()
scd4x.start_periodic_measurement()
uart=UART(0,baudrate=9600,tx=Pin(0),rx=Pin(1),bits=8,stop=1)
dust_sensor=sds011.SDS011(uart)
spi = SPI(1,
                  baudrate=1000000,
                  polarity=0,
                  phase=0,
                  bits=8,
                  firstbit=machine.SPI.MSB,
                  sck=machine.Pin(14),
                  mosi=machine.Pin(15),
                  miso=machine.Pin(12))
cs = Pin(13, Pin.OUT)
sd = sdcard.SDCard(spi, cs)
vfs = uos.VfsFat(sd)
uos.mount(vfs, "/sd")
files=uos.listdir("/sd/")
num=0
for i in files:
    if "data" in i:
        newnum=int(i.split('.')[-2].split('_')[-1])
        if num < newnum+1:
            num=newnum+1
filename='/sd/data_'+str(num)+'.txt'
oled.fill(0)
async def main(rylr):
    await rylr.init()
    co2=0;co2t=0;co2rh=0
    hour=0;minute=0;second=0;lon=0.;lat=0.;alt=0
    nwrite=0
    outfile=open(filename,'a')
    while True:
#    while True:
        bme = []
        bme = bme280.readData()
        pressure = round(bme[0], 2) 
        temp = round(bme[1], 2) 
        hum = round(bme[2], 2)
        lux = round(light.Lux(), 2)
        uvs = uv.UVS()
        sgpgas = round(sgp.measureRaw(temp,hum), 2)
        voc = voc_sgp.VocAlgorithm_process(sgpgas)
        icm = []
        icm = mpu.ReadAll()
        g_no2 = gas.calc_vol(gas.get_gm102b())
        g_c2h5oh = gas.calc_vol(gas.get_gm302b())
        g_voc = gas.calc_vol(gas.get_gm502b())
        g_co = gas.calc_vol(gas.get_gm702b())
        o3value=o3.get_ozone_data(20)
        dust_sensor.read()
        pm25=dust_sensor.pm25
        pm10=dust_sensor.pm10
        if nwrite%20==0:
            try:
               utc=gps.get_utc()
               alon=gps.get_lon()
               alat=gps.get_lat()
               alt=gps.get_alt()
               hour=utc.hour
               minute=utc.minute
               second=utc.second
               lon=alon.lonitude
               lat=alat.latitude
            except:
                pass
        if scd4x.data_ready:
            co2=scd4x.CO2
            co2t=scd4x.temperature
            co2rh=scd4x.relative_humidity
        print("==================================================")
        print("pressure : %7.2f hPa" %pressure)
        print("temp : %-6.2f ℃" %temp)
        print("hum : %6.2f ％" %hum)
        print("lux : %d " %lux)
        print("uv : %d " %uvs)
        print("gas : %6.2f " %sgpgas)
        print("VOC : %d " %voc)
        print("Acceleration: X = %d, Y = %d, Z = %d" %(icm[0],icm[1],icm[2]))
        print("Gyroscope:     X = %d , Y = %d , Z = %d" %(icm[3],icm[4],icm[5]))
        print("Magnetic:      X = %d , Y = %d , Z = %d" %(icm[6],icm[7],icm[8]))
        print("Ozone:   %d"% o3value)
        print("NO2: %.3f"%  g_no2)
        print("C2H5OH: %.3f"%  g_c2h5oh)
        print("VOC: %.3f"%  g_voc)
        print("CO: %.3f"%  g_co)
        print("CO2:%d T:%d RH:%d"%(co2,co2t,co2rh))
        print("PM25:%d PM10:%d "%(pm25,pm10))
        out=[nwrite,hour,minute,second,lon,lat,alt,pressure,temp,hum,lux,uvs,sgpgas,voc,icm[0],icm[1],icm[2],icm[3],
             icm[4],icm[5],icm[6],icm[7],icm[8],o3value,g_no2,g_c2h5oh,g_voc,g_co,co2,co2t,co2rh,pm25,pm10]
        outstr=''
        for i in out:
            outstr=outstr+str(i)+','
        print(outstr)
        print(filename)
        if nwrite%10==0:
            await rylr.send(outstr)
            outfile.close()
            outfile=open(filename,'a')
        outfile.write(outstr+'\n')
        nwrite=nwrite+1
        if nwrite==10000:
            break
        oled.fill(0)
        oled.text('VOC:%d'%voc,8,56)
        oled.text('PM25:%5.1f'%pm25,8,48)
        oled.text('O3:%5.1f'%o3value,8,40)
        oled.text('CO:%5.3f'%g_co,8,32)
        oled.text('UV:%5.2f'%uvs,8,24)
        oled.text('CO2:%5.2f'%co2,8,16)
        oled.text('LUX:%d'%lux,8,8)
        oled.text('P:%6.1f'%pressure,8,0)
        oled.show()
        led.on()
        time.sleep(0.1)
        led.off()
    outfile.close()
    await rylr.send('Complete collection')
    files=uos.listdir('/sd/')
    for file in files:
        if "dat" in file and len(file.split('.'))==2:
            await rylr.send(file)
            await asyncio.sleep(0.2)
            f=open('/sd/'+file,'r')
            while True:
                try:
                   for m in range(10):
                       i=f.readline().strip()
                   if i!='':
                       print(i)
                       await rylr.send(i)
                       await asyncio.sleep(0.1)
                   else:
                       break
                except:
                    break
            f.close()

        
    

loop = asyncio.get_event_loop()
loop.create_task(rylr.loop())
loop.create_task(main(rylr))
loop.run_forever()

