from odoo import api, fields, models

class ResUser(models.Model):
    _inherit = "res.users"

    ali_test_field = fields.Char()
    property_ids = fields.One2many(
        'estate.property',
        'sale_person_id',
        string="Properties",
        domain="[('state','!=','sold')]"
    )