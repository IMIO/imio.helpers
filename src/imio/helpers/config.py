# -*- coding: utf-8 -*-
#
# GNU General Public License (GPL)
#

import pkg_resources


HAS_DASHBOARD = True
try:
    pkg_resources.get_distribution('collective.eeafaceted.dashboard')
except pkg_resources.DistributionNotFound:
    HAS_DASHBOARD = False
