from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    is_card_deck = fields.Boolean('Is Card Deck')
    card_deck_type = fields.Selection([
        ('gift', 'Gift Cards'),
        ('followup', 'Follow-up Cards'),
        ('participant', 'Participant Card Deck'),
        ('facilitator', 'Facilitator Card Deck')
    ], string='Card Deck Type')