"""Synthetic controls only; no claim of GQ-1358 site registration."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from pyproj import Transformer

SCRIPT=Path(__file__).resolve().parents[1]/'scripts'/'geology'/'validate_warren_plate_gcps.py'
spec=importlib.util.spec_from_file_location('gq1358_preflight',SCRIPT)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class TestGQ1358Preflight(unittest.TestCase):
    def synthetic(self, path):
        # Deliberately synthetic plate controls to test affine alignment behavior.
        path.write_bytes(b'NOT AN ACTUAL PLATE')
        trans=Transformer.from_crs('EPSG:26986','EPSG:4326',always_xy=True)
        def p(x,y):
            e,n=141000+2*x,884000-2*y
            lon,lat=trans.transform(e,n)
            return {'pixel_x':x,'pixel_y':y,'longitude':lon,'latitude':lat}
        return {'source':'USGS GQ-1358 1977','plate_path':str(path),
                'gcps':[p(0,0),p(1000,0),p(0,1000),p(1000,1000)],
                'holdouts':[p(200,300),p(700,550)]}
    def test_clean_qa_alone_does_not_verify_site(self):
        with tempfile.TemporaryDirectory() as d:
            r=m.check_plate(self.synthetic(Path(d)/'synthetic.tif'))
            self.assertEqual(r['status'],'candidate_alignment_manual_review')
            self.assertFalse(r['site_geology_verified'])
            self.assertFalse(r['quarry_origin_verified'])
            self.assertLess(r['independent_check_max_m'],1)
    def test_bad_holdout_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            data=self.synthetic(Path(d)/'synthetic.tif');data['holdouts'][1]['longitude']+=0.01
            r=m.check_plate(data)
            self.assertEqual(r['status'],'failed_alignment_qa')
    def test_tie_point_reuse_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            data=self.synthetic(Path(d)/'synthetic.tif');data['holdouts'][0]=dict(data['gcps'][0])
            with self.assertRaises(ValueError):m.check_plate(data)
    def test_unavailable_plate_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            data=self.synthetic(Path(d)/'synthetic.tif');Path(data['plate_path']).unlink()
            with self.assertRaises(FileNotFoundError):m.check_plate(data)
    def test_wrong_map_source_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            data=self.synthetic(Path(d)/'synthetic.tif');data['source']='USGS GQ-1357 1977'
            with self.assertRaises(ValueError):m.check_plate(data)

if __name__=='__main__':unittest.main()