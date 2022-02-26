from .adsb import Adsbexchange

adsb = None

def start():
    global adsb
    adsb = Adsbexchange(start=False)
    print("====================================")
    print("STARTING ADS-B SCRAPER")

    while True:
        print("\n====================================")
        print("Home")
        print("====================================")
        print("[0] - Quit")
        print("[1] - Manage data sets")
        print("[2] - Manage airspaces")
        print("[3] - Manage flight tracks")
        print("[4] - Manage recording")

        user_resp = get_resp()
        if user_resp == 0:
            return
        elif user_resp == 1:
            manage_datasets()
        elif user_resp == 2:
            manage_airspaces()
        elif user_resp == 3:
            manage_tracks()
        elif user_resp == 4:
            manage_recording()
        else:
            print("invalid selection")

        print()


def manage_datasets():
    while True:
        print("\n====================================")
        print("Home => Manage Data Sets")
        print("====================================")
        print("[0] - back")
        print("[1] - list by airspace")
        print("[2] - list by aircraft")

        user_resp = get_resp()
        if user_resp == 0:
            return
        elif user_resp == 1:
            pass
        elif user_resp == 2:
            pass
        else:
            print("invalid selection")


def manage_airspaces():
    while True:
        print("\n====================================")
        print("Home => Manage Air Spaces")
        print("====================================")
        print("[0] - back")
        print("[1] - list airspaces")
        print("[2] - list by date/time")
        print("[3] - list by duration")
        print("[4] - list by physical area")
        print("[5] - list by number of craft")
        print("[6] - select airspace")
        print("[7] - select all airspaces")
        print("[8] - deselect")
        print("[9] - visualize selection")
        print("[10] - create new airspace")
        print("[11] - delete airspace")

        user_resp = get_resp()
        if user_resp == 0:
            return
        elif user_resp == 1:
            pass
        elif user_resp == 2:
            pass
        elif user_resp == 3:
            pass
        elif user_resp == 4:
            pass
        else:
            print("invalid selection")


def manage_tracks():
    while True:
        print("\n====================================")
        print("Home => Manage Tracks")
        print("====================================")
        print("[0] - back")
        print("[1] - list by hex")
        print("[2] - list by class")
        print("[3] - list by most recent")
        print("[4] - list by location")

        user_resp = get_resp()
        if user_resp == 0:
            return
        elif user_resp == 1:
            pass
        elif user_resp == 2:
            pass
        elif user_resp == 3:
            pass
        elif user_resp == 4:
            pass
        else:
            print("invalid selection")


def manage_recording():
    while True:
        print("\n====================================")
        print("Home => Manage Recordings")
        print("====================================")
        print("[0] - back")
        print("[1] - airspace recordings")
        print("[2] - flight track recordings")

        user_resp = get_resp()

        if user_resp == 0:
            return
        elif user_resp == 1:
            print("[1] - start/stop recording")
            print("[2] - new recording")
        elif user_resp == 2:
            print("[1] - start/stop recording")
            print("[2] - new recording")
        else:
            print("invalid selection")


def get_resp():
    import sys
    user_resp = ""
    while not user_resp.isdecimal():
        print("make a numeric selection: ", end="")
        user_resp = input()
    print(f"input: {user_resp}")
    print("output:")
    return int(user_resp)


if __name__ == "__main__":
    from connection.serverconnection import ServerConnection
    from adsbexchange.datum.airspace import Airspace
    air_sp = Airspace(35.222569, -97.439476, 200)
    conn = ServerConnection()
    conn.add_airspace(air_sp)
