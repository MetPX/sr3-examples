This is a proof of concept for publishing to a cloud hosted instance of azure storage.

It contains two subscribe configurations and a plugin.

- The dd-swob configuration subscribes to swob files from dd.weather and downloads them locally, then publishes a message to a local broker advertising the file.
- The publisher configuration takes those messages, and invokes the plugin to publish to the azure storage defined in the environment variables.
- Optionally, the publisher configuration can post messages to a broker, advertising those files posted to azure. Any subscribers receiving those messages will download from the cloud environment. (Ensure permissions for public downloads are set)
- *Ensure you update the configuration files with the correct file paths and connection information on your system.*

You will need to install the packages in requirements.txt in order for the plugins to make the function calls to cloud - as well as setup or have available a broker to post messages to.

pip3 install -r requirements.txt

The required environment variables are within default.conf. Add the environment variable information within the default.conf, or whichever way is preferable.

The plugin is invoked in the after_accept flow callback. This means that it is invoked before file downloads begin. Therefore the files must be available locally for the plugin to work (thus the 2 subscriber configurations). This design was chosen due to allow more flexibility to use with other configuration types. For example, if this plugin is used on a watch configuration, it can monitor directories and after accepting files, immediately post them to the cloud environment. The alternative callback point would be after_work, which is only called after a file is downloaded or sent, which would not be called in some configurations.
