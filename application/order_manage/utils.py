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
