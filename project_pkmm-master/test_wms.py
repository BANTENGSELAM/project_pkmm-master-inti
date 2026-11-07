import os, unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from firms_wms import bp

class WmsTests(unittest.TestCase):
    def setUp(self):
        os.environ['FIRMS_MAP_KEY']='secret'
        app=Flask(__name__)
        app.register_blueprint(bp)
        self.client=app.test_client()
    def tearDown(self):
        os.environ.pop('FIRMS_MAP_KEY',None)
    def _mock(self, status=200, ctype='image/png', content=b'IMG'):
        m=MagicMock()
        m.status_code=status
        m.headers={'Content-Type':ctype}
        m.content=content
        return m
    def test_layers(self):
        for ly in ['fires_viirs_24','fires_viirs_48','fires_viirs_72','fires_viirs_7','fires_modis_24','fires_modis_48','fires_modis_72','fires_modis_7']:
            with patch('firms_wms.requests.get', return_value=self._mock()):
                r=self.client.get('/api/firms/wms?LAYERS='+ly+'&BBOX=0,0,1,1')
                self.assertEqual(r.status_code,200)
    def test_invalid_layer(self):
        r=self.client.get('/api/firms/wms?LAYERS=foo&BBOX=0,0,1,1')
        self.assertEqual(r.status_code,400)
    def test_invalid_bbox(self):
        r=self.client.get('/api/firms/wms?LAYERS=fires_viirs_24&BBOX=bad')
        self.assertEqual(r.status_code,400)
    def test_invalid_size(self):
        r=self.client.get('/api/firms/wms?LAYERS=fires_viirs_24&BBOX=0,0,1,1&WIDTH=9999')
        self.assertEqual(r.status_code,400)
    def test_invalid_srs(self):
        r=self.client.get('/api/firms/wms?LAYERS=fires_viirs_24&BBOX=0,0,1,1&SRS=EPSG:4326')
        self.assertEqual(r.status_code,400)
    def test_missing_key(self):
        os.environ.pop('FIRMS_MAP_KEY',None)
        r=self.client.get('/api/firms/wms?LAYERS=fires_viirs_24&BBOX=0,0,1,1')
        self.assertEqual(r.status_code,503)
    def test_timeout(self):
        with patch('firms_wms.requests.get', side_effect=Exception('timeout')):
            r=self.client.get('/api/firms/wms?LAYERS=fires_viirs_24&BBOX=0,0,1,1')
            self.assertEqual(r.status_code,502)
    def test_upstream_error(self):
        with patch('firms_wms.requests.get', return_value=self._mock(status=500)):
            r=self.client.get('/api/firms/wms?LAYERS=fires_viirs_24&BBOX=0,0,1,1')
            self.assertEqual(r.status_code,502)
    def test_non_image(self):
        with patch('firms_wms.requests.get', return_value=self._mock(ctype='text/xml')):
            r=self.client.get('/api/firms/wms?LAYERS=fires_viirs_24&BBOX=0,0,1,1')
            self.assertEqual(r.status_code,502)
    def test_no_key_leak(self):
        os.environ['FIRMS_MAP_KEY']='SECRET123'
        with patch('firms_wms.requests.get', return_value=self._mock()):
            r=self.client.get('/api/firms/wms?LAYERS=fires_viirs_24&BBOX=0,0,1,1')
            self.assertNotIn(b'SECRET123', r.data)
    def test_forward_params(self):
        with patch('firms_wms.requests.get', return_value=self._mock()) as m:
            self.client.get('/api/firms/wms?LAYERS=fires_viirs_24&BBOX=0,0,1,1')
            url=m.call_args.args[0]
            self.assertIn('fires_viirs_24', url)



    def test_lowercase_params(self):
        with patch('firms_wms.requests.get', return_value=self._mock()):
            r=self.client.get('/api/firms/wms?layers=fires_viirs_24&bbox=0,0,1,1&width=256&height=256&srs=EPSG:3857&format=image/png')
            self.assertEqual(r.status_code,200)

if __name__=='__main__':
    unittest.main()
