from odoo import models, fields, api
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta

class FacilitationSession(models.Model):
    _name = 'facilitation.session'
    _description = 'Facilitation Session'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'session_date desc, id desc'
    
    name = fields.Char('Session Name', required=True, tracking=True)
    facilitator_id = fields.Many2one('res.partner', string='Facilitator', 
                                     domain=[('is_facilitator', '=', True)], tracking=True)
    facilitator_type = fields.Selection(related='facilitator_id.facilitator_type', store=True, readonly=True)
    
    session_date = fields.Date('Session Date', tracking=True)
    company_name = fields.Char('Company Name', tracking=True)
    language = fields.Char('Language')
    country_id = fields.Many2one('res.country', string='Country')
    participant_count = fields.Integer('Number of Participants', tracking=True)
    team_lead = fields.Char('Team Lead Name')
    
    # Link to sales
    sale_order_id = fields.Many2one('sale.order', string='Sales Order')
    invoice_status = fields.Selection(related='sale_order_id.invoice_status', string='Invoice Status', readonly=True)
    
    # Card deck information
    card_product_ids = fields.Many2many('product.product', string='Card Decks',
                                      domain=[('is_card_deck', '=', True)])
    
    session_type = fields.Selection([
        ('journey', 'iN-Clue Journey'),
        ('leadership', 'Leadership Workshop'),
        ('coaching', 'Coaching Session')
    ], string='Session Type', tracking=True)
    
    qr_code = fields.Char('QR Code Reference', readonly=True, copy=False)
    participant_ids = fields.One2many('facilitation.participant', 'session_id', string='Participants')
    
    # Dashboard metrics
    response_rate = fields.Float(compute='_compute_metrics', string='Response Rate', store=True)
    follow_up_completion = fields.Float(compute='_compute_metrics', string='Follow-up Completion', store=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    @api.model
    def create(self, vals):
        # Generate a unique QR code
        vals['qr_code'] = self.env['ir.sequence'].next_by_code('facilitation.session.qr')
        return super(FacilitationSession, self).create(vals)
    
    @api.depends('participant_ids', 'participant_ids.has_responded', 'participant_ids.has_followed_up')
    def _compute_metrics(self):
        for record in self:
            total_participants = len(record.participant_ids)
            if total_participants > 0:
                responded = len(record.participant_ids.filtered(lambda p: p.has_responded))
                followed_up = len(record.participant_ids.filtered(lambda p: p.has_followed_up))
                record.response_rate = (responded / total_participants) * 100
                record.follow_up_completion = (followed_up / total_participants) * 100
            else:
                record.response_rate = 0
                record.follow_up_completion = 0
    
    def action_confirm(self):
        self.write({'state': 'confirmed'})
    
    def action_complete(self):
        self.write({'state': 'completed'})
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})
    
    def action_reset_to_draft(self):
        self.write({'state': 'draft'})
    
    def _send_followup_reminders(self):
        # Find sessions that are 6 months to 1 year old with participants missing follow-ups
        today = fields.Date.today()
        six_months_ago = today - relativedelta(months=6)
        one_year_ago = today - relativedelta(years=1)
        
        sessions = self.search([
            ('session_date', '>=', one_year_ago),
            ('session_date', '<=', six_months_ago),
            ('state', '=', 'completed')
        ])
        
        template = self.env.ref('facilitation_dashboard.email_template_followup_reminder', False)
        if not template:
            return
            
        for session in sessions:
            for participant in session.participant_ids:
                if not participant.has_followed_up and participant.email:
                    template.send_mail(participant.id, force_send=True)