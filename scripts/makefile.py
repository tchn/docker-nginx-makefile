#!/usr/bin/env python3

import yaml
import argparse
import pathlib
import os

data_source_file = "config.yml"
data_source = {}
compose_yml_file = "docker-compose.yml"
compose_yml_template = "docker-compose.yml.template"
compose_yml_template_data = {}
nginx_conf_dir = "files/etc/nginx"
nginx_conf_template = os.path.join(nginx_conf_dir, "conf.d/default.conf.template")
nginx_conf_file = os.path.join(nginx_conf_dir, "conf.d/default.conf")
ssl_params_template = os.path.join(nginx_conf_dir, "ssl_params.template")
ssl_params_file = os.path.join(nginx_conf_dir, "ssl_params")

def generate_compose_file(data_source, cmdargs):

    with open(os.path.join(cmdargs.rootdir, compose_yml_template), "r") as stream:
        compose_yml_template_data = yaml.safe_load(stream)

    compose_yml_template_data["version"] = data_source["var"]["compose_file_ver"]
    if data_source["var"]["volumes"]:
        compose_yml_template_data["services"]["nginx"]["volumes"] = data_source["var"]["volumes"]
    if data_source["var"]["environment"]:
        compose_yml_template_data["services"]["nginx"]["environment"] = data_source["var"]["environment"]
    if data_source["var"]["tls"] == True:
        compose_yml_template_data["services"]["nginx"]["ports"] = ["443:443"]

    with open(os.path.join(cmdargs.outdir, compose_yml_file), "w") as outfile:
        yaml.dump(compose_yml_template_data, outfile, default_flow_style=False, allow_unicode=True)

def generate_nginx_conf(data_source, cmdargs):

    is_tls = bool(False)
    srv_role = str()
    server_name = data_source["var"]["server_name"]
    listen_port = str(data_source["var"]["listen_port"])
    server_root = str(data_source["var"]["server_root"])
    proxies = dict()
    proxied_domain = list()
    rev_proxy_block = str()
    proxied_srv = str()
    proxied_proto = str()
    proxied_host = str()
    proxied_port = str()

    is_tls = False if data_source["var"]["tls"] is False else True
    srv_role = "standalone" if data_source["var"]["srv_role"] == "standalone" else "reverse-proxy"
    listen_replace_text = f"listen {listen_port} ssl;\n\tinclude /etc/nginx/ssl_params" if is_tls == True else f"listen {listen_port}"
    server_root = data_source["var"]["server_root"]
    if srv_role == "reverse-proxy":
        proxies = data_source["var"]["proxy"]
        for key in proxies.keys():
            proxied_srv = key
            proxied_proto = proxies[key]["protocol"]
            proxied_host = proxies[key]["host"]
            proxied_port = str(proxies[key]["port"])
            rev_proxy_block += f"server {{\n\tserver_name {proxied_srv};\n\tlisten {listen_port};\n\t\n\tlocation / {{\n\t\tinclude /etc/nginx/proxy_params;\n\t\tproxy_pass {proxied_proto}://{proxied_host}:{proxied_port};\n\t}}\n}}\n\n"

    conf_str = open(os.path.join(cmdargs.rootdir, nginx_conf_template), "r").read()
    if srv_role == "reverse-proxy":
        conf_str = conf_str.replace("# @placeholder@", rev_proxy_block)
    conf_str = conf_str.replace("${SERVER_NAME}", server_name)
    conf_str = conf_str.replace("${LISTEN}", listen_replace_text)
    conf_str = conf_str.replace("${SERVER_ROOT}", server_root)
    open(os.path.join(cmdargs.outdir, nginx_conf_file), "w").write(conf_str)
    
    if is_tls == True:
        ssl_params_str = open(os.path.join(cmdargs.rootdir, ssl_params_template), "r").read()
        ssl_params_str = ssl_params_str.replace("${SERVER_NAME}", server_name)
        open(os.path.join(cmdargs.outdir, ssl_params_file), "w").write(ssl_params_str)
     
def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=pathlib.Path, required=True, dest="rootdir")
    parser.add_argument("--outdir", type=pathlib.Path, required=True, dest="outdir")
    cmdargs = parser.parse_args()

    with open(os.path.join(cmdargs.rootdir, data_source_file), "r") as stream:
        data_source = yaml.safe_load(stream)

    generate_compose_file(data_source, cmdargs)
    if not os.path.exists(os.path.join(cmdargs.outdir, nginx_conf_dir, "conf.d")):
            os.makedirs(os.path.join(cmdargs.outdir, nginx_conf_dir, "conf.d"), exist_ok=True)
    generate_nginx_conf(data_source, cmdargs)

if __name__ == "__main__":
    main()
