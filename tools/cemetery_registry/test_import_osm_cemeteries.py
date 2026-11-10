import unittest
from import_osm_cemeteries import build, distance_m, distance_to_route_m

class CemeteryRegistryTests(unittest.TestCase):
    def test_distance(self):
        self.assertLess(distance_m(42.20909,-72.19660,42.20909,-72.19660),1)
        self.assertGreater(distance_m(42.20909,-72.19660,43.20909,-72.19660),100000)

    def test_center_candidate_and_boundary(self):
        data={'elements':[{'type':'way','id':55,'tags':{'landuse':'cemetery','name':'Example Ground'},'center':{'lat':42.21,'lon':-72.197},
              'geometry':[{'lat':42.21,'lon':-72.197},{'lat':42.21,'lon':-72.196},{'lat':42.211,'lon':-72.196},{'lat':42.21,'lon':-72.197}]}]}
        result=build(data)
        self.assertEqual(result['count'],1)
        obj=result['entities'][0]
        self.assertEqual(obj['geometry']['type'],'Polygon')
        self.assertFalse(obj['verified_cemetery'])
        self.assertIsNone(obj['combined_complex_id'])

    def test_unclosed_relation_centroid_only(self):
        data={'elements':[{'type':'relation','id':5,'tags':{'amenity':'grave_yard'},'center':{'lat':42.20909,'lon':-72.19660}}]}
        self.assertEqual(build(data)['entities'][0]['geometry_status'],'mapped_point_or_centroid_unverified')

    def test_outside_excluded(self):
        data={'elements':[{'type':'node','id':5,'tags':{'landuse':'cemetery'},'lat':44.,'lon':-72.2}]}
        self.assertEqual(build(data)['count'],0)

    def test_route_corridor_adds_outside_radius(self):
        route={'type':'LineString','coordinates':[[-72.6,42.4],[-72.55,42.38]]}
        data={'elements':[{'type':'node','id':6,'tags':{'amenity':'grave_yard','name':'Route Test'},'lat':42.39,'lon':-72.57}]}
        result=build(data,route)
        self.assertEqual(result['count'],1)
        self.assertIn('route9_3mi_corridor',result['entities'][0]['zones'])

if __name__=='__main__':unittest.main()