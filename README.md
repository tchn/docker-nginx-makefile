# docker-nginx-makefile
script and template to generate files for docker-nginx

## How to use

1. Customize values in `config.yml`
2. Run `python3 scripts/makefile.py --root $ROOTDIR --outdir $OUTDIR`

$ROODIR is a directory `config.yml` is located.
$OUTDIR is a directory you want the output to go to.

Following files will be generated and can be used as config files of nginx.
```
files/etc/nginx/ssl_params
files/etc/nginx/proxy_params
files/etc/nginx/conf.d/default.conf
```
