from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LibraryLoan(models.Model):
    _name = 'library.loan'
    _description = 'Préstamo de Libro'

    member_id = fields.Many2one(
        'res.partner',
        string="Socio",
        required=True,
        domain=[('is_library_member', '=', True)]
    )

    book_id = fields.Many2one(
        'library.book',
        string="Libro",
        required=True,
        domain=[('available', '=', True)]
    )

    loan_date = fields.Date(
        string="Fecha de Préstamo",
        default=fields.Date.today
    )

    return_date = fields.Date(
        string="Fecha de Devolución"
    )

    state = fields.Selection([
        ('ongoing', 'En curso'),
        ('returned', 'Devuelto'),
        ('late', 'Atrasado'),
    ], string="Estado", default='ongoing')

    @api.onchange('return_date')
    def _onchange_return_date(self):
        for loan in self:
            if loan.return_date and loan.return_date < loan.loan_date:
                loan.return_date = loan.loan_date

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            member = self.env['res.partner'].browse(vals.get('member_id'))
            book = self.env['library.book'].browse(vals.get('book_id'))

            if not book.available:
                raise ValidationError("El libro no está disponible para préstamo.")

            active_loans = self.search_count([
                ('member_id', '=', member.id),
                ('state', '=', 'ongoing')
            ])

            if active_loans >= 5:
                raise ValidationError("El socio ya tiene 5 préstamos activos.")

        records = super().create(vals_list)

        for record in records:
            record.book_id.available = False

        return records

    def action_mark_returned(self):
        for loan in self:
            loan.state = 'returned'
            loan.book_id.available = True

    def action_mark_late(self):
        for loan in self:
            if loan.state == 'ongoing':
                loan.state = 'late'

    def action_renew(self):
        for loan in self:
            if loan.state == 'ongoing':
                loan.loan_date = fields.Date.today()

    def cron_check_overdue_loans(self):
        loans = self.search([('state', '=', 'ongoing')])
        today = fields.Date.today()

        for loan in loans:
            if loan.loan_date:
                days = (today - loan.loan_date).days
                if days > 30:
                    loan.state = 'late'
                    if loan.member_id.email:
                        loan.message_post(
                            body=f"El préstamo del libro '{loan.book_id.name}' se encuentra vencido."
                        )

    @api.model
    def create_loan_from_pos(self, partner, product):
        book = self.env['library.book'].search([
            ('product_id', '=', product.id),
            ('available', '=', True)
        ], limit=1)

        if not book:
            return False

        member = self.env['res.partner'].search([
            ('id', '=', partner.id),
            ('is_library_member', '=', True)
        ], limit=1)

        if not member:
            return False

        self.create({
            'member_id': member.id,
            'book_id': book.id,
        })

        return True

    def unlink(self):
        for loan in self:
            if loan.book_id:
                loan.book_id.available = True
        return super().unlink()