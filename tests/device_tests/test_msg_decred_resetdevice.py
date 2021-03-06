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

import unittest
import common
import hashlib

from trezorlib import messages_pb2 as proto
from mnemonic import Mnemonic
from pgp_wordlist import wordlist

# helper functions to generate PGP wordlist mnemonics to check device generated mnemonics against
def calculate_checksum(seed):
    intermediate_hash = hashlib.sha256(seed).digest()
    hash = hashlib.sha256(intermediate_hash).digest()
    return hash[0]

def byte_to_mnemonic(data_byte, index):
    bb = data_byte * 2
    if((index % 2) != 0):
        bb += 1
    return wordlist[bb-1]

def mnemonics_from_seed(seed):
    mnemonics = ''
    i = 0
    for b in seed:
        mnemonics += byte_to_mnemonic(b, i)
        mnemonics += ' '
        i += 1
    checksum = calculate_checksum(seed)
    num = int(checksum.encode('hex'), 16)
    mnemonics += byte_to_mnemonic(num, i)
    return mnemonics


def generate_entropy(strength, internal_entropy, external_entropy):
    '''
    strength - length of produced seed. One of 128, 192, 256
    random - binary stream of random data from external HRNG
    '''
    if strength not in (128, 192, 256):
        raise Exception("Invalid strength")

    if not internal_entropy:
        raise Exception("Internal entropy is not provided")

    if len(internal_entropy) < 32:
        raise Exception("Internal entropy too short")

    if not external_entropy:
        raise Exception("External entropy is not provided")

    if len(external_entropy) < 32:
        raise Exception("External entropy too short")

    entropy = hashlib.sha256(internal_entropy + external_entropy).digest()
    entropy_stripped = entropy[:strength // 8]

    if len(entropy_stripped) * 8 != strength:
        raise Exception("Entropy length mismatch")

    return entropy_stripped

class TestDeviceReset(common.DecredTrezorTest):
    def test_reset_device(self):

        self.wipeDevice()

        # No PIN, no passphrase
        external_entropy = b'zlutoucky kun upel divoke ody' * 2
        strength = 256

        ret = self.client.call_raw(proto.ResetDevice(display_random=False,
                                               strength=strength,
                                               passphrase_protection=False,
                                               pin_protection=False,
                                               language='english',
                                               label='test'))

        # Provide entropy
        self.assertIsInstance(ret, proto.EntropyRequest)
        internal_entropy = self.client.debug.read_reset_entropy()
        ret = self.client.call_raw(proto.DecredEntropyAck(entropy=external_entropy))

        # Generate mnemonic locally
        entropy = generate_entropy(strength, internal_entropy, external_entropy)
        seed = bytearray.fromhex(entropy.encode('hex'))
        expected_mnemonic = mnemonics_from_seed(seed)

        mnemonic = []
        for _ in range(33):
            self.assertIsInstance(ret, proto.ButtonRequest)
            mnemonic.append(self.client.debug.read_reset_word())
            self.client.debug.press_yes()
            self.client.call_raw(proto.ButtonAck())

        mnemonic = ' '.join(mnemonic)

        # Compare that device generated proper mnemonic for given entropies
        self.assertEqual(mnemonic, expected_mnemonic)

        mnemonic = []
        for _ in range(33):
            self.assertIsInstance(ret, proto.ButtonRequest)
            mnemonic.append(self.client.debug.read_reset_word())
            self.client.debug.press_yes()
            resp = self.client.call_raw(proto.ButtonAck())

        self.assertIsInstance(resp, proto.Success)

        mnemonic = ' '.join(mnemonic)

        # Compare that second pass printed out the same mnemonic once again
        self.assertEqual(mnemonic, expected_mnemonic)

        # Check if device is properly initialized
        resp = self.client.call_raw(proto.Initialize())
        self.assertFalse(resp.pin_protection)
        self.assertFalse(resp.passphrase_protection)

        # Do passphrase-protected action, PassphraseRequest should NOT be raised
        resp = self.client.call_raw(proto.Ping(passphrase_protection=True))
        self.assertIsInstance(resp, proto.Success)

        # Do PIN-protected action, PinRequest should NOT be raised
        resp = self.client.call_raw(proto.Ping(pin_protection=True))
        self.assertIsInstance(resp, proto.Success)

    def test_reset_device_pin(self):

        self.wipeDevice()
        
        external_entropy = b'zlutoucky kun upel divoke ody' * 2
        strength = 256

        ret = self.client.call_raw(proto.ResetDevice(display_random=True,
                                               strength=strength,
                                               passphrase_protection=True,
                                               pin_protection=True,
                                               language='english',
                                               label='test'))

        self.assertIsInstance(ret, proto.ButtonRequest)
        self.client.debug.press_yes()
        ret = self.client.call_raw(proto.ButtonAck())

        self.assertIsInstance(ret, proto.PinMatrixRequest)

        # Enter PIN for first time
        pin_encoded = self.client.debug.encode_pin('654')
        ret = self.client.call_raw(proto.PinMatrixAck(pin=pin_encoded))
        self.assertIsInstance(ret, proto.PinMatrixRequest)

        # Enter PIN for second time
        pin_encoded = self.client.debug.encode_pin('654')
        ret = self.client.call_raw(proto.PinMatrixAck(pin=pin_encoded))

        # Provide entropy
        self.assertIsInstance(ret, proto.EntropyRequest)
        internal_entropy = self.client.debug.read_reset_entropy()
        ret = self.client.call_raw(proto.DecredEntropyAck(entropy=external_entropy))

        # Generate mnemonic locally
        entropy = generate_entropy(strength, internal_entropy, external_entropy)
        seed = bytearray.fromhex(entropy.encode('hex'))
        expected_mnemonic = mnemonics_from_seed(seed)

        mnemonic = []
        for _ in range(33):
            self.assertIsInstance(ret, proto.ButtonRequest)
            mnemonic.append(self.client.debug.read_reset_word())
            self.client.debug.press_yes()
            self.client.call_raw(proto.ButtonAck())

        mnemonic = ' '.join(mnemonic)

        # Compare that device generated proper mnemonic for given entropies
        self.assertEqual(mnemonic, expected_mnemonic)

        mnemonic = []
        for _ in range(33):
            self.assertIsInstance(ret, proto.ButtonRequest)
            mnemonic.append(self.client.debug.read_reset_word())
            self.client.debug.press_yes()
            resp = self.client.call_raw(proto.ButtonAck())

        self.assertIsInstance(resp, proto.Success)

        mnemonic = ' '.join(mnemonic)

        # Compare that second pass printed out the same mnemonic once again
        self.assertEqual(mnemonic, expected_mnemonic)

        # Check if device is properly initialized
        resp = self.client.call_raw(proto.Initialize())
        self.assertTrue(resp.pin_protection)
        self.assertTrue(resp.passphrase_protection)

        # Do passphrase-protected action, PassphraseRequest should be raised
        resp = self.client.call_raw(proto.Ping(passphrase_protection=True))
        self.assertIsInstance(resp, proto.PassphraseRequest)
        self.client.call_raw(proto.Cancel())

        # Do PIN-protected action, PinRequest should be raised
        resp = self.client.call_raw(proto.Ping(pin_protection=True))
        self.assertIsInstance(resp, proto.PinMatrixRequest)
        self.client.call_raw(proto.Cancel())

if __name__ == '__main__':
    unittest.main()
