from odoo import models, fields


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _order = "sequence,name"

    name = fields.Char(required=True)
    property_ids = fields.One2many("estate.property", "property_type_id", string="Estate Properties")
    sequence =fields.Integer('Sequence',default=1)
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id')
    offer_count = fields.Integer(compute='_compute_offer_count')

    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)

    _sql_constraints = [
        ('unique_property_type', 'UNIQUE(name)', 'The estate property type must be unique.'),
    ]