# convert demographic-manager data to google sheets data
# to be interpreted by gas-demoman

# for information on gas-demoman, see
# https://git.beepboop.systems/stupidcomputer/gas-demoman
# and https://github.com/stupidcomputer/gas-demoman

# because the majority of the code that is in this repo
# is crap, we'll just be reimplementing the existing
# datastructures

import json
from typing import Any

def get_json_for_filename(filename: str) -> Any:
    with open(filename, "r") as file:
        return json.loads(file.read())

def replace_manifest_filename_references(manifest: dict) -> Any:
    for site in manifest["sites"]:
        to_replace = site["usedrecord"]
        site["usedrecord"] = get_json_for_filename("data/" + site["usedrecord"])["payload"]
    
    return manifest

json_data = get_json_for_filename("data/manifest.json")
json_data = replace_manifest_filename_references(json_data)
intern_data = get_json_for_filename("data/staffrecord.json")["payload"]

def translate_shortcodes_to_human_readable(shortcode: Any) -> str:
    mapping = {
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
        "unk": "Unknown",
        "u/o": "Unknown/Other",
        "ai/an": "American Indian/Alaskan Native",
        "nh/opi": "Native Hawaiian/Other Pacific Islander",
        "i": "Intern",
        "None": "Unknown",
    }

    return mapping[str(shortcode)]

def generate_intern_data_table(intern_data: dict) -> Any:
    output = [["First Name", "Last Name", "Gender", "Ethnicity", "Race"]]
    for intern in intern_data:
        result = []
        name = intern["name"].split(' ')
        result.append(name[0])
        result.append(name[1])
        result.append(translate_shortcodes_to_human_readable(intern["innerpayload"]["gender"]))
        result.append(translate_shortcodes_to_human_readable(intern["innerpayload"]["ethnicity"]))
        result.append(translate_shortcodes_to_human_readable(intern["innerpayload"]["race"]))

        output.append(result)

    return output

def generate_site_name_data_table(manifest: dict) -> Any:
    output = [["Site name", "Date", "Those Present", "Data leads", "On-site lead(s)", "Who collected?"]]

    for site in manifest["sites"]:
        result = []
        result.append(site["name"])
        result.append("{} {}".format(
            site["date"],
            site["time"],
        ))
        result.append(', '.join(site["present"]))
        result.append(', '.join(site["commleads"]))
        result.append(', '.join(site["onsiteleads"]))
        result.append(site["records"][0]["submitter"])

        output.append(result)

    return output

def generate_demographic_data_table(manifest: dict) -> Any:
    output = [["Site name", "Count", "Age", "Gender", "Ethnicity", "Race"]]

    for site in manifest["sites"]:
        for datum in site["usedrecord"]:
            fields = [
                "age",
                "gender",
                "ethnicity",
                "race"
            ]

            def mapper(x) -> Any:
                return translate_shortcodes_to_human_readable(datum[x])
            
            fields = map(mapper, fields)
            final = [site["name"], "1", *fields]
            output.append(final)

    return output

def convert_table_to_tsv(table: list[list[str]]) -> str:
    output = ""

    for row in table:
        output += "\t".join(row)
        output += "\n"
    
    return output

def write_file(filename: str, data: str) -> None:
    with open(filename, "w") as file:
        file.write(data)

write_file("demographic_data.tsv", convert_table_to_tsv(
    generate_demographic_data_table(json_data)
))

write_file("sites.tsv", convert_table_to_tsv(
    generate_site_name_data_table(json_data)
))

write_file("interns.tsv", convert_table_to_tsv(
    generate_intern_data_table(intern_data)
))