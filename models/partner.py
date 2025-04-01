from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    is_facilitator = fields.Boolean('Is Facilitator')
    facilitator_type = fields.Selection([
        ('internal', 'Internal'),
        ('external', 'External')
    ], string='Facilitator Type')
    facilitation_session_ids = fields.One2many('facilitation.session', 'facilitator_id', string='Facilitation Sessions')
    facilitation_session_count = fields.Integer(compute='_compute_facilitation_count', string='Session Count')
    
    @api.depends('facilitation_session_ids')
    def _compute_facilitation_count(self):
        for partner in self:
            partner.facilitation_session_count = len(partner.facilitation_session_ids)