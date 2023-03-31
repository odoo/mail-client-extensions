# -*- coding: utf-8 -*-

import base64

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version

TEST_DATA_JPG = (
    b"/9j/4AAQSkZJRgABAQEBLAEsAAD//gATQ3JlYXRlZCB3aXRoIEdJTVD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQE"
    b"RMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wgARCAAQAB"
    b"ADAREAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAX/xAAWAQEBAQAAAAAAAAAAAAAAAAAABAX/2gAMAwEAAhADEAAAAYdm0AP/xAAUEAEAAAAAAAAAAAAAAAA"
    b"AAAAg/9oACAEBAAEFAh//xAAUEQEAAAAAAAAAAAAAAAAAAAAg/9oACAEDAQE/AR//xAAUEQEAAAAAAAAAAAAAAAAAAAAg/9oACAECAQE/AR//xAAUEAEAAAAAAAAA"
    b"AAAAAAAAAAAg/9oACAEBAAY/Ah//xAAUEAEAAAAAAAAAAAAAAAAAAAAg/9oACAEBAAE/IR//2gAMAwEAAgADAAAAECSf/8QAFBEBAAAAAAAAAAAAAAAAAAAAIP/aA"
    b"AgBAwEBPxAf/8QAFBEBAAAAAAAAAAAAAAAAAAAAIP/aAAgBAgEBPxAf/8QAFBABAAAAAAAAAAAAAAAAAAAAIP/aAAgBAQABPxAf/9k="
)
TEST_DATA_TXT = base64.b64encode("Simple txt".encode("utf-8"))
TEST_DATA_HTML = base64.b64encode("<html></html>".encode("utf-8"))
TESTS = (
    ("file.gif", "text/plain", TEST_DATA_TXT, "txt"),
    ("file.txt", "text/plain", TEST_DATA_TXT, "txt"),
    ("file", "text/plain", TEST_DATA_TXT, "txt"),
    ("file.jpg", "image/jpeg", TEST_DATA_JPG, "jpg"),
    ("file.JPG", "image/jpeg", TEST_DATA_JPG, "jpg"),
    ("file.jpeg", "image/jpeg", TEST_DATA_JPG, "jpeg"),
    # Use extension from file name as it is compatible with mimetype
    ("file.JPEG", "image/jpeg", TEST_DATA_JPG, "jpeg"),
    ("file.txt", "image/jpeg", TEST_DATA_JPG, "jpg"),
    ("file", "image/jpeg", TEST_DATA_JPG, "jpg"),
    ("file", "text/html", TEST_DATA_JPG, "html"),
    # Use extension from file name as it is compatible with mimetype
    ("file.htm", "text/html", TEST_DATA_JPG, "htm"),
    ("file.htmL", "text/html", TEST_DATA_JPG, "html"),
)


@change_version("saas~16.3")
class TestAddFileExtensionField(UpgradeCase):
    """Test the initialization of the new field extension (based on mimetype and name)."""

    def prepare(self):
        Document = self.env["documents.document"]
        folder_id = self.env["documents.folder"].create({"name": "Test folder"}).id

        return {
            test_idx: Document.create(
                {
                    "datas": datas,
                    "folder_id": folder_id,
                    "mimetype": mimetype,
                    "name": name,
                }
            ).id
            for test_idx, (name, mimetype, datas, _) in enumerate(TESTS)
        }

    def check(self, init):
        Document = self.env["documents.document"]
        for test_idx, (name, mimetype, datas, expected_extension) in enumerate(TESTS):
            document = Document.browse(init[str(test_idx)])
            self.assertEqual(document.name, name)
            self.assertEqual(document.mimetype, mimetype)
            self.assertEqual(document.datas, datas)
            self.assertEqual(document.file_extension, expected_extension)
