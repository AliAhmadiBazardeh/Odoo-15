from odoo import models, fields


class EstatePropertyFeature(models.Model):
    _name = 'estate.property.feature'

    name = fields.Char(string='Name')
    property_ids = fields.Many2many('estate.property',string='Properties')