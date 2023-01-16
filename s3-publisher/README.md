This is a proof of concept for publishing to s3 (Simple Storage Service) via either cloud based (AWS) or locally hosted minio.

It contains three configurations and a plugin.

The configurations consist of a watch, sarra, and subscriber.

- The watch monitors a local directory, and announces products received to the broker.
- The sarra receives the messages from the broker, publishes them to s3, and reannounces the messages with the updated file location.
- The subscribe downloads the products from s3 using the messages generated from the sarra configuration.
- *Ensure you update the configuration files with the correct file paths and connection information on your system.*

The plugin is used for the sarra configuration, which handles the publishing to s3 and message alteration to set the file path on the message to the s3 location.

This example also contains a docker compose file to setup the rabbitmq broker, minio storage, as well as run sr3 within a container.

You will need to install the package boto3 in order for the plugin to make the function calls to s3.

pip3 install -r requirements.txt

Publishing to Azure is yet to be implemented. Currently it is s3 only.
