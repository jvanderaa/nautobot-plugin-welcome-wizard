"""Tests for Merlin Views."""

from django.contrib.auth import get_user_model
from django.urls import reverse

from nautobot.dcim.models import Manufacturer, DeviceType
from nautobot.utilities.testing.views import TestCase

from merlin.models.importer import DeviceTypeImport, ManufacturerImport

User = get_user_model()


class ManufacturerTestCase(TestCase):
    """Tests the ManufacturerImport Views."""

    def test_manufacturer_bulk_import_permission_denied(self):
        """Tests the ManufacturerImport Bulk Import View with no pemissions."""
        ManufacturerImport.objects.create(name="Acme", slug="acme")
        self.add_permissions("merlin.view_manufacturerimport")
        data = {"pk": [ManufacturerImport.objects.first().pk]}
        response = self.client.post(reverse("plugins:merlin:manufacturer_import"), data=data, follow=True)
        self.assertHttpStatus(response, 403)
        try:
            Manufacturer.objects.get(name="Acme")
            self.fail("Manufacturer object should not exist.")
        except Manufacturer.DoesNotExist:
            pass

    def test_manufacturer_bulk_import(self):
        """Tests the ManufacturerImport Bulk Import View with correct pemissions."""
        ManufacturerImport.objects.create(name="Acme", slug="acme")
        # Ensure we can add a new manufacturer
        self.add_permissions("dcim.add_manufacturer", "dcim.view_manufacturer", "merlin.view_manufacturerimport")

        data = {"pk": [ManufacturerImport.objects.first().pk]}
        response = self.client.post(reverse("plugins:merlin:manufacturer_import"), data=data, follow=True)
        self.assertHttpStatus(response, 200)
        manufacturer = Manufacturer.objects.get(name="Acme")
        self.assertIsNotNone(manufacturer)

    def test_manufacturer_bulk_import_get(self):
        ManufacturerImport.objects.create(name="Acme", slug="acme")
        self.add_permissions("dcim.add_manufacturer", "dcim.view_manufacturer", "merlin.view_manufacturerimport")

        lookup_key = ManufacturerImport.objects.first().pk
        response = self.client.get(f'{reverse("plugins:merlin:manufacturer_import")}?pk={lookup_key}')
        self.assertHttpStatus(response, 200)

    def test_manufacturer_bulk_import_get_empty(self):
        self.add_permissions("dcim.add_manufacturer", "dcim.view_manufacturer", "merlin.view_manufacturerimport")
        response = self.client.get(reverse("plugins:merlin:manufacturer_import"), follow=True)

        self.assertRedirects(response, reverse("plugins:merlin:manufacturer"), status_code=302)

    def test_manufacturer_list(self):
        """Tests the ManufacturerImport List View with correct pemissions."""
        self.add_permissions("merlin.view_manufacturerimport")
        response = self.client.get(reverse("plugins:merlin:manufacturer"))
        self.assertHttpStatus(response, 200)

    def test_manufacturer_list_permission_denied(self):
        """Tests the ManufacturerImport List View with no pemissions."""
        response = self.client.get(reverse("plugins:merlin:manufacturer"))
        self.assertHttpStatus(response, 403)


class DeviceTypeTestCase(TestCase):
    """Tests the DeviceTypeImport Views."""

    def test_devicetype_bulk_import_permission_denied(self):
        """Tests the DeviceTypeImport Bulk Import View with no pemissions."""
        manufacturer = ManufacturerImport.objects.create(name="Generic", slug="generic")
        Manufacturer.objects.create(name="Generic", slug="generic")
        DeviceTypeImport.objects.create(
            name="shelf-2he",
            filename="shelf-2he.yaml",
            manufacturer=manufacturer,
            device_type_data={
                "manufacturer": "Generic",
                "model": "shelf-2he",
                "slug": "shelf-2he",
                "u_height": 2,
                "full_depth": False,
            },
        )
        self.add_permissions("merlin.view_devicetypeimport")
        data = {"pk": [DeviceTypeImport.objects.first().pk]}
        response = self.client.post(reverse("plugins:merlin:devicetype_import"), data=data, follow=True)
        self.assertHttpStatus(response, 403)
        try:
            DeviceType.objects.get(model="shelf-2he")
            self.fail("DeviceType Object should not exist.")
        except DeviceType.DoesNotExist:
            pass

    def test_devicetype_bulk_import(self):
        """Tests the DeviceTypeImport Bulk Import View with correct pemissions."""
        manufacturer = ManufacturerImport.objects.create(name="Generic", slug="generic")
        Manufacturer.objects.create(name="Generic", slug="generic")
        DeviceTypeImport.objects.create(
            name="shelf-2he",
            filename="shelf-2he.yaml",
            manufacturer=manufacturer,
            device_type_data={
                "manufacturer": "Generic",
                "model": "shelf-2he",
                "slug": "shelf-2he",
                "u_height": 2,
                "full_depth": False,
            },
        )
        # Ensure we can add a new devicetype
        self.add_permissions(
            "dcim.add_manufacturer",
            "dcim.view_manufacturer",
            "dcim.add_devicetype",
            "dcim.view_devicetype",
            "merlin.view_devicetypeimport",
        )

        data = {"pk": [DeviceTypeImport.objects.first().pk]}
        response = self.client.post(reverse("plugins:merlin:devicetype_import"), data=data, follow=True)
        self.assertHttpStatus(response, 200)
        devicetype = DeviceType.objects.get(model="shelf-2he")
        self.assertIsNotNone(devicetype)

        # Test a duplicate import
        response = self.client.post(reverse("plugins:merlin:devicetype_import"), data=data, follow=True)
        self.assertHttpStatus(response, 200)

    def test_devicetype_list(self):
        """Tests the DeviceTypeImport List View with correct pemissions."""
        self.add_permissions("merlin.view_devicetypeimport")
        response = self.client.get(reverse("plugins:merlin:devicetype"))
        self.assertHttpStatus(response, 200)

    def test_devicetype_list_permission_denied(self):
        """Tests the DeviceTypeImport List View with no pemissions."""
        response = self.client.get(reverse("plugins:merlin:devicetype"))
        self.assertHttpStatus(response, 403)

    def test_devicetype_job_with_components(self):
        """Tests the DeviceTypeImport Bulk Import View with more data."""
        manufacturer = ManufacturerImport.objects.create(name="Juniper", slug="juniper")
        Manufacturer.objects.create(name="Juniper", slug="juniper")
        DeviceTypeImport.objects.create(
            name="MX80",
            filename="MX80.yaml",
            manufacturer=manufacturer,
            device_type_data={
                "manufacturer": "Juniper",
                "model": "MX80",
                "slug": "mx80",
                "is_full_depth": True,
                "u_height": 2,
                "interfaces": [
                    {"name": "fxp0", "type": "1000base-t", "mgmt_only": True},
                    {"name": "xe-0/0/0", "type": "10gbase-x-xfp"},
                    {"name": "xe-0/0/1", "type": "10gbase-x-xfp"},
                    {"name": "xe-0/0/2", "type": "10gbase-x-xfp"},
                    {"name": "xe-0/0/3", "type": "10gbase-x-xfp"},
                ],
                "power-ports": [
                    {
                        "name": "PEM0",
                        "type": "iec-60320-c14",
                        "maximum_draw": 500,
                        "allocated_draw": 365,
                    },
                    {
                        "name": "PEM1",
                        "type": "iec-60320-c14",
                        "maximum_draw": 500,
                        "allocated_draw": 365,
                    },
                ],
                "console-ports": [{"name": "Console", "type": "rj-45"}],
            },
        )
        # Ensure we can add a new devicetype
        self.add_permissions(
            "dcim.add_manufacturer",
            "dcim.view_manufacturer",
            "dcim.add_devicetype",
            "dcim.view_devicetype",
            "merlin.view_devicetypeimport",
        )

        data = {"pk": [DeviceTypeImport.objects.first().pk]}
        response = self.client.post(reverse("plugins:merlin:devicetype_import"), data=data, follow=True)
        self.assertHttpStatus(response, 200)

        devicetype = DeviceType.objects.get(model="MX80")
        self.assertIsNotNone(devicetype)


class MiddlewareTestCase(TestCase):
    """Tests the Middleware."""

    def test_middleware_missing_required(self):
        """Test middleware when dcim:devicetype is missing required fields."""
        self.add_permissions(
            "dcim.add_devicetype",
            "dcim.view_devicetype",
        )

        response = self.client.get(reverse("dcim:devicetype_add"))
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "You need to configure a <a href='/dcim/manufacturers/add/'>Manufacturer</a> before you create this item.",
        )
        self.assertHttpStatus(response, 200)

    def test_middleware_no_missing_required(self):
        """Test middleware when dcim:devicetype is not missing required fields."""
        Manufacturer.objects.create(name="Generic", slug="generic")
        self.add_permissions(
            "dcim.add_devicetype",
            "dcim.view_devicetype",
        )

        response = self.client.get(reverse("dcim:devicetype_add"))
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 0)
        self.assertHttpStatus(response, 200)

    def test_middleware_exceptions(self):
        """Ensure middleware exception does not break pages."""
        self.add_permissions(
            "circuits.add_circuit",
            "circuits.view_circuit",
        )

        response = self.client.get(reverse("circuits:circuit_add"))
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 2)
        self.assertHttpStatus(response, 200)