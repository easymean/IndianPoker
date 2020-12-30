# 리스트를 string으로 파싱
def parse_list_into_str(given_list):
    return ','.join(given_list)


def parse_bytes_into_list(given_bytes):
    if given_bytes is None:
        raise Exception

    parsed_list = []
    if given_bytes == '':
        return parsed_list

    decoded_given_str = given_bytes.decode()
    for ele in decoded_given_str.split(','):
        parsed_list.append(ele)

    return parsed_list


def parse_bytes_into_int(given_bytes):
    decoded_str = given_bytes.decode()
    return int(decoded_str)


def parse_bytes_into_str(given_bytes):
    if given_bytes is None:
        raise Exception

    return given_bytes.decode('UTF-8')
