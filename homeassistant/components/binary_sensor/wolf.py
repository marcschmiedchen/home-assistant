"""
Support for Wolf heating via ISM8 adapter
"""
import logging
import asyncio
from wolf_ism8.ism8 import Ism8

from homeassistant.const import (
    TEMP_CELSIUS 
    , DEVICE_CLASS_TEMPERATURE
    , DEVICE_CLASS_PRESSURE
    , STATE_PROBLEM
    , STATE_OK
    , STATE_ON
    , STATE_OFF
    , STATE_UNKNOWN
    )
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    sensors=[]
    
    for dp_nbr, dp in Ism8.datapoints.items():
        if ( dp[Ism8.DP_DEVICE] in discovery_info and 
             dp[Ism8.DP_TYPE] in ("DPT_Switch",
                                "DPT_Bool",
                                "DPT_Enable",
                                "DPT_OpenClose"
                                )
            ):
            sensors.append ( WolfBinarySensor(dp_nbr, dp) )
    
    async_add_entities(sensors)

class WolfBinarySensor(Entity):
    """Implementation of Wolf Heating System Sensor via ISM8-network adapter
        dp_nbr represents the uniqui identifier of the up to 200 different
        sensors
    """
        
    def __init__(self, dp_nbr, dp):
        self._nbr      = dp_nbr
        self._device   = dp[Ism8.DP_DEVICE]
        self._name     = dp[Ism8.DP_NAME]
        self._type     = dp[Ism8.DP_TYPE]
        self._writable = dp[Ism8.DP_RW]
        self._unit     = dp[Ism8.DP_UNIT]
        self._state    = STATE_UNKNOWN
        _LOGGER.debug('setup binary sensor no. {} as {}'.format(self._nbr, self._type))
    
    @property
    def name(self):
        """Return the name of this sensor."""
        return (self._device+ "_" + self._name).lower().replace(' ','_')
        
    @property
    def unique_id(self):
        """Return the id of this sensor."""
        return self._nbr

    @property
    def state(self):
        """Return the state of the device."""
        if self.device_class == 'problem':
            return STATE_PROBLEM if self.is_on else STATE_OK
        else:
            return STATE_ON if self.is_on else STATE_OFF
        
    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self._state
        
    @property
    def device_class(self):
        """Return the class of the device."""
        if (self._name == 'Stoerung'): 
            return 'problem'
        elif (self._name in ['Status Brenner / Flamme',
                             'Status E-Heizung']): 
            return 'heat'
        elif (self._name in ['Status Heizkreispumpe',
                            'Status Speicherladepumpe',
                            'Status Mischerkreispumpe',
                            'Status Solarkreispumpe SKP1'
                            'Status Zubringer-/Heizkreispumpe']):
            return 'moving'
        else:
            return None
        
   
    async def async_update(self):
        """Return state"""
        if (self._nbr in Ism8.dp_values.keys()):
            self._state = Ism8.dp_values[self._nbr]
        return        
       
 
