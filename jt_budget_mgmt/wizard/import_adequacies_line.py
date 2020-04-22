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


class ImportAdequaciesLine(models.TransientModel):

    _name = 'import.adequacies.line'
    _description = 'Import Adequacies Line'

    folio = fields.Integer(string='Folio')
    budget_id = fields.Many2one('expenditure.budget', string='Budget')
    record_number = fields.Integer(string='Number of records')
    file = fields.Binary(string='File')
    filename = fields.Char(string='File name')
    dwnld_file = fields.Binary(string='Download File')
    dwnld_filename = fields.Char(string='Download File name')

    def download_file(self):
        file_path = get_resource_path(
            'jt_budget_mgmt', 'static/file/import_line', 'import_adequacies_line.xls')
        file = False
        with open(file_path, 'rb') as file_date:
            file = base64.b64encode(file_date.read())
        self.dwnld_filename = 'import_adequacies_line.xls'
        self.dwnld_file = file
        return {
            'name': 'Download Sample File',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'import.adequacies.line',
            'domain': [],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
        }

    def import_line(self):
        self.ensure_one()
        adequacies = self.env['adequacies'].browse(
            self._context.get('active_id'))
        if adequacies.folio != self.folio:
            raise UserError(_('Folio does not match.'))
        elif self.file:
            try:
                data = base64.decodestring(self.file)
                book = open_workbook(file_contents=data or b'')
                sheet = book.sheet_by_index(0)

                total_rows = self.record_number + 1
                if sheet.nrows != total_rows:
                    raise UserError(_('Number of records do not match with file'))

                headers = []
                for rowx, row in enumerate(map(sheet.row, range(1)), 1):
                    for colx, cell in enumerate(row, 1):
                        headers.append(cell.value)

                result_vals = []
                for rowx, row in enumerate(map(sheet.row, range(1, sheet.nrows)), 1):
                    result_dict = {}
                    counter = 0
                    for colx, cell in enumerate(row, 1):
                        result_dict.update({headers[counter]: cell.value})
                        counter += 1
                    result_vals.append(result_dict)
                data = result_vals
                if adequacies:
                    adequacies.write({
                        'budget_file': self.file,
                        'filename': self.filename,
                        'import_status': 'in_progress',
                        'total_rows': self.record_number,
                    })

                # for rec in data:
                #     vals = {'program': rec.get('program'),
                #             'line_type': rec.get('line_type'),
                #             'amount': rec.get('amount'),
                #             'creation_type': rec.get('creation_type'),
                #             'adequacies_id': adequacies.id,
                #             'imported': True,
                #             }
                #     adequacies.adequacies_lines_ids.create(vals)
            except UserError as e:
                raise UserError(e)
