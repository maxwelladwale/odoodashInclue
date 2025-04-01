{
    'name': 'Facilitation Dashboards',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'Custom dashboard for tracking facilitation activities',
    'description': """
        Custom dashboard to track:
        - Internal/External Facilitators
        - Card Deck Orders
        - Session Participants
        - Follow-up Responses
    """,
    'author': 'Your Company',
    'website': 'https://yourcompany.com',
    'depends': [
        'base', 
        'web', 
        'mail', 
        'survey', 
        'board', 
        'sale', 
        'contacts',
        'product'
    ],
    'data': [
        'data/ir_sequence_data.xml',
        'data/ir_cron_data.xml',
        'security/ir.model.access.csv',
        'views/partner_views.xml',
        'views/product_views.xml',
        'views/session_views.xml',
        'views/participant_views.xml',
        'views/dashboard_views.xml',
        'views/menu_views.xml',
    ],
    'qweb': [
        'static/src/xml/dashboard_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'facilitation_dashboard/static/src/js/dashboard.js',
            'facilitation_dashboard/static/src/scss/dashboard.scss',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}