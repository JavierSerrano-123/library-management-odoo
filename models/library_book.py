from odoo import models, fields, api
from datetime import date

class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Libro de Biblioteca'

    name = fields.Char(string="Título", required=True)
    author = fields.Char(string="Autor")
    isbn = fields.Char(string="ISBN")
    publication_date = fields.Date(string="Fecha de Publicación")
    available = fields.Boolean(string="Disponible", default=True)
    product_id = fields.Many2one(
    'product.product',
    string="Producto POS"
)

    years_since_publication = fields.Integer(
        string="Años desde publicación",
        compute="_compute_years_since_publication",
        store=True
    )

    @api.depends('publication_date')
    def _compute_years_since_publication(self):
        today = date.today()

        for book in self:

            if book.publication_date:
                book.years_since_publication = (
                    today.year - book.publication_date.year
                )

            else:
                book.years_since_publication = 0