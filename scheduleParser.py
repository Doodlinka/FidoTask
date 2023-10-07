# input: a folder with .tsv and .doc files in it
# output: a .json with ALL of their data

# json structure:
# faculty
# year
# specialty
# ??? (but put the teacher separately if you can)
import os
import os.path as path
import pprint
# import json


# TODO: write down marker constants (faculties, specialties, week days etc)
FACULTIES = {"Факультет інформатики"}
SPECIALTIES = {"Інженерія програмного забезпечення"}
# TODO: П'ятниця is broken, has different apostrophes in different files
# either compare to the end of the token or flatten the charset somehow
DAYS = {"Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота"}
INDIR = "input"



# stolen from stackoverflow, will likely need later
# def merge_dicts(tgt, enhancer):
#     for key, val in enhancer.items():
#         if key not in tgt:
#             tgt[key] = val
#             continue

#         if isinstance(val, dict):
#             merge_dicts(tgt[key], val)
#         else:
#             tgt[key] = val
#     return tgt



# TODO: consider passing in the result of fd.read()
# TODO: consider introducing "stages", so that, for instance,
# specialties are checked only if you're at the faculty level (here, once)
def parseTSV(fd) -> dict:
    output = {}
    faculty, year, specialty = "", "", ""

    for line in fd.readlines():
        for t in line.split("\t"):
            t = t.strip()
            if not t: continue
            # print(t)

            if not faculty and t in FACULTIES:
                faculty = t
                output[faculty] = {}

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
            # TODO: how to handle weeks? make them values
            # will probably have to convert to number range either way



workdir = os.path.join(os.path.abspath(os.path.dirname(__file__)), INDIR)
for fn in [os.path.join(workdir, f) for f in os.listdir(INDIR) if path.isfile(path.join(INDIR, f))]:
    if fn.endswith(".tsv"):
        with open(fn, encoding="utf-8") as fd:
            parseTSV(fd)
            # pprint.pprint(fd.read().split("\t"))