from datetime import timedelta, date

from Tools.scripts import diff

from odoo import models, fields, api


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

    validity = fields.Integer(default=3, string='Validity(days)')
    date_deadline = fields.Date(compute='_compute_date_deadline',inverse='_inverse_deadline')

    @api.depends('validity')
    def _compute_date_deadline(self):
        for record in self:
            create = record.create_date or fields.Date.today()
            record.date_deadline = create + timedelta(days=record.validity)

    def _inverse_deadline(self):
        for record in self:
            create = record.create_date.date() or fields.Date.today()
            day_diff = record.date_deadline - create
            record.validity = day_diff.days
