# This file is part of the TREZOR project.
#
# Copyright (C) 2012-2016 Marek Palatinus <slush@satoshilabs.com>
# Copyright (C) 2012-2016 Pavol Rusnak <stick@satoshilabs.com>
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function

import unittest
import hashlib

from trezorlib.client import TrezorClient, TrezorClientDebugLink
from trezorlib import tx_api


tx_api.cache_dir = '../txcache'


try:
    from trezorlib.transport_hid import HidTransport
    HID_ENABLED = True
except ImportError as e:
    print('HID transport disabled:', e)
    HID_ENABLED = False

try:
    from trezorlib.transport_pipe import PipeTransport
    PIPE_ENABLED = True
except ImportError as e:
    print('PIPE transport disabled:', e)
    PIPE_ENABLED = False

try:
    from trezorlib.transport_udp import UdpTransport
    UDP_ENABLED = True
except ImportError as e:
    print('UDP transport disabled:', e)
    UDP_ENABLED = False


def pipe_exists(path):
    import os
    import stat
    try:
        return stat.S_ISFIFO(os.stat(path).st_mode)
    except:
        return False


def get_transport():
    if HID_ENABLED and HidTransport.enumerate():
        devices = HidTransport.enumerate()
        wirelink = devices[0]
        debuglink = devices[0].find_debug()

    elif PIPE_ENABLED and pipe_exists('/tmp/pipe.trezor.to'):
        wirelink = PipeTransport('/tmp/pipe.trezor', False)
        debuglink = PipeTransport('/tmp/pipe.trezor_debug', False)

    elif UDP_ENABLED:
        wirelink = UdpTransport()
        debuglink = UdpTransport()

    return wirelink, debuglink


if HID_ENABLED and HidTransport.enumerate():
    print('Using TREZOR')
elif PIPE_ENABLED and pipe_exists('/tmp/pipe.trezor.to'):
    print('Using Emulator (v1=pipe)')
elif UDP_ENABLED:
    print('Using Emulator (v2=udp)')


class TrezorTest(unittest.TestCase):

    def setUp(self):
        wirelink, debuglink = get_transport()
        self.client = TrezorClientDebugLink(wirelink)
        self.client.set_debuglink(debuglink)
        self.client.set_tx_api(tx_api.TxApiBitcoin)
        # self.client.set_buttonwait(3)

        #                     1      2     3    4      5      6      7     8      9    10    11    12
        self.mnemonic12 = 'alcohol woman abuse must during monitor noble actual mixed trade anger aisle'
        self.mnemonic18 = 'owner little vague addict embark decide pink prosper true fork panda embody mixture exchange choose canoe electric jewel'
        self.mnemonic24 = 'dignity pass list indicate nasty swamp pool script soccer toe leaf photo multiply desk host tomato cradle drill spread actor shine dismiss champion exotic'
        self.mnemonic_all = ' '.join(['all'] * 12)

        self.pin4 = '1234'
        self.pin6 = '789456'
        self.pin8 = '45678978'

        self.client.wipe_device()
        self.client.transport.session_begin()

        print("Setup finished")
        print("--------------")

    def setup_mnemonic_allallall(self):
        self.client.load_device_by_mnemonic(mnemonic=self.mnemonic_all, pin='', passphrase_protection=False, label='test', language='english')

    def setup_mnemonic_nopin_nopassphrase(self):
        self.client.load_device_by_mnemonic(mnemonic=self.mnemonic12, pin='', passphrase_protection=False, label='test', language='english')

    def setup_mnemonic_pin_nopassphrase(self):
        self.client.load_device_by_mnemonic(mnemonic=self.mnemonic12, pin=self.pin4, passphrase_protection=False, label='test', language='english')

    def setup_mnemonic_pin_passphrase(self):
        self.client.load_device_by_mnemonic(mnemonic=self.mnemonic12, pin=self.pin4, passphrase_protection=True, label='test', language='english')

    def tearDown(self):
        self.client.transport.session_end()
        self.client.close()


def generate_entropy(strength, internal_entropy, external_entropy):
    '''
    strength - length of produced seed. One of 128, 192, 256
    random - binary stream of random data from external HRNG
    '''
    if strength not in (128, 192, 256):
        raise ValueError("Invalid strength")

    if not internal_entropy:
        raise ValueError("Internal entropy is not provided")

    if len(internal_entropy) < 32:
        raise ValueError("Internal entropy too short")

    if not external_entropy:
        raise ValueError("External entropy is not provided")

    if len(external_entropy) < 32:
        raise ValueError("External entropy too short")

    entropy = hashlib.sha256(internal_entropy + external_entropy).digest()
    entropy_stripped = entropy[:strength // 8]

    if len(entropy_stripped) * 8 != strength:
        raise ValueError("Entropy length mismatch")

    return entropy_stripped


class DecredTrezorTest(unittest.TestCase):
    def setUp(self):
        wirelink, debuglink = get_transport()
        self.client = TrezorClientDebugLink(wirelink)
        self.client.set_debuglink(debuglink)
        self.client.set_tx_api(tx_api.TxApiBitcoin)
        # self.client.set_buttonwait(3)

        self.pgpwordlist = "endorse performance frighten butterfat stagnate exodus checkup amulet absurd newsletter solo resistor Athens sensation island sensation sentence breakaway absurd decimal rematch guitarist beeswax savagery kiwi Burlington commence Atlantic scorecard Camelot eightball impartial ratchet"

        self.pin4 = '1234'
        self.pin6 = '789456'
        self.pin8 = '45678978'

        self.client.wipe_device()

        print("Setup finished")
        print("--------------")

    def setup_mnemonic_allallall(self):
        self.client.load_device_by_decred_wordlist(mnemonic=self.pgpwordlist, pin='', passphrase_protection=False, label='test', language='english')

    def setup_mnemonic_nopin_nopassphrase(self):
        self.client.load_device_by_decred_wordlist(mnemonic=self.pgpwordlist, pin='', passphrase_protection=False, label='test', language='english')

    def setup_mnemonic_pin_nopassphrase(self):
        self.client.load_device_by_decred_wordlist(mnemonic=self.pgpwordlist, pin=self.pin4, passphrase_protection=False, label='test', language='english')

    def setup_mnemonic_pin_passphrase(self):
        self.client.load_device_by_decred_wordlist(mnemonic=self.pgpwordlist, pin=self.pin4, passphrase_protection=True, label='test', language='english')

    def tearDown(self):
        self.client.close()

    def wipeDevice(self):
        ret = self.client.wipe_device()
