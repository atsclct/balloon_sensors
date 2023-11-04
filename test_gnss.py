import time
import gnss
from machine import I2C,Pin
i2c=I2C(1,sda=Pin(26),scl=Pin(27))
print(i2c.scan())
print(gnss.GNSS_DEVICE_ADDR)
gps = gnss.DFRobot_GNSS_I2C(i2c, gnss.GNSS_DEVICE_ADDR)
while (gps.begin() == False):
    print("Sensor initialize failed!!")
    time.sleep(1)
gps.enable_power()        # Enable gnss power
gps.set_gnss(gnss.GPS_BeiDou_GLONASS)

while True:
  rslt = gps.get_all_gnss()
  a=''
  for i in rslt:a+=i
  print(a)
  utc=gps.get_utc()
  lon=gps.get_lon()
  lat=gps.get_lat()
  alt=gps.get_alt()
  print(utc.hour,utc.minute,utc.second)
  print(lat.latitude_degree,lon.lonitude_degree,alt)
  time.sleep(3)


