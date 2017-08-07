#!/usr/bin/env python
import os
import sys

from collections import OrderedDict
from mock import patch, Mock, MagicMock
from pytest import skip

ONLINE = (os.environ.get('TEST_ONLINE', '1') == '1')

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..')))


def patch_offline(*args, **kwargs):
    if not ONLINE:
        return patch(*args, **kwargs)


class OnlineBase(object):
    conf = dict(
        ClusterName='ceph',
    )

    def setup(self):
        self.patchers = OrderedDict()
        self.mocks = dict()
        self.add_patchers()
        self.start_patchers()

    def add_patchers(self):
        m_collectd = Mock()
        self.mocks['m_collectd'] = m_collectd
        self.patchers['collectd'] = patch.dict(
            'sys.modules', collectd=m_collectd)

    def start_patchers(self):
        for name, patcher in self.patchers.items():
            self.mocks[name] = patcher.start()
        # self.patchers['collectd'] = patch.dict(
        #         'sys.modules', collectd=m_collectd)
        # self.mocks['collectd'] = m_collectd

    def get_obj(self, need_role=None):
        import cephmetrics
        cephmetrics.setup_module_logging('debug', path=None)
        self.klass = cephmetrics.Ceph
        obj = cephmetrics.CEPH = self.klass()
        obj.cluster_name = self.conf['ClusterName']
        obj.probe()
        if need_role and getattr(obj, need_role) is None:
            skip("No %s found" % need_role)
        return obj

    def teardown(self):
        for patcher in self.patchers.values():
            patcher.stop()


class OfflineBase(OnlineBase):
    def add_patchers(self):
        super(OfflineBase, self).add_patchers()
        m_ceph_daemon = Mock()
        self.mocks['m_ceph_daemon'] = m_ceph_daemon
        self.patchers['ceph_daemon'] = patch.dict(
            'sys.modules', ceph_daemon=m_ceph_daemon)
        m_rados = MagicMock()
        m_rados.__enter__.return_value.__exit__.side_effect = RuntimeError
        self.mocks['m_rados'] = m_rados
        self.patchers['rados'] = patch.dict(
            'sys.modules', rados=m_rados)
        m_rbd = MagicMock()
        self.mocks['m_rbd'] = m_rbd
        self.patchers['rbd'] = patch.dict(
            'sys.modules', rbd=m_rbd)
        self.patchers['get_osd_type'] = patch(
            'cephmetrics.collectors.osd.OSDs.get_osd_type',
        )
        self.patchers['_get_fssize'] = patch(
            'cephmetrics.collectors.common.Disk._get_fssize',
        )
        self.patchers['mon_get_version'] = patch(
            'cephmetrics.collectors.mon.Mon._get_version',
        )
        self.patchers['mon_get_version'].return_value = 11.0
        self.patchers['mon_get_pool_stats'] = patch(
            'cephmetrics.collectors.mon.Mon._get_pool_stats',
        )
        self.patchers['mon_get_osd_states'] = patch(
            'cephmetrics.collectors.mon.Mon._get_osd_states',
        )

        def fake_exists(path):
            if path.endswith('.asok'):
                return True
            self.patchers['exists'].stop()
            result = os.path.exists(path)
            self.mocks['exists'] = self.patchers['exists'].start()
            return result

        self.patchers['exists'] = patch(
            'os.path.exists',
            fake_exists,
        )
        self.patchers['freadlines'] = patch(
            'cephmetrics.collectors.common.freadlines',
        )
        self.patchers['fread'] = patch(
            'cephmetrics.collectors.common.fread',
        )

    def start_patchers(self):
        super(OfflineBase, self).start_patchers()
        self.mocks['get_osd_type'].return_value = 'filestore'
        self.mocks['_get_fssize'].return_value = \
            (994349350912, 96942489600, 10.0)


if ONLINE:
    Base = OnlineBase
else:
    Base = OfflineBase
