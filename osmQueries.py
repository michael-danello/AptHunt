BUILDINGS = """
[out:json];
node(40.7023095051428,-73.95399570465088,40.72631561468468,-73.9200496673584)["station"="subway"]->.subway_stops;
(
  way(around.subway_stops:10)["building"="yes"];
  way(around.subway_stops:10)["addr"="housenumber"];

);
out tags;
"""

BUILDINGS_BY_SUBWAY = """
[out:json];
(
  way(around:500,{},{})["building"="yes"];
  way(around:500,{},{})["addr"="housenumber"];
);
out tags;
"""
