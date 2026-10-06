from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from apps.clients.models import Client, ClientUser
from apps.projects.models import Project, Vendor, VendorUser, PurchaseOrder
from apps.documents.models import Document
from config.access_control import scoped_queryset

User = get_user_model()

class TenantScopeTests(TestCase):
    def setUp(self):
        self.client_a = Client.objects.create(client_code="A", name="Client A")
        self.client_b = Client.objects.create(client_code="B", name="Client B")
        self.user_a = User.objects.create_user(email="a@example.test", password="Safe-Test-Password-123")
        self.user_b = User.objects.create_user(email="b@example.test", password="Safe-Test-Password-123")
        requester = Group.objects.create(name="client_requester")
        self.user_a.groups.add(requester)
        self.user_b.groups.add(requester)
        ClientUser.objects.create(user=self.user_a, client=self.client_a, role="requester")
        ClientUser.objects.create(user=self.user_b, client=self.client_b, role="requester")
        self.project_a = Project.objects.create(client=self.client_a, project_code="PA", name="Project A")
        self.project_b = Project.objects.create(client=self.client_b, project_code="PB", name="Project B")

    def test_client_user_only_sees_own_tenant(self):
        self.assertEqual(list(scoped_queryset(self.user_a, Client.objects.all())), [self.client_a])
        self.assertEqual(list(scoped_queryset(self.user_a, Project.objects.all())), [self.project_a])

    def test_unassigned_user_fails_closed(self):
        user = User.objects.create_user(email="no-role@example.test", password="Safe-Test-Password-123")
        self.assertFalse(scoped_queryset(user, Project.objects.all()).exists())

    def test_global_admin_can_see_all_tenants(self):
        admin = User.objects.create_superuser(email="admin@example.test", password="Safe-Test-Password-123")
        self.assertEqual(scoped_queryset(admin, Client.objects.all()).count(), 2)

    def test_vendor_rep_only_sees_linked_vendor_and_purchase_order_projects(self):
        vendor_a = Vendor.objects.create(name="Vendor A")
        vendor_b = Vendor.objects.create(name="Vendor B")
        vendor_user = User.objects.create_user(email="vendor@example.test", password="Safe-Test-Password-123")
        vendor_user.groups.add(Group.objects.create(name="vendor_rep"))
        VendorUser.objects.create(user=vendor_user, vendor=vendor_a, role="representative")
        PurchaseOrder.objects.create(project=self.project_a, po_number="PO-A", vendor=vendor_a)
        PurchaseOrder.objects.create(project=self.project_b, po_number="PO-B", vendor=vendor_b)
        self.assertEqual(list(scoped_queryset(vendor_user, Vendor.objects.all())), [vendor_a])
        self.assertEqual(list(scoped_queryset(vendor_user, Project.objects.all())), [self.project_a])
        self.assertEqual(list(scoped_queryset(vendor_user, PurchaseOrder.objects.all()).values_list("po_number", flat=True)), ["PO-A"])

    def test_document_scope_is_tenant_owned_not_uploader_owned(self):
        # Uploading a file must never grant visibility to a different tenant's record.
        from django.core.files.uploadedfile import SimpleUploadedFile
        doc = Document.objects.create(title="A document", client=self.client_a,
            uploaded_by=self.user_b, file=SimpleUploadedFile("spec.pdf", b"test", content_type="application/pdf"))
        self.assertTrue(scoped_queryset(self.user_a, Document.objects.all()).filter(pk=doc.pk).exists())
        self.assertFalse(scoped_queryset(self.user_b, Document.objects.all()).filter(pk=doc.pk).exists())
