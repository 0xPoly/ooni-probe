# -*- encoding: utf-8 -*-
#
# :authors: Arturo Filastò
# :licence: see LICENSE

from ooni.templates import scapyt
from scapy.all import *
class ExampleScapy(scapyt.ScapyTest):
    inputs = [IP()/TCP()]
