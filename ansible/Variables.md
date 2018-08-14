# Variables
Cephmetrics allows for a number of variables to be set in order to change the default behavior of many of the Ansible roles used for deployment.

Defaults for each role's variables are stored in
`roles/<role_name>/defaults/main.yml`, as the value of a `dict` called
`defaults`. A fake example for simplicity's sake:

    $ cat ./ceph-fake-role/defaults/main.yaml
    ---
    defaults:
      fake_role:
        a_dict:
          a_key: a_value
        another_option: true

While each role's variables are stored as a single dict, individual values may be overridden without having to redundantly specify values for the rest.

Below, we'll document the variables used by our various roles.

## ceph-collectd

  cluster: ceph
  collector_dependencies:
    yum:
      # For the json python module
      - python-libs
      # For the rados python module
      - python-rados
      # For the ceph_daemon python module
      - ceph-common
      # For semodule
      - make
      - libsemanage-python
      - policycoreutils-python
      - selinux-policy-devel
    apt:
      # For the json module, via libpython2.7-stdlib
      - python2.7
      # For the rados python module
      - python-rados
      # For the ceph_daemon python module
      - ceph-common


## ceph-docker
  docker:
    packages:
      yum:
        - docker
        - docker-python
      apt:
        - docker.io
        - python-docker
    network_name: cephmetrics
    service_name: docker

## ceph-grafana
  # graphite defaults are now in the cephmetrics-common role since the
  # ceph-collectd role needs access to them
  replace_dashboards: true
  update_alerts: false
  grafana:
    container_name: "grafana/grafana"
    container_cpu_period: 100000
    container_cpu_cores: 2
    # container_memory is in GB
    container_memory: 4
    # version currently only applies to containers
    version: latest
    uid: 472
    datasource: Local
    # You need to change these in the web UI on an already deployed machine, first
    # New deployments work fine
    admin_user: admin
    admin_password: admin
    plugins:
      - vonage-status-panel
      - grafana-piechart-panel
devel_packages:
  yum:
    # unzip is needed to extract the Vonage plugin
    - unzip
    - grafana
    # for dashUpdater.py
    - PyYAML
    - python-requests
  apt:
    # unzip is needed to extract the Vonage plugin
    - unzip
    - grafana
    # for dashUpdater.py
    - python-yaml
    - python-requests
---
devel_packages:
  yum:
    - graphite-web
    - python-carbon
  apt:
    - graphite-web
    - apache2
    - libapache2-mod-wsgi
    - graphite-carbon

## ceph-mgr
There are no variables to set for this role.

## ceph-node-exporter
  node_exporter:
    arch_map:
      x86_64: amd64
      i386: '386'
    packages:
      apt:
        - prometheus-node-exporter
      yum:
        - prometheus-node_exporter
  service_name: node_exporter

## ceph-prometheus
  prometheus:
    container_name: prom/prometheus
    container_cpu_period: 100000
    container_cpu_cores: 2
    # container_memory is in GB
    container_memory: 4
    # This is passed directly to the docker_container module. It is only used
    # for containerized deployments.
    etc_hosts: {}
    version: latest
    data_dir: /var/lib/cephmetrics
    user_id: '65534'  # This is the UID used by the prom/prometheus docker image

## cephmetrics-common
  containerized: true
  backend:
    metrics: mgr  # mgr, cephmetrics
    storage: prometheus  # prometheus, graphite
  devel_mode: true
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
