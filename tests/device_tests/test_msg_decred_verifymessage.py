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
import binascii
import base64

from trezorlib.client import CallException

class TestMsgVerifymessage(common.DecredTrezorTest):

    def test_message_verify_b64(self):
        self.setup_mnemonic_nopin_nopassphrase()
        sig = base64.b64decode('H1WVReAsbaacfm/ZHDVoXhZrj6rXz5p17VmP8CR9cz1FHpi8b63XOBs+9ldzgIlzb4DJg3w8q6FmBpVKW8boS3I=')
        ret = self.client.decred_verify_message(
            'DspDtjHb9aMymZzZjheNUjoPax3eWtrqaQf',
            sig,
            'Waldo was here')
        self.assertTrue(ret)

    def test_message_verify(self):
        self.setup_mnemonic_nopin_nopassphrase()
        ret = self.client.decred_verify_message(
            'DspDtjHb9aMymZzZjheNUjoPax3eWtrqaQf',
            binascii.unhexlify('1f559545e02c6da69c7e6fd91c35685e166b8faad7cf9a75ed598ff0247d733d451e98bc6fadd7381b3ef657738089736f80c9837c3caba16606954a5bc6e84b72'),
            "Waldo was here"
        )
        self.assertTrue(ret)

        # FAIL - wrong sig
        ret = self.client.decred_verify_message(
            'DspDtjHb9aMymZzZjheNUjoPax3eWtrqaQf',
            binascii.unhexlify('1f559545e02c6da69c7e6fd9ffff685e166b8faad7cf9a75ed598ff0247d733d451e98bc6fadd7381b3ef657738089736f80c9837c3caba16606954a5bc6e84b72'),
            "Waldo was here"
        )
        self.assertFalse(ret)

        # FAIL - wrong msg
        ret = self.client.decred_verify_message(
            'DspDtjHb9aMymZzZjheNUjoPax3eWtrqaQf',
            binascii.unhexlify('1f559545e02c6da69c7e6fd91c35685e166b8faad7cf9a75ed598ff0247d733d451e98bc6fadd7381b3ef657738089736f80c9837c3caba16606954a5bc6e84b72'),
            "Waldo was INVALID"
        )
        self.assertFalse(ret)

        # FAIL - wrong address
        ret = self.client.decred_verify_message(
            'DspDtjHb9aMymZzZjheNUjoPax3ffffffff',
            binascii.unhexlify('1f559545e02c6da69c7e6fd91c35685e166b8faad7cf9a75ed598ff0247d733d451e98bc6fadd7381b3ef657738089736f80c9837c3caba16606954a5bc6e84b72'),
            "Waldo was here"
        )
        self.assertFalse(ret)

if __name__ == '__main__':
    unittest.main()
