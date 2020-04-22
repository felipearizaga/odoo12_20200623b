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
import base64
import io
import re
from datetime import datetime
from xlrd import open_workbook
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class Adequacies(models.Model):

    _name = 'adequacies'
    _description = 'Adequacies'
    _rec_name = 'folio'

    def _get_count(self):
        for record in self:
            record.record_number = len(record.adequacies_lines_ids)
            record.imported_record_number = len(
                record.adequacies_lines_ids.filtered(lambda l: l.imported == True))

    def _compute_total_amounts(self):
        for adequacies in self:
            total_decreased = 0
            total_increased = 0
            for line in adequacies.adequacies_lines_ids:
                if line.line_type == 'decrease':
                    total_decreased += line.amount
                if line.line_type == 'increase':
                    total_increased += line.amount
            adequacies.total_decreased = float(total_decreased)
            adequacies.total_decreased = float(total_increased)

    total_decreased = fields.Float(string='Total Decreased Amount', compute="_compute_total_amounts")
    total_increased = fields.Float(string='Total Decreased Amount', compute="_compute_total_amounts")
    folio = fields.Integer(string='Folio', states={'accepted': [('readonly', True)]})
    budget_id = fields.Many2one('expenditure.budget', string='Budget', states={'accepted': [('readonly', True)]})
    from_date = fields.Date(string='Observations', states={'accepted': [('readonly', True)]})
    to_date = fields.Date(states={'accepted': [('readonly', True)]})
    reason = fields.Text(string='Reason for rejection')
    record_number = fields.Integer(
        string='Number of records', compute='_get_count')
    imported_record_number = fields.Integer(
        string='Number of records imported.', compute='_get_count')
    state = fields.Selection(
        [('draft', 'Draft'), ('confirmed', 'Confirmed'),
         ('accepted', 'Accepted'), ('rejected', 'Rejected')],
        default='draft', required=True, string='State')
    adequacies_lines_ids = fields.One2many(
        'adequacies.lines', 'adequacies_id', string='Adequacies Lines', states={'accepted': [('readonly', True)]})

    def _compute_failed_rows(self):
        for record in self:
            record.failed_rows = 0
            try:
                data = eval(record.failed_row_ids)
                record.failed_rows = len(data)
            except:
                pass

    def _compute_success_rows(self):
        for record in self:
            record.success_rows = 0
            try:
                data = eval(record.success_row_ids)
                record.success_rows = len(data)
            except:
                pass

    # Import related fields
    allow_upload = fields.Boolean(string='Allow Update XLS File?')
    budget_file = fields.Binary(string='Uploaded File')
    filename = fields.Char(string='File name')
    import_status = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Completed')], default='draft', copy=False)
    failed_row_file = fields.Binary(string='Failed Rows File')
    fialed_row_filename = fields.Char(
        string='File name', default="Failed_Rows.txt")
    failed_rows = fields.Integer(
        string='Failed Rows', compute="_compute_failed_rows")
    success_rows = fields.Integer(
        string='Success Rows', compute="_compute_success_rows")
    success_row_ids = fields.Text(
        string='Success Row Ids', default="[]", copy=False)
    failed_row_ids = fields.Text(
        string='Failed Row Ids', default="[]", copy=False)
    pointer_row = fields.Integer(
        string='Current Pointer Row', default=1, copy=False)
    total_rows = fields.Integer(string="Total Rows", copy=False)

    _sql_constraints = [
        ('folio', 'unique(folio)', 'The folio must be unique.')]

    @api.constrains('from_date', 'to_date')
    def _check_dates(self):
        if self.from_date and self.to_date:
            if self.from_date > self.to_date:
                raise ValidationError("Please select correct date")

    def import_lines(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'import.adequacies.line',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(False, 'form')],
            'target': 'new',
        }

    def validate_and_add_budget_line(self):
        if self.budget_file:
            budget_obj = self.env['expenditure.budget'].sudo(
            ).with_context(from_adequacies=True)

            # If user re-scan for failed rows
            re_scan_failed_rows_ids = eval(self.failed_row_ids)

            counter = 0
            cnt = 0
            pointer = self.pointer_row
            success_row_ids = []
            failed_row_ids = []

            data = base64.decodestring(self.budget_file)
            book = open_workbook(file_contents=data or b'')
            sheet = book.sheet_by_index(0)

            headers = []
            for rowx, row in enumerate(map(sheet.row, range(1)), 1):
                for colx, cell in enumerate(row, 1):
                    headers.append(cell.value)

            result_vals = []
            lines_to_iterate = self.pointer_row + 10000
            total_sheet_rows = sheet.nrows - 1
            if total_sheet_rows < lines_to_iterate:
                lines_to_iterate = total_sheet_rows + 1
            failed_row = ""

            conditional_list = range(self.pointer_row, lines_to_iterate)
            if self._context.get('re_scan_failed'):
                conditional_list = []
                for row in re_scan_failed_rows_ids:
                    conditional_list.append(row - 1)

            for rowx, row in enumerate(map(sheet.row, conditional_list), 1):
                p_code = ''
                cnt += 1
                pointer = self.pointer_row + cnt
                if self._context.get('re_scan_failed'):
                    pointer = conditional_list[rowx - 1] + 1

                result_dict = {}
                counter = 0
                for colx, cell in enumerate(row, 1):
                    result_dict.update({headers[counter]: cell.value})
                    counter += 1
                result_vals.append(result_dict)
                final_dict = {}

                # Validate year format
                year = budget_obj.validate_year(result_dict.get('AÑO', ''))
                if year:
                    p_code += year.name
                else:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Year Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validate Program(PR)
                program = budget_obj.validate_program(
                    result_dict.get('Programa', ''))
                if program:
                    final_dict['program_id'] = program.id
                    p_code += program.key_unam
                else:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Program(PR) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validate Sub-Program
                subprogram = budget_obj.validate_subprogram(
                    result_dict.get('SubPrograma', ''), program)
                if subprogram:
                    final_dict['sub_program_id'] = subprogram.id
                    p_code += subprogram.sub_program
                else:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid SubProgram(SP) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validate Dependency
                dependency = budget_obj.validate_dependency(
                    result_dict.get('Dependencia', ''))
                if dependency:
                    final_dict['dependency_id'] = dependency.id
                    p_code += dependency.dependency
                else:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Dependency(DEP) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validate Sub-Dependency
                subdependency = budget_obj.validate_subdependency(
                    result_dict.get('SubDependencia', ''), dependency)
                if subdependency:
                    final_dict['sub_dependency_id'] = subdependency.id
                    p_code += subdependency.sub_dependency
                else:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Sub Dependency(DEP) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validate Item
                item = budget_obj.validate_item(result_dict.get(
                    'Partida', ''), result_dict.get('Cve Ejercicio', ''))
                if item:
                    final_dict['item_id'] = item.id
                    p_code += item.item
                else:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Expense Item(PAR) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                if result_dict.get('Digito Verificador'):
                    p_code += str(result_dict.get('Digito Verificador')
                                  )[:1].replace('.', '').zfill(2)

                # Validate Origin Of Resource
                origin_resource = budget_obj.validate_origin_resource(
                    result_dict.get('Digito Centraliador', ''))
                if origin_resource:
                    final_dict['resource_origin_id'] = origin_resource.id
                    p_code += origin_resource.key_origin
                else:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Origin Of Resource(OR) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Institutional Activity Number
                institutional_activity = budget_obj.validate_institutional_activity(
                    result_dict.get('Actividad Institucional', ''))
                if institutional_activity:
                    final_dict['institutional_activity_id'] = institutional_activity.id
                    p_code += institutional_activity.number
                else:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Institutional Activity Number(AI) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Conversion Program SHCP
                shcp = budget_obj.validate_shcp(
                    result_dict.get('Conversion Programa', ''), program)
                if shcp:
                    final_dict['budget_program_conversion_id'] = shcp.id
                    p_code += shcp.shcp
                else:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Conversion Program SHCP(CONPP) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Federal Item
                conversion_item = budget_obj.validate_conversion_item(
                    result_dict.get('Conversion Partida', ''))
                if conversion_item:
                    final_dict['conversion_item_id'] = conversion_item.id
                    p_code += conversion_item.federal_part
                else:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid SHCP Games(CONPA) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Expense Type
                expense_type = budget_obj.validate_expense_type(
                    result_dict.get('Tipo de gasto', ''))
                if expense_type:
                    final_dict['expense_type_id'] = expense_type.id
                    p_code += expense_type.key_expenditure_type
                else:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Expense Type(TG) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Expense Type
                geo_location = budget_obj.validate_geo_location(
                    result_dict.get('Ubicación geografica', ''))
                if geo_location:
                    final_dict['location_id'] = geo_location.id
                    p_code += geo_location.state_key
                else:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Geographic Location (UG) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Wallet Key
                wallet_key = budget_obj.validate_wallet_key(
                    result_dict.get('Clave Cartera', ''))
                if wallet_key:
                    final_dict['portfolio_id'] = wallet_key.id
                    p_code += wallet_key.wallet_password
                else:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Wallet Key(CC) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Project Type
                project_type = budget_obj.validate_project_type(
                    result_dict.get('Tipo de Proyecto', ''), result_dict)
                if project_type:
                    final_dict['project_type_id'] = project_type.id
                    p_code += project_type.project_type_identifier
                    p_code += project_type.number
                else:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Project Type(TP) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Stage
                stage = budget_obj.validate_stage(
                    result_dict.get('Etapa', ''), project_type.project_id)
                if stage:
                    final_dict['stage_id'] = stage.id
                    p_code += stage.stage_identifier
                else:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Stage(E) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Agreement Type
                agreement_type = budget_obj.validate_agreement_type(result_dict.get(
                    'Tipo de Convenio', ''), project_type.project_id, result_dict.get('No. de Convenio', ''))
                if agreement_type:
                    final_dict['agreement_type_id'] = agreement_type.id
                    p_code += agreement_type.agreement_type
                    p_code += result_dict.get('No. de Convenio', '')
                else:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Agreement Type(TC) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Amount
                amount = budget_obj.validate_asigned_amount(
                    result_dict.get('amount', ''))
                if amount == "False":
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Amount Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Type
                typee = str(result_dict.get('line_type')
                            ).replace(' ', '').lower()
                if typee not in ['increase', 'decrease']:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Type Format\n"
                    failed_row_ids.append(pointer)
                    continue

                try:
                    program_code = False
                    if year and program and subprogram and dependency and subdependency and item and origin_resource and institutional_activity and shcp and conversion_item and expense_type and geo_location and wallet_key and project_type and stage and agreement_type:
                        program_code = self.env['program.code'].sudo().search([
                            ('year', '=', year.id),
                            ('program_id', '=', program.id),
                            ('sub_program_id', '=', subprogram.id),
                            ('dependency_id', '=', dependency.id),
                            ('sub_dependency_id', '=', subdependency.id),
                            ('item_id', '=', item.id),
                            ('resource_origin_id', '=', origin_resource.id),
                            ('institutional_activity_id', '=', institutional_activity.id),
                            ('budget_program_conversion_id', '=', shcp.id),
                            ('conversion_item_id', '=', conversion_item.id),
                            ('expense_type_id', '=', expense_type.id),
                            ('location_id', '=', geo_location.id),
                            ('portfolio_id', '=', wallet_key.id),
                            ('project_type_id', '=', project_type.id),
                            ('stage_id', '=', stage.id),
                            ('agreement_type_id', '=', agreement_type.id),
                            ('state', '=', 'validated'),
                        ], limit=1)

                        budget_line = self.env['expenditure.budget.line'].sudo().search([('program_code_id', '=', program_code.id), ('expenditure_budget_id', '=', self.budget_id.id)], limit=1)
                        if not budget_line:
                            1 / 0

                    if not program_code:
                        1 / 0
                    success_row_ids.append(pointer)

                    if self._context.get('re_scan_failed'):
                        failed_row_ids_eval_refill = eval(self.failed_row_ids)
                        failed_row_ids_eval_refill.remove(pointer)
                        self.write({'failed_row_ids': str(
                            failed_row_ids_eval_refill)})

                    line_vals = {
                        'program': program_code.id,
                        'line_type': typee,
                        'amount': amount,
                        'creation_type': 'imported',
                        'imported': True,
                    }
                    self.write({'adequacies_lines_ids': [(0, 0, line_vals)]})
                except:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Row Data Are Not Corrected or Validated Program Code Not Found!"
                    failed_row_ids.append(pointer)

            failed_row_ids_eval = eval(self.failed_row_ids)
            success_row_ids_eval = eval(self.success_row_ids)
            if len(success_row_ids) > 0:
                success_row_ids_eval.extend(success_row_ids)
            if len(failed_row_ids) > 0:
                failed_row_ids_eval.extend(failed_row_ids)

            vals = {
                'failed_row_ids': str(failed_row_ids_eval),
                'success_row_ids': str(success_row_ids_eval),
                'pointer_row': pointer,
            }

            failed_data = False
            if failed_row != "":
                content = ""
                if self.failed_row_file:
                    file_data = base64.b64decode(self.failed_row_file)
                    content += io.StringIO(file_data.decode("utf-8")).read()
                content += "\n"
                content += "...................Failed Rows " + \
                    str(datetime.today()) + "...............\n"
                content += str(failed_row)
                failed_data = base64.b64encode(content.encode('utf-8'))
                vals['failed_row_file'] = failed_data
            if pointer == sheet.nrows:
                vals['import_status'] = 'done'
            self.write(vals)

            if pointer == sheet.nrows and len(failed_row_ids_eval) > 0:
                self.write({'allow_upload': True})

            if self.failed_row_ids == 0 or len(failed_row_ids_eval) == 0:
                self.write({'allow_upload': False})

            if len(failed_row_ids) == 0:
                return{
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'All rows are imported successfully!',
                        'type': 'rainbow_man',
                    }
                }

    def validate_data(self):
        for adequacies in self:
            total_decreased = 0
            total_increased = 0
            counter_decreased = 0
            counter_increased = 0
            for line in adequacies.adequacies_lines_ids:
                if line.line_type == 'decrease':
                    total_decreased += line.amount
                    counter_decreased += 1
                if line.line_type == 'increase':
                    total_increased += line.amount
                    counter_increased += 1
            if total_decreased != total_increased:
                raise ValidationError("The total amount of the increases and the total amount of the decreases must be equal")

    def confirm(self):
        self.validate_data()
        self.state = 'confirmed'

    def accept(self):
        self.validate_data()
        for line in self.adequacies_lines_ids:
            if line.program:
                budget_line = self.env['expenditure.budget.line'].sudo().search([('program_code_id', '=', line.program.id), ('expenditure_budget_id', '=', self.budget_id.id)], limit=1)
                if budget_line:
                    amount = budget_line.assigned
                    if line.line_type == 'decrease':
                        final_amount = amount - line.amount
                        budget_line.write({'assigned': final_amount})
                    if line.line_type == 'increase':
                        final_amount = amount + line.amount
                        budget_line.write({'assigned': final_amount})
        self.state = 'accepted'

    def reject(self):
        self.state = 'rejected'


class AdequaciesLines(models.Model):

    _name = 'adequacies.lines'
    _description = 'Adequacies Lines'
    _rec_name = ''

    program = fields.Many2one('program.code', string='Program', domain="[('state', '=', 'validated')]")
    line_type = fields.Selection(
        [('increase', 'Increase'), ('decrease', 'Decrease')], string='Type')
    amount = fields.Float(string='Amount')
    creation_type = fields.Selection(
        [('manual', 'Manual'), ('imported', 'Imported')],
        string='Creation type')
    adequacies_id = fields.Many2one('adequacies', string='Adequacies', ondelete="cascade")
    imported = fields.Boolean(default=False)

    _sql_constraints = [
        ('uniq_program', 'unique(program)',
         'The Program code must be unique!'),
    ]
