class Aircraft:
    def __init__(self, hex: str) -> None:
        self.hex                = hex
        self.last_track_fetch   = 0
        self.registration       = None
        self.tail_number        = None
        self.description        = None
        self.owner              = None
        self.year               = None
        self.category           = None
        

    def __eq__(self, __o: object) -> bool:
        if type(__o) != Aircraft:
            return False
        return self.hex.lower() == __o.hex.lower()

    def __hash__(self) -> int:
        return hash(self.hex.lower())


categories = {
    'A0': "Unspecified powered aircraft",
    'A1': "Light (< 15 500 lbs.)",
    'A2': "Small (15 500 to 75 000 lbs.)",
    'A3': "Large (75 000 to 300 000 lbs.)",
    'A4': "High Vortex Large(aircraft such as B-757)",
    'A5': "Heavy (> 300 000 lbs.)",
    'A6': "High Performance ( > 5 g acceleration and > 400kts)",
    'A7': "Rotorcraft",
    'B0': "Unspecified unpowered aircraft or UAV or spacecraft",
    'B1': "Glider/sailplane",
    'B2': "Lighter-than-Air",
    'B3': "Parachutist/Skydiver",
    'B4': "Ultralight/hang-glider/paraglider",
    'B5': "Reserved",
    'B6': "Unmanned Aerial Vehicle",
    'B7': "Space/Trans-atmospheric vehicle",
    'C0': "Unspecified ground installation or vehicle",
    'C1': "Surface Vehicle - Emergency Vehicle",
    'C2': "Surface Vehicle - Service Vehicle",
    'C3': "Fixed Ground or Tethered Obstruction"
}

description = {
    'H': ['helicopter', 1],
    'G': ['gyrocopter', 1],
    'L1P': ['cessna', 1],
    'A1P': ['cessna', 1],
    'L1T': ['single_turbo', 1],
    'L1J': ['hi_perf', 0.92],
    'L2P': ['twin_small', 1],
    'A2P': ['twin_large', 0.96],
    'A2P-M': ['twin_large', 1.12],
    'L2T': ['twin_large', 0.96],
    'L2T-M': ['twin_large', 1.12],
    'A2T': ['twin_large', 0.96],
    'A2T-M': ['twin_large', 1.06],
    'L1J-L': ['jet_nonswept', 1], 
    'L2J-L': ['jet_nonswept', 1], 
    'L2J-M': ['airliner', 1], 
    'L2J-H': ['heavy_2e', 0.96], 
    'L3J-H': ['md11', 1], 
    'L4T-M': ['c130', 1],
    'L4T-H': ['c130', 1.07],
    'L4T': ['c130', 0.96],
    'L4J-H': ['b707' , 1],
    'L4J-M': ['b707' , 0.8],
    'L4J': ['b707' , 0.8],
}

icao_type = {}