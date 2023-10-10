# input: a folder with .tsv and .doc files in it
# output: a .json with ALL of their data

# json structure:
# faculty
# year
# specialty
# ??? (but put the teacher separately if you can)
import os, re, json, pprint


FACULTIES = {"Факультет інформатики"}
# SPECIALTIES = {"Інженерія програмного забезпечення"}
# TODO: П'ятниця is broken, has different apostrophes in different files
# put all of them in?
DAYS = {"Понеділок", "Вівторок", "Середа", "Четвер", "П`ятниця", "’ятниця", "Субота"}
TIMEREGEXP = "([01]?[0-9]|2[0-4]):([0-5]\d)-([01]?[0-9]|2[0-4]):([0-5]\d)"
DAYORDER = ("subject,teacher", "group", "weeks", "location")

INDIR = "input"
OUTFILE = "schedule.json"



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



def parseTSV(fd) -> dict:
    dayindex = 0
    output = {}
    root = output
    dayroot = root
    curtime = ""
    curlessons = []
    pastheader = False

    for line in fd.readlines():
        for t in line.split("\t"):
            t = t.strip()
            if not t: continue
            # print(t)
            # continue
            if not pastheader:
                if t in FACULTIES:
                    output[t] = {}
                    root = root[t]

                elif t.startswith("Спеціальність"):
                    spl = t.split('"')
                    # year
                    root[spl[2][2]] = {}
                    root = root[spl[2][2]]
                    # specialty
                    spec = spl[1].strip()
                    root[spec] = {}
                    root = root[spec]

            if t in DAYS:
                root[t] = {}
                dayroot = root[t]
                pastheader = True
                # print(t)

            # TODO: handle several lessons at one time
            # an array of dicts? a dict of dicts with either subject or group as keys?
            elif pastheader:
                # switch time if encountered
                if re.match(TIMEREGEXP, t):
                    curlessons = [{}]
                    dayroot[t] = curlessons
                    dayindex = 0
                    continue
                # reset the lesson here to not add empty dicts
                if dayindex >= len(DAYORDER):
                    curlessons.append({})
                    dayindex = 0
                # separate subject and teacher
                elif dayindex == 0:
                    spl = t.split(",", 1)
                    # print(t)
                    curlessons[-1]["subject"] = spl[0].strip()
                    curlessons[-1]["teacher"] = spl[1].strip()
                # convert weeks to a list of numbers
                elif dayindex == 2:
                    weeks = []
                    nums = t.split(",")
                    for n in nums:
                        r = n.split("-")
                        # print(r)
                        if len(r) == 1:
                            weeks.append(int(r[0]))
                        else:
                            weeks.extend(list(range(int(r[0]), int(r[1]) + 1)))
                    curlessons[-1][DAYORDER[dayindex]] = weeks
                # handle everything else
                else:
                    # print(dayindex, t)
                    curlessons[-1][DAYORDER[dayindex]] = t
                
                dayindex += 1
                    
    # pprint.pprint(output)
    return output


workdir = os.path.join(os.path.abspath(os.path.dirname(__file__)), INDIR)
for fn in [os.path.join(workdir, f) for f in os.listdir(INDIR) if os.path.isfile(os.path.join(INDIR, f))]:
    if fn.endswith(".tsv"):
        with open(fn, encoding="utf-8") as infd, open(os.path.join(workdir, OUTFILE), "w", encoding="utf-8") as outfd:
            json.dump(parseTSV(infd), outfd, ensure_ascii=False, indent="\t")