import argparse
from lib import *

parser = argparse.ArgumentParser(description='Fetch temporal statistics from a list of rasters.')
parser.add_argument('-s', '--start-year', help='YYYY', required=True, type=int)
parser.add_argument('-e', '--end-year', help='YYYY', required=True, type=int)
parser.add_argument('-f', '--first-day', help='ddd', required=True)
parser.add_argument('-l', '--last-day', help='ddd', required=True)
parser.add_argument('-d', '--directory-path', help='Path to directory containing the data.', required=True)
parser.add_argument('-k', '--data-file-regex', help='Filter files using this expression. Make sure to wrap this in'
                                                    ' single quotes.', required=True)
parser.add_argument('-r', '--reliability-file-regex', help='Filter files using this expression. Make sure to wrap this'
                                                           ' in single quotes.', required=True)
parser.add_argument('-j', '--date-regex', help='Extract the date using this expression. Make sure to wrap this in '
                                               'single quotes.', required=True)
parser.add_argument('-x', '--dry-run', help="List the files to be processed but don't take any statistics.",
                    action="store_true")
parser.add_argument('-v', '--verbose', help="Verbose run.", action="store_true")
parser.add_argument('-c', '--no-check', help="Don't check that the data and reliability files match up. This could "
                                             "result in the wrong mask being created.")
parser.add_argument('-b', '--log-file', help="Name of the file to log info and warnings.")
args = parser.parse_args()

logger = logging.getLogger(__name__)
format_handler = logging.Formatter(fmt="%(asctime)s %(message)s")
logger.addHandler(format_handler)
if args.verbose:
    logger.setLevel(logging.DEBUG)
if args.log_file is not None:
    file_handler = logging.FileHandler(args.log_file)
    logger.addHandler(file_handler)

data_files, reliability_files = get_data_and_reliability_lists(args.directory_path, args.data_file_regex,
                                                               args.date_regex, args.reliability_file_regex)
validate_reliability(data_files, reliability_files, args.date_regex)
for year in range(args.start_year, args.end_year + 1):
    data_files_in_range, reliability_files_in_range = filter_files_in_range(data_files, reliability_files, year,
                                                                            args.first_day, args.last_day,
                                                                            args.date_regex)
    space_time = retrieve_space_time(data_files_in_range, reliability_files_in_range, args.date_regex)
    if args.dry_run is False:
        mean_dat, min_dat, max_dat, sd_dat = average_overage_time_then_space(space_time)
        print str(year) + "," + str(mean_dat) + "," + str(min_dat) + "," + str(max_dat) + "," + str(sd_dat)
