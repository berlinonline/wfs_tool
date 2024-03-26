import argparse
import json
import logging
from pyproj import Transformer
from owslib.wfs import WebFeatureService

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

default_wfs_url = "https://fbinter.stadt-berlin.de/fb/wfs/data/senstadt/s_luftbild1979"
default_source_projection = 'EPSG:25833' # 25833 is the projection used in Berlin's Open Data ("Soldner")
default_target_projection = 'EPSG:4326' # 4326 is WGS84

default_output_format = "application/geo+json"
default_start = 0
default_maxfeatures = 10

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
# parser.add_argument('--format',
#                     help=f"Desired output format. Default: {default_output_format}",
#                     default=default_output_format,
#                     )
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
args = parser.parse_args()

wfs_url = args.url
maxfeatures = args.max
outputformat = default_output_format
startindex = args.start
source_projection = args.source
target_projection = args.target

# Connect to the WFS service
wfs = WebFeatureService(wfs_url, version="2.0.0")

# Get information about available feature types (layers)
feature_types = list(wfs.contents)

# Print the available feature types
LOG.info(" Available feature types:")
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