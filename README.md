# docker-nginx-makefile
script and template to generate files for docker-nginx

## How to use

1. Customize values in `config.yml`
2. Run `python3 scripts/makefile.py`

Following files will be generated and can be used as config files of nginx.
```
files/etc/nginx/ssl_params
files/etc/nginx/proxy_params
files/etc/nginx/conf.d/default.conf
```
