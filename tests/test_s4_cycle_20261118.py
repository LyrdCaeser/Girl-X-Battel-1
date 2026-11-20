"""S4 cycle/access tests. Only synthetic times & mocked HTTP, no production edits."""
from unittest import TestCase, mock
from gxb2 import s4_exclusive, auth, live_service
from server import HTTPHandler


class TestS4Cycle(TestCase):
    EPOCH = 1794980000

    def test_boundary_exact_72h_and_48h(self):
        c=s4_exclusive.cycle(self.EPOCH,self.EPOCH)
        self.assertEqual(c['phase'],'open')
        self.assertEqual(c['remaining_seconds'],72*3600)
        last_open=s4_exclusive.cycle(self.EPOCH+72*3600-1,self.EPOCH)
        self.assertEqual(last_open['phase'],'open')
        self.assertEqual(last_open['remaining_seconds'],1)
        locked=s4_exclusive.cycle(self.EPOCH+72*3600,self.EPOCH)
        self.assertEqual(locked['phase'],'locked')
        self.assertEqual(locked['remaining_seconds'],48*3600)
        last_lock=s4_exclusive.cycle(self.EPOCH+5*86400-1,self.EPOCH)
        self.assertEqual(last_lock['phase'],'locked')
        self.assertEqual(last_lock['remaining_seconds'],1)
        reopened=s4_exclusive.cycle(self.EPOCH+5*86400,self.EPOCH)
        self.assertEqual(reopened['phase'],'open')
        self.assertEqual(reopened['remaining_seconds'],72*3600)
        self.assertEqual(reopened['cycle_index'],1)
        self.assertEqual(s4_exclusive.cycle(self.EPOCH+10*86400,self.EPOCH)['cycle_index'],2)

    def test_lock_checks_server_only(self):
        with mock.patch.object(s4_exclusive,'cycle',return_value={'phase':'locked'}):
            for sid in ('S1','S2','S3'):
                self.assertIsNone(s4_exclusive.ensure_open(sid))
            with self.assertRaisesRegex(ValueError, '48 giờ'):
                s4_exclusive.ensure_open('S4')
        with mock.patch.object(s4_exclusive,'cycle',return_value={'phase':'open'}):
            self.assertIsNotNone(s4_exclusive.ensure_open('s4'))

    def test_auth_create_character_stops_before_insert(self):
        current={'account':{'uid':'UID-TEST','server_id':'S1'}}
        with mock.patch.object(auth,'session',return_value=current), \
             mock.patch.object(s4_exclusive,'ensure_open',side_effect=ValueError('48 giờ')), \
             mock.patch.object(live_service,'register_player') as register, \
             mock.patch.object(live_service,'player') as player:
            with self.assertRaisesRegex(ValueError,'48 giờ'):
                auth.create_character('fake','S4','Test')
            register.assert_not_called()
            player.assert_not_called()

    def test_auth_switch_stops_before_db_or_player_access(self):
        current={'account':{'uid':'UID-TEST','server_id':'S2'}}
        with mock.patch.object(auth,'session',return_value=current), \
             mock.patch.object(s4_exclusive,'ensure_open',side_effect=ValueError('48 giờ')), \
             mock.patch.object(live_service,'player') as player:
            with self.assertRaisesRegex(ValueError,'48 giờ'):
                auth.switch_server('fake','S4')
            player.assert_not_called()

    def test_require_auth_423_for_s4_with_valid_session(self):
        handler=object.__new__(HTTPHandler)
        handler.auth_context=lambda: {'account':{'uid':'T','server_id':'S4'}}
        handler.send=mock.Mock()
        cycle={'server_id':'S4','phase':'locked','phase_end':123}
        with mock.patch.object(s4_exclusive,'cycle',return_value=cycle):
            self.assertIsNone(HTTPHandler.require_auth(handler))
        handler.send.assert_called_once()
        args=handler.send.call_args.args
        self.assertEqual(args[0],423)
        self.assertEqual(args[1]['code'],'S4_LOCKED')
        self.assertEqual(args[1]['s4_cycle'],cycle)

    def test_require_auth_no_effect_s1_to_s3(self):
        for server in ('S1','S2','S3'):
            handler=object.__new__(HTTPHandler)
            ctx={'account':{'uid':'T','server_id':server}}
            handler.auth_context=lambda:ctx
            handler.send=mock.Mock()
            with mock.patch.object(s4_exclusive,'cycle') as cyc:
                self.assertIs(HTTPHandler.require_auth(handler),ctx)
                cyc.assert_not_called()
            handler.send.assert_not_called()

    def test_locked_client_gets_cycle_from_immutable_world_anchor(self):
        with mock.patch.object(live_service,'worlds',return_value=[
             {'server_id':'S1','created_at':self.EPOCH-100},
             {'server_id':'S4','created_at':self.EPOCH}]):
            with mock.patch.object(s4_exclusive,'_s4_epoch',None):
                status=s4_exclusive.cycle(now=self.EPOCH+72*3600)
                self.assertEqual(status['phase'],'locked')
                self.assertEqual(status['server_id'],'S4')
                self.assertEqual(status['started_at'],self.EPOCH)
