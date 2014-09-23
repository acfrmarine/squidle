#!/usr/bin/python
import csv
import os
import os.path
import errno
import datetime
from dateutil.tz import tzutc
import Image

def timestamp_to_standard(seconds):
    return str(datetime.datetime.fromtimestamp(seconds, tz=tzutc()))

def convert_image(image_folder, image_name):
    source_image = os.path.join(image_folder, image_name)
    image_name = "{0}.jpg".format(os.path.splitext(image_name)[0])
    destination_image = "images/{0}".format(image_name)

    try:
        im = Image.open(source_image)
        im.save(destination_image, "JPEG", quality=95)
    except IOError as err:
        print "Error: {0}".format(source_image)

    return image_name
    #print source_image, '=>', destination_image

def convert(renav_folder, image_folder, ignore_imgs=False, link_imgs=False):
    # preliminaries - create sensors and cameras.csv
    # also create empty/default description.txt and create
    # images directory

    # link images or make image directory
    if link_imgs:
        try:
            os.symlink(image_folder, 'images')
        except OSError as exc:
            raise
    elif not ignore_imgs :
        try:
            os.mkdir('images')
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir('images'):
                pass
            else:
                raise

    cameras = """name,angle,filename,columnname,sensors
Left Colour, Downward, path.csv, Left Image"""
    sensors = """sensortype,filename,columnname,camera
    Altitude, path.csv, Altitude, None"""
    description = """Blank description."""

    with open('cameras.csv', 'w') as camera_file:
        camera_file.write(cameras)

    with open('sensors.csv', 'w') as sensor_file:
        sensor_file.write(sensors)

    with open('description.txt', 'w') as description_file:
        description_file.write(description)

    # load up the stereo poses and related info
    stereo_pose_est = open(os.path.join(renav_folder, 'stereo_pose_est.data'))
    headings = ['time', 'latitude', 'longitude', 'depth', 'Left Image', 'Altitude']

    reader = csv.reader(stereo_pose_est, delimiter='\t')
    writer = csv.DictWriter(open('path.csv','w'), fieldnames=headings)

    writer.writeheader()

    for line in reader:

        if len(line) <= 2:
            continue

        # path requirements
        output = [timestamp_to_standard(float(line[1]))] # time
        output.append(line[2].strip()) # lat
        output.append(line[3].strip()) # lon
        output.append(line[6].strip()) # depth

        ## extra things!
        #output_file = "{0}.jpg".format(os.path.splitext(line[10].strip())[0])

        # image
        if not ignore_imgs:
            output_file = convert_image(image_folder, line[10].strip())
            output.append(output_file) # image name
        else :
            output.append(line[10].strip()) # image name

        # altitude
        output.append(line[12].strip())

        writer.writerow(dict(zip(headings, output)))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("renav_directory")
    parser.add_argument("image_directory")
    parser.add_argument("--ignore-images", action='store_true', default=False)
    parser.add_argument("--link-images", action='store_true', default=False)
    args = parser.parse_args()

    if args.link_images :
        convert(args.renav_directory, args.image_directory, ignore_imgs=True, link_imgs=True)
    elif args.ignore_images :
        convert(args.renav_directory, args.image_directory, ignore_imgs=True)
    else :
        convert(args.renav_directory, args.image_directory)
    #if args.ignore_images:
    #    convert(args.renav_directory, None)
    #else:
    #    convert(args.renav_directory, args.image_directory)

