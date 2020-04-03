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
from odoo import models, fields


class ProgramCode(models.Model):

    _name = 'program.code'
    _description = 'Program Code'
    _rec_name = 'program_code'

    year_id = fields.Many2one('year', string='Year')
    program_id = fields.Many2one('program', string='Program')
    description_id = fields.Many2one('program', string='Program description')
    sub_program_id = fields.Many2one('sub.program', string='Sub program')
    sub_program_name_id = fields.Many2one(
        'sub.program', string='Sub program name')
    unit_id = fields.Many2one('dependency', string='Unit')
    dependency_name_id = fields.Many2one(
        'dependency', string='Dependency name')
    sub_dependency_id = fields.Many2one(
        'sub.dependency', string='Sub dependency')
    sub_dependency_name_id = fields.Many2one(
        'sub.dependency', string='Sub dependency name')
    expenditure_item_id = fields.Many2one(
        'expenditure.item', string='Expenditure item')
    expenditure_item_name_id = fields.Many2one(
        'expenditure.item', string='Expenditure item name')
    check_digit_id = fields.Many2one('verifying.digit', string='Check digit')
    resource_origin_id = fields.Many2one(
        'resource.origin', string='Origin of the resource')
    resource_origin_name_id = fields.Many2one(
        'resource.origin', string='Resource origin name')
    institutional_activity_id = fields.Many2one(
        'institutional.activity', string='Institutional activity')
    institutional_activity_name_id = fields.Many2one(
        'institutional.activity', string='Institutional activity name')
    budget_program_conversion_id = fields.Many2one(
        'budget.program.conversion', string='Conversion of budgetary program')
    activity_id = fields.Many2one(
        'budget.program.conversion', string='Activity')
    conversion_item_id = fields.Many2one(
        'departure.conversion', string='Conversion with item')
    conversion_item_name_id = fields.Many2one(
        'departure.conversion', string='Conversion item name')
    expense_type_id = fields.Many2one(
        'expense.type', string='Expenditure type')
    expense_type_name_id = fields.Many2one(
        'expense.type', string='Expense type name')
    location_id = fields.Many2one(
        'geographic.location', string='Geographic location')
    state_id = fields.Many2one('geographic.location', string='State name')
    portfolio_id = fields.Many2one('key.wallet', string='Key portfolio')
    portfolio_name_id = fields.Many2one('key.wallet', string='Portfolio name')
    project_type_id = fields.Many2one('project.type', string='Project type')
    project_type_identifier_id = fields.Many2one(
        'project.type', string='Identifier')
    # project_number_id = fields.Many2one(
    #     'project.number', string='Project number')
    # identifier_id = fields.Many2one('project.type', string='Identifier')
    stage_id = fields.Many2one('stage', string='Stage')
    # identifier_id = fields.Many2one('project.type', string='Identifier')
    agreement_type_id = fields.Many2one(
        'agreement.type', string='Agreement type')
    # identifier_id = fields.Many2one('project.type', string='Identifier')
    # agreement_number_id = fields.Many2one(
    #     'agreement.number', string='Agreement number')
    # agreement_number_description_id = fields.Many2one('agreement.number', string='Agreement number description')
    program_code = fields.Char(string='Program code')
