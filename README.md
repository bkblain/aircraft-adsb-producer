# Aircraft ADS-B

## Installing RTL-SDR

Install RTL-SDR linux libraries

```
sudo apt install rtl-sdr
```

## Installing Python Build Tools

Install VENV for the virtual environment, PIP for package management, and PyLint for code linting

```
sudo apt install python3-venv python3-pip pylint
```

Don't install application packages directly through pip, instead install pipenv which can be used to generate a virtual environment.

```
python3 -m pip install --user pipenv
```

Restart your computer or user profile to refresh the `PATH` for the `pipenv` command.

## Installing Python Dependencies

Inside the project directory, install the python project dependencies.

```
pipenv install
```

## Execute Project Files

```
pipenv run python src/adsb_streamer.py
```

## Build Python Wheel

```
pipenv run python -m build
```

## Installing Apache Kafka

https://kafka.apache.org/quickstart

https://stackoverflow.com/questions/34512287/how-to-automatically-start-kafka-upon-system-startup-in-ubuntu


## Environment Variables Configuration

Create the `/etc/environment.d/adsb.conf`

```
ADSB_KAFKA_CONFIG=
ADSB_KAFKA_TOPIC=adsb
ADSB_PYTHON_PATH=~/.local/share/virtualenvs/aircraft-adsb-producer-####
```

The file will run automatically on your computer restart. However, if this is your first time configuring or need to change the value, use the `export` command. Example:

```
export ADSB_KAFKA_TOPIC=adsb
```

## Kafka Installation

https://hub.docker.com/r/ubuntu/kafka

```
docker run -d --name zookeeper -p 2181:2181 ubuntu/zookeeper:edge
```

```
docker run -d --name kafka -e TZ=UTC -p 9092:9092 -e ZOOKEEPER_HOST=host.docker.internal ubuntu/kafka:3.1-22.04_beta
```

When adding a new container, docker assigns an IP address 172.17.0.n. So when adding these two containers, investigate the zookeeper container to determine the static IP necessary to send into the kafka container.

```
-e ZOOKEEPER_HOST=[IP]
```

TODO: is there a way to have DNS or FQDN with docker containers?

Log into the kafka server to create and test the topic following the quickstart guide. Kafka is installed under the `/opt/kafka` directory.

https://kafka.apache.org/quickstart

```
docker exec -it kafka /bin/bash
```


# References

https://inst.eecs.berkeley.edu/~ee123/sp14/lab/lab1-Time_Domain_III-SDR.html

https://mode-s.org/decode/misc/preface.html

https://pysdr.org/index.html

https://en.wikipedia.org/wiki/List_of_airline_codes

https://en.wikipedia.org/wiki/List_of_aircraft_type_designators#cite_note-ICAOcode-3

https://pyrtlsdr.readthedocs.io/en/latest/

https://cdn.knmi.nl/knmi/pdf/bibliotheek/knmipubTR/TR336.pdf

kafka-python docs
https://kafka-python.readthedocs.io/en/master/index.html


To Read

https://junzis.com/files/pymodes.pdf

https://pyrtlsdr.readthedocs.io/_/downloads/en/latest/pdf/


Example how to demodulate signal

https://github.com/junzis/pyModeS


Main with CLI

https://softwareengineering.stackexchange.com/questions/418600/best-practice-for-python-main-function-definition-and-program-start-exit

