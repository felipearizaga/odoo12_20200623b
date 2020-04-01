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


class ExpenseType(models.Model):

    _name = 'expense.type'
    _description = 'Expense Type'
    _rec_name = 'code'

    code = fields.Char(string='Abbreviation of the programmatic code')
    description = fields.Text(string='Description of the programmatic code')
    expenditure_key = fields.Integer(string='Expenditure key')
    designation = fields.Text(string='Designation')

    _sql_constraints = [('expenditure_key', 'unique(expenditure_key)',
                         'The expenditure key must be unique.')]

    @api.constrains('code')
    def _check_code(self):
        if self.code and not len(self.code) == 2:
            raise ValidationError(_('The code size must be two.'))

    @api.constrains('expenditure_key')
    def _check_expenditure_key(self):
        if self.expenditure_key and not len(str(self.expenditure_key)) == 2:
            raise ValidationError(_('The expenditure key size must be two.'))
