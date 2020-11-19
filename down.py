#!/usr/bin/python3
#
# Based on the offical Google Chromium sources, especially:
#
#   https://chromium.googlesource.com/chromium/src/+/master/chrome/browser/chromeos/backdrop_wallpaper_handlers/backdrop_wallpaper.proto
#   https://chromium.googlesource.com/chromium/src/+/master/chrome/browser/chromeos/backdrop_wallpaper_handlers/backdrop_wallpaper_handlers.cc
#
# first you need to run the Protocol Buffer Compiler to generate the necessary Python wrapper, by running:
#
#   cd proto
#   protoc --python_out=.. backdrop_wallpaper.proto
#

import os
import requests
import backdrop_wallpaper_pb2

# create output directory
if not os.path.exists("output"):
    os.mkdir("output")

# fetch image collections
response = requests.post("https://clients3.google.com/cast/chromecast/home/wallpaper/collections?rt=b", headers={"Content-Type": "application/protobuf"})
collections_response = backdrop_wallpaper_pb2.GetCollectionsResponse()
collections_response.ParseFromString(response.content)

# iterate over the collections and fetch the list of images within each collection
for c in collections_response.collections:
    print("Found collection:", c.collection_name)
    
    if not os.path.exists("output/"+c.collection_name):
        os.mkdir("output/"+c.collection_name)
    
    # retrieve all images for the collection
    backdrop_request=backdrop_wallpaper_pb2.GetImagesInCollectionRequest()
    backdrop_request.collection_id = c.collection_id
    backdrop_request.filtering_label.append("chromebook")
    backdrop_request.filtering_label.append("google_branded_chromebook")
    response=requests.post("https://clients3.google.com/cast/chromecast/home/wallpaper/collection-images?rt=b",headers={"Content-Type": "application/protobuf"},data=backdrop_request.SerializeToString())
    
    # parse the response and fetch each individual image
    images_response = backdrop_wallpaper_pb2.GetImagesInCollectionResponse()
    images_response.ParseFromString(response.content)
    for i in images_response.images:
        full_url=i.image_url+"=s3840"
        print("    downloading:", full_url)      
        response = requests.get(full_url)
        if response.status_code==200 and response.headers['Content-Type']=='image/jpeg':
            destination="output/"+c.collection_name+"/"+str(i.asset_id)+".jpg"
            output_file=open(destination,"wb")
            output_file.write(response.content)
            output_file.close()
                    
