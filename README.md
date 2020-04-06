## Supervisor and Privoxy StormProxies config generator


### How to use

Into `build_storm_privoxy.py` script

Set `LOCAL_IP` with your server IP.

Set `START_PORT` with a number of port that you want to use. It will define the port range to use.

For example, if you have 50 gateways to use, and `START_PORT` is 6971 (default) the port range will be 6971-7021

Set `SUPERVISOR_BASE_DIR` with the directory you will use as base for the project

Set `PRIVOXY_CONFIG_PATH` with path where there will be all of the Privoxy config files

The proxy list must be into three files into the project directory: 'main.txt', '3min.txt', '15min.txt'

Then you should run the script `build_storm_privoxy.py`

It will read those files and generate one privoxy config for each proxy server. Also will generate a file named `stormproxies.conf` with the config to use with supervisor.

Also it will generate three new files with names ending with `_local.txt` that are the list of proxies to use in your program or script.
