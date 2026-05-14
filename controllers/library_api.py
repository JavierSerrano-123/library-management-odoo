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

            data = {
                'error': 'ISBN requerido'
            }

            return request.make_response(
                json.dumps(data),
                headers=[('Content-Type', 'application/json')]
            )

        book = request.env['library.book'].sudo().search([
            ('isbn', '=', isbn)
        ], limit=1)

        if not book:

            data = {
                'error': 'Libro no encontrado'
            }

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