import re
import os
import gdal
import argparse
import numpy as np
import numpy.ma as ma
from lib import build_qa_mask
from datetime import datetime

parser = argparse.ArgumentParser(description='Fetch temporal statistics from a list of rasters.')
parser.add_argument('-s', '--start-year', help='YYYY', required=True, type=int)
parser.add_argument('-e', '--end-year', help='YYYY', required=True, type=int)
parser.add_argument('-f', '--first-day', help='ddd', required=True)
parser.add_argument('-l,' '--last-day', help='ddd', required=True)
parser.add_argument('-d', '--directory-path', help='Path to directory containing the data.', required=True)
parser.add_argument('-k', '--data-file-regex', help='Filter files using this expression.', required=True)
parser.add_argument('-r', '--reliability-file-regex', help='Filter files using this expression.', required=True)
parser.add_argument('-j', '--date-regex', help='Match file date using this expression.', required=True)
parser.add_argument('-x', '--dry-run', help="List the files to be processed but don't take any statistics.",
                    action="store_true")
args = parser.parse_args()

TIME_AXIS = 2
YEAR_DAY = "%Y%j"


def get_filenames_list(file_name):
    with open(file_name) as dat:
        data_files = dat.readlines()
        data_files = [dat.strip() for dat in data_files]
        return data_files


def open_raster_file(file_name, array_type):
    rast = gdal.Open(file_name)
    band = rast.getRasterBand(1)
    return np.array(band.ReadAsArray(), array_type)


def create_masked_array(array_file, array_type, mask_file, mask_type):
    raster_array = open_raster_file(array_file, array_type)
    rel_array = open_raster_file(mask_file, mask_type)
    build_qa_mask(raster_array, rel_array)
    return ma.array(raster_array, mask=rel)


def get_files_in_time_range(start, end, files, date_regex):
    filtered_files = []
    for fl in files:
        fl_time = re.compile(date_regex).search(fl).group()
        file_datetime = datetime.strptime(fl_time, YEAR_DAY)
        if file_datetime is not None and start <= file_datetime <= end:
            filtered_files.append(fl)
    return filtered_files


def get_matching_files(directory, file_regex):
    files = os.listdir(directory)
    names = filter(lambda x: re.compile(file_regex).search(x) is not None, files)
    return map(lambda x: directory + x)


data_files = get_matching_files(args.directory_path, args.data_file_regex)
reliability_files = get_matching_files(args.directory_path, args.reliability_file_regex)
for year in range(args.start_year, args.end_year + 1):
    start_date = datetime.strptime(str(year) + args.first_day, YEAR_DAY)
    end_date = datetime.strptime(str(year) + args.last_day, YEAR_DAY)
    data_files_in_range = get_files_in_time_range(start_date, end_date, data_files, args.date_regex)
    reliability_files_in_range = get_files_in_time_range(start_date, end_date, reliability_files, args.date_regex)
    space_list = []
    for raster, rel in zip(data_files_in_range, reliability_files_in_range):
        print "Processing data: " + raster
        print "Applying reliability mask: " + rel
        space_list.append(create_masked_array(raster, np.int16, rel, np.int8))
    # Lon, Lat, Time.
    space_time = np.stack(space_list, axis=TIME_AXIS)
    if args.dry_run is False:
        # Average over time, then over space.
        mean_dat = space_time.mean(axis=TIME_AXIS).mean()
        min_dat = space_time.min(axis=TIME_AXIS).mean()
        max_dat = space_time.max(axis=TIME_AXIS).mean()
        sd_dat = space_time.std(axis=TIME_AXIS).mean()
        print str(mean_dat) + "," + str(min_dat) + "," + str(max_dat) + "," + str(sd_dat)

