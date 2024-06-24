import json
import common
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font

def mapper(string):
    # map to human-readable values
    try:
        return common.mapper_data[string]
    except KeyError:
        return "WARNING: {}".format(string)

def aggregate_demographic_totals(payload, adultonly, childonly):
    results = {"age": {}, "gender": {}, "ethnicity": {}, "race": {}}

    for i in payload:
        if adultonly and i["age"] == "c":
            continue

        if childonly and i["age"] == "a":
            continue

        # for every entry we get
        for key in results.keys():
            # for every field we have
            results[key].setdefault(i[key], 0)
            results[key][i[key]] += 1

    return results

def get_totals_for_specific_attribute_on_specific_site(site, adultonly=False, childonly=False):
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

    return aggregate_demographic_totals(payload, adultonly, childonly)

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

def handle_writing_of_attrs(worksheet, totals, offset):
    count = 0
    maxlen = 0
    for i in totals.keys():
        tmp = generate_table_for_attr(i, totals)
        maxlen = max(maxlen, len(tmp))

        write_dataarray_to_specific_cell(offset, count * 3, tmp, worksheet)
        count += 1

    return maxlen

def adjust_column_width(worksheet, times):
    for i in range(times):
        worksheet.column_dimensions[get_column_letter((i * 3) + 1)].width = 20

def write_information_to_spreadsheet(totals, worksheet, offset):
    return handle_writing_of_attrs(ws, totals, offset)

def handle_spreadsheet_decoration(ws, providers, persons, commleads, onsiteleads):
    ws["A1"].value = "Information for {} site attendance.".format(ws.title)
    ws["A2"].value = "Fields not present should be assumed 0."
    ws["A3"].value = "Data submitted by {} in person after conclusion of site operations.".format(generate_provider_string(providers))
    ws["A4"].value = "Interns present: {}".format(generate_provider_string(persons))
    ws["A5"].value = "Communication Lead(s): {}".format(generate_provider_string(commleads))
    ws["A6"].value = "On Site Lead(s): {}".format(generate_provider_string(onsiteleads))
    ws.merge_cells("A1:E1")
    ws.merge_cells("A2:E2")
    ws.merge_cells("A3:H3")
    ws.merge_cells("A4:H4")
    ws.merge_cells("A5:H5")
    ws.merge_cells("A6:H6")

fd = open("data/manifest.json", "r")
json_data = json.loads(fd.read())
wb = Workbook()

for site in json_data["sites"]:
    providers = []
    for record in site["records"]:
        providers.append(record['submitter'])

    persons = site["present"]
    commleads = site["commleads"]
    onsiteleads = site["onsiteleads"]

    length = 8
    ws = wb.create_sheet(site["name"])

    ws.cell(row=length, column=1, value="Combined Totals")
    length += write_information_to_spreadsheet(get_totals_for_specific_attribute_on_specific_site(site["name"]), ws, length) + 2

    ws.cell(row=length, column=1, value="Adults")
    length += write_information_to_spreadsheet(get_totals_for_specific_attribute_on_specific_site(site["name"], adultonly=True), ws, length) + 3

    ws.cell(row=length, column=1, value="Children")
    length += write_information_to_spreadsheet(get_totals_for_specific_attribute_on_specific_site(site["name"], childonly=True), ws, length) + 3

    adjust_column_width(ws, 4)
    handle_spreadsheet_decoration(ws, providers, persons, commleads, onsiteleads)

del wb["Sheet"]
wb.save("test.xlsx")
