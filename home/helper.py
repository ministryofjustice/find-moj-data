def filter_json_dict(json_dict, target_value):
    filtered_dict = {
        key: value for key, value in json_dict.items() if value == target_value
    }
    return filtered_dict


def sort_output(json_dict, sortvalue):
    return None
