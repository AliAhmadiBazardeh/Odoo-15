from odoo import models, fields


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'

    name = fields.Char(required=True)

    _sql_constraints = [
        ('unique_property_type', 'UNIQUE(name)', 'The estate property type must be unique.'),
    ]