#!/usr/bin/env python

#
# Copyright 2022 Yudai Yamagishi <yudai@yamagishi.net>
#
# Disclaimer: Use at your own risk!
#

import os
from datetime import datetime
from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_utils.plugins.functions import print_result
from tqdm import tqdm

OUTPUT_DIR_PREFIX = "config"

def collect_stat_and_config(task: Task, bar: tqdm, dst_dir: str) -> Result:
    net_connect = task.host.get_connection("netmiko", task.nornir.config)
    net_connect.enable()
    fname = f"{task.host}.txt"
    f = open(os.path.join(dst_dir, fname), "w")

    # show version
    r = net_connect.send_command("show version")
    tqdm.write(f"{task.host}: Retrieved show version..")
    f.write(f"## show version\n")
    for l in r.splitlines():
        f.write(f"# {l}\n")
    f.write(f"#\n")

    # show chassis hardware
    r = net_connect.send_command("show chassis hardware")
    tqdm.write(f"{task.host}: Retrieved show chassis hardware..")
    f.write(f"## show chassis hardware\n")
    for l in r.splitlines():
        f.write(f"# {l}\n")
    f.write(f"#\n")

    # show interface terse
    r = net_connect.send_command("show interface terse")
    tqdm.write(f"{task.host}: Retrieved show interface terse..")
    f.write(f"## show interface terse\n")
    for l in r.splitlines():
        f.write(f"# {l}\n")
    f.write(f"#\n")

    # show route
    r = net_connect.send_command("show route")
    tqdm.write(f"{task.host}: Retrieved show route..")
    f.write(f"## show route\n")
    for l in r.splitlines():
        f.write(f"# {l}\n")
    f.write(f"#\n")

    # show configuration
    f.write(f"## show configuration\n")
    r = net_connect.send_command("show configuration")
    tqdm.write(f"{task.host}: Retrieved configuration..")
    f.write(r)

    # Complete
    f.close()
    tqdm.write(f"{task.host}: Written configuration to {fname}") 
    bar.update()

if __name__ == "__main__":
    tstart = datetime.now().strftime('%Y%m%d%H%M%S')
    output_dir = f"{OUTPUT_DIR_PREFIX}_{tstart}"
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    nr = InitNornir(config_file="config.yml")

    with tqdm(total=len(nr.inventory.hosts), desc="Collect device statistics and configuration") as get_config_bar:
        r = nr.run(task=collect_stat_and_config, bar=get_config_bar, dst_dir=output_dir)
    
    print_result(r)
