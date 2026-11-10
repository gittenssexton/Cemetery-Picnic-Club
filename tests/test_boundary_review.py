"""Unit tests for proximity results; no remote service required."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import geopandas as gpd
from shapely.geometry import Point, box

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'geology' / 'build_boundary_review.py'
spec=importlib.util.spec_from_file_location('boundary_review',SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class ReviewTests(unittest.TestCase):
    def test_two_adjacent_units_not_overstated(self):
        lat,lon=42.20909,-72.1966
        pt=gpd.GeoSeries([Point(lon,lat)],crs=4326).to_crs(26986).iloc[0]
        x,y=pt.x,pt.y
        shape=gpd.GeoDataFrame({'BEDROCK_1':['Ops','Dl'],'ROCK_GPB':['Sulfidic Schists','Pelitic Rocks']},
            geometry=[box(x-100,y-200,x+50,y+200),box(x+50,y-200,x+250,y+200)],crs=26986)
        with tempfile.TemporaryDirectory() as t:
            shp=Path(t)/'test.shp'; shape.to_file(shp)
            obj=mod.review(shp,lat,lon)
            self.assertEqual(obj['map_point_symbol'],'Ops')
            self.assertEqual(set(p['symbol'] for p in obj['neighborhood'][0]['nearby_polygons']),{'Ops','Dl'})
            self.assertEqual(obj['site_assignment_status'],'boundary_sensitive_unverified')
    def test_missing_map_field_fails(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'test.shp'
            gpd.GeoDataFrame({'BEDROCK_1':['Ops']},geometry=[box(0,0,1,1)],crs=26986).to_file(p)
            with self.assertRaises(ValueError):mod.review(p,42.20909,-72.1966)
if __name__=='__main__':unittest.main()