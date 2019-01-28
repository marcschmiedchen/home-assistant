"""
Support for Wolf heating via ISM8 adapter
"""
import logging
import asyncio
from ism8.ism8 import Ism8

from homeassistant.const import (
    TEMP_CELSIUS, DEVICE_CLASS_TEMPERATURE, DEVICE_CLASS_PRESSURE)
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    sensors=[]
        
    for dp_nbr, dp in Ism8.datapoint.items():
        if ( dp[Ism8.DP_DEVICE] in discovery_info and 
             dp[Ism8.DP_TYPE] not in ("DPT_Switch",
                                "DPT_Bool",
                                "DPT_Enable",
                                "DPT_OpenClose"
                                )
            ):
            sensors.append ( WolfSensor(dp_nbr, dp) )
    
    async_add_entities(sensors)

class WolfSensor(Entity):
    """Implementation of Wolf Heating System Sensor via ISM8-network adapter
        dp_nbr represents the unique identifier of the up to 200 different
        sensors
    """
        
    def __init__(self, dp_nbr, dp):
        self._nbr      = dp_nbr
        self._device   = dp[Ism8.DP_DEVICE]
        self._name     = dp[Ism8.DP_NAME]
        self._type     = dp[Ism8.DP_TYPE]
        self._writable = dp[Ism8.DP_RW]
        self._unit     = dp[Ism8.DP_UNIT]
        self._state    = None
        _LOGGER.debug('setup Sensor no. {} as {}'.format(self._nbr, self._type))
    
    @property
    def name(self):
        """Return the name of this sensor."""
        return (self._device+ "_" + self._name).lower().replace(' ','_')
        
    @property
    def unique_id(self):
        """Return the id of this sensor."""
        return (self._nbr)

    @property
    def state(self):
        """Return the state of the device."""
        if self._state==None:
            return None
        elif type(self._state) is str:
            return self._state
        else:
            return round(self._state,2)
        
    @property
    def device_class(self) -> str:
        """Return the state of the device."""
        if self._type=='DPT_Value_Temp':
            return DEVICE_CLASS_TEMPERATURE
        elif self._type=='DPT_Value_Pres':
            return DEVICE_CLASS_PRESSURE
        else:
            return None
        
    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity."""
        if self._type=='DPT_Value_Temp':
            return TEMP_CELSIUS
        else:
            return self._unit
        
                
    @property
    def precision(self):
        """Return the precision of the system."""
        return PRECISION_TENTHS
        

    async def async_update(self):
        """Return state"""
        if (self._nbr in Ism8.dp_values.keys()):
            self._state = Ism8.dp_values[self._nbr]
        return        
       
 
