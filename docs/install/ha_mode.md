# HA setup

Infrabox support ha mode when deployed multi clusters.

Related configuratios:
```yaml
ha:
    enabled: false

    check_interval: 10

    active_timeout: 60

    entry_host: #<required if use ha>

    entry_port: 443
```

## Enable HA mode
set `ha.enabled = true` to enable ha mode

HA mode makes every cluster accessable, we need to set a fixed entrypoint by setting

`entry_host, entry_port`


## Configure HA mode

- When ha mode is enabled, Infrabox checks every cluster repeatedly. 
Check interval can be configured by `check_interval (seconds)`

- By default, a cluster not running for 60 seconds is considered inactive, jobs will not be scheduled to this cluster.
HA timeout time can be configurated by `ha.active_timeout`

- Jobs without cluster selector will be scheduled to clusters with `default` label, it's better to add label `default` to your clusters.

- In ha mode, we don't have a master cluster, so there is no need to set a cluster with name master

