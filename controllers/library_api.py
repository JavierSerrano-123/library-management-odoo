from odoo import http
from odoo.http import request
import json


class LibraryAPI(http.Controller):

    @http.route(
        '/api/book',
        type='http',
        auth='public',
        methods=['GET'],
        csrf=False
    )
    def get_book(self, isbn=None, **kwargs):
        if not isbn:
            data = {'error': 'ISBN requerido'}
            return request.make_response(
                json.dumps(data),
                headers=[('Content-Type', 'application/json')]
            )

        book = request.env['library.book'].sudo().search([
            ('isbn', '=', isbn)
        ], limit=1)

        if not book:
            data = {'error': 'Libro no encontrado'}
            return request.make_response(
                json.dumps(data),
                headers=[('Content-Type', 'application/json')]
            )

        data = {
            'title': book.name,
            'author': book.author,
            'isbn': book.isbn,
            'available': book.available,
        }

        return request.make_response(
            json.dumps(data),
            headers=[('Content-Type', 'application/json')]
        )

    @http.route('/my/loans', type='http', auth='user', website=True)
    def my_loans(self, **kwargs):
        partner = request.env.user.partner_id
        loans = request.env['library.loan'].sudo().search([
            ('member_id', '=', partner.id)
        ])
        return request.render('library_management.portal_my_loans', {
            'loans': loans,
        })

    @http.route('/my/loans/renew/<int:loan_id>', type='http', auth='user', website=True)
    def renew_loan(self, loan_id, **kwargs):
        loan = request.env['library.loan'].sudo().browse(loan_id)
        if loan and loan.member_id == request.env.user.partner_id:
            if loan.state == 'ongoing':
                loan.action_renew()
        return request.redirect('/my/loans')