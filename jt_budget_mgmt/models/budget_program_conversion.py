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
from odoo.exceptions import ValidationError, UserError
import re


class BudgetProgramConversion(models.Model):

    _name = 'budget.program.conversion'
    _description = 'Budget Program Conversion'
    _rec_name = 'code'

    code = fields.Char(string='Abbreviation of the programmatic code')
    description = fields.Text(string='Description of the programmatic code')
    # pp_unam_id = fields.Many2one('', string='Pp UNAM')
    desc = fields.Text(string='Description')
    pp_shcp = fields.Char(string='PP SHCP')
    activity = fields.Text(string='Activity')

    _sql_constraints = [('pp_shcp', 'unique(pp_shcp)',
                         'The pp_shcp must be unique.')]

    @api.constrains('code')
    def _check_code(self):
        if self.code and not len(self.code) == 5:
            raise ValidationError(_('The code size must be five.'))

    @api.constrains('pp_shcp')
    def _check_pp_shcp(self):
        if self.pp_shcp and not len(self.pp_shcp) == 4:
            raise ValidationError(_('The pp shcp size must be four.'))
        if self.pp_shcp and len(self.pp_shcp) == 4:
            if not (re.match("[A-Z]{1}\d{3}", self.pp_shcp.upper())):
                raise UserError(
                    _('Please enter first digit as letter and last 3 digits as numbers.'))
