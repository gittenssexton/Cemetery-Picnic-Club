"""CPC geology: synthetic polygon and safety tests; no invented source geology."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

SRC=Path(__file__).resolve().parents[1]/'scripts/geology/ingest_bedlith_offline.py'
spec=importlib.util.spec_from_file_location('bedlith',SRC)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class TestOffline(unittest.TestCase):
    def _fixture(self,path):
        import fiona
        from shapely.geometry import Polygon, mapping
        schema={'geometry':'Polygon','properties':{'BEDROCK_1':'str:30','ROCK_GPA':'str:50','LITHO_CODE':'int'}}
        with fiona.open(str(path), 'w',driver='ESRI Shapefile',crs='EPSG:4326',schema=schema) as dst:
            dst.write({'geometry':mapping(Polygon([(-72.22,42.19),(-72.18,42.19),(-72.18,42.23),(-72.22,42.23)])),
                       'properties':{'BEDROCK_1':'TEST_ONLY','ROCK_GPA':'synthetic','LITHO_CODE':7}})
    def test_point_in_polygon_and_caveat(self):
        with tempfile.TemporaryDirectory() as t:
            shp=Path(t)/'demo.shp';self._fixture(shp)
            points=[{'point_id':'P01','place':'Synthetic','latitude':'42.20909','longitude':'-72.1966','location_basis':'synthetic'}]
            result=m.analyze(shp,points)
            self.assertEqual(result['qa_points'][0]['matches'][0]['BEDROCK_1'],'TEST_ONLY')
            self.assertFalse(result['production_ready'])
            self.assertIn('quarry',result['caveat'])
            self.assertEqual(result['point_count'],1)
            self.assertGreater(result['qa_points'][0]['boundary_distance_m'][0],0)
    def test_outside_polygon(self):
        with tempfile.TemporaryDirectory() as t:
            shp=Path(t)/'demo.shp';self._fixture(shp)
            result=m.analyze(shp,[{'point_id':'P02','place':'Synthetic','latitude':'40.0','longitude':'-72.1966','location_basis':'synthetic'}])
            self.assertEqual(result['qa_points'][0]['query_status'],'no_intersection')
    def test_zip_missing_sidecars(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'bad.zip'
            with zipfile.ZipFile(p,'w') as z:z.writestr('anything.shp','a')
            with self.assertRaises(ValueError):m.open_vector(p)
    def test_zip_traversal(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'bad.zip'
            with zipfile.ZipFile(p,'w') as z:z.writestr('../bad.shp','a')
            with self.assertRaises(ValueError):m.open_vector(p)
    def test_invalid_lat(self):
        with tempfile.TemporaryDirectory() as t:
            shp=Path(t)/'demo.shp';self._fixture(shp)
            with self.assertRaises(ValueError):m.analyze(shp,[{'point_id':'bad','place':'Synthetic','latitude':'999','longitude':'0','location_basis':'synthetic'}])

if __name__=='__main__':unittest.main()