from model import SectionConstraint
from country_solver import count_weeks, solve_trip_scheduling

AFRICA = "Southeast Africa"
AT = "Appalachian Trail"
CENTRAL_ASIA = "Central Asia"
CHINA = "China"
JAPAN = "Japan"
NEPAL_AND_INDIA = "Nepal and India"
NZ = "New Zealand"
PI = "Pacific Islands"
SEA = "Southeast Asia"
SOUTH_AMERICA = "South America"

ALL = [AFRICA, AT, CENTRAL_ASIA, CHINA, JAPAN, NEPAL_AND_INDIA, NZ, SEA, SOUTH_AMERICA]

sections = [
    SectionConstraint(AT, ["March", "April", "May", "June"], 5, required_neighbours={JAPAN}),
    SectionConstraint(CENTRAL_ASIA, ["May", "June", "July", "August", "September"], 10, required_neighbours={CHINA}),
    SectionConstraint(CHINA, ["May", "June", "July", "August", "September"], 4),
    SectionConstraint(
        JAPAN,
        ["April", "May", "June", "July", "August", "September", "October"],
        4,
        required_neighbours={CHINA},
    ),
    SectionConstraint(NZ, ["January 0", "February", "March", "April", "October", "November 0", "December 0"], 7),
    # SectionConstraint(PI, ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
    #                        "December"], 2, required_neighbours={NZ}, banned_neighbours={AFRICA, AT, CENTRAL_ASIA, CHINA, NEPAL_AND_INDIA, SOUTH_AMERICA}),
    SectionConstraint(NEPAL_AND_INDIA, ["January", "February", "March", "April", "October", "November", "December"], 6),
    SectionConstraint(
        SOUTH_AMERICA,
        ["January 1", "February 1", "March 1", "April", "May", "September", "October", "November 1", "December 1"],
        9,
        # required_neighbours={AFRICA},
        # banned_neighbours={NZ, NEPAL_AND_INDIA},
    ),
    SectionConstraint(
        AFRICA,
        ["January 1", "February 1", "March", "April", "July", "August", "September", "October", "November 1", "December 1"],
        9,
    ),
    SectionConstraint(
        SEA,
        ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
        5,
    ),
]

print(f"{len(sections)} sections totalling {count_weeks(sections)} weeks")
for s in sections:
    print(s)
solve_trip_scheduling(sections, start_week=47)
