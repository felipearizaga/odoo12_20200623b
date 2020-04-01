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


class ProjectType(models.Model):

    _name = 'project.type'
    _description = 'Project Type'
    _rec_name = 'code'

    code = fields.Char(string='Acronym for program code')
    description = fields.Text(string='Description of program code')
    # project_type_id = fields.Many2one('', string='Project type identifier')
    # desc_id = fields.Many2one('', string='Description')

    # _sql_constraints = [('project_type_id', 'unique(project_type_id)',
    #                      'The project type must be unique.')]

    @api.constrains('code')
    def _check_code(self):
        if self.code and not len(self.code) == 2:
            raise ValidationError(_('The code size must be two.'))

    # @api.constrains('project_type_id')
    # def _check_project_type_id(self):
    #     if self.project_type_id and not len(str(self.project_type_id)) == 2:
    #         raise ValidationError(_('The project type size must be two.'))
