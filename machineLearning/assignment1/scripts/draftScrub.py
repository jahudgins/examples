import re
import sys
# import pdb

from optparse import OptionParser

def scrubError(message):
    # pdb.set_trace()
    sys.stderr.write(message + "\n")
    print(message)
    sys.exit(1)

def validMatch(matchObjects, key):
    return matchObjects.has_key(key) and len(matchObjects[key].group('value')) > 0

parser = OptionParser()
parser.add_option("-f", "--file", dest="filename", help="draft file to scrub", metavar="FILE")
parser.add_option("-s", "--season", dest="season", help="season to collect stats for")

(options, args) = parser.parse_args()

if not options.filename:
    parser.error("Must specifiy filename (-f)")
if not options.season:
    parser.error("Must specifiy season (-s 2004-05)")

file = open(options.filename)
lines = file.readlines()
file.close


startStats = False

tags = [['fullName',        "Full Name"],
        ['position',        "Position"],
        ['heightWeight',    "Height/Weight"],
        ['birthdate',       "Birthdate"],
        ['college',         "College"],
        ['country',         "Country"],
        ['highschool',      "High School"]]

statOrder = []
statOrder.append("Season")
statOrder.append("G")
statOrder.append("GS")
statOrder.append("FGM")
statOrder.append("FGA")
statOrder.append("PCT")
statOrder.append("FTM")
statOrder.append("FTA")
statOrder.append("PCT")
statOrder.append("3PM")
statOrder.append("3PA")
statOrder.append("PCT")
statOrder.append("REB")
statOrder.append("AST")
statOrder.append("STL")
statOrder.append("BL")
statOrder.append("PTS")
statOrder.append("AVG")

stats = [0.] * len(statOrder)

matchObjects = dict()
collectStats = False
count = 0
season = None
foundStats = False

for line in lines:
    personalStats = re.match(r'.*personal stats', line)
    startStats = startStats or personalStats != None
    if not startStats:
        continue

    for [key, tag] in tags:
        m = re.match(r'.*{0}:</b>(?P<value>.*\S)\s*'.format(tag), line)
        if m:
            matchObjects[key] = m

    # start collecting when we see a season
    if not season:
        season = re.match(r'.*<td.*Season<', line)

    if season:
        m = re.match(r'.*<td.*{0}<'.format(statOrder[count]), line)
        if not m:
            scrubError("Error stats are not in the expected order!")
        count += 1
        if count == len(statOrder):
            season = None
            count = 0

    # only collect stats for the specified season
    if re.match(r'.*<td[^>]*>{0}</td>'.format(options.season), line):
        collectStats = True
        statIdx = 0

    if collectStats:
        foundStats = True
        if re.match(r'.*</tr>', line):
            collectStats = False
        else:
            m = re.match(r'.*<td[^>]*>(?P<value>.*)</td>', line)
            if m:
                if statIdx == 0:
                    stats[statIdx] = m.group('value')
                else:
                    # skip empty string
                    if len(m.group('value')) != 0:
                        stats[statIdx] += float(m.group('value'))


                statIdx += 1
            
        
    """
    if playfor:
        team = re.match(r'<font .*<b>(?P<value>.*)</b>', line)
        if re.match(r'.*</table>', line):
            matchStats['GS'] = gs
            playfor = None
    """
    
# just skip this player no-stats
if not foundStats:
    sys.stderr.write("No stats found for {0} (expected)\n".format(options.filename))
    sys.exit(0)

for [key, tag] in tags:
    if key in ['college', 'country', 'highschool']:
        continue

    if not matchObjects[key]:
        scrubError("no {0} match found".format(key))

    sys.stdout.write("{0},".format(matchObjects[key].group('value').strip()))


if validMatch(matchObjects, 'college'):
    sys.stdout.write("college,")
elif validMatch(matchObjects, 'country'):
    sys.stdout.write("international,")
elif validMatch(matchObjects, 'highschool'):
    sys.stdout.write("highschool,")
else:
    scrubError("unexpected college/country")

for stat in stats:
    sys.stdout.write("{0},".format(stat))
sys.stdout.write("\n")

