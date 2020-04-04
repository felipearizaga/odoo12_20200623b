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
from odoo.exceptions import UserError


class ImportStandardizationLine(models.TransientModel):

    _name = 'import.standardization.line'
    _description = 'Import Standardization Line'

    folio = fields.Integer(string='Folio')
    record_number = fields.Integer(string='Number of records')
    file = fields.Binary(string='File')
    filename = fields.Char(string='File name')
    dwnld_file = fields.Binary(string='Download File')
    dwnld_filename = fields.Char(string='Download File name')

    def download_file(self):
        file_path = get_resource_path(
            'jt_budget_mgmt', 'static/file/import_line', 'import_standardization_line.xls')
        file = False
        with open(file_path, 'rb') as file_date:
            file = base64.b64encode(file_date.read())
        self.dwnld_filename = 'import_standardization_line.xls'
        self.dwnld_file = file
        return {
            'name': 'Download Sample File',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'import.standardization.line',
            'domain': [],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
        }

    def import_line(self):
        standardization = self.env['standardization'].browse(
            self._context.get('active_ids'))
        if standardization.folio != self.folio:
            raise UserError(_('Folio does not match.'))
        elif standardization.record_number != self.record_number:
            raise UserError(_('Number of records do not match.'))
        elif self.file:
            data = base64.decodestring(self.file)
            book = open_workbook(file_contents=data or b'')
            sheet = book.sheet_by_index(0)
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
            for rec in data:
                code = self.env['program.code'].search(
                    [('program_code', '=', rec.get('code_id'))], limit=1)
                budget = self.env['expenditure.budget'].search(
                    [('budget_name', '=', rec.get('budget_id'))], limit=1)
                key = int(rec.get('origin_id'))
                origin = self.env['resource.origin'].search(
                    [('key_origin', '=', str(key))], limit=1)
                stage = self.env['stage'].search(
                    [('stage_id.name', '=', rec.get('stage_id'))], limit=1)
                if not code:
                    raise UserError(_('Program code not found.'))
                elif not budget:
                    raise UserError(_('Budget name not found.'))
                elif not origin:
                    raise UserError(_('Origin key not found.'))
                elif not stage:
                    raise UserError(_('State name not found.'))
                else:
                    vals = {'folio': rec.get('folio'),
                            'code_id': code.id,
                            'budget_id': budget.id,
                            'amount': rec.get('amount'),
                            'origin_id': origin.id,
                            'quarter': rec.get('quarter'),
                            'stage_id': stage.id,
                            'reason': rec.get('reason'),
                            'standardization_id': standardization.id,
                            'imported': True,
                            }
                    standardization.line_ids.create(vals)
