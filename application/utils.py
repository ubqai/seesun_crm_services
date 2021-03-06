import datetime
import calendar


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = int(sourcedate.year + month / 12 )
    month = month % 12 + 1
    day = min(sourcedate.day,calendar.monthrange(year,month)[1])
    return datetime.date(year,month,day)


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    except TypeError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


def num2moneyformat(change_number):
    """
    .转换数字为大写货币格式( format_word.__len__() - 3 + 2位小数 )
    change_number 支持 float, int, long, string
    """
    format_word = ["分", "角", "元",
               "拾", "百", "千", "万",
               "拾", "百", "千", "亿",
               "拾", "百", "千", "万",
               "拾", "百", "千", "兆"]

    format_num = ["零", "壹", "贰", "叁", "肆", "伍", "陆", "柒", "捌", "玖"]
    if type(change_number) == str:
        # - 如果是字符串,先尝试转换成float或int.
        if '.' in change_number:
            try:
                change_number = float(change_number)
            except:
                return None
        else:
            try:
                change_number = int(change_number)
            except:
                return None

    if type(change_number) == float:
        real_numbers = []
        for i in range(len(format_word) - 3, -3, -1):
            if change_number >= 10 ** i or i < 1:
                real_numbers.append(int(round(change_number/(10**i), 2) % 10))

    elif isinstance(change_number, int):
        real_numbers = [int(i) for i in str(change_number) + '00']

    else:
        return None

    zflag = 0                       # 标记连续0次数，以删除万字，或适时插入零字
    start = len(real_numbers) - 3
    change_words = []
    for i in range(start, -3, -1):  # 使i对应实际位数，负数为角分
        if 0 != real_numbers[start-i] or len(change_words) == 0:
            if zflag:
                change_words.append(format_num[0])
                zflag = 0
            change_words.append(format_num[real_numbers[start - i]])
            change_words.append(format_word[i+2])

        elif 0 == i or (0 == i % 4 and zflag < 3):    # 控制 万/元
            change_words.append(format_word[i+2])
            zflag = 0
        else:
            zflag += 1

    if change_words[-1] not in (format_word[0], format_word[1]):
        # - 最后两位非"角,分"则补"整"
        change_words.append("整")

    return ''.join(change_words)
