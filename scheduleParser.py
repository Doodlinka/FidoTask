import os, re, json, pprint


FACULTIES = {"Факультет інформатики", "Факультет економічних наук"}
# these are hardcoded, but idk how to figure them out from the file
DOCSPECS = {"Факультет економічних наук": {"ек": "Економіка",
    "мар": "Маркетинг",
    "мен": "Менеджмент",
    "фін": "Фінанси, банківська справа та страхування"}}
# TODO: П'ятниця is broken, has different apostrophes in different files
# put all of them in?
DAYS = {"Понеділок", "Вівторок", "Середа", "Четвер", "П`ятниця", "’ятниця", "Субота"}
TIMEREGEXP = "([01]?[0-9]|2[0-4]):([0-5]\d)-([01]?[0-9]|2[0-4]):([0-5]\d)"
DAYORDER = ("subject,teacher", "group", "weeks", "location")

INDIR = "input"
OUTFILE = "schedule.json"



# stolen from stackoverflow
def merge_dicts(tgt, enhancer):
    for key, val in enhancer.items():
        if key not in tgt:
            tgt[key] = val
            continue

        if isinstance(val, dict):
            merge_dicts(tgt[key], val)
        else:
            tgt[key] = val
    return tgt



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


# the subject and teacher are separated by the specialty here
# the spec. is noted in all kinds of ways, need to know them all?
def parseTXT(fd) -> dict:
    dayindex = 0
    output = {}
    root = output
    curday = ""
    curtime = ""
    curspecs = []
    faculty = ""
    pastheader = False

    for line in fd.readlines():
        t = t.strip()
        if not t: continue
        # print(t)
        # continue
        if not pastheader:
            if t in FACULTIES:
                output[t] = {}
                root = root[t]
                faculty = ""

            elif t.startswith("Спеціальність"):
                root[t[-6]] = {}
                root = root[t[-6]]
                # specialty
                for spec in DOCSPECS[faculty].values():
                    root[spec] = {}

        if t in DAYS:
            root[t] = {}
            dayroot = root[t]
            pastheader = True
            # print(t)

        elif pastheader:
            # switch time if encountered
            if re.match(TIMEREGEXP, t):
                curspecs = []
                dayindex = 0
                continue
            # reset the lesson here to not add empty dicts
            if dayindex >= len(DAYORDER):
                curspecs = []
                dayindex = 0
            # separate subject and teacher
            elif dayindex == 0:
                before = t.find("(")
                after = t.find(")")
                # print(t)
                for s in DOCSPECS[faculty]:
                    if s in t[before:after]:
                        curspecs.append(DOCSPECS[faculty][s])
                        # TODO: is it possible that something is already in this dict?
                        # don't clear it then
                        root[DOCSPECS[faculty][s]] = {}

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
output = {}

for fn in [os.path.join(workdir, f) for f in os.listdir(INDIR) if os.path.isfile(os.path.join(INDIR, f))]:
    if fn.endswith(".tsv"):
        with open(fn, encoding="utf-8") as infd:
            merge_dicts(output, parseTSV(infd))
    if fn.endswith(".txt"):
        with open(fn, encoding="utf-8") as infd:
            merge_dicts(output, parseTXT(infd))
    
with open(os.path.join(workdir, OUTFILE), "w", encoding="utf-8") as outfd:
    json.dump(output, outfd, ensure_ascii=False, indent="\t")