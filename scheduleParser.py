# input: a folder with .tsv and .doc files in it
# output: a .json with ALL of their data

# json structure:
# faculty
# year
# specialty
# ??? (but put the teacher separately if you can)
import os
import os.path as path
# import json


# TODO: write down marker constants (faculties, specialties, week days etc)
FACULTIES = {"Факультет інформатики"}
SPECIALTIES = {"Інженерія програмного забезпечення"}
# TODO: П'ятниця is broken, has different apostrophes in different files
# either compare to the end of the token or flatten the charset somehow
DAYS = {"Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота"}
INDIR = "input"



# TODO: consider introducing "stages", so that, for instance,
# specialties are checked only if you're at the faculty level (here, once)
# TODO: updating the dictpath takes 2 actions, make it take 1
# or ditch the thing, or find a library to make working with dicts easier
def parseTSV(fd) -> dict:
    output = {}
    dictpath = [output]

    for t in fd.read().split("\t"):
        t = t.strip()
        if not t: continue

        if t in FACULTIES:
            dictpath[-1][t] = {}
            dictpath.append(dictpath[-1][t])

        elif t.beginswith("Спеціальність"):
            spl = t.split('"')
            dictpath[-1][spl[2][2]] = {}
            dictpath.append(dictpath[-1][spl[2][2]])
            spec = spl[1].strip()
            dictpath[-1][spec] = {}
            dictpath.append(dictpath[-1][spec])

        elif t in DAYS:
            dictpath[-1][t] = {}
            dictpath.append(dictpath[-1][t])

        # TODO: check for times, if found, look for the following in that order:
        # subject+teacher (comma separated), group, weeks, location
        # TODO: how to handle weeks? makes them keys or values?
        # will probably have to convert to number range either way



os.curdir = os.path.abspath(__file__)
for fn in [f for f in os.listdir(INDIR) if os.isfile(path.join(INDIR, f))]:
    if fn.endswith(".tsv"):
        with open(fn) as fd:
            parseTSV(fd)