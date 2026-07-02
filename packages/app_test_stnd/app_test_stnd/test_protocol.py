import unittest
from generated_protocol import GetStatus, StatusResponse, parse_response, GETSTATUS_CODE


class TestProtocol(unittest.TestCase):
    def test_serialize_getstatus(self):
        cmd = GetStatus()  # без параметров
        data = cmd.to_bytes()
        self.assertEqual(data, b'')   # пустой запрос

    def test_parse_status_response(self):
        # Ответ: powered = True (1)
        data = b'\x01'   # bool упаковывается как 0x01
        resp = parse_response(201, data)  # код 201 = StatusResponse
        self.assertTrue(resp.powered)

        # Ответ: powered = False (0)
        data = b'\x00'
        resp = parse_response(201, data)
        self.assertFalse(resp.powered)


if __name__ == '__main__':
    unittest.main()
