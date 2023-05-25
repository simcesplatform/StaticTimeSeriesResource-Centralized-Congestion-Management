# -*- coding: utf-8 -*-
# Copyright 2021 Tampere University and VTT Technical Research Centre of Finland
# This software was developed as a part of the ProCemPlus project: https://www.senecc.fi/projects/procemplus
# This source code is licensed under the MIT license. See LICENSE in the repository root directory.
# Author(s): Otto Hylli <otto.hylli@tuni.fi>
#            Antti Keski-Koukkari <antti.keski-koukkari@vtt.fi>

'''
Contains class for a simulation platform component used to simulate simple load and generator forecaster whose published states are determined by a file containing a simple time series of attribute values for each epoch.
'''
import asyncio

from tools.components import AbstractSimulationComponent
from tools.tools import FullLogger, load_environmental_variables
from domain_messages.resource import ResourceStateMessage
from tools.message.block import TimeSeriesBlock, ValueArrayBlock

from resource_forecaster.components import SimulationComponents

# names of used environment variables
RESOURCE_STATE_TOPIC = "RESOURCE_STATE_TOPIC"
RESOURCE_TYPES = "RESOURCE_TYPES"
RESOURCE_STATE_COMPONENT_IDS = "RESOURCE_STATE_COMPONENT_IDS"
RESOURCE_STATE_CSV_FOLDER = "RESOURCE_STATE_CSV_FOLDER"
RESOURCE_STATE_CSV_DELIMITER = "RESOURCE_STATE_CSV_DELIMITER"
FORECAST_HORIZON = "FORECAST_HORIZON"
UNIT_OF_MEASURE = "UNIT_OF_MEASURE"

# allowed values for resource type
ACCEPTED_resource_state_typeS = [ "Load", "Generator" ]

LOGGER = FullLogger( __name__ )

class StaticTimeSeriesResourceForecaster(AbstractSimulationComponent):
    '''
    A simulation platform component used to simulate simple load and generator forecaster whose published states are determined by a file containing a simple time series of attribute values for each epoch.
    '''

    def __init__(self, resource_state_component_ids: str, resource_state_csv_folder: str,
                 resource_state_csv_delimiter: str, resource_types: str,resource_state_topic: str):
        '''
        Create components which use the given csv source for its published resource forecast states.
        '''
        super().__init__()

        self.__simulation_components = SimulationComponents()
        self._resource_state_component_ids = resource_state_component_ids.split(",")
        self._resource_state_topic = resource_state_topic
        # publish resource forecasts to these topics
        self._result_topics = {}
        
        for component in self._resource_forecast_component_ids:
            self.__simulation_components.add_component(component,
                                                       resource_state_csv_folder, resource_state_csv_delimiter)
        
        self._types = resource_types.split(",")
        
        for resource_state_type in self._types:
            if resource_state_type == '' or resource_state_type not in ACCEPTED_resource_state_typeS:
                if resource_state_type == '':
                    self.initialization_error = f'Required item in environment variable {resource_types} was missing.'
                else:
                    self.initialization_error = f'Environment variable {resource_types} had an invalid value "{resource_state_type}" for resource type. Accepted values: {", ".join( ACCEPTED_resource_state_typeS )}.'
        
        for component, resource_state_type in zip(self._resource_forecast_component_ids, self._types):
            self._result_topics[component] = '.'.join( [ self._resource_forecast_topic, resource_state_type, component ])
            
    async def process_epoch(self) -> bool:
        '''
        Handles the processing of an epoch by publishing the resource forecast state for the epoch.
        '''
        LOGGER.debug( 'Starting epoch.' )
        try:
            await self._send_resource_forecast_message()

        except Exception as error:
            description = f'Unable to create or send a ResourceForecast message: {str( error )}'
            LOGGER.error( description )
            await self.send_error_message(description)
            return False

        return True
        
    async def _send_resource_forecast_message(self):
        '''
        Sends a ResourceForecast message for the current epoch.
        '''
        for component in self._resource_forecast_component_ids:
            resourceForecast = self._get_resource_state_message(component)
            await self._rabbitmq_client.send_message(self._result_topics[component], resourceForecast.bytes())
        
    def _get_resource_state_message(self, component) -> ResourceForecastPowerMessage:
        '''
        Create a ResourceForecastMessage from the next resource state info available from the state source.
        '''
        state = self.__simulation_components.get_component(component).getNextEpochData(self._latest_epoch_message, component)
        
        message = ResourceStateMessage(
            SimulationId = self.simulation_id,
            Type = ResourceStateMessage.CLASS_MESSAGE_TYPE,
            SourceProcessId = self.component_name,
            MessageId = next(self._message_id_generator),
            EpochNumber = self._latest_epoch,
            TriggeringMessageIds = self._triggering_message_ids,
            CustomerId = state.customerid,
            RealPower = state.real_power,
            ReactivePower = state.reactive_power,
            Node = state.node
            )

        return message
        
def create_component() -> StaticTimeSeriesResourceForecaster:
    '''
    Create a StaticTimeSeriesResourceForecaster. Initialized with a folder that contains csv files for components.
    '''
    # get information about the used source csv file, forecasted component names and types and forecasting horizon. 
    env_variables = load_environmental_variables(
        ( RESOURCE_STATE_CSV_FOLDER, str ),
        ( RESOURCE_STATE_CSV_DELIMITER, str, "," ),
        ( RESOURCE_STATE_TOPIC, str, "ResourceState" ),
        ( RESOURCE_TYPES, str ),
        ( RESOURCE_STATE_COMPONENT_IDS, str )
        )

    return StaticTimeSeriesResourceForecaster(
        resource_state_component_ids=env_variables[RESOURCE_STATE_COMPONENT_IDS],
        resource_state_csv_folder=env_variables[RESOURCE_STATE_CSV_FOLDER],
        resource_state_csv_delimiter=env_variables[RESOURCE_STATE_CSV_DELIMITER],
        resource_types=env_variables[RESOURCE_TYPES],
        resource_state_topic=env_variables[RESOURCE_STATE_TOPIC])

async def start_component():
    '''
    Start a StaticTimeSeriesResourceForecaster component.
    '''
    resource = create_component()
    await resource.start()
    while not resource.is_stopped:
        await asyncio.sleep( 2 )

if __name__ == '__main__':
    asyncio.run(start_component())
