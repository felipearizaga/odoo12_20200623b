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


class SubProgram(models.Model):

    _name = 'sub.program'
    _description = 'Sub-Program'
    _rec_name = 'name'

    code = fields.Char(string='Programmatic code acronym')
    description = fields.Text(string='Programmatic code description')
    # pp_unam_id = fields.Many2one('', string='Pp UNAM')
    sub_program = fields.Integer(string='Sub program')
    dependency_id = fields.Many2one('dependency', string='Dependency')
    sub_dependency_id = fields.Many2one('sub.dependency', string='Sub dependency')
    name = fields.Text(string='Name sub program')

    @api.constrains('code')
    def _check_code(self):
        if self.code and not len(self.code) == 2:
            raise ValidationError(_('The code size must be two.'))

    @api.constrains('sub_program')
    def _check_sub_program(self):
        if self.sub_program and not len(str(self.sub_program)) == 2:
            raise ValidationError(_('The sub program size must be two.'))
