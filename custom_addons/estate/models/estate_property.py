from odoo import models,fields,api
from datetime import timedelta, date

from odoo.tools.populate import compute


class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Real Estate Property'

    name = fields.Char(required=True)
    description = fields.Text(compute="_compute_description")
    @api.depends("name", "total_area", "date_availability", "offer_ids")
    def _compute_description(self):
        for record in self:
            name = record.name or "Unknown"
            area = record.total_area or 0
            available_date = record.date_availability.strftime(
                '%Y-%m-%d') if record.date_availability else "an unknown date"
            offer_count = len(record.offer_ids)
            offer_word = "offer" if offer_count == 1 else "offers"

            record.description = (
                f"'{name}' with an area of {area} sqm will be available from {available_date}. "
                f"So far, {offer_count} {offer_word} have been submitted for this house."
            )

    property_type_id = fields.Many2one('estate.property.type', string='Property Type')
    buyer_id = fields.Many2one('res.partner', string='Buyer',copy=False)
    sale_person_id = fields.Many2one('res.users', string='Sale Person',default=lambda self: self.env.user)
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    best_offer = fields.Float(compute="_compute_offers")
    @api.depends("offer_ids")
    def _compute_offers(self):
        for record in self:
            prices = record.offer_ids.mapped("price")
            record.best_offer = max(prices) if prices else 0.0

    postcode = fields.Char()
    date_availability = fields.Date(
        copy=False,
        default=lambda self: date.today() + timedelta(days=90)
    )
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)

    facades = fields.Integer()
    garden = fields.Boolean()
    garden_orientation = fields.Selection(
        [('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],
        string="Garden Orientation"
    )

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = None

    garden_area = fields.Float()
    living_area = fields.Float()
    total_area = fields.Float(compute="_compute_total_area")
    @api.depends("living_area","garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    active = fields.Boolean(default=True)
    state = fields.Selection(
        [
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('canceled', 'Canceled')
        ],
        required=True,
        default='new',
        copy=False
    )