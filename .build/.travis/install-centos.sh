#!/usr/bin/env bash
yum update -y
yum groupinstall -y "Development Tools"
yum install -y python3 python3-devel
yum install -y pkgconfig openssl-devel dbus-glib-devel dbus-python libffi-devel
