import argparse


def run_from_cli():
    # TODO finish this
    parser = argparse.ArgumentParser(
        prog="i129f_dhl_tracker",
        description="Automatically track NVC shipments through DHL",
        epilog="The wait is long, but we know how long",
    )

    parser.add_argument("filename")  # positional argument
    parser.add_argument("-c", "--count")  # option that takes a value
    parser.add_argument("-v", "--verbose", action="store_true")  # on/off flag
    parser.add_argument("-v", "--verbose", action="store_true")  # on/off flag
