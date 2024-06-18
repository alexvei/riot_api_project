from collections import Counter


def list_to_dict(list_to_convert: list)-> dict:
    """
    Counts the items of the list and sorts them in a descending order, returning a dictionary.
    """
    list_to_convert_dict = Counter(list_to_convert)
    sorted_dict = dict(sorted(list_to_convert_dict.items(), key=lambda x:x[1], reverse=False))
    return sorted_dict