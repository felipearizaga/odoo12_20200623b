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


class VerifyingDigit(models.Model):

    _name = 'verifying.digit'
    _description = 'Verifying Digit'
    _rec_name = 'code'

    code = fields.Char(string='Sigla of the program code')
    description = fields.Text(string='Description of the program code')
    pp_unam = fields.Integer(string='Pp UNAM')
    sub_program = fields.Integer(string='Sub program')
    unit = fields.Integer(string='Unit')
    sub_unit = fields.Integer(string='Sub unit')
    item = fields.Integer(string='Item')
    verifying_digit = fields.Integer(string='Verifying digit')

    @api.constrains('code')
    def _check_code(self):
        if self.code and not len(self.code) == 2:
            raise ValidationError(_('The code size must be two.'))

    @api.constrains('pp_unam')
    def _check_pp_unam(self):
        if self.pp_unam and not len(str(self.pp_unam)) == 2:
            raise ValidationError(_('The Pp UNAM size must be two.'))

    @api.constrains('sub_program')
    def _check_sub_program(self):
        if self.sub_program and not len(str(self.sub_program)) == 2:
            raise ValidationError(_('The sub program size must be two.'))

    @api.constrains('unit')
    def _check_unit(self):
        if self.unit and not len(str(self.unit)) == 3:
            raise ValidationError(_('The unit size must be three.'))

    @api.constrains('sub_unit')
    def _check_sub_unit(self):
        if self.sub_unit and not len(str(self.sub_unit)) == 2:
            raise ValidationError(_('The sub unit size must be two.'))

    @api.constrains('item')
    def _check_item(self):
        if self.item and not len(str(self.item)) == 3:
            raise ValidationError(_('The item size must be three.'))

    @api.constrains('verifying_digit')
    def _check_verifying_digit(self):
        if self.verifying_digit and not len(str(self.verifying_digit)) == 2:
            raise ValidationError(_('The verifying digit size must be two.'))
