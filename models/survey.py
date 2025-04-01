# models/survey.py
from odoo import models, fields, api

class SurveySurvey(models.Model):
    _inherit = 'survey.survey'
    
    is_facilitation_survey = fields.Boolean('Is Facilitation Survey')
    survey_type = fields.Selection([
        ('pre', 'Pre-Session'),
        ('post', 'Post-Session'),
        ('followup', 'Follow-up')
    ], string='Survey Type')

class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'
    
    facilitation_participant_id = fields.Many2one('facilitation.participant', string='Facilitation Participant')