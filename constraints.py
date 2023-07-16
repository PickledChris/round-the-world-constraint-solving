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

ALL = [AFRICA, AT, CENTRAL_ASIA, CHINA, JAPAN, NEPAL_AND_INDIA, NZ, PI, SEA, SOUTH_AMERICA]

sections = [
    SectionConstraint(AT, ["March", "April", "May", "June"], 5),
    SectionConstraint(CENTRAL_ASIA, ["May", "June", "July", "August", "September"], 8),
    SectionConstraint(CHINA, ["May", "June", "July", "August", "September"], 4),
    SectionConstraint(JAPAN, ["April", "May", "June", "July", "August", "September", "October"], 4, banned_neighbours={AFRICA}),
    SectionConstraint(NZ, ["January", "February", "March", "April", "October", "November", "December"], 4,
                      banned_neighbours={SOUTH_AMERICA}),
    SectionConstraint(PI, ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
                           "December"], 2, required_neighbours={NZ}, banned_neighbours={AFRICA, AT, CENTRAL_ASIA, CHINA, NEPAL_AND_INDIA, SOUTH_AMERICA}),
    SectionConstraint(
        NEPAL_AND_INDIA, ["January", "February", "March", "April", "October", "November", "December"], 4
    ),
    SectionConstraint(
        SOUTH_AMERICA,
        ["January", "February", "March", "April", "May", "September", "October", "November", "December"],
        9,
        banned_neighbours={AFRICA, SEA, NEPAL_AND_INDIA, CHINA, NZ, PI},
    ),
    SectionConstraint(
        AFRICA,
        ["January", "February", "March", "April", "July", "August", "September", "October", "November", "December"],
        10
        ,
    ),
    SectionConstraint(
        SEA,
        ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
        6
        ,
    ),
]

print(f"{len(sections)} sections totalling {count_weeks(sections)} weeks")
for s in sections:
    print(s)
solve_trip_scheduling(sections, start_week=47)
