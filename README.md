# WFS Connector

A simple script that uses [OWSLib](https://owslib.readthedocs.io/en/latest/) to connect to a WFS and retrieve some data.

## Requirements

- Python and Pip (tested with 3.12, other versions might also work)

## Installation

Create a virtual environment, activate it, then install the [dependencies](requirements.txt) into it:

```
$ python -m venv venv
$ . venv/bin/activate
(venv) $ pip install -r requirements.txt
```

## Usage

```
(venv) $ python wfs_connect.py --help 
usage: wfs_connect.py [-h] [--url URL] [--source SOURCE] [--target TARGET] [--start START] [--max MAX]

Connect to a WFS, list the features (layers) and get some data from them.

options:
  -h, --help       show this help message and exit
  --url URL        URL of the WFS. Default: https://fbinter.stadt-berlin.de/fb/wfs/data/senstadt/s_luftbild1979
  --source SOURCE  Source projection of the data. Default: EPSG:25833
  --target TARGET  Target projection of the data. Default: EPSG:4326. Use 'none' for no projection conversion.
  --start START    Start index. Default: 0
  --max MAX        Maximum number of features to be returned. Default: 10
```

## Projection Conversion

Map coordinates can come in different projections.
To convert from the source projection the WFS offers (such as the default EPSG:25833 or 'Soldner') to a target projection (such as EPSG:4326' or WGS84), use the `--source` and `--target` parameters.
The script uses [pyproj](https://github.com/pyproj4/pyproj) for conversion, so the names of the projections must be based on that.
Use `--target=none` if no conversion is desired.

## CSV-Output

The script is hard-coded to output GeoJSON, because that makes post-processing with [jq](https://jqlang.github.io/jq/) (needs to be installed separately) easier.
For example, jq can be used to convert the output to CSV – some WFSes offer CSV-export out of the box, but not all.

Converting to CSV with jq can look like this:

```
(venv) $ python wfs_connect.py --url https://fbinter.stadt-berlin.de/fb/wfs/data/senstadt/s_wfs_adressenberlin | \
jq '[.features[] | .properties + { coordinates: .geometry.coordinates | join(",")}]' | \
jq -r '(map(keys) | add | unique) as $cols | map(. as $row | $cols | map($row[.])) as $rows | $cols, $rows[] | @csv'
INFO:__main__: Available feature types:
INFO:__main__: fis:s_wfs_adressenberlin
INFO:__main__: converting map projection from EPSG:25833 to EPSG:4326
INFO:__main__: Retrieved features:
"adr_datum","adressid","bez_name","bez_nr","blk","coordinates","hko_id","hnr","hnr_zusatz","ort_name","ort_nr","plr_name","plr_nr","plz","qualitaet","str_datum","str_name","str_nr","typ"
"","S26680","Charlottenburg-Wilmersdorf","04","","13.281063091754831,52.48277042137358","","","","Grunewald","0404","Hagenplatz","04400728","14193","RBS","2011-05-04T00:00:00","Joseph-Joachim-Platz","07025","Platz/Straße ohne HNR"
"","S26813","Mitte","01","","13.385002857291411,52.51819536166907","","","","Mitte","0101","Unter den Linden","01100206","10117","RBS","2012-02-07T00:00:00","Neustädtischer Kirchplatz","10753","Platz/Straße ohne HNR"
"","S6397","Tempelhof-Schöneberg","07","","13.378243459875783,52.4660225914178","","","","Tempelhof","0703","Bosepark","07400824","12103","RBS","1960-01-01T00:00:00","Berlinickeplatz","06927","Platz/Straße ohne HNR"
"","S21009","Lichtenberg","11","","13.492133789547339,52.53949277382288","","","","Alt-Hohenschönhausen","1110","Große-Leege-Straße","11200513","13055","RBS","1960-01-01T00:00:00","Strausberger Platz","43245","Platz/Straße ohne HNR"
"","S26439","Pankow","03","","13.440674879147275,52.54702617496678","","","","Prenzlauer Berg","0301","Ostseestraße","03601245","10409","RBS","1960-01-01T00:00:00","Ostseeplatz","42163","Platz/Straße ohne HNR"
"","S22600","Pankow","03","","13.437055365281893,52.532955692352644","","","","Prenzlauer Berg","0301","Bötzowstraße","03701660","10407","RBS","1993-02-04T00:00:00","Arnswalder Platz","44889","Platz/Straße ohne HNR"
"","S19610","Lichtenberg","11","","13.47984679713975,52.52053737036246","","","","Lichtenberg","1103","Rathaus Lichtenberg","11300722","10367","RBS","1960-01-01T00:00:00","Loeperplatz","41814","Platz/Straße ohne HNR"
"","S26417","Tempelhof-Schöneberg","07","","13.397163710478978,52.39671063368912","","","","Lichtenrade","0706","Kettinger Straße","07601442","12305","RBS","1960-01-01T00:00:00","Ekensunder Platz","06961","Platz/Straße ohne HNR"
"","S20312","Friedrichshain-Kreuzberg","02","","13.4567946405513,52.5023798358904","","","","Friedrichshain","0201","Stralauer Kiez","02500835","10245","RBS","1960-01-01T00:00:00","Rudolfplatz","42486","Platz/Straße ohne HNR"
"","S6517","Reinickendorf","12","","13.32782743099606,52.56405334694123","","","","Reinickendorf","1201","Scharnweberstraße","12200309","13405","RBS","1960-01-01T00:00:00","Kurt-Schumacher-Platz","07048","Platz/Straße ohne HNR"
```

## License

All code in this repository is published under the [MIT License](License).

