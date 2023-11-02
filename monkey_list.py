
MONKEY_COLORS = {
    # new colors
    #  Luminance: 30%, Saturation 100%
    "PURPLE1": 0x006699,
    "GREEN1": 0x8F9900,  # 1
    "DARKBLUE": 0x001C99,  # 2
    "BROWN": 0x995C00,  # 2
    "KAKI": 0x999100,  # 3
    "PURPLE": 0x420099,  # 4
    "TURQUOISE1": 0x00998A,  # 5
    "ROST": 0x992E00,  # 6
    "BLUE1": 0x001499,  # 7
    "SAND": 0x995E00,  # 8
    "BLUE2": 0x0A0099,  # 9
    "ORANGE": 0x996B00,  # 10
    "ROSTBROWN": 0x993800,  # 11
    "TURQUOISE2": 0x008A99,  # 12
    "OLIVE": 0x879900,  # 13
    "PURPLE2": 0x660099,  # 14
    "ROST2": 0x993D00,  # 15
    "TURQUOISE3": 0x007A99,  # 16
    "SKYBLUE": 0x005E99,  # 17
    "BROWN2": 0x994500,  # 18




    "BLACK": 0x000000,
    "RED": 0xFF0000,  # red lever light
    "WHITE": 0xFFFFFF,  # choice training
    "BLUE": 0x0000FF,  # choice training
    "LIGHTYELLOW": 0xEDF425,
    "GREY": 0x9CC9C7

}

MONKEYS = {
    "DUMMY": {
        "NAME": "dummy",
        "SEX": "F",
        "AGE": "23",
        "COLOR_RISK": MONKEY_COLORS["GREY"],
        "COLOR_SAFE": MONKEY_COLORS["LIGHTYELLOW"],
        "COLOR_RISK_SAMPLING2": MONKEY_COLORS["GREY"],
        "COLOR_SAFE_SAMPLING2": MONKEY_COLORS["LIGHTYELLOW"],
        "DISTRIBUTOR_FIRST": "machine_first",
        "CONTROLLER_ID": "Judit",
        "DISTRIBUTOR_ID": "Carina",
    },
    "MORITZ": {
        "NAME": "moritz",
        "SEX": "M",
        "AGE": "60",
        "COLOR_RISK": MONKEY_COLORS["PURPLE1"],
        "COLOR_SAFE": MONKEY_COLORS["GREEN1"],
        "COLOR_RISK_SAMPLING2": MONKEY_COLORS["TURQUOISE1"],
        "COLOR_SAFE_SAMPLING2": MONKEY_COLORS["ROST"],
        "DISTRIBUTOR_FIRST": "human_first",
        "CONTROLLER_ID": "Judit",
        "DISTRIBUTOR_ID": "Carina",
    },
    "MADITA": {
        "NAME": "madita",
        "SEX": "F",
        "AGE": "49",
        "COLOR_RISK": MONKEY_COLORS["DARKBLUE"],
        "COLOR_SAFE": MONKEY_COLORS["BROWN"],
        "COLOR_RISK_SAMPLING2": MONKEY_COLORS["ROSTBROWN"],
        "COLOR_SAFE_SAMPLING2": MONKEY_COLORS["TURQUOISE2"],
        "DISTRIBUTOR_FIRST": "machine_first",
        "CONTROLLER_ID": "Judit",
        "DISTRIBUTOR_ID": "Carina",
    },
    "SIMON": {
        "NAME": "simon",
        "SEX": "M",
        "AGE": "48",
        "COLOR_RISK": MONKEY_COLORS["KAKI"],
        "COLOR_SAFE": MONKEY_COLORS["PURPLE"],
        "COLOR_RISK_SAMPLING2": MONKEY_COLORS["SKYBLUE"],
        "COLOR_SAFE_SAMPLING2": MONKEY_COLORS["BROWN2"],
        "DISTRIBUTOR_FIRST": "human_first",
        "CONTROLLER_ID": "Carina",
        "DISTRIBUTOR_ID": "Judit",
    },
    "INGEBORG": {
        "NAME": "ingeborg",
        "SEX": "F",
        "AGE": "11",
        "COLOR_RISK": MONKEY_COLORS["TURQUOISE1"],
        "COLOR_SAFE": MONKEY_COLORS["ROST"],
        "COLOR_RISK_SAMPLING2": MONKEY_COLORS["ROST"],
        "COLOR_SAFE_SAMPLING2": MONKEY_COLORS["TURQUOISE1"],
        "DISTRIBUTOR_FIRST": "machine_first",
        "CONTROLLER_ID": "Carina",
        "DISTRIBUTOR_ID": "Judit",
    },
    "MICHEL": {
        "NAME": "michel",
        "SEX": "M",
        "AGE": "28",
        "COLOR_RISK": MONKEY_COLORS["BLUE1"],
        "COLOR_SAFE": MONKEY_COLORS["SAND"],
        "COLOR_RISK_SAMPLING2": MONKEY_COLORS["ROST2"],
        "COLOR_SAFE_SAMPLING2": MONKEY_COLORS["TURQUOISE3"],
        "DISTRIBUTOR_FIRST": "machine_first",
        "CONTROLLER_ID": "Judit",
        "DISTRIBUTOR_ID": "Carina",
    },
    "SCHROEDER": {
        "NAME": "schroeder",
        "SEX": "M",
        "AGE": "28",
        "COLOR_RISK": MONKEY_COLORS["BLUE2"],
        "COLOR_SAFE": MONKEY_COLORS["ORANGE"],
        "COLOR_RISK_SAMPLING2": MONKEY_COLORS["TURQUOISE2"],
        "COLOR_SAFE_SAMPLING2": MONKEY_COLORS["ROSTBROWN"],
        "DISTRIBUTOR_FIRST": "human_first",
        "CONTROLLER_ID": "Judit",
        "DISTRIBUTOR_ID": "Carina",
    },
    "MILA": {
        "NAME": "mila",
        "SEX": "F",
        "AGE": "111",
        "COLOR_RISK": MONKEY_COLORS["ROSTBROWN"],
        "COLOR_SAFE": MONKEY_COLORS["TURQUOISE2"],
        "COLOR_RISK_SAMPLING2": MONKEY_COLORS["BROWN2"],
        "COLOR_SAFE_SAMPLING2": MONKEY_COLORS["SKYBLUE"],
        "DISTRIBUTOR_FIRST": "human_first",
        "CONTROLLER_ID": "Judit",
        "DISTRIBUTOR_ID": "Carina",
    },
    "MOLLY": {
        "NAME": "molly",
        "SEX": "F",
        "AGE": "33",
        "COLOR_RISK": MONKEY_COLORS["OLIVE"],
        "COLOR_SAFE": MONKEY_COLORS["PURPLE2"],
        "COLOR_RISK_SAMPLING2": MONKEY_COLORS["BROWN"],
        "COLOR_SAFE_SAMPLING2": MONKEY_COLORS["DARKBLUE"],
        "DISTRIBUTOR_FIRST": "machine_first",
        "CONTROLLER_ID": "Carina",
        "DISTRIBUTOR_ID": "Judit",
    },
    "MEIWI": {
        "NAME": "meiwi",
        "SEX": "F",
        "AGE": "68",
        "COLOR_RISK": MONKEY_COLORS["ROST2"],
        "COLOR_SAFE": MONKEY_COLORS["TURQUOISE3"],
        "COLOR_RISK_SAMPLING2": MONKEY_COLORS["DARKBLUE"],
        "COLOR_SAFE_SAMPLING2": MONKEY_COLORS["BROWN"],
        "DISTRIBUTOR_FIRST": "human_first",
        "CONTROLLER_ID": "Carina",
        "DISTRIBUTOR_ID": "Judit",
    },
    "SAM": {
        "NAME": "sam",
        "SEX": "M",
        "AGE": "36",
        "COLOR_RISK": MONKEY_COLORS["SKYBLUE"],
        "COLOR_SAFE": MONKEY_COLORS["BROWN2"],
        "COLOR_RISK_SAMPLING2": MONKEY_COLORS["TURQUOISE3"],
        "COLOR_SAFE_SAMPLING2": MONKEY_COLORS["ROST2"],
        "DISTRIBUTOR_FIRST": "machine_first",
        "CONTROLLER_ID": "Carina",
        "DISTRIBUTOR_ID": "Judit",
    },
    "ISABELLA": {
        "NAME": "isabella",
        "SEX": "F",
        "AGE": "84",
        "COLOR_RISK": MONKEY_COLORS["SKYBLUE"],
        "COLOR_SAFE": MONKEY_COLORS["BROWN2"],
        "COLOR_RISK_SAMPLING2": MONKEY_COLORS["TURQUOISE3"],
        "COLOR_SAFE_SAMPLING2": MONKEY_COLORS["ROST2"],
        "DISTRIBUTOR_FIRST": "human_first",
        "CONTROLLER_ID": "Judit",
        "DISTRIBUTOR_ID": "Carina",
    },
    "INGMAR": {
        "NAME": "ingmar",
        "SEX": "M",
        "AGE": "9",
        "COLOR_RISK": MONKEY_COLORS["SKYBLUE"],
        "COLOR_SAFE": MONKEY_COLORS["BROWN2"],
        "COLOR_RISK_SAMPLING2": MONKEY_COLORS["TURQUOISE3"],
        "COLOR_SAFE_SAMPLING2": MONKEY_COLORS["ROST2"],
        "DISTRIBUTOR_FIRST": "human_first",
        "CONTROLLER_ID": "Carina",
        "DISTRIBUTOR_ID": "Judit",
    },
    "INDIRA": {
        "NAME": "indira",
        "SEX": "F",
        "AGE": "257",
        "COLOR_RISK": MONKEY_COLORS["SKYBLUE"],
        "COLOR_SAFE": MONKEY_COLORS["BROWN2"],
        "COLOR_RISK_SAMPLING2": MONKEY_COLORS["TURQUOISE3"],
        "COLOR_SAFE_SAMPLING2": MONKEY_COLORS["ROST2"],
        "DISTRIBUTOR_FIRST": "human_first",
        "CONTROLLER_ID": "Carina",
        "DISTRIBUTOR_ID": "Judit",
    },
    "LENNY": {
        "NAME": "lenny",
        "SEX": "M",
        "AGE": "149",
        "COLOR_RISK": MONKEY_COLORS["SKYBLUE"],
        "COLOR_SAFE": MONKEY_COLORS["BROWN2"],
        "COLOR_RISK_SAMPLING2": MONKEY_COLORS["TURQUOISE3"],
        "COLOR_SAFE_SAMPLING2": MONKEY_COLORS["ROST2"],
        "DISTRIBUTOR_FIRST": "machine_first",
        "CONTROLLER_ID": "Carina",
        "DISTRIBUTOR_ID": "Judit",
    },
    "INKA": {
        "NAME": "inka",
        "SEX": "F",
        "AGE": "37",
        "COLOR_RISK": MONKEY_COLORS["SKYBLUE"],
        "COLOR_SAFE": MONKEY_COLORS["BROWN2"],
        "COLOR_RISK_SAMPLING2": MONKEY_COLORS["TURQUOISE3"],
        "COLOR_SAFE_SAMPLING2": MONKEY_COLORS["ROST2"],
        "DISTRIBUTOR_FIRST": "machine_first",
        "CONTROLLER_ID": "Carina",
        "DISTRIBUTOR_ID": "Judit",
    },
}


def getMonkeyDBVariables(monkey):
    return (
        monkey["NAME"],
        monkey["SEX"],
        monkey["AGE"],
        monkey["COLOR_RISK"],
        monkey["COLOR_SAFE"],
        monkey["DISTRIBUTOR_FIRST"],
        monkey["CONTROLLER_ID"],
        monkey["DISTRIBUTOR_ID"],
    )


def getMonkeyDBVariablesSampling2(monkey):
    return (
        monkey["NAME"],
        monkey["SEX"],
        monkey["AGE"],
        monkey["COLOR_RISK_SAMPLING2"],
        monkey["COLOR_SAFE_SAMPLING2"],
        monkey["DISTRIBUTOR_FIRST"],
        monkey["CONTROLLER_ID"],
        monkey["DISTRIBUTOR_ID"],
    )
