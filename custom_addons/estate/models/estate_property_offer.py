from datetime import timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero

from odoo import models, fields, api


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _order = "price desc"

    price = fields.Float()
    status = fields.Selection(
        [('accepted', 'Accepted'),
         ('refused', 'Refused')
         ],
        copy=False,
    )
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    property_id = fields.Many2one('estate.property', string='Estate Property', required=True)
    property_type_id = fields.Many2one(
        related='property_id.property_type_id',
        store=True,
        readonly=True
    )
    validity = fields.Integer(default=3, string='Validity(days)')
    date_deadline = fields.Date(compute='_compute_date_deadline', inverse='_inverse_deadline')

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
            rec.property_id.state = 'offer_accepted'
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

    @api.model
    def create(self, vals):

        property_id = vals.get('property_id')

        if property_id:
            property = self.env['estate.property'].browse(property_id)

            new_price = vals.get('price')

            related_properties = self.env['estate.property.offer'].search([
                ('property_id', '=', property_id)
            ])
            if related_properties:
                max_price = max(related_properties.mapped('price'), default=0)

                if float_compare(new_price, max_price * 0.9, precision_digits=2) < 0:
                    raise ValidationError("New offer price cannot be lower than 90% of the existing offer price.")

            property.state = 'offer_received'

        return super().create(vals)
