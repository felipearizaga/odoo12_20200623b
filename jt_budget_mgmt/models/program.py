# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Program(models.Model):

    _name = 'program'
    _description = 'Program'
    _rec_name = 'code'

    code = fields.Char(string='Program code acronym')
    description = fields.Text(string='Description of the programmatic code')
    pp_unam = fields.Integer(string='Pp UNAM')
    desc = fields.Text(string='Description')

    _sql_constraints = [('pp_unam', 'unique(pp_unam)', 'The pp unam must be unique.')]

    # @api.depends('pp_unam', 'description')
    # def name_get(self):
    #     result = []
    #     if self.env.context.get('params').get('model') == 'program.code':
    #         for record in self:
    #             name = record.pp_unam
    #             result.append((record.id, name))
    #     return result

    @api.constrains('code')
    def _check_code(self):
        if self.code and not len(self.code) == 2:
            raise ValidationError(_('The code size must be two.'))

    @api.constrains('pp_unam')
    def _check_pp_unam(self):
        if self.pp_unam and not len(str(self.pp_unam)) == 2:
            raise ValidationError(_('The Pp UNAM size must be two.'))
