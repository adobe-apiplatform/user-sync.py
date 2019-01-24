#!/usr/bin/env bash
yum groupinstall -y "Development Tools"
yum install -y epel-release
yum install -y https://centos7.iuscommunity.org/ius-release.rpm
yum install -y python36u-devel python36u-pip python36u-virtualenv
yum install -y python-devel python-pip python-virtualenv
yum install -y pkgconfig openssl-devel openldap-devel dbus-glib-devel dbus-python libffi-devel
