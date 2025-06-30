from odoo import models, fields


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _order = "sequence,name"

    name = fields.Char(required=True)
    property_ids = fields.One2many("estate.property", "property_type_id", string="Estate Properties")
    sequence =fields.Integer('Sequence',default=1)
    _sql_constraints = [
        ('unique_property_type', 'UNIQUE(name)', 'The estate property type must be unique.'),
    ]