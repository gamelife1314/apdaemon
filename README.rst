apdaemon: Python Process Daemon Tool.
====================================

Install
-------

via pip ::

    pip3 install apdaemon

example::

    from apdaemon.daemon import daemon

    @daemon(service="maind")
    def main():
        import time
        while True:
            print("hello world")
            time.sleep(3)

    if __name__ == '__main__':
        main()

    run command: python3 daemon.py [start[default]|status|stop|restart]
