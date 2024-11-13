# wol proxy
proxies all requests
but sends a WOL in the middle

## why make this? 
ya most reverse proxies probably have wol tools. i use traefik in my k8s cluster and the wol plugin for traefik gave me cancer. 

this tool replaces that and easily integrates using a traefik ingress handler. 

## Usage

```yaml
services:
    wol_proxy:
        image: thearyadev0/wol-proxy:latest # or version tag
        network_mode: host # required for WOL. NOTE: service runs on port 8000
        environment:
            PROXY_URL: "http://192.168.1.11:11434" # proxy target
            WOL_INT: ens18 # host interface to send wol
            WOL_MAC: B4:2E:99:4D:5C:B4 # target machine mac
            GET_CACHE: "False" # Optional: GET requests will be cached
            GET_CACHE_INVALIDATE_SECONDS: "1800" # Optional: Time to invalidate get cache in seconds
            TIMEOUT: "30" # Optional: default is 30. Time in seconds to wait for a request to resolve (computer may be turning on)
```


all requests sent to <ip>:8000 will be forwarded to http://192.168.1.11:11434
