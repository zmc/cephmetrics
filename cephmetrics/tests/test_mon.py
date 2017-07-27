#!/usr/bin/env python
from pytest import skip

from base import Base


class TestMon(Base):
    def test_get_pools(self):
        obj = self.get_obj(need_role='mon')
        pools = obj.mon.get_pools()
        assert 'rbd' in pools

    def test_stats(self):
        obj = self.get_obj(need_role='mon')
        stats = obj.mon.get_stats()
        print stats
        assert stats.keys() == ['mon']
        mon = stats['mon']
        top_level_keys = sorted([
            'num_mds_up', 'features', 'num_mds_in', 'num_bytes',
            'num_rbds', 'num_pool', 'osd_bytes', 'num_object_misplaced',
            'osd_bytes_avail', 'osd_epoch', 'num_osd_up', 'num_osd',
            'num_mds_failed', 'health', 'num_pg_active_clean', 'mds_epoch',
            'num_mon', 'num_pg_peering', 'num_object', 'num_pgs_stuck',
            'num_object_unfound', 'num_object_degraded', 'num_pg',
            'num_mon_quorum', 'num_osd_in', 'num_pg_active', 'mon_status',
            'osd_state', 'pools', 'num_osd_hosts', 'osd_bytes_used',
        ])
        assert sorted(mon.keys()) == top_level_keys
        assert len(mon['osd_state']) == mon['num_osd']
        assert len(mon['mon_status']) == mon['num_mon']
        assert mon['pools'].keys() == obj.mon.get_pools()
