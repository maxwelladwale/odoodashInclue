# controllers/main.py
from odoo import http
from odoo.http import request
import json

class DashboardController(http.Controller):
    
    @http.route('/facilitation_dashboard/data', type='json', auth='user')
    def get_dashboard_data(self):
        # Get summary counts
        session_count = request.env['facilitation.session'].search_count([])
        internal_count = request.env['facilitation.session'].search_count([('facilitator_type', '=', 'internal')])
        external_count = request.env['facilitation.session'].search_count([('facilitator_type', '=', 'external')])
        participant_count = request.env['facilitation.participant'].search_count([])
        
        # Get sessions by month
        query = """
            SELECT 
                to_char(session_date, 'YYYY-MM') as month,
                COUNT(*) as count
            FROM 
                facilitation_session
            WHERE 
                session_date IS NOT NULL
            GROUP BY 
                to_char(session_date, 'YYYY-MM')
            ORDER BY 
                month
        """
        request.env.cr.execute(query)
        sessions_by_month = request.env.cr.dictfetchall()
        
        # Get response rates
        query = """
            SELECT 
                fs.name as session_name,
                COUNT(fp.id) as total_participants,
                COUNT(CASE WHEN fp.has_responded THEN 1 ELSE NULL END) as responded,
                COUNT(CASE WHEN fp.has_followed_up THEN 1 ELSE NULL END) as followed_up
            FROM 
                facilitation_session fs
            LEFT JOIN 
                facilitation_participant fp ON fp.session_id = fs.id
            GROUP BY 
                fs.id, fs.name
            ORDER BY 
                fs.session_date DESC
            LIMIT 10
        """
        request.env.cr.execute(query)
        response_rates = request.env.cr.dictfetchall()
        
        return {
            'summary': {
                'session_count': session_count,
                'internal_count': internal_count,
                'external_count': external_count,
                'participant_count': participant_count,
            },
            'sessions_by_month': sessions_by_month,
            'response_rates': response_rates
        }
    
    @http.route('/facilitation/qr/<string:code>', type='http', auth='public', website=True)
    def process_qr_code(self, code, **kw):
        session = request.env['facilitation.session'].sudo().search([('qr_code', '=', code)], limit=1)
        if not session:
            return request.render('facilitation_dashboard.qr_not_found', {})
        
        return request.render('facilitation_dashboard.participant_form', {
            'session': session,
        })
    
    @http.route('/facilitation/submit_response', type='http', auth='public', website=True)
    def submit_response(self, **post):
        # Process form submission
        participant_name = post.get('name')
        session_id = int(post.get('session_id'))
        response_type = post.get('response_type', 'pre')
        
        # Create participant if needed
        participant = request.env['facilitation.participant'].sudo().search([
            ('name', '=', participant_name),
            ('session_id', '=', session_id)
        ], limit=1)
        
        if not participant:
            participant = request.env['facilitation.participant'].sudo().create({
                'name': participant_name,
                'email': post.get('email'),
                'session_id': session_id,
                'team_lead': post.get('team_lead')
            })
        
        # Create survey response
        survey_id = None
        if response_type == 'pre':
            survey_id = participant.pre_survey_id.id
        elif response_type == 'post':
            survey_id = participant.post_survey_id.id
        elif response_type == 'followup':
            survey_id = participant.followup_survey_id.id
            
        if survey_id:
            # Create survey user input
            user_input = request.env['survey.user_input'].sudo().create({
                'survey_id': survey_id,
                'partner_id': participant.id,
                'facilitation_participant_id': participant.id,
                'email': participant.email,
            })
            
            # Create answers
            for i in range(1, 6):
                question_key = f'q{i}'
                answer = post.get(question_key)
                if answer:
                    # Find the question
                    question = request.env['survey.question'].sudo().search([
                        ('survey_id', '=', survey_id),
                        ('sequence', '=', i)
                    ], limit=1)
                    
                    if question:
                        request.env['survey.user_input.line'].sudo().create({
                            'user_input_id': user_input.id,
                            'question_id': question.id,
                            'value_text_box': answer,
                        })
            
            # Mark the survey as completed
            user_input.write({'state': 'done'})
        
        return request.render('facilitation_dashboard.response_thank_you', {})