from odoo import models,fields

class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _order = "name"

    name = fields.Char(required=True)
    color = fields.Integer("Color")
    _sql_constraints = [
        ('unique_property_tag', 'UNIQUE(name)', 'The tag must be unique.'),
    ]