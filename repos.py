import signal

import sys


# 中断执行
def signal_handler(signal_num, frame):
    sys.exit(signal_num)


def main():
    signal.signal(signal.SIGINT, signal_handler)


if __name__ == '__main__':
    main()

