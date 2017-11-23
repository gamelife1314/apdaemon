# -*- coding:utf-8 -*-

import os
import sys
import atexit
import signal
from functools import wraps

import psutil

__all__ = [
    "daemon"
]


def __check_process_is_running(pid):
    try:
        return psutil.Process(int(pid)).status() == psutil._common.STATUS_RUNNING
    except (psutil.NoSuchProcess, ValueError, Exception):
        return False


def daemon(service, pidfile="/tmp/python-daemon.pid",
           stdin="/dev/null", stdout="/tmp/python-daemon.log", stderr="/tmp/python-daemon.log",
           work_dir="/"):
    """
    ----------------------------------------------
            run process in daemon way.
    ----------------------------------------------

    >>> from apdaemon.daemon import daemon
    >>> @daemon(service="maind")
    >>> def main():
    >>>     import time
    >>>     while True:
    >>>           print("hello world")
    >>>           time.sleep(3)
    >>> main()

    * service:  service name;
    * pidfile:  daemon process pid file;
    * stdin:    stdin;
    * stdout:   stdout redirect;
    * stderr:   stderr redirect.
    * work_dir: daemon process work directory.
    """

    def start():
        # 检查进程是否已经启动
        if os.path.exists(pidfile):
            pid = open(pidfile, "r").read().strip()
            if __check_process_is_running(pid) is True:
                print("Process %s is already running." % pid)
                sys.exit(0)
            else:
                os.remove(pidfile)

        # 从父进程分离
        try:
            if os.fork() > 0:
                raise SystemExit(0)
        except OSError:
            raise RuntimeError("fork #1 failed.")

        os.chdir(work_dir)
        os.umask(0)
        os.setsid()

        # 放弃进程控制权
        try:
            if os.fork() > 0:
                raise SystemExit(0)
        except OSError:
            raise RuntimeError("fork #2 failed.")

        # 清空IO缓存
        sys.stdout.flush()
        sys.stderr.flush()

        # 替换文件描述符，原先向控制台输出的都安静输出到相应的文件中
        with open(stdin, "rb", 0) as f:
            os.dup2(f.fileno(), sys.stdin.fileno())
        with open(stdout, "ab", 0) as f:
            os.dup2(f.fileno(), sys.stdout.fileno())
        with open(stderr, "ab", 0) as f:
            os.dup2(f.fileno(), sys.stderr.fileno())

        with open(pidfile, "w") as f:
            f.write(str(os.getpid()))

        def remove_pidfile_atexit():
            if os.path.exists(pidfile):
                os.remove(pidfile)

        atexit.register(remove_pidfile_atexit)

        def term_signal_handler(sig, frame):
            raise SystemExit(1)

        signal.signal(signal.SIGTERM, term_signal_handler)

    def stop(exit_=True):
        if os.path.exists(pidfile):
            pid = open(pidfile, "r").read().strip()
            if __check_process_is_running(pid) is True:
                os.kill(int(pid), signal.SIGTERM)
            os.remove(pidfile)

        if exit_ is True:
            sys.exit(0)

    def status():
        running = False
        pid = ""
        if os.path.exists(pidfile):
            pid = open(pidfile, "r").read().strip()
            if __check_process_is_running(pid) is True:
                running = True

        if running is False:
            print("Service %s is stopped." % service, file=sys.stdout)
        else:
            print("Service %s is running. pid：%s" % (service, pid), file=sys.stdout)
        sys.exit(0)

    def restart():
        stop(exit_=False)
        start()

    command = sys.argv[1] if len(sys.argv) >= 2 else "start"
    if command in ["start", "stop", "restart", "status"]:
        locals()[command]()

    def decorate(func):
        @wraps(func)
        def execute(*args, **kwargs):
            return func(*args, **kwargs)
        return execute
    return decorate
