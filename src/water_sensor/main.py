from hub import Hub
hub = Hub()
hub.enable = True

from components.retain import Retain
hub.add(Retain)

from alarm import Alarm
hub.add(Alarm)

from sensor import Sensor
hub.add(Sensor)

from battery import Battery
hub.add(Battery)
    
from internet import Internet
hub.add(Internet)

from deepsleep import Deepsleep
hub.add(Deepsleep)

hub.run()
