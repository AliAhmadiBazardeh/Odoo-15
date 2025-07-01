from odoo import models, Command


class EstateProperty(models.Model):
    _inherit = 'estate.property'

    def action_sold(self):
        result = super().action_sold()

        for property in self:

            if not property.buyer_id:
                continue

            journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)

            fees = 100
            commission = property.selling_price * 0.06

            line_ids = [
                Command.create({
                    "name": "fees",
                    "quantity": 1,
                    "price_unit": fees,
                }),
                Command.create({
                    "name": "commission",
                    "quantity": 1,
                    "price_unit": commission,
                }),
            ]

            values = {
                'partner_id': property.buyer_id.id,
                'move_type': 'out_invoice',
                'journal_id': journal.id,
                'invoice_line_ids': line_ids,
            }

            invoice = self.env['account.move'].create(values)
            print('invoice created:', invoice)

        return result
