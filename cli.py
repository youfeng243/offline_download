#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  gikieng.li
# @Date    2017-03-03 14:25

import click
import os
from conf import m_settings
from libs.daemon import Daemon
from scheduler import GScheduler


PRO_DIR = m_settings.PROJECTDIR
TASKS_DIR = os.path.join(PRO_DIR, "sites")


class SDaemon(Daemon):
    """
    linux守护进程类
    """
    def __init__(self, pidifle=PRO_DIR + "/scheduler.pid"):
        Daemon.__init__(self, pidfile=pidifle)

    def run(self):
        GScheduler().start()


def create_task(task_name):
    """
    :param task_name:
    :return:
    """
    task_dir = os.path.join(TASKS_DIR, task_name)
    if os.path.isdir(task_dir):
        print '[', task_name,']', ' existed'
        exit(0)
    else:
        os.mkdir(task_dir)
        exit(0)


def start_schedule(bg=True):
    if bg:
        sd = SDaemon()
        sd.start()
    else:
        GScheduler().start()


def stop_schedule():
    sd = SDaemon()
    sd.stop()


@click.group()
def cli():
    pass


@click.command()
@click.option("--task", required=True)
def create(**option):
    create_task(option['task'])


@click.command()
@click.argument("list", required=False)
def list_task(**option):
    for line in os.listdir(TASKS_DIR):
        if os.path.isdir(os.path.join(TASKS_DIR, line)):
            print line


@click.command()
@click.option("--background", default=True, type=bool)
@click.argument("stop", required=False)
def scheduler(**option):
    if option.get('background'):
        if option.get("stop"):
            stop_schedule()
        else:
            start_schedule(True)
    else:
        start_schedule(False)


cli.add_command(list_task, name="list")
cli.add_command(create)
cli.add_command(scheduler)
if __name__ == "__main__":
    cli()