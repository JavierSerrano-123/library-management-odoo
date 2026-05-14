from odoo import models
from odoo.exceptions import UserError


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def action_pos_order_paid(self):

        result = super().action_pos_order_paid()

        loan_model = self.env['library.loan']

        for order in self:

            partner = order.partner_id

            if not partner:
                continue

            for line in order.lines:

                product = line.product_id

                book = self.env['library.book'].search([
                    ('product_id', '=', product.id),
                ], limit=1)

                if not book:
                    continue

                if not book.available:
                    raise UserError(
                        f"El libro '{book.name}' no está disponible para préstamo."
                    )

                active_loans = loan_model.search_count([
                    ('member_id', '=', partner.id),
                    ('state', '=', 'ongoing')
                ])

                if active_loans >= 5:
                    raise UserError(
                        f"El socio '{partner.name}' ya tiene 5 préstamos activos."
                    )

                loan_model.create_loan_from_pos(partner, product)

        return result