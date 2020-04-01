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


class Dependency(models.Model):

    _name = 'dependency'
    _description = 'Dependency'
    _rec_name = 'name'

    code = fields.Char(string='Program code acronym')
    description = fields.Text(string='Program code description')
    dependency = fields.Integer(string='Dependency')
    name = fields.Text(string='Name')

    _sql_constraints = [('dependency', 'unique(dependency)', 'The dependency must be unique.')]

    @api.constrains('code')
    def _check_code(self):
        if self.code and not len(self.code) == 3:
            raise ValidationError(_('The code size must be three.'))

    @api.constrains('dependency')
    def _check_dependency(self):
        if self.dependency and not len(str(self.dependency)) == 3:
            raise ValidationError(_('The dependency size must be three.'))
