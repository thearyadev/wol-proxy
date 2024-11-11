# wol proxy
proxies all requests
but sends a WOL in the middle

## why make this? 
ya most reverse proxies probably have wol tools. i use traefik in my k8s cluster and the wol plugin for traefik gave me cancer. 

this tool replaces that and easily integrates using a traefik ingress handler. 
