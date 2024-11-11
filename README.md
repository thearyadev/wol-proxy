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
        environment:
            PROXY_URL: "http://192.168.1.11:11434" # proxy target
        ports:
            - 80:8000

```


all requests sent to <ip>:80 will be forwarded to http://192.168.1.11:11434
