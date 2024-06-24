import curses
import logging
import json
import sys
import common

# logging.basicConfig(filename="enterer.log", level=logging.DEBUG)

def serialize_finalsels_to_json(finalsels, filename):
    json_wrapper = {"payload": []}
    json_objs = []
#    logging.debug("lllllllllllll {}".format(finalsels))
    for i in finalsels:
        new_json_obj = {"age": None, "gender": None, "ethnicity": None, "race": None}
        for j in i[1]:
            if j in common.age:
                new_json_obj["age"] = j

            if j in common.gender:
                new_json_obj["gender"] = j

            if j in common.ethnicity:
                new_json_obj["ethnicity"] = j

            if j in common.race:
                new_json_obj["race"] = j

        for _ in range(i[0]):
            json_objs.append(new_json_obj)

    json_wrapper["payload"] = json_objs
#    logging.debug((json_objs, json_wrapper))
    with open(filename, "w", encoding="utf-8") as f:
        f.write(json.dumps(json_wrapper, indent=4))

## TODO: add padding for window elements
## TODO: add exportation
def pad_out_rest_of_line(window):
    window.refresh()
    height, width = window.getmaxyx()
    y, x = window.getyx()
    diff = width - x
#    logging.debug("lakfdjalskfjalskdfjalkfjsd {}".format(str(diff)))
    window.addstr(y, x, " " * diff, curses.A_REVERSE)

def check_if_attr_selected(attr, sel):
#    logging.debug(attrtable[attr])
#    logging.debug((attrtable[attr], attr[attrtable[attr]], sel))
    if attr[common.attrtable[attr]] == sel:
        return True
    return False

def equality_sel_check(attr, sel):
    return attr == sel

def generate_outstring_format_values(sels):
    output = []
    for i in common.attrtable.keys(): # will always be sorted, in order
        for j in sels:
            if check_if_attr_selected(i, j):
                output.append("[{}]".format(i))
                break
        if not "[{}]".format(i) in output:
            output.append("{}".format(i))

    return output

def convert_sels_arr_to_attrs(sels):
    output = []
    for i in common.attrtable.keys(): # will always be sorted, in order
        for j in sels:
#            logging.debug(str((i, j)))
            if check_if_attr_selected(i, j):
                output.append(i)
                break
    return output

def get_attr_cata_counts(sels):
    ages = 0
    genders = 0
    ethnicities = 0
    races = 0
    for i in sels:
        if i in common.age:
            ages += 1
        if i in common.gender:
            genders += 1
        if i in common.ethnicity:
            ethnicities += 1
        if i in common.race:
            races += 1

    return (ages, genders, ethnicities, races)

def resolve_sel_conflict(sels):
    final = convert_sels_arr_to_attrs(sels)
    ages, genders, ethnicities, races = get_attr_cata_counts(final)

#    logging.debug(final)
#    logging.debug((ages, genders, ethnicities, races))

    if ages > 1:
        for i in final:
            if i in common.age:
                final.remove(i)

    if genders > 1:
        for i in final:
            if i in common.gender:
                final.remove(i)

    if ethnicities > 1:
        for i in final:
            if i in common.ethnicity:
                final.remove(i)

    if races > 1:
        for i in final:
            if i in common.race:
                final.remove(i)

    finalfinal = []
    for i in final:
        finalfinal.append(i[common.attrtable[i]])

    return finalfinal

def main(stdscr):
    stdscr.clear()
    outputsels = []
    currentsels = []
    previoussels = []
    lines = 1
    count = ""
    errstring = ""
    status = ""
    outfile = sys.argv[1]

    while True:
        stdscr.addstr(0, 0, "enterer - normal mode - {}".format(status), curses.A_REVERSE)
        pad_out_rest_of_line(stdscr)
        stdscr.move(lines, 0)
        stdscr.clrtoeol()
        stdscr.addstr(lines, 0, "{}{} | {} {} | {} {} {} | {} {} | {} {} {} {} {} {} {}".format(
            errstring,
            count,
            *generate_outstring_format_values(currentsels)
        ))
        newsel = stdscr.getkey()

        if errstring != "":
            errstring = ""

        if status != "":
            status = ""

        if newsel == '\\':
            currentsels, previoussels = previoussels, currentsels
            continue

        if newsel in [str(i) for i in range(10)]:
            count += newsel
            continue


        if newsel in ('KEY_BACKSPACE', '\b', '\x7f'):
            count = count[:-1]
            continue

        if newsel == ']':
            final_output = []
            for i in outputsels:
                temp = convert_sels_arr_to_attrs(i[1])
                final_output.append([i[0], temp])

#            logging.debug("selsconverter" + str(final_output))
            try:
                serialize_finalsels_to_json(final_output, outfile)
            except FileNotFoundError:
                status = "failed to write. changing outfile to __RESCUE_OUTFILE.json. write again"
                outfile = "__RESCUE_OUTFILE.json"

            status = "written to {}".format(outfile)
            continue

        if newsel == ' ':
            catagories_data = get_attr_cata_counts(convert_sels_arr_to_attrs(currentsels))
            not_all_one = False
            for i in catagories_data:
                if not i == 1:
                    not_all_one = True
                    break

            if not_all_one:
                errstring += "!"
                continue

            if count == "":
                count = 1

            outputsels.append((int(count), currentsels))
            count = ""
            previoussels = currentsels
            currentsels = []
            lines += 1
            continue

        if not newsel in currentsels:
            currentsels.append(newsel)
        else:
            currentsels.remove(newsel)

        currentsels = resolve_sel_conflict(currentsels)


    stdscr.refresh()
    stdscr.getkey()

curses.wrapper(main)
