import sys
import time


def main():
    source_file = sys.argv[1]
    dest_file = sys.argv[2]

    lines_per_interval = 20
    interval = 1

    with open(source_file) as sf:
        with open(dest_file, 'w') as df:
            while True:
                content = ''.join(sf.readline() for _ in range(lines_per_interval))
                if not content:
                    break
                print(content, file=df, flush=True, end="")
                time.sleep(interval)


if __name__ == '__main__':
    main()
