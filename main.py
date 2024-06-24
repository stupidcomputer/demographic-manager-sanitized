import json
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font

mapper_data = {
    "age": "Age",
    "gender": "Gender",
    "ethnicity": "Ethnicity",
    "race": "Race",
    "a": "Adult",
    "c": "Child",
    "wh": "White",
    "as": "Asian",
    "f": "Female",
    "m": "Male",
    "1+": "More than one race",
    "nh": "Not Hispanic",
    "h": "Hispanic",
    "b/aa": "Black/African American",
}

def mapper(string):
    # map to human-readable values
    try:
        return mapper_data[string]
    except KeyError:
        return "WARNING: {}".format(string)

def aggregate_demographic_totals(payload):
    results = {"age": {}, "gender": {}, "ethnicity": {}, "race": {}}

    for i in payload:
        # for every entry we get
        for key in results.keys():
            # for every field we have
            results[key].setdefault(i[key], 0)
            results[key][i[key]] += 1

    return results

def get_totals_for_specific_attribute_on_specific_site(site):
    manifest = open("data/manifest.json")
    manifest_data = json.loads(manifest.read())

    record_to_be_used = manifest_data["sites"]
    site_object = None
    for i in manifest_data["sites"]:
        if i["name"] == site:
            site_object = i

    if not site_object:
        raise TypeError("site argument is not valid")

    used_filename = site_object["usedrecord"]

    site_specific_data_file = open("data/" + used_filename)

    demographic_data_json = json.loads(site_specific_data_file.read())

    payload = demographic_data_json["payload"]

    return aggregate_demographic_totals(payload)

def generate_table_for_attr(attr, totals):
    dataarray = [[mapper(attr), "Count"]]
    print(totals)
    for key, value in totals[attr].items():
        print(key, value)
        dataarray.append([mapper(key), value])

    return dataarray

def write_dataarray_to_specific_cell(x, y, dataarray, worksheet):
    i_c = 0
    for i in dataarray:
        j_c = 0
        for j in i:
            worksheet.cell(row=i_c + 1 + x, column=j_c + 1 + y, value=dataarray[i_c][j_c])
            j_c += 1
        i_c += 1

def generate_provider_string(providers):
    if len(providers) > 1:
        before_and = ', '.join(providers[:-1])
        and_string = ' and {}'.format(providers[-1])
        return before_and + and_string
    return providers[0]

def handle_writing_of_attrs(worksheet, totals, providers):
    # each set of fields is two long
    worksheet["A1"].value = "Information for {} site attendance.".format(worksheet.title)
    worksheet["A2"].value = "Fields not present should be assumed 0."
    worksheet["A10"].value = "Data submitted by {}.".format(generate_provider_string(providers))
    worksheet.merge_cells("A1:E1")
    worksheet.merge_cells("A2:E2")
    worksheet.merge_cells("A10:E10")
    count = 0
    for i in totals.keys():
        tmp = generate_table_for_attr(i, totals)

        write_dataarray_to_specific_cell(3, count * 3, tmp, worksheet)
        count += 1

def adjust_column_width(worksheet, times):
    for i in range(times):
        worksheet.column_dimensions[get_column_letter((i * 3) + 1)].width = 20

def write_information_to_spreadsheet(totals, worksheet, providers):
    handle_writing_of_attrs(ws, totals, providers)
    adjust_column_width(ws, 4)

fd = open("data/manifest.json", "r")
json_data = json.loads(fd.read())
wb = Workbook()

for site in json_data["sites"]:
    ws = wb.create_sheet(site["name"])
    providers = []
    for record in site["records"]:
        providers.append(record['submitter'])

    write_information_to_spreadsheet(get_totals_for_specific_attribute_on_specific_site(ws.title), ws, providers)
del wb["Sheet"]
wb.save("test.xlsx")
