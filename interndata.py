import json

intern_data_file = "data/staffrecord.json"

def get_staff_records():
    with open(intern_data_file, "r") as fd:
        return json.loads(fd.read())

def map_name_to_record(name, data, first=True):
    for i in data["payload"]:
        if first:
            if i["name"].split()[0] == name:
                return i["innerpayload"]
        else:
            if i["name"] == name:
                return i["innerpayload"]

    return None

def return_intern_data_from_present_array(array, data):
    output = []
    for i in array:
        record = map_name_to_record(i, data)
        if record:
            output.append(record)

    return output
