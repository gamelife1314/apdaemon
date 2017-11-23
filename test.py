from apdaemon.daemon import daemon


@daemon(service="maind")
def main():
    import time
    while True:
        print("hello world")
        time.sleep(3)


if __name__ == '__main__':
    main()

