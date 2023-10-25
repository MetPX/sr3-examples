## Purpose

More and more systems are moving to containerize their workloads, separating the hardware/compute from the proccesses, and making them more scaleable, flexible and fault-tolerant.

This is a proof of concept using Docker Swarm, and a specific Docker image in order to achieve simple scaling of a given SR3 config.

**Note:** Not all components, configurations, and options will properly support scaling, so lots of testing for your specific config will be required in order to ensure it works the way you intend it to.

## SR3 Configurations

This proof of concept contains a single `subscribe` configuration.

- `dd_all` subscribes to all files from dd.weather and downloads them locally 


## Usage

**Pre-requisites**
- Linux system (VM, physical, WSL)
- Docker
- Git

Assuming you have git and Docker installed on any flavour of Linux, or WSL, these steps should get you up and running with a single replica of the `dd_all` subscriber configuration. 

1. Clone repo and change to right directory  
    `git clone https://github.com/MetPX/sr3-examples.git`  
    `cd sr3-examples/container-scaling`
2. Create some directories needed for proper operation  
    `mkdir -p metrics/subscribe/dd_all data/redis`
3. Inialize Docker Swarm
    `docker swarm init`
4. Build Docker images  
    `docker build -t sr3-example-container-scaling .`
5. Deploy Docker Stack  
    `docker stack deploy -c docker-compose.yml sr3-example`
6. Start Redis instance  
    `docker service scale sr3-example_redis=1`
7. Verify Redis started, and is running  
    `docker service logs sr3-example_redis`  
    Look for *Server initialized* and *Ready to accept connections tcp* messages
8. Start **1** SR3 instance  
    `docker service scale sr3-example_subscribe-dd_all=1`
9. Verify that the instance started up  
    - `docker service ps sr3-example_subscribe-dd_all`  
        Checking for at least one task to be in the *Running* state  
    - `docker service logs sr3-example_subscribe-dd_all 2>&1 |grep instance`  
        Should see a line something like *sarracenia.flow run pid: 10 subscribe/subscribe/dd_all instance: 1*.
    - `ls data/sr3/subscribe/dd_all`  
        Check that there's files/folders inside the right *data* dir  
10. Scale up the number of SR3 instances  
    `docker service scale sr3-example_subscribe-dd_all=5`  
11. Verify that the instances are all started up by running  
    - `docker service logs sr3-example_subscribe-dd_all`  
        Checking for at least one task to be in the *Running* state
    - `docker service logs sr3-example_subscribe-dd_all 2>&1 |grep instance`    
        Should see 5 lines something like *sarracenia.flow run pid: 10 subscribe/subscribe/dd_all instance: XX*, where XX is a number between 1-5.
    - `ls data/sr3/subscribe/dd_all`  
        Check that there's files/folders inside the right *data* dir

### Metrics

The various instances of a given config each write metrics to a file, which can be polled a regular intervals to gather information on how they're each doing.

In the `config/telegraf` directory, there's very basic [Telegraf](https://github.com/influxdata/telegraf/tree/master) configuration that will do just that. It doesn't have an "output" configured, but running the following command should give you some idea what is captured:  
`docker run --rm --name sr3-example_telegraf -v $PWD/config/telegraf/telegraf.conf:/etc/telegraf/telegraf.conf:ro -v $PWD/metrics:/metrics:ro telegraf --test`.

It would be simple to send these metrics to your timeseries database of choice (Prometheus, Graphite, SQL, etc..), or any ther destination that Telegraf supports as an [output](https://github.com/influxdata/telegraf/tree/master/plugins/outputs).

If they're sent somewhere that Grafana can use as a datasource, then you can easily graph the performance of these metrics, track them over time, alert on any condition you chose.

Depending on the configuration of either Telegraf, or Grafana, it should even be possible to scale up/down the replica count for a given config/service to react to various conditions (deep queue depth, long lag, lots of retries, etc...)