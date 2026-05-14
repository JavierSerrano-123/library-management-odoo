from odoo import models, fields, api


class LibraryMember(models.Model):
    _inherit = 'res.partner'

    is_library_member = fields.Boolean(string="Socio de Biblioteca")
    member_code = fields.Char(string="Código de Socio", readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.is_library_member and not record.member_code:
                record.member_code = self.env['ir.sequence'].next_by_code('library.member.code')
        return records

    def write(self, vals):
        result = super().write(vals)
        if vals.get('is_library_member'):
            for record in self:
                if not record.member_code:
                    record.member_code = self.env['ir.sequence'].next_by_code('library.member.code')
        return result