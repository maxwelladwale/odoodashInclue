# models/participant.py
from odoo import models, fields, api

class FacilitationParticipant(models.Model):
    _name = 'facilitation.participant'
    _description = 'Session Participant'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char('Name', required=True, tracking=True)
    email = fields.Char('Email', tracking=True)
    phone = fields.Char('Phone')
    session_id = fields.Many2one('facilitation.session', string='Session', tracking=True)
    team_lead = fields.Char('Team Lead', tracking=True)
    
    # Pre-session survey responses
    pre_survey_id = fields.Many2one('survey.survey', string='Pre-Session Survey', 
                                   domain=[('is_facilitation_survey', '=', True), ('survey_type', '=', 'pre')])
    pre_user_input_id = fields.Many2one('survey.user_input', string='Pre-Session Responses')
    
    # Post-session survey responses
    post_survey_id = fields.Many2one('survey.survey', string='Post-Session Survey',
                                    domain=[('is_facilitation_survey', '=', True), ('survey_type', '=', 'post')])
    post_user_input_id = fields.Many2one('survey.user_input', string='Post-Session Responses')
    
    # Follow-up survey responses
    followup_survey_id = fields.Many2one('survey.survey', string='Follow-up Survey',
                                       domain=[('is_facilitation_survey', '=', True), ('survey_type', '=', 'followup')])
    followup_user_input_id = fields.Many2one('survey.user_input', string='Follow-up Responses')
    
    has_responded = fields.Boolean(compute='_compute_response_status', store=True, tracking=True)
    has_followed_up = fields.Boolean(compute='_compute_response_status', store=True, tracking=True)
    
    @api.depends('post_user_input_id', 'followup_user_input_id')
    def _compute_response_status(self):
        for record in self:
            record.has_responded = bool(record.post_user_input_id and record.post_user_input_id.state == 'done')
            record.has_followed_up = bool(record.followup_user_input_id and record.followup_user_input_id.state == 'done')
    
    def action_send_pre_survey(self):
        self.ensure_one()
        if not self.pre_survey_id or not self.email:
            return
            
        # Create survey response and send invitation
        self.pre_survey_id.with_context(default_partner_ids=self.id).action_send_survey()
        
    def action_send_post_survey(self):
        self.ensure_one()
        if not self.post_survey_id or not self.email:
            return
            
        # Create survey response and send invitation
        self.post_survey_id.with_context(default_partner_ids=self.id).action_send_survey()
    
    def action_send_followup_survey(self):
        self.ensure_one()
        if not self.followup_survey_id or not self.email:
            return
            
        # Create survey response and send invitation
        self.followup_survey_id.with_context(default_partner_ids=self.id).action_send_survey()