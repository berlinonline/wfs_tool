import argparse
import json
import logging
import sys

from owslib.wfs import WebFeatureService
from pyproj import Transformer

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

default_wfs_url = "https://fbinter.stadt-berlin.de/fb/wfs/data/senstadt/s_luftbild1979"
default_source_projection = 'EPSG:25833' # 25833 is the projection used in Berlin's Open Data ("Soldner")
default_target_projection = 'EPSG:4326' # 4326 is WGS84

default_output_format = "application/json"
default_start = 0
default_maxfeatures = 10
default_features_types = 'all'

parser = argparse.ArgumentParser(
    description="Connect to a WFS, list the features (layers) and get some data from them.")
parser.add_argument('--url',
                    help=f"URL of the WFS. Default: {default_wfs_url}",
                    default=default_wfs_url,
                    )
parser.add_argument('--source',
                    help=f"Source projection of the data. Default: {default_source_projection}",
                    default=default_source_projection,
                    )
parser.add_argument('--target',
                    help=f"Target projection of the data. Default: {default_target_projection}. Use 'none' for no projection conversion.",
                    default=default_target_projection,
                    )
parser.add_argument('--format',
                    help=f"Desired output format. Default: {default_output_format}",
                    default=default_output_format,
                    )
parser.add_argument('--start',
                    help=f"Start index. Default: {default_start}",
                    type=int,
                    default=default_start,
                    )
parser.add_argument('--max',
                    help=f"Maximum number of features to be returned. Default: {default_maxfeatures}",
                    type=int,
                    default=default_maxfeatures,
                    )
parser.add_argument('--types',
                    help=f"Names of feature types to be queried (separated by comma), or 'all'. Default: {default_features_types}",
                    type=str,
                    default=default_features_types,
                    )
parser.add_argument("--types_only",
                    action="store_true", 
					help="Boolean. Only list the available types, don't query any features. Off by default."
                    )

args = parser.parse_args()

wfs_url = args.url
maxfeatures = args.max
outputformat = args.format
startindex = args.start
source_projection = args.source
target_projection = args.target

# Connect to the WFS service
wfs = WebFeatureService(wfs_url, version="2.0.0")

# Get information about available feature types (layers)
feature_types_available = list(wfs.contents)

# Print the available feature types
LOG.info(f" Available feature types: {', '.join(feature_types_available)}")

if args.types_only:
    print(json.dumps(feature_types_available))
    sys.exit(0)

# print requested feature types
feature_types_requested = args.types.split(',')
feature_types_requested = [ feature_type.strip() for feature_type in feature_types_requested ]
LOG.info(f" Requested feature types: {', '.join(feature_types_requested)}")

if args.types == 'all':
    feature_types = feature_types_available
else:
    feature_types = feature_types_requested

for feature_type in feature_types:
    LOG.info(f" {feature_type}")

    # Perform a GetFeature request to retrieve data for a feature type
    response = wfs.getfeature(
        typename=feature_type,
        maxfeatures=maxfeatures,
        outputFormat=outputformat,
        startindex=startindex
    )

    output = response.read().decode("utf-8")

    if target_projection.lower() != 'none':
        LOG.info(f" converting map projection from {source_projection} to {target_projection}")
        features_data = json.loads(output)

        transformer = Transformer.from_crs(source_projection, target_projection)

        # transform bounding box
        if 'bbox' in features_data:
            bbox_original = features_data['bbox']
            bbox_wgs84_sw = transformer.transform(bbox_original[0], bbox_original[1])
            bbox_wgs84_ne = transformer.transform(bbox_original[2], bbox_original[3])
            features_data['bbox'] = list(reversed(bbox_wgs84_sw)) + list(reversed(bbox_wgs84_ne))

        # transform each features coordinates
        for index, feature in enumerate(features_data['features']):
            original = feature['geometry']['coordinates']
            wgs84 = transformer.transform(original[0], original[1])
            wgs84_list = list(wgs84)
            features_data['features'][index]['geometry']['coordinates'] = list(reversed(wgs84_list))

        # change projection reference to the new target projection
        features_data['crs']['properties']['name'] = target_projection
        output = json.dumps(features_data)

    else:
        LOG.info(" no projection conversion")

    LOG.info(" Retrieved features:")
    print(output)


# To CSV:
# python test.py --url https://fbinter.stadt-berlin.de/fb/wfs/data/senstadt/s_wfs_adressenberlin --max=1000 | jq '[.features[] | .properties + { coordinates: .geometry.coordinates | join(",")}]' | jq -r '(map(keys) | add | unique) as $cols | map(. as $row | $cols | map($row[.])) as $rows | $cols, $rows[] | @csv'