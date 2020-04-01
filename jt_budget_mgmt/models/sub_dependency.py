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


class SubDependency(models.Model):

    _name = 'sub.dependency'
    _description = 'Sub-Dependency'
    _rec_name = 'name'

    code = fields.Char(string='Program code acronym')
    description = fields.Text(string='Program code description')
    dependency_id = fields.Many2one('dependency', string='Dependency')
    sub_dependency = fields.Integer(string='Sub dependency')
    name = fields.Text(string='Name sub dependency')

    @api.constrains('code')
    def _check_code(self):
        if self.code and not len(self.code) == 2:
            raise ValidationError(_('The code size must be two.'))

    @api.constrains('sub_dependency')
    def _check_sub_dependency(self):
        if self.sub_dependency and not len(str(self.sub_dependency)) == 2:
            raise ValidationError(_('The sub dependency size must be two.'))
