from model import SectionConstraint
from country_solver import count_weeks, solve_trip_scheduling

AFRICA = "Southeast Africa"
AT = "Appalachian Trail"
CENTRAL_ASIA = "Central Asia"
CHINA = "China"
JAPAN = "Japan"
NEPAL_AND_INDIA = "Nepal and India"
NZPI = "New Zealand and PI"
SEA = "Southeast Asia"
SOUTH_AMERICA = "South America"

ALL = [AFRICA, AT, CENTRAL_ASIA, CHINA, JAPAN, NEPAL_AND_INDIA, NZPI, SEA, SOUTH_AMERICA]

sections = [
    SectionConstraint(AT, ["March", "April", "May", "June"], 5, banned_neighbours=set()),
    SectionConstraint(CENTRAL_ASIA, ["May", "June", "July", "August", "September"], 8, banned_neighbours=set()),
    SectionConstraint(CHINA, ["May", "June", "July", "August", "September"], 4, banned_neighbours=set()),
    SectionConstraint(JAPAN, ["April", "May", "June", "July", "August", "September", "October"], 4, banned_neighbours=set()),
    SectionConstraint(NZPI, ["January", "February", "March", "April", "October", "November", "December"], 6, banned_neighbours=set()),
    SectionConstraint(
        NEPAL_AND_INDIA, ["January", "February", "March", "April", "October", "November", "December"], 4, banned_neighbours=set()
    ),
    SectionConstraint(
        SOUTH_AMERICA,
        ["January", "February", "March", "April", "May", "September", "October", "November", "December"],
        9,
        banned_neighbours={AFRICA, SEA, NEPAL_AND_INDIA, CHINA, NZPI},
    ),
    SectionConstraint(
        AFRICA,
        ["January", "February", "March", "April", "July", "August", "September", "October", "November", "December"],
        10,
        banned_neighbours=set(),
    ),
    SectionConstraint(
        SEA,
        ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
        6,
        banned_neighbours=set(),
    ),
]

print(f"{len(sections)} sections totalling {count_weeks(sections)} weeks")
for s in sections:
    print(s)
solve_trip_scheduling(sections, start_week=47)