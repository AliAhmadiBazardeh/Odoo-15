from datetime import timedelta, date
from odoo.exceptions import UserError

from Tools.scripts import diff

from odoo import models, fields, api


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'

    price = fields.Float()
    status = fields.Selection(
        [('accepted', 'Accepted'),
                  ('refused', 'Refused')
         ],
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

    def action_confirm(self):
        for rec in self:
            if rec.status == 'accepted':
                raise UserError("This offer has already been confirmed.")

            # check any property_id has offer that status was accepted
            if any(offer.status == 'accepted' for offer in rec.property_id.offer_ids):
                raise UserError("Only one offer can be accepted for a given property!")

            rec.property_id.buyer_id = rec.partner_id
            rec.property_id.selling_price = rec.price
            rec.property_id.state = 'sold'
            rec.status = 'accepted'

        return True

    def action_refuse(self):
        for rec in self:
            if rec.status == 'refused':
                raise UserError("This offer has already been refused.")
            if rec.status == 'accepted':
                raise UserError("Accepted offers cannot be refused.")

            rec.status = 'refused'
        return True