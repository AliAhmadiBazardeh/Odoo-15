from odoo import models,fields


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'

    price = fields.Float()
    status = fields.Selection(
        [('accepted', 'Accepted'),
                  ('refused', 'Refused')
         ],
    required = True,
    copy = False,
    )
    partner_id = fields.Many2one('res.partner',string='Partner',required=True)
    property_id = fields.Many2one('estate.property',string='Estate Property',required=True)
