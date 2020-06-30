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
    _rec_name = 'display_name'

    dependency = fields.Char(string='Dependency', size=3)
    description = fields.Text(string='Dependency description')

    _sql_constraints = [('dependency', 'unique(dependency)', 'The dependency must be unique.')]

    def _compute_display_name(self):
        for record in self:
            if 'from_move' in self._context:
                name = ''
                if record.dependency:
                    name += str(record.dependency)
                if record.description:
                    name += ' '
                    name += str(record.description)
                record.display_name = name
            else:
                record.display_name = record.dependency

    display_name = fields.Char(string='Dependency Name', compute="_compute_display_name")

    @api.constrains('dependency')
    def _check_dependency(self):
        if not str(self.dependency).isnumeric():
            raise ValidationError(_('The Dependency must be numeric value'))

    def fill_zero(self, code):
        return str(code).zfill(3)

    @api.model
    def create(self, vals):
        if vals.get('dependency') and len(vals.get('dependency')) != 3:
            vals['dependency'] = self.fill_zero(vals.get('dependency'))
        return super(Dependency, self).create(vals)

    def write(self, vals):
        if vals.get('dependency') and len(vals.get('dependency')) != 3:
            vals['dependency'] = self.fill_zero(vals.get('dependency'))
        return super(Dependency, self).write(vals)

    def unlink(self):
        for dependency in self:
            program_code = self.env['program.code'].search([('dependency_id', '=', dependency.id)], limit=1)
            if program_code:
                raise ValidationError(_('You can not delete dependency which are mapped with program code!'))
            sub_dependancy = self.env['sub.dependency'].search([('dependency_id', '=', dependency.id)], limit=1)
            if sub_dependancy:
                raise ValidationError(_('You can not delete Dependency which are mapped with Sub Dependancy!'))
        return super(Dependency, self).unlink()

    def validate_dependency(self, dependency_string):
        if len(str(dependency_string)) > 2:
            dependency_str = str(dependency_string).zfill(3)
            if dependency_str.isnumeric():
                dependency = self.search(
                    [('dependency', '=', dependency_str)], limit=1)
                if dependency:
                    return dependency
        return False
