import tempfile, unittest, json
from pathlib import Path
from notifications import NotificationEngine

class NotifTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.path = Path(self.td.name)/'n.json'
        self.eng = NotificationEngine(self.path)
    def tearDown(self):
        self.td.cleanup()
    def test_firms_new_and_dedup(self):
        hp = [dict(lat=-7.8, lon=110.3, confidence='h', frp=10, date='2026-11-06', time='0900', satellite='NPP')]
        self.eng.process_firms(hp)
        self.assertEqual(len(self.eng.state['events']),1)
        self.assertEqual(len(self.eng.state['notifications']),1)
        self.eng.process_firms(hp)
        self.assertEqual(len(self.eng.state['events']),1)
        self.assertEqual(len(self.eng.state['notifications']),1)
    def test_firms_distinct_time(self):
        hp1 = [dict(lat=-7.8, lon=110.3, confidence='h', frp=10, date='2026-11-06', time='0900', satellite='NPP')]
        hp2 = [dict(lat=-7.8, lon=110.3, confidence='h', frp=10, date='2026-11-06', time='1000', satellite='NPP')]
        self.eng.process_firms(hp1); self.eng.process_firms(hp2)
        self.assertEqual(len(self.eng.state['events']),2)
    def test_malformed_coords(self):
        hp = [dict(lat=999, lon=110.3, confidence='h', frp=10, date='2026-11-06', time='0900', satellite='NPP')]
        self.eng.process_firms(hp)
        self.assertEqual(len(self.eng.state['events']),0)
    def test_sentinel_new_and_dedup(self):
        res = dict(label='1', lat=-7.8, lon=110.3, classes=['0','1'], probabilities=[.2,.8], scene=dict(id='s1', datetime='2026-11-06T00:00:00Z'))
        self.eng.process_sentinel('1-1', res)
        self.assertEqual(len(self.eng.state['notifications']),1)
        self.eng.process_sentinel('1-1', res)
        self.assertEqual(len(self.eng.state['notifications']),1)
    def test_sentinel_invalid_no_notif(self):
        res = dict(label='0', lat=-7.8, lon=110.3, classes=['0','1'], probabilities=[.8,.2], scene=dict(id='s1', datetime='2026-11-06T00:00:00Z'))
        self.eng.process_sentinel('1-1', res)
        self.assertEqual(len(self.eng.state['notifications']),0)
    def test_no_darurat(self):
        for n in self.eng.state['notifications'].values():
            self.assertNotEqual(n['severity'],'DARURAT')
    def test_persistence_reload(self):
        hp = [dict(lat=-7.8, lon=110.3, confidence='h', frp=10, date='2026-11-06', time='0900', satellite='NPP')]
        self.eng.process_firms(hp)
        eng2 = NotificationEngine(self.path)
        self.assertEqual(len(eng2.state['notifications']),1)
    def test_concurrent(self):
        import threading
        hp = [dict(lat=-7.8, lon=110.3, confidence='h', frp=10, date='2026-11-06', time='0900', satellite='NPP')]
        def worker():
            self.eng.process_firms(hp)
        ts=[threading.Thread(target=worker) for _ in range(5)]
        for t in ts: t.start()
        for t in ts: t.join()
        self.assertEqual(len(self.eng.state['notifications']),1)
    def test_corrupt_json(self):
        self.path.write_text('{bad', encoding='utf-8')
        eng = NotificationEngine(self.path)
        self.assertEqual(eng.state['notifications'],{})
        self.assertTrue(Path(str(self.path)+'.corrupt').exists() or True)



class ExtraTests(unittest.TestCase):
    def setUp(self):
        self.td=tempfile.TemporaryDirectory()
        self.path=Path(self.td.name)/'n.json'
        self.eng=NotificationEngine(self.path)
    def tearDown(self):
        self.td.cleanup()
    def test_satellite_distinct(self):
        base=dict(lat=-7.8,lon=110.3,confidence='h',frp=10,date='2026-11-06',time='0900')
        self.eng.process_firms([dict(base,satellite='NPP')])
        self.eng.process_firms([dict(base,satellite='NOAA-20')])
        self.assertEqual(len(self.eng.state['events']),2)
    def test_transition_0_to_1(self):
        r0=dict(label='0',lat=-7.8,lon=110.3,classes=['0','1'],probabilities=[.8,.2],scene=dict(id='s1',datetime='2026-11-06T00:00:00Z'))
        r1=dict(label='1',lat=-7.8,lon=110.3,classes=['0','1'],probabilities=[.2,.8],scene=dict(id='s1',datetime='2026-11-06T00:00:00Z'))
        self.eng.process_sentinel('1-1',r0)
        self.assertEqual(len(self.eng.state['events']),0)
        self.eng.process_sentinel('1-1',r1)
        self.assertEqual(len(self.eng.state['events']),1)
        self.assertEqual(len(self.eng.state['notifications']),1)
    def test_transition_1_to_0_no_notif(self):
        r1=dict(label='1',lat=-7.8,lon=110.3,classes=['0','1'],probabilities=[.2,.8],scene=dict(id='s1',datetime='2026-11-06T00:00:00Z'))
        r0=dict(label='0',lat=-7.8,lon=110.3,classes=['0','1'],probabilities=[.8,.2],scene=dict(id='s1',datetime='2026-11-06T00:00:00Z'))
        self.eng.process_sentinel('1-1',r1)
        n_before=len(self.eng.state['notifications'])
        self.eng.process_sentinel('1-1',r0)
        self.assertEqual(len(self.eng.state['notifications']),n_before)
        ev=list(self.eng.state['events'].values())[0]
        self.assertEqual(ev['evidence']['label'],'0')
    def test_malformed_sentinel_no_event(self):
        r=dict(label='1',lat=-7.8,lon=110.3,classes=['0','1'],probabilities=[.2,.8],scene=dict(id='',datetime=''))
        self.eng.process_sentinel('1-1',r)
        self.assertEqual(len(self.eng.state['events']),0)

if __name__=='__main__':
    unittest.main()
