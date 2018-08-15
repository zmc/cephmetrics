=========
Variables
=========

Most users will not need to deviate from our defaults, save for the Grafana admin user's password. This document attempts to explain them just in case.

-------------------
Overriding Defaults
-------------------
Cephmetrics allows for a number of variables to be set in order to change the default behavior of many of the Ansible roles used for deployment.


Defaults for each role's variables are stored in
``roles/<role_name>/defaults/main.yml``\ , as the value of a dict called
``defaults``. A fake example for simplicity's sake:

.. code-block::

   $ cat ./ceph-fake-role/defaults/main.yaml
   ---
   defaults:
     fake_role:
       a_dict:
         a_key: a_value
       another_option: true


While each role's variables are stored as a single dict, individual values may be overridden without having to redundantly specify values for the rest. Using the above example, if you wanted to override ``another_option``:

.. code-block::

  $ cat ./my-inventory/group_vars/all.yml
  ---
  fake_role:
    another_option: false


Below, we'll document the variables used by our various roles. To avoid clutter, we avoid listing default values when they are large and unlikely to be overridden.

----------------
Settings by Role
----------------

ceph-collectd
=============

Note that these variables *only* apply to collectd-based deployments, which
are deprecated.

``cluster``\ : The name of the Ceph cluster. Default: ceph

``collector_dependencies.(yum|apt)``\ : Lists of packages that the cephmetrics
collectors require. Should not need overriding.


ceph-docker
===========
``docker.packages.(yum|apt)``\ : The names of the docker and docker-python
packages to install

``network_name``\ : The name of the Docker network to create for the containers. Default: cephmetrics

``service_name``\ : The name of the systemd service that controls the docker
daemon. This will depend on the package used; for example, RHEL offers an
alternative docker-latest package which would require setting this value to
docker-latest as well. Default: docker

ceph-grafana
============

Top-level settings
------------------

``replace_dashboards``\ : Whether to override existing dashboards with the same name. Default: true

``update_alerts``\ : Whether to update the alerts dashboard along with the rest. Removes any user-defined alerts. Default: false

``devel_packages.(yum|apt)``\ : Dependency packages to install when in ``devel_mode``.


``grafana`` settings
--------------------
``container_name``\ : The name of the container to use, in [registry[:port]/]user/repo format. Default: grafana/grafana.

``container_cpu_period``\ : This is passed to docker using the --cpu-period flag. Default: 100000

``container_cpu_cores``\ : This is multiplied by container_cpu_period and passed to docker using the --cpu-quota flag. Default: 2

``container_memory``\ : The size of the container's RAM quota, in GB. Default: 4

``version``\ : Only for containers; this is the tag value passed to docker. Default: latest

``uid``\ : The UID of the grafana-server process inside the container. Default: 472

``datasource``\ : The name of the datasource to create in Grafana. Currently unsafe to change. Default: Local

``admin_user`` and ``admin_password``\ : These are safe to set on new deployments. If you need to change the admin user's password later, use the web UI and then override the setting for any future re-deployments. Default: admin/admin

``plugins``\ : The Grafana plugins to install. Default: vonage-status-panel, grafana-piechart-panel


ceph-graphite
=============
Note that most of the settings relevant to Graphite are currently stored in the ``defaults.yml`` for cephmetrics-common_.

Top-level settings
------------------

``devel_packages.(yum|apt)``\ : Dependency packages to install when in ``devel_mode``.


ceph-mgr
========
There are no variables to set for this role.

ceph-node-exporter
==================
``node_exporter`` settings
--------------------------

``arch_map``\ : When in ``devel_mode``, this is used when searching for upstream releases to download. Users should not need to override this.

``packages.(apt|yum)``\ : The name of the node_exporter package. Only relevant when ``devel_mode`` is false.

``service_name``\ : The name of the systemd service controlling node_exporter. On RHEL, this should be set to prometheus-node-exporter. Default: node_exporter.


ceph-prometheus
===============
``prometheus`` settings
--------------------
``container_name``\ : The name of the container to use, in [registry[:port]/]user/repo format. Default: prom/prometheus.

``container_cpu_period``\ : This is passed to docker using the --cpu-period flag. Default: 100000

``container_cpu_cores``\ : This is multiplied by container_cpu_period and passed to docker using the --cpu-quota flag. Default: 2

``container_memory``\ : The size of the container's RAM quota, in GB. Default: 4

``version``\ : Only for containers; this is the tag value passed to docker. Default: latest

``user_id``\ : The UID of the prometheus process. Default: 65534

``data_dir``\ : The location where prometheus data and configuration will be stored. Default: /var/lib/cephmetrics

``etc_hosts``\ : This is passed directly to the `docker container module <https://docs.ansible.com/ansible/latest/modules/docker_container_module.html#docker-container>`_. It is only used for containerized deployments. Default: {}


cephmetrics-common
==================

Top-level settings
------------------

``devel_mode``\ : This setting controls various aspects of the deployment. Currently, ``devel_mode`` is most suitable for most non-RHEL users.

``containerized``\ : Whether or not to deploy Grafana and Prometheus as containers (as opposed to packages)

``backend`` settings
````````````````````

``metrics``\ : The source of Ceph metrics. The default, and only supported setting is 'mgr'\ ; the older collectd system can be used by setting 'cephmetrics' here.

``storage``\ : The storage mechanism used for the metrics. With 'mgr' metrics, use 'prometheus'. With 'cephmetrics', use 'collectd'.

.. code-block::

   graphite:
     service: graphite-web
     web_port: "{{ graphite_port | default('8080') }}"
     api_port: 8888
     # The unix account running the graphite-web process
     unix_user:
       yum: apache
       apt: _graphite
     build_index:
       yum: '/usr/bin/graphite-build-index'
       apt: '/usr/bin/graphite-build-search-index'
     apache_name:
       yum: 'httpd'
       apt: 'apache2'
     apache_conf:
       yum: '/etc/httpd/conf/httpd.conf'
       apt: '/etc/apache2/apache2.conf'
     site_conf:
       yum: '/etc/httpd/conf.d/graphite-web.conf'
       apt: '/etc/apache2/sites-available/graphite-web.conf'
     app_conf:
       yum: '/etc/graphite-web/local_settings.py'
       apt: '/etc/graphite/local_settings.py'
   carbon:
     unix_user:
       yum: carbon
       apt: _graphite
     storage_dir:
       yum: /var/lib/carbon
       apt: /var/lib/graphite
   whisper:
     retention:
       - ['10s', '7d']
       - ['1m', '30d']
       - ['15m', '5y']
   # The firewalld zone that carbon and grafana will use
   firewalld_zone: public
