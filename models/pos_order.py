from odoo import models


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

                loan_model.create_loan_from_pos(
                    partner,
                    product
                )

        return result