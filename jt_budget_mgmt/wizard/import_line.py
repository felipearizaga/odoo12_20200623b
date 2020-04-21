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
from odoo import models, fields, _
import base64
from odoo.modules.module import get_resource_path
from xlrd import open_workbook
from odoo.exceptions import UserError, ValidationError


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
        if budget.budget_name != self.budget_name:
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

                total_budget_amount = 0
                result_vals = []
                for rowx, row in enumerate(map(sheet.row, range(1, sheet.nrows)), 1):
                    result_dict = {}
                    counter = 0
                    for colx, cell in enumerate(row, 1):
                        result_dict.update({headers[counter]: cell.value})
                        counter += 1
                    if 'Importe 1a Asignacion' in result_dict:
                        total_budget_amount += float(
                            result_dict.get('Importe 1a Asignacion'))
                    result_vals.append(result_dict)
                print("---------> ", total_budget_amount, self.total_budget)
                if total_budget_amount != self.total_budget:
                    raise UserError(
                        _('The sum of the assigned amounts is not equal to the total of the budget'))

                if budget:
                    budget.write({
                        'budget_file': self.file,
                        'filename': self.filename,
                        'import_status': 'in_progress',
                        'total_rows': self.record_number,
                    })
            except UserError as e:
                raise UserError(e)
