import os
import xml.etree.ElementTree as ET
INDIR = "input"


workdir = os.path.abspath(os.path.dirname(__file__))
indir = os.path.join(workdir, INDIR)
output = {}
print("\n\n\n")


def FENBeforeTable(fd, parser):
    for line in fd.readlines():
        parser.feed(line)
        for event, elem in parser.read_events():
            tag = elem.tag.removeprefix("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}")
            if event == "start":
                if tag == "tbl":
                    return
                continue
            if tag == "t":
                print(elem.text)



for fn in [os.path.join(indir, f) for f in os.listdir(INDIR) if os.path.isfile(os.path.join(INDIR, f))]:
    if fn.endswith(".xml"):
        with open(fn, encoding="utf-8") as xml:
            parser = ET.XMLPullParser(["start", "end"])
            row = []
            cell = ""
            # foundTable = False
            FENBeforeTable(xml, parser)
            for line in xml.readlines():
                parser.feed(line)
                for event, elem in parser.read_events():
                    # that's what the innocent-looking w: actually parses to
                    tag = elem.tag.removeprefix("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}")
                    
                    if event == "start":
                        # if tag == "tbl":
                        #     foundTable = True
                        continue

                    # if not foundTable:
                    #     # faculty, specialty etc
                    #     continue
                    
                    if tag == "tr":
                        print(row)
                        row = []
                    elif tag == "tc":
                        row.append(cell)
                        cell = ""
                    if tag == "t" and elem.text:
                        cell += elem.text