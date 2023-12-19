# StaticTimeSeriesResource-centralized

A simulation platform component cab be used to simulate simple loads and generators whose published states are determined by a file containing a time series of attribute values for each epoch. The component is centralized meaning that several loads or generators within one container can be deployed whereas in [StaticTimeSeriesResource](https://github.com/simcesplatform/static-time-series-resource) every load/generator is run in a seperate container. Therefore, the StaticTimeSeriesCentralized needs less computational resources and makes the simulations faster.

The component is only deployable in the [SimCES ](https://simcesplatform.github.io/)platform.

## Requirements

* python
* pip for installing requirements

Install requirements:

```shell
# optional create a virtual environment:
python3 -m venv .env
# activate it
. .env/bin/activate # *nix
.env\scripts\activate # windows.
# install required packages
pip install -r requirements.txt
```

## Usage

The component is based on the AbstractSimulationCompoment class from the [simulation-tools](https://github.com/simcesplatform/simulation-tools) repository. It is configured via environment variables which include common variables for all AbstractSimulationComponent subclasses such as rabbitmq connection and component name. Environment variables specific to this component are listed below:

* RESOURCE_STATE_TOPIC (optional): The upper level topic under whose subtopics the resource states are published. If this environment variable is not present ResourceState is used.
* RESOURCE_TYPE (required): Type of this resource. Accepted values are Generator or Load.
* RESOURCE_STATE_CSV_FILE (required): Location of the csv file which contains the resource state information used in the simulation. Relative file paths are in relation to the current working directory.
* RESOURCE_STATE_CSV_DELIMITER (optional): Delimiter used in the csv file. The default is ,

The csv file should contain columns named after the ResourceState message attributes: RealPower, ReactivePower, CustomerId and Node. The Node column is optional. Each row containing values will then represent data for one epoch. There should be at least as many data rows as there will be epochs.

## **Implementation details**

**Language and platform**

| Programming language | Python 3.11.4                                             |
| -------------------- | ---------------------------------------------------------- |
| Operating system     | Docker version 20.10.21 running on windows 10 version 22H2 |

**External packages**

The following packages are needed.

| Package          | Version   | Why needed                                                                                | URL                                                                                                   |
| ---------------- | --------- | ----------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Simulation Tools | (Unknown) | "Tools for working with simulation messages and with the RabbitMQ message bus in Python." | [https://github.com/simcesplatform/simulation-tools](https://github.com/simcesplatform/simulation-tools) |
