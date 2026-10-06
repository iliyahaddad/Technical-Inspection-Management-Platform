from django.utils.translation import gettext_lazy as _

ROLE_CHOICES = [
    ('sys_admin', _('System Administrator')),
    ('gm', _('Company General Manager')),
    ('tech_manager', _('Technical Manager')),
    ('quality_manager', _('Quality Manager')),
    ('project_manager', _('Project Manager')),
    ('coordinator', _('Inspection Coordinator')),
    ('inspector', _('Inspector')),
    ('reviewer', _('Independent Report Reviewer')),
    ('client_admin', _('Client Administrator')),
    ('client_requester', _('Client Requester')),
    ('client_approver', _('Client Approver')),
    ('vendor_rep', _('Vendor Representative')),
    ('finance_officer', _('Finance Officer')),
    ('auditor', _('Read-Only Auditor')),
]
