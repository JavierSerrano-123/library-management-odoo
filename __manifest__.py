{
    'name': 'Library Management',
    'version': '1.0',
    'summary': 'Gestión de biblioteca: socios, libros y préstamos',
    'description': 'Módulo para administrar socios, catálogo de libros y préstamos.',
    'author': 'Javier',
    'category': 'Library',
    'depends': ['base', 'contacts', 'portal', 'mail', 'point_of_sale'],
 'data': [
    'data/library_sequence.xml',
    'security/library_category.xml',
    'data/library_cron.xml',
    'security/library_groups.xml',
    'security/library_rules.xml',
    'security/ir.model.access.csv',

    'reports/report_library_loans.xml',
    'reports/report_library_loans_template.xml',

    'views/library_member_views.xml',
    'views/library_book_views.xml',
    'views/library_loan_views.xml',
],
'images': ['static/description/icon.png'],



    'installable': True,
    'application': True,
}
