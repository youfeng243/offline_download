#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  gikieng.li
# @Date    2017-03-03 16:04
import importlib
import os
import signal
import subprocess
import sys
import time
from threading import Thread

import redis
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler as Scheduler

from conf import m_settings
from libs.loghandler import getLogger

logger = getLogger("scheduler", console_out=True, level="debug")

"""
tasks = {
    task_path:{
        "cron" : 调度周期,
        "job" : 调度器job实例,
        "last_check" : 上次检查时间,
        "path": 代码路径/task_path
        "name": name
        "last_run": 上次运行时间
    }
}
"""


def parser_cron(string):
    minute, hour, day, month, weekday = string.split()
    cron = {
        "minute": minute,
        "hour": hour,
        "day": day,
        "month": month,
        "day_of_week": weekday
    }
    return cron


RUNNING = 1
STOP = 2


class GScheduler(object):
    def __init__(self, task_prefix="sites", sch_file_name="sch.py"):
        self.__task_prefix = task_prefix
        self.__sch_file_name = sch_file_name
        self.__sch_module = self.__sch_file_name.split(".")[0]
        self.__tasks_dir = os.path.join(m_settings.PROJECTDIR, self.__task_prefix)
        self.tasks = {
        }
        executors = {
            'default': ThreadPoolExecutor(100),
        }
        self.scheduler = Scheduler(logger=logger, executors=executors, timezone="Asia/Shanghai")

        self.scan_running = True
        self.scan_thread = Thread(target=self.scan_task_config)
        self.scan_thread.daemon = True
        self.redis_cli = redis.Redis(host=m_settings.SCHEDULER_REDIS['host'],
                                     port=m_settings.SCHEDULER_REDIS['port'],
                                     db=m_settings.SCHEDULER_REDIS['db'],
                                     password=m_settings.SCHEDULER_REDIS['password'],
                                     )

    def do_task(self, task_path):
        try:
            task = self.tasks[task_path]
            for cmd in task['cmd']:
                try:
                    run_cmd = "cd %s; %s" % (task['path'], cmd)
                    logger.info("Task start:{}\n{}".format(task['path'], run_cmd))
                    subp = subprocess.Popen(run_cmd,
                                            shell=True,
                                            stdin=open(os.devnull, "w"),
                                            stdout=open(os.devnull, "w"),
                                            stderr=sys.stderr,
                                            )
                    ret = subp.communicate()
                    if subp.returncode != 0:
                        logger.warning("Task return error:{}\t{}\t{}".format(task['path'], cmd, ret))
                except Exception as e:
                    logger.error("Task error:{}".format(e.message))
                    logger.exception(e)
            logger.info("Task finish:{}".format(task['path']))
        except Exception as e:
            logger.error("Execute error:{}".format(task_path))
            logger.exception(e)

    def path2module(self, task_path):
        task_module = task_path.split('/')[-1]
        topic_module = task_path.split("/")[-2]
        mof = ".".join((self.__task_prefix, topic_module, task_module, self.__sch_module))
        if sys.modules.has_key(mof):
            reload(sys.modules[mof])
        m = importlib.import_module(mof)
        return m

    @staticmethod
    def _check_sch_config(mod):
        if not hasattr(mod, "status") or not mod.status:
            return False
        if hasattr(mod, "cron") and hasattr(mod, "site") and hasattr(mod, "cmd"):
            if not isinstance(mod.cmd, (list, tuple)) or not mod.cmd:
                return False
            if not isinstance(mod.cron, basestring) or not mod.cron:
                return False
            if not isinstance(mod.site, basestring) or not mod.site:
                return False
        else:
            return False
        return True

    def add_task(self, task_path):
        ret = False
        try:
            m = self.path2module(task_path)
            if self._check_sch_config(m):
                logger.info("Add task:{}".format(task_path))
                task = {'site': m.site,
                        'cron': m.cron,
                        'path': task_path,
                        'last_check': -1}
                job = self.scheduler.add_job(func=self.do_task,
                                             args=[task_path, ],
                                             trigger="cron",
                                             **parser_cron(m.cron))
                task['job'] = job
                task['cmd'] = m.cmd
                self.tasks[task_path] = task
                logger.info("Add task finished:{}\t{}".format(task_path, m.cron))
                ret = True
            else:
                # logger.warning("Add task failed by INVALID `sch.py` FILE:{}".format(task_path))
                ret = False
        except Exception as e:
            logger.warning("Add task failed: {}".format(task_path))
            logger.exception(e)
        return ret

    def modify_task(self, task_path):
        ret = False
        try:
            m = self.path2module(task_path)
            if not self._check_sch_config(m):
                logger.warning("Exists task has INVALID `sch.py`, will be removed:{}".format(task_path))
                self.remove_task(task_path, kill=True)
            else:
                task = self.tasks[task_path]
                task['site'] = m.site
                task['cron'] = m.cron
                task['path'] = task_path
                task['last_check'] = -1
                task['cmd'] = m.cmd
                self.scheduler.remove_job(task['job'].id)
                job = self.scheduler.add_job(func=self.do_task,
                                             args=[task_path, ],
                                             trigger="cron",
                                             **parser_cron(m.cron))
                task['job'] = job
                self.tasks[task_path] = task
                ret = True
        except Exception as e:
            logger.error("What happen when modify:{}\t{}".format(task_path, e.message))
            logger.exception(e)
            self.remove_task(task_path)
        return ret

    def remove_task(self, task_path, kill=True):
        logger.info("Reomve task:{}".format(task_path))
        task = self.tasks[task_path]
        self.scheduler.remove_job(task['job'].id)
        if kill and task.has_key("process"):
            try:
                task['process'].kill()
            except Exception as e:
                logger.error("What happen when reomve:{}\t[}".format(task_path, e.message))
                logger.exception(e)
        try:
            self.tasks.pop(task_path)
        except Exception as e:
            logger.error("What happen when reomve:{}\t[}".format(task_path, e.message))
            logger.exception(e)
        logger.info("Remove task:{} finished".format(task_path))

    def scan_task_config(self):
        while self.scan_running:
            now_time = time.time()
            # 遍历任务目录
            for parent_line in os.listdir(self.__tasks_dir):
                parent_task_path = os.path.join(self.__tasks_dir, parent_line)
                # 非文件夹跳过
                if not os.path.isdir(parent_task_path):
                    continue

                for line in os.listdir(parent_task_path):
                    task_path = os.path.join(parent_task_path, line)

                    # 非文件夹跳过
                    if not os.path.isdir(task_path):
                        continue

                    conf_path = os.path.join(task_path, self.__sch_file_name)
                    # 查找调度配置文件
                    if os.path.isfile(conf_path):
                        # 调度器中已经存在该任务路径
                        if self.tasks.has_key(task_path):
                            # 判断是否有更改
                            if os.path.getmtime(conf_path) > self.tasks[task_path]['last_check']:
                                logger.info("Change task:{}".format(task_path))
                                # 已经存在的任务
                                if self.modify_task(task_path):
                                    self.tasks[task_path]['last_check'] = now_time
                            else:
                                self.tasks[task_path]['last_check'] = now_time
                        else:
                            if self.add_task(task_path):
                                logger.info("Find new task:{}".format(task_path))
                                self.tasks[task_path]['last_check'] = now_time
            for key, value in self.tasks.items():
                if value['last_check'] != now_time:
                    logger.info("Lost task conf:{}".format(key))
                    self.remove_task(key)
            time.sleep(10)

    def start(self):
        self.scan_running = True
        self.scan_thread.start()
        self.scheduler.start()
        while self.scan_running:
            time.sleep(1)

    def shutdown(self, a, b):
        logger.info("kill")
        self.scan_running = False
        self.scheduler.shutdown()
        try:
            os.killpg(os.getgid(), signal.SIGINT)
        except Exception as e:
            logger.exception(e)


if __name__ == "__main__":
    scheduler = GScheduler()
    scheduler.start()
