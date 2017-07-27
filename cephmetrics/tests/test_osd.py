#!/usr/bin/env python

from base import Base


class TestOSD(Base):
    def test_type(self):
        obj = self.get_obj(need_role='osd')
        obj.osd._dev_to_osd()
        print obj.osd.osd
        assert len(obj.osd.osd) > 0
        for key, val in obj.osd.osd.items():
            if not key.isdigit():
                continue
            assert val._osd_type in ('filestore', 'bluestore')

    def test_osd_stats(self):
        obj = self.get_obj(need_role='osd')
        osd_stats = obj.osd.get_stats()
        assert osd_stats['num_osds'] > 0
        assert len(filter(lambda k: k.isdigit(), obj.osd.osd.keys())) \
            == osd_stats['num_osds']
        assert len(osd_stats['jrnl']) == osd_stats['num_osds']
