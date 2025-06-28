from odoo import models,fields

class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'

    name = fields.Char(required=True)

    _sql_constraints = [
        ('unique_property_tag', 'UNIQUE(name)', 'The tag must be unique.'),
    ]