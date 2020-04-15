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


class ProjectProject(models.Model):

    _inherit = 'project.project'

    project_type_identifier = fields.Char(string='Project Type Identifier', size=2)
    number = fields.Char(string='Number', size=6)
    stage_identifier = fields.Char(string="Stage Identifier", size=2)
    desc_stage = fields.Text(string='Description Stage')
    agreement_type = fields.Char(string='Agreement Type', size=2)
    name_agreement = fields.Text(string='Name Agreement')
    number_agreement = fields.Char(string='Number Agreement', size=6)

    _sql_constraints = [('uniq_project_type_identifier', 'unique(project_type_identifier)',
                         'The Project Type Identifier must be unique!')]

    _sql_constraints = [('uniq_number_project', 'unique(number)',
                         'The number must be unique!')]

    _sql_constraints = [('uniq_number_agreement', 'unique(number_agreement)',
                         'The Number Agreement must be unique!')]

    @api.constrains('project_type_identifier')
    def _check_project_type_identifier(self):
        if not str(self.project_type_identifier).isnumeric():
            raise ValidationError(_('The Project Type Identifier must be numeric value'))

    @api.constrains('number')
    def _check_number(self):
        if not str(self.number).isnumeric():
            raise ValidationError(_('The Number must be numeric value'))

    @api.constrains('stage_identifier')
    def _check_stage_identifier(self):
        if not str(self.stage_identifier).isnumeric():
            raise ValidationError(_('The Stage Identifier must be numeric value'))

    @api.constrains('agreement_type')
    def _check_agreement_type(self):
        if not str(self.agreement_type).isnumeric():
            raise ValidationError(_('The Agreement Type must be numeric value'))

    @api.constrains('number_agreement')
    def _check_number_agreement(self):
        if not str(self.number_agreement).isnumeric():
            raise ValidationError(_('The Number Agreement must be numeric value'))
