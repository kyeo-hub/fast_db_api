import datetime
def convert_timestamp(timestamp):
    timestamp = int(timestamp)
    timestamp = timestamp / 1000
    timestamp = datetime.datetime.fromtimestamp(timestamp)
    timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')

    return timestamp_str

if __name__ == '__main__':
    print(convert_timestamp(1730166768907))