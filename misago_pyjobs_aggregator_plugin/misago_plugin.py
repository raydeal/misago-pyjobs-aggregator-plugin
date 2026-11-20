"""Misago plugin manifest.

The package is intentionally a regular Django application. Misago discovers
the package because it contains this manifest and installs its migrations and
admin integration as part of the normal plugin bootstrap.
"""

PLUGIN_NAME = "Python Jobs Aggregator"
PLUGIN_VERSION = "0.1.0"
