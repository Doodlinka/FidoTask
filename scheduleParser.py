import os, re, json, itertools
import xml.etree.ElementTree as ET


FACULTIES = {"Факультет інформатики", "Факультет економічних наук"}
# these are hardcoded, but idk how to figure them out from the file
DOCSPECS = {"Факультет економічних наук": {
    "ек": "Економіка",
    "мар": "Маркетинг",
    "мен": "Менеджмент",
    "фін": "Фінанси, банківська справа та страхування"}}
# П'ятниця is kinda broken, has different apostrophes in different files
DAYS = {"Понеділок", "Вівторок", "Середа", "Четвер", "П`ятниця", "’ятниця", "Субота", "Неділя"}
TIMEREGEXP = "([01]?[0-9]|2[0-4])[:.]([0-5]\d)-([01]?[0-9]|2[0-4])[:.]([0-5]\d)"
LESSONORDER = ("subject,teacher", "group", "weeks", "location")
# that's what the innocent-looking w: actually parses to
WPREFIX = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
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


# this is vulnerable because it reads the entire
# (potentially huge) file into memory
def splitAndStripGen(fd, sep = "\n"):
    for t in re.split(sep, fd.read()):
        t = t.strip()
        if t: yield t



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
                if dayindex >= len(LESSONORDER):
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
                    curlessons[-1][LESSONORDER[dayindex]] = weeks
                # handle everything else
                else:
                    # print(dayindex, t)
                    curlessons[-1][LESSONORDER[dayindex]] = t
                
                dayindex += 1
                    
    return output


def getXMLBeforeTable(fd, parser):
    faculty = ""
    year = ""
    specs = []
    isspec = False
    for line in fd:
        parser.feed(line)
        for event, elem in parser.read_events():
            tag = elem.tag.removeprefix(WPREFIX)
            if event == "start":
                if tag == "tbl":
                    return (faculty, year, specs)
                continue
            if not elem.text: continue

            if tag == "t":
                if elem.text in FACULTIES:
                    faculty = elem.text
                    if faculty in DOCSPECS:
                        specs.extend(DOCSPECS[faculty].values())
                elif elem.text.startswith("Спеціальність"):
                    isspec = True
                elif isspec:
                    # if xml is used for the other type, look for specialty here
                    year = elem.text[-6]
                    isspec = False
    return (faculty, year, specs)


def XMLTableRowGen(fd, parser):
    row = []
    cell = ""
    for line in fd:
        parser.feed(line)
        for event, elem in parser.read_events():
            tag = elem.tag.removeprefix(WPREFIX)
            if event == "start":
                continue
            if tag == "tr":
                yield row
                row = []
            elif tag == "tc":
                row.append(cell)
                cell = ""
            if tag == "t" and elem.text:
                cell += elem.text


def parseXML(fd):
    parser = ET.XMLPullParser(["start", "end"])
    output = {}
    root = output

    header = getXMLBeforeTable(fd, parser)
    faculty = header[0]
    root[header[0]] = {}
    root = root[header[0]]
    root[header[1]] = {}
    root = root[header[1]]
    for spec in header[2]:
        root[spec] = {}

    curday = ""
    curtime = ""
    rows = XMLTableRowGen(fd, parser)
    # skip the header
    next(rows)
    
    for row in rows:
        if row[0]:
            curday = row[0]
            for spdict in root.values():
                spdict[row[0]] = {}
        if row[1]:
            curtime = row[1]
            for spdict in root.values():
                spdict[curday][row[1]] = []
        # some lessons are empty, even if they have the week or time
        if not row[2]: continue

        # separate subject, teacher, specialty
        before = row[2].find("(")
        after = row[2].find(")")
        subject = row[2][:before].strip()
        teacher = row[2][after+1:].strip()
        # convert weeks to number range
        weeks = []
        nums = row[4].split(",")
        for n in nums:
            r = n.split("-")
            if len(r) == 1:
                weeks.append(int(r[0]))
            else:
                weeks.extend(list(range(int(r[0]), int(r[1]) + 1)))
        
        # save the data
        for spcode in DOCSPECS[faculty]:
            if spcode in row[2][before:after]:
                outdict = {}
                root[DOCSPECS[faculty][spcode]][curday][curtime].append(outdict)
                outdict["subject"] = subject
                outdict["teacher"] = teacher
                outdict["weeks"] = weeks
                outdict["group"] = row[3]
                outdict["location"] = row[5]

    return output


# the subject and teacher are separated by the specialty here
def parseTXT(tokens, minsubjectlen = 20) -> dict:
    output = {}
    root = output
    faculty = ""
    t = next(tokens)

    while t not in FACULTIES:
        t = next(tokens)
    output[t] = {}
    root = root[t]
    faculty = t

    while not t.startswith("Спеціальність"):
        t = next(tokens)
    root[t[-6]] = {}
    root = root[t[-6]]
    for spec in DOCSPECS[faculty].values():
        root[spec] = {}

    while t not in DAYS:
        t = next(tokens) 
    curday = t
    for spdict in root.values():
        spdict[t] = {}  

    curlesson = []
    curtime = ""  

    while tokens:
        # print(t)
        if t in DAYS:
            curday = t
            for spdict in root.values():
                spdict[t] = {}
            t = next(tokens)

        if re.match(TIMEREGEXP, t):
            # print(curday, t)
            curtime = t
            for spdict in root.values():
                spdict[curday][t] = []
            t = next(tokens)

        # the subject+teacher field is sometimes split over 2 tokens
        # take 4 of 'em and check if the next is long enough to be the next subject
        for _ in range(len(LESSONORDER)):
            curlesson.append(t)
            t = next(tokens)
        # if it's not, glue the teacher to the subject and read another token for the location
        # also make sure it's not the next time
        # TODO: checking this in any way eats the next subject, how to avoid?
        # - peek and check for time and day here
        # - remember the current time and day separately, check for time, day and the subject on the next iteration
        # - check for subject on the next iteration, check for time and day twice (to change them after the lesson is recorded)
        if len(t) < minsubjectlen and not re.match(TIMEREGEXP, t) and t not in DAYS:
            curlesson[0] += " " + curlesson.pop(1)
            curlesson.append(t)
            t = next(tokens)
        # tokens = itertools.chain([t], tokens) \

        print(curlesson)
        # separate subject, teacher, specialty
        before = curlesson[0].find("(")
        after = curlesson[0].find(")")
        subject = curlesson[0][:before].strip()
        teacher = curlesson[0][after+1:].strip()
        # convert weeks to number range
        weeks = []
        nums = curlesson[2].split(",")
        for n in nums:
            r = n.split("-")
            # print(r)
            if len(r) == 1:
                weeks.append(int(r[0]))
            else:
                weeks.extend(list(range(int(r[0]), int(r[1]) + 1)))
        # add all of that + group and location to each specialty's day and time
        for spcode in DOCSPECS[faculty]:
            if spcode in t[before:after]:
                outdict = {}
                root[DOCSPECS[faculty][spcode]][curday][curtime].append(outdict)
                outdict["subject"] = subject
                outdict["teacher"] = teacher
                outdict["weeks"] = weeks
                outdict[LESSONORDER[1]] = curlesson[1]
                outdict[LESSONORDER[3]] = curlesson[3]

        curlesson = []


    # for t in fd.readlines():
    #     t = t.strip()
    #     if not t: continue
    #     # print(t)
    #     # continue
    #     if not pastheader:
    #         if t in FACULTIES:
    #             output[t] = {}
    #             root = root[t]
    #             faculty = t

    #         elif t.startswith("Спеціальність"):
    #             root[t[-6]] = {}
    #             root = root[t[-6]]
    #             # specialty
    #             for spec in DOCSPECS[faculty].values():
    #                 root[spec] = {}

    #     if t in DAYS:
    #         for spdict in root.values():
    #             spdict[t] = {}
    #         pastheader = True
    #         # print(t)

    #     elif pastheader:
    #         # switch time if encountered
    #         if re.match(TIMEREGEXP, t):
    #             curspecdicts = []
    #             dayindex = 0
    #             continue
    #         # reset the lesson here to not add empty dicts
    #         if dayindex >= len(LESSONORDER):
    #             curspecdicts = []
    #             dayindex = 0
    #         # separate subject, specialty and teacher
    #         if dayindex == 0:
    #             before = t.find("(")
    #             after = t.find(")")
    #             subject = t[:before].strip()
    #             teacher = t[after+1:].strip()
    #             if not teacher:
    #                 print("lost teacher")
    #                 foundTeacher = False
    #             # print(t)
    #             for spcode in DOCSPECS[faculty]:
    #                 if spcode in t[before:after]:
    #                     spdict = root[DOCSPECS[faculty][spcode]]
    #                     curspecdicts.append(spdict)
    #                     spdict["subject"] = subject
    #                     spdict["teacher"] = teacher
    #         # the teacher may sometimes be on the next line, account for that
    #         elif not foundTeacher:
    #             foundTeacher = True
    #             print("teacher handling")
    #             for spdict in curspecdicts:
    #                 spdict["teacher"] = t
    #             continue
    #         # convert weeks to a list of numbers
    #         elif dayindex == 2:
    #             weeks = []
    #             nums = t.split(",")
    #             for n in nums:
    #                 r = n.split("-")
    #                 # print(r)
    #                 if len(r) == 1:
    #                     weeks.append(int(r[0]))
    #                 else:
    #                     weeks.extend(list(range(int(r[0]), int(r[1]) + 1)))
    #             for spdict in curspecdicts:
    #                 spdict[LESSONORDER[dayindex]] = weeks
    #         # handle everything else
    #         else:
    #             # print(dayindex, t)
    #             for spdict in curspecdicts:
    #                 spdict[LESSONORDER[dayindex]] = t
            
    #         print(dayindex, t)
    #         print(foundTeacher)
    #         dayindex += 1
                    
    return output



workdir = os.path.abspath(os.path.dirname(__file__))
indir = os.path.join(workdir, INDIR)
output = {}
print("\n\n\n")

for fn in [os.path.join(indir, f) for f in os.listdir(INDIR) if os.path.isfile(os.path.join(INDIR, f))]:
    if fn.endswith(".tsv"):
        with open(fn, encoding="utf-8") as infd:
            merge_dicts(output, parseTSV(infd))
    if fn.endswith(".xml"):
        with open(fn, encoding="utf-8") as infd:
            merge_dicts(output, parseXML(infd))
    
with open(os.path.join(workdir, OUTFILE), "w", encoding="utf-8") as outfd:
    json.dump(output, outfd, ensure_ascii=False, indent="\t")