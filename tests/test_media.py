import unittest

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from media import decrypt, encrypt


class MediaTests(unittest.TestCase):
    def setUp(self):
        self.key = AESGCM.generate_key(bit_length=256)
        self.data = b'video-test-data' * 4096
        self.payload = encrypt(self.data, self.key)

    def test_round_trip(self):
        self.assertEqual(decrypt(self.payload, self.key), self.data)

    def test_corrupted_payload_is_rejected(self):
        changed = self.payload[:-1] + bytes([self.payload[-1] ^ 1])
        with self.assertRaises(InvalidTag):
            decrypt(changed, self.key)

    def test_wrong_key_is_rejected(self):
        with self.assertRaises(InvalidTag):
            decrypt(self.payload, AESGCM.generate_key(bit_length=256))

    def test_invalid_envelope_is_rejected(self):
        for value in (b'', b'invalid', self.payload[:15]):
            with self.subTest(value=value), self.assertRaises(ValueError):
                decrypt(value, self.key)


if __name__ == '__main__':
    unittest.main()
