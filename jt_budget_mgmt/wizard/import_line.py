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
import base64
import xlrd
from datetime import datetime
from odoo.modules.module import get_resource_path
from xlrd import open_workbook
from odoo.exceptions import UserError


class ImportLine(models.TransientModel):

    _name = 'import.line'
    _description = 'Import Line'

    budget_name = fields.Text(string='Name of the budget')
    total_budget = fields.Float(string='Total budget')
    record_number = fields.Integer(string='Number of records')
    file = fields.Binary(string='File')
    filename = fields.Char(string='File name')
    dwnld_file = fields.Binary(string='Download File')
    dwnld_filename = fields.Char(string='Download File name')

    @api.model
    def default_get(self, fields):
        res = super(ImportLine, self).default_get(fields)
        budget = self.env['expenditure.budget'].browse(
            self._context.get('active_id'))
        if budget and budget.name:
            res['budget_name'] = budget.name
        return res

    def download_file(self):
        file_path = get_resource_path(
            'jt_budget_mgmt', 'static/file/import_line', 'import_line.xlsx')
        file = False
        with open(file_path, 'rb') as file_date:
            file = base64.b64encode(file_date.read())
        self.dwnld_filename = 'import_line.xlsx'
        self.dwnld_file = file
        return {
            'name': 'Download',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'import.line',
            'domain': [],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
        }

    def import_line(self):
        budget = self.env['expenditure.budget'].browse(
            self._context.get('active_ids'))
        if budget.name != self.budget_name:
            raise UserError(_('Budget name does not match.'))
        elif self.file:
            try:
                data = base64.decodestring(self.file)
                book = open_workbook(file_contents=data or b'')
                sheet = book.sheet_by_index(0)

                total_rows = self.record_number + 1
                if sheet.nrows != total_rows:
                    raise UserError(
                        _('The number of imported lines is not equal to the number of records'))

                headers = []
                for rowx, row in enumerate(map(sheet.row, range(1)), 1):
                    for colx, cell in enumerate(row, 1):
                        headers.append(cell.value)

                field_headers = ['year', 'program', 'subprogram', 'dependency', 'subdependency', 'item', 'dv', 'origin_resource', 'ai', 'conversion_program', 'departure_conversion',
                                 'expense_type', 'location', 'portfolio', 'project_type', 'project_number', 'stage', 'agreement_type', 'agreement_number', 'exercise_type', 'assigned', 'authorized', 'start_date', 'end_date']

                total_budget_amount = 0
                result_vals = []
                for rowx, row in enumerate(map(sheet.row, range(1, sheet.nrows)), 1):
                    result_dict = {
                        'imported': True,
                        'state': 'draft',
                    }
                    counter = 0
                    for colx, cell in enumerate(row, 1):
                        value = cell.value
                        if field_headers[counter] in ['year', 'dv'] and type(value) is int or type(value) is float:
                            value = int(cell.value)

                        if field_headers[counter] == 'start_date':
                            try:
                                start_date = False
                                if type(value) is str:
                                    start_date = datetime.strptime(str(value), '%m/%d/%Y').date()
                                elif type(value) is int or type(value) is float:
                                    start_date = datetime(*xlrd.xldate_as_tuple(value, 0)).date()
                                if start_date:
                                    value = start_date
                                else:
                                    value = False
                            except:
                                pass

                        if field_headers[counter] == 'end_date':
                            try:
                                end_date = False
                                if type(value) is str:
                                    end_date = datetime.strptime(str(value), '%m/%d/%Y').date()
                                elif type(value) is int or type(value) is float:
                                    end_date = datetime(*xlrd.xldate_as_tuple(value, 0)).date()
                                if end_date:
                                    value = end_date
                                else:
                                    value = False
                            except:
                                pass

                        result_dict.update(
                            {field_headers[counter]: value})
                        counter += 1
                    if 'assigned' in result_dict:
                        total_budget_amount += float(
                            result_dict.get('assigned', 0))

                    # if self._context.get('reimport'):
                    #     has_code = self.env['expenditure.budget.line'].search([
                    #         ('state', '=', 'success'),
                    #         ('year', '=', str(result_dict.get('year'))),
                    #         ('program', '=', str(result_dict.get('program'))),
                    #         ('subprogram', '=', str(result_dict.get('subprogram'))),
                    #         ('dependency', '=', str(result_dict.get('dependency'))),
                    #         ('subdependency', '=', str(
                    #             result_dict.get('subdependency'))),
                    #         ('item', '=', str(result_dict.get('item'))),
                    #         ('dv', '=', str(result_dict.get('dv'))),
                    #         ('origin_resource', '=', str(
                    #             result_dict.get('origin_resource'))),
                    #         ('ai', '=', str(result_dict.get('ai'))),
                    #         ('conversion_program', '=', str(
                    #             result_dict.get('conversion_program'))),
                    #         ('departure_conversion', '=', str(
                    #             result_dict.get('departure_conversion'))),
                    #         ('expense_type', '=', str(
                    #             result_dict.get('expense_type'))),
                    #         ('location', '=', str(result_dict.get('location'))),
                    #         ('portfolio', '=', str(result_dict.get('portfolio'))),
                    #         ('project_type', '=', str(
                    #             result_dict.get('project_type'))),
                    #         ('project_number', '=', str(
                    #             result_dict.get('project_number'))),
                    #         ('stage', '=', str(result_dict.get('stage'))),
                    #         ('agreement_type', '=', str(
                    #             result_dict.get('agreement_type'))),
                    #         ('agreement_number', '=', str(result_dict.get('agreement_number')))], limit=1)
                    #     if not has_code:
                    #         result_vals.append((0, 0, result_dict))
                    # else:
                    #     result_vals.append((0, 0, result_dict))
                    result_vals.append((0, 0, result_dict))
                print("---------> ", total_budget_amount, self.total_budget)
                if total_budget_amount != self.total_budget:
                    raise UserError(
                        _('The sum of the assigned amounts is not equal to the total of the budget'))

                data = result_vals
                if budget:
                    if self._context.get('reimport'):
                        budget.line_ids.filtered(
                            lambda l: l.state != 'manual').unlink()
                        budget.success_line_ids.filtered(
                            lambda l: l.state != 'manual').unlink()
                        budget.write({'state': 'draft'})
                    budget.write({
                        'import_status': 'in_progress',
                        'line_ids': data,
                    })
            except UserError as e:
                raise UserError(e)
