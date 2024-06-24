attrtable = {
#   attr, sel[i]
    "a": 0,
    "c": 0,
    "m": 0,
    "f": 0,
    "u/o": 0,
    "h": 0,
    "nh": 0,
    "ai/an": 1,
    "as": 1,
    "b/aa": 1,
    "nh/opi": 3,
    "wh": 0,
    "1+": 0,
    "unk": 2,
}

age = ["a", "c"]
gender = ["m", "f", "u/o"]
ethnicity = ["h", "nh"]
race = ["ai/an", "as", "b/aa", "nh/opi", "wh", "1+", "unk"]

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
    "unk": "Unknown",
    "ai/an": "American Indian/Alaskan Native",
    "None": "Unknown",
    "nh/opi": "Native Hawaiian/Other Pacific Islander",
    "i": "Intern",
}
