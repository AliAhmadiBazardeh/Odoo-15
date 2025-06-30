from odoo import models,fields,api
from datetime import timedelta, date
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero

class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Real Estate Property'
    _order = "id desc"

    name = fields.Char(required=True)
    description = fields.Text(compute="_compute_description")
    property_type_id = fields.Many2one('estate.property.type', string='Property Type')
    buyer_id = fields.Many2one('res.partner', string='Buyer',copy=False)
    sale_person_id = fields.Many2one('res.users', string='Sale Person',default=lambda self: self.env.user)
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    feature_ids = fields.Many2many('estate.property.feature',string="Features")
    best_offer = fields.Float(compute="_compute_offers")
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=lambda self: date.today() + timedelta(days=90))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    facades = fields.Integer()
    garden = fields.Boolean()
    garden_orientation = fields.Selection(
        [('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],
        string="Garden Orientation"
    )
    garden_area = fields.Float()
    living_area = fields.Float()
    total_area = fields.Float(compute="_compute_total_area")
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

    @api.depends("offer_ids")
    def _compute_offers(self):
        for record in self:
            prices = record.offer_ids.mapped("price")
            record.best_offer = max(prices) if prices else 0.0

    @api.depends("living_area","garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = None

    @api.constrains('selling_price')
    def _check_price(self):
        for rec in self:
            if float_is_zero(rec.selling_price, precision_digits=2):
                continue


            if float_compare(rec.selling_price, rec.expected_price * 0.9, precision_digits=2) < 0:
                raise ValidationError("Selling price  cannot be lower than 90% of the expected price.")

    def action_sold(self):
        for rec in self:
            if rec.state == 'canceled':
                raise UserError("Cancelled property cannot be sold.")
            rec.state = 'sold'

        return True

    def action_cancel(self):
        for rec in self:
            if rec.state == 'sold':
                raise UserError("Sold property cannot be canceled.")
            rec.state = 'canceled'
        return True

    _sql_constraints = [
        ('selling_price', 'CHECK(selling_price >= 0)', 'The Selling Price must be positive.'),
        ('expected_price', 'CHECK(expected_price >= 0 )', 'The Expected Price must be positive.'),
    ]

    @api.ondelete(at_uninstall=True)
    def _check_state(self):
        for rec in self:
            if rec.state == 'canceled' or rec.state == 'new':
                continue
            raise UserError("Only new and canceled state allowed to delete!")
