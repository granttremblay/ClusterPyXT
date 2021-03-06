# version 0.8.2
# Nov 28, 2018

import sys
import errno
import argparse
import acb
import pypeline_io as io


# import setup_for_testing as test
# test.setup_testing_environment()

import config

config.initialize_pypeline()

import menu

try:
    #from ciao_contrib.cda.data import download_chandra_obsids
    import ciao_contrib
except ImportError or ModuleNotFoundError:
    print("Failed to import CIAO python scripts. \n CIAO must be running prior to starting this script!")
    exit()


import cluster
import ciao


def process_commandline_arguments(cluster_obj):
    print("Processing commandline arguments")
    args = get_arguments()
    if io.file_exists(args.batch_file):
        ciao.automated_cluster_init(args.batch_file)
    if None not in [args.name, args.abundance, args.nH, args.redshift, args.obsids]:
        ciao.initialize_cluster(name=args.name, obsids=args.obsids, abundance=args.abundance,
                                redshift=args.redshift, nH=args.nH)
    if args.init_cluster:
        cluster_obj.initialize_cluster()
    if args.config_file != "":
        cluster_obj = get_cluster(args.config_file)
    if args.cont:
        ciao.start_from_last(cluster_obj)
    if args.download_data:
        if 0 == cluster_obj.last_step_completed:
            cluster_obj.get_cluster_info_from_user()
        ciao.download_data(cluster_obj)
    if args.remove_sources:
        ciao.remove_sources(cluster_obj)
    return cluster_obj


def get_cluster(config_file_arg):
    if io.file_exists(config_file_arg):
        cluster_obj = cluster.read_cluster_data(config_file_arg)
    else:
        config_file = cluster.get_cluster_config(config_file_arg)
        if config_file:
            cluster_obj = cluster.read_cluster_data(config_file)
        else:
            print("Error finding cluster configuration file. Try passing the full path to the file.")
            return
    return cluster_obj

def get_arguments():
    help_str = """
    pypeline help string
    """

    prog = 'pypeline'

    # logger.debug("Getting commandline arguments.")
    parser = argparse.ArgumentParser(description=help_str, prog=prog)
    parser.add_argument("--initialize_cluster", dest="init_cluster", action="store_true",
                        help="First step in the pypeline. Creates the directory and initial configuration")
    parser.add_argument("--config_file", "-c", dest="config_file", action="store", default="",
                        help="The path and filename of the configuration file.")

    parser.add_argument("--download_chandra_data", "-d", dest="download_data", action='store_true',
                        help="Download the observations given in the config file. Also requires a configuration file")

    # parser.add_argument("--find_chandra_data", "-f", dest="find_data", action='store_true',
    #                    help="Find chandra observations to download")

    parser.add_argument("--remove_sources", "-r", dest="remove_sources", action='store_true',
                        help="Remove sources given the supplied region file.")

    parser.add_argument("--continue", dest='cont', action='store_true',
                        help='Continue where you left off (must also specify --config_file)')

    parser.add_argument("--batch_init", '-b', dest="batch_file", action='store', default="",
                        help="Supply a CSV file with the relevant meta data for batch processing."
                        "See documentation for full usage instructions.")

    parser.add_argument("--nH", dest='nH', action='store', default=None)
    parser.add_argument("--redshift", '-z', dest='redshift', action='store', default=None)
    parser.add_argument('--cluster_name', '-n', dest='name', action='store', default=None)
    parser.add_argument('--obsids', dest='obsids', action='store', nargs='+', default=None)
    parser.add_argument('--abundance', dest='abundance', action='store', default=None)
    args = parser.parse_args()

    # logger.debug("Finished getting commandline arguments")

    return args




if __name__ == "__main__":
    if 1 == len(sys.argv):
        menu.make_menu()
    else:
        cluster_obj = cluster.ClusterObj()
        args = process_commandline_arguments(cluster_obj)
