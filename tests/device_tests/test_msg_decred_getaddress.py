# This file is part of the TREZOR project.
#
# Copyright (C) 2012-2016 Marek Palatinus <slush@satoshilabs.com>
# Copyright (C) 2017 Peter Banik <peter@froggle.org>
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

import unittest
import common
import trezorlib.ckd_public as bip32
import binascii

class TestMsgDecredGetaddress(common.DecredTrezorTest):

    def test_decred_getaddress(self):
        self.setup_mnemonic_nopin_nopassphrase()

        # [Chain m/44']
        address = self.client.decred_get_address([
            0x80000000 + 44,
        ])
        self.assertEqual(address, 'DsYEbndBQxJEZqvCmH1ZwvR5cfArUnp9i8E')

        # [Chain m/44'/20'/0']
        address = self.client.decred_get_address([
            0x80000000 + 44,
            0x80000000 + 20,
            0x80000000 + 0,
        ])
        self.assertEqual(address, 'DsXA1Lb5aLZNgakhPd8Z45WU8eqv7QrDmzK')

if __name__ == '__main__':
    unittest.main()
