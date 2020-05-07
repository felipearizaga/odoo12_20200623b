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
from datetime import datetime
from xlrd import open_workbook
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Adequacies(models.Model):

    _name = 'adequacies'
    _description = 'Adequacies'
    _rec_name = 'folio'

    # Function calculate total imported and manufal rows
    def _get_count(self):
        for record in self:
            record.record_number = len(record.adequacies_lines_ids)
            record.imported_record_number = len(
                record.adequacies_lines_ids.filtered(lambda l: l.imported == True))

    # Function to calculate total increase amount and total decrease amount
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

    # Total increased and decreased fields
    total_decreased = fields.Float(
        string='Total Decreased Amount', compute="_compute_total_amounts")
    total_increased = fields.Float(
        string='Total Decreased Amount', compute="_compute_total_amounts")

    folio = fields.Char(string='Folio', states={
        'accepted': [('readonly', True)], 'rejected': [('readonly', True)]})
    budget_id = fields.Many2one('expenditure.budget', string='Budget', states={
                                'accepted': [('readonly', True)], 'rejected': [('readonly', True)]})
    reason = fields.Text(string='Reason for rejection')

    # Total imported or manual rows
    record_number = fields.Integer(
        string='Number of records', compute='_get_count')
    imported_record_number = fields.Integer(
        string='Number of records imported.', compute='_get_count')

    state = fields.Selection(
        [('draft', 'Draft'), ('confirmed', 'Confirmed'),
         ('accepted', 'Accepted'), ('rejected', 'Rejected')],
        default='draft', required=True, string='State')

    observation = fields.Text(string='Observation')
    adaptation_type = fields.Selection(
        [('compensated', 'Compensated Adjustments'), ('liquid', 'Liquid Adjustments')], default='compensated', states={
            'accepted': [('readonly', True)], 'rejected': [('readonly', True)]})
    adequacies_lines_ids = fields.One2many(
        'adequacies.lines', 'adequacies_id', string='Adequacies Lines', states={'accepted': [('readonly', True)], 'rejected': [('readonly', True)]})

    _sql_constraints = [
        ('folio_uniq', 'unique(folio)', 'The folio must be unique.')]

    @api.constrains('folio')
    def _check_folio(self):
        if not str(self.folio).isnumeric():
            raise ValidationError('Folio Must be numeric value!')

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

    # Import process related fields
    allow_upload = fields.Boolean(string='Allow Update XLS File?')
    budget_file = fields.Binary(string='Uploaded File', states={'accepted': [
                                ('readonly', True)], 'rejected': [('readonly', True)]})
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
            # Objects
            year_obj = self.env['year.configuration']
            program_obj = self.env['program']
            subprogram_obj = self.env['sub.program']
            dependancy_obj = self.env['dependency']
            subdependancy_obj = self.env['sub.dependency']
            item_obj = self.env['expenditure.item']
            origin_obj = self.env['resource.origin']
            activity_obj = self.env['institutional.activity']
            shcp_obj = self.env['budget.program.conversion']
            dpc_obj = self.env['departure.conversion']
            expense_type_obj = self.env['expense.type']
            location_obj = self.env['geographic.location']
            wallet_obj = self.env['key.wallet']
            project_type_obj = self.env['project.type']
            stage_obj = self.env['stage']
            agreement_type_obj = self.env['agreement.type']

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

                # Validate year format
                year = year_obj.validate_year(result_dict.get('AÑO', ''))
                if not year:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Year Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validate Program(PR)
                program = program_obj.validate_program(
                    result_dict.get('Programa', ''))
                if not program:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Program(PR) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validate Sub-Program
                subprogram = subprogram_obj.validate_subprogram(
                    result_dict.get('SubPrograma', ''), program)
                if not subprogram:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid SubProgram(SP) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validate Dependency
                dependency = dependancy_obj.validate_dependency(
                    result_dict.get('Dependencia', ''))
                if not dependency:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Dependency(DEP) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validate Sub-Dependency
                subdependency = subdependancy_obj.validate_subdependency(
                    result_dict.get('SubDependencia', ''), dependency)
                if not subdependency:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Sub Dependency(DEP) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validate Item
                item = item_obj.validate_item(result_dict.get(
                    'Partida', ''), result_dict.get('Cve Ejercicio', ''))
                if not item:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Expense Item(PAR) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                if result_dict.get('Digito Verificador'):
                    p_code += str(result_dict.get('Digito Verificador')
                                  )[:1].replace('.', '').zfill(2)

                # Validate Origin Of Resource
                origin_resource = origin_obj.validate_origin_resource(
                    result_dict.get('Digito Centraliador', ''))
                if not origin_resource:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Origin Of Resource(OR) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Institutional Activity Number
                institutional_activity = activity_obj.validate_institutional_activity(
                    result_dict.get('Actividad Institucional', ''))
                if not institutional_activity:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Institutional Activity Number(AI) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Conversion Program SHCP
                shcp = shcp_obj.validate_shcp(
                    result_dict.get('Conversion Programa', ''), program)
                if not shcp:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Conversion Program SHCP(CONPP) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Federal Item
                conversion_item = dpc_obj.validate_conversion_item(
                    result_dict.get('Conversion Partida', ''))
                if not conversion_item:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid SHCP Games(CONPA) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Expense Type
                expense_type = expense_type_obj.validate_expense_type(
                    result_dict.get('Tipo de gasto', ''))
                if not expense_type:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Expense Type(TG) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Expense Type
                geo_location = location_obj.validate_geo_location(
                    result_dict.get('Ubicación geografica', ''))
                if not geo_location:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Geographic Location (UG) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Wallet Key
                wallet_key = wallet_obj.validate_wallet_key(
                    result_dict.get('Clave Cartera', ''))
                if not wallet_key:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Wallet Key(CC) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Project Type
                project_type = project_type_obj.with_context(from_adjustment=True).validate_project_type(
                    result_dict.get('Tipo de Proyecto', ''), result_dict)
                if not project_type:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Project Type(TP) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Stage
                stage = stage_obj.validate_stage(
                    result_dict.get('Etapa', ''), project_type.project_id)
                if not stage:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Stage(E) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Agreement Type
                agreement_type = agreement_type_obj.validate_agreement_type(result_dict.get(
                    'Tipo de Convenio', ''), project_type.project_id, result_dict.get('No. de Convenio', ''))
                if not agreement_type:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Agreement Type(TC) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Amount
                amount = 0
                try:
                    amount = float(result_dict.get('amount', 0))
                    if float(amount) < 10000:
                        failed_row += str(list(result_dict.values())) + \
                            "------>> Amount should be 10000 or greater than 10000\n"
                        failed_row_ids.append(pointer)
                        continue
                except:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Amount Format or Amount should be greater than or equal to 10000"
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
                            ('institutional_activity_id',
                             '=', institutional_activity.id),
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

                        if program_code:
                            budget_line = self.env['expenditure.budget.line'].sudo().search(
                                [('program_code_id', '=', program_code.id), ('expenditure_budget_id', '=', self.budget_id.id)], limit=1)
                            if not budget_line:
                                1 / 0

                    if not program_code:
                        1 / 0
                    success_row_ids.append(pointer)

                    if self._context.get('re_scan_failed'):
                        failed_row_ids_eval_refill = eval(self.failed_row_ids)
                        failed_row_ids_eval_refill.remove(pointer)
                        self.write({'failed_row_ids': str(
                            list(set(failed_row_ids_eval_refill)))})

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
                'failed_row_ids': str(list(set(failed_row_ids_eval))),
                'success_row_ids': str(list(set(success_row_ids_eval))),
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
            if len(self.adequacies_lines_ids.ids) == 0:
                raise ValidationError("Please select or import any lines!")
            for line in adequacies.adequacies_lines_ids:
                if line.amount < 10000:
                    raise ValidationError(
                        "The total amount of the increases/decreases should be greater than or equal to 10000")
                if line.line_type == 'decrease':
                    if self.adaptation_type == 'liquid':
                        raise ValidationError(
                            "In liquid adjustment, you can only increase amount of budget!")
                    budget_line = self.env['expenditure.budget.line'].sudo().search(
                        [('program_code_id', '=', line.program.id), ('expenditure_budget_id', '=', self.budget_id.id)], limit=1)
                    if budget_line and budget_line.assigned < line.amount:
                        raise ValidationError("You can not decrease amount more than assigned amount!")

                    total_decreased += line.amount
                    counter_decreased += 1
                if line.line_type == 'increase':
                    total_increased += line.amount
                    counter_increased += 1
            if self.adaptation_type == 'compensated' and total_decreased != total_increased:
                raise ValidationError(
                    "The total amount of the increases and the total amount of the decreases must be equal for compensated adjustments!")

    def confirm(self):
        self.validate_data()
        self.state = 'confirmed'

    def accept(self):
        self.validate_data()
        for line in self.adequacies_lines_ids:
            if line.program:
                budget_line = self.env['expenditure.budget.line'].sudo().search(
                    [('program_code_id', '=', line.program.id), ('expenditure_budget_id', '=', self.budget_id.id)], limit=1)
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

    def unlink(self):
        for adequacies in self:
            if adequacies.state not in ('draft'):
                raise ValidationError(
                    'You can not delete confirmed/rejected adjustments!')
        return super(Adequacies, self).unlink()


class AdequaciesLines(models.Model):

    _name = 'adequacies.lines'
    _description = 'Adequacies Lines'
    _rec_name = ''

    line_type = fields.Selection(
        [('increase', 'Increase'), ('decrease', 'Decrease')], string='Type', default='increase')
    amount = fields.Float(string='Amount')
    creation_type = fields.Selection(
        [('manual', 'Manual'), ('imported', 'Imported')],
        string='Creation type', default='manual')
    adequacies_id = fields.Many2one(
        'adequacies', string='Adequacies', ondelete="cascade")
    imported = fields.Boolean(default=False)
    program = fields.Many2one(
        'program.code', string='Program', domain="[('state', '=', 'validated'), ('budget_id', '=', parent.budget_id)]")

    _sql_constraints = [('uniq_program_per_adequacies_id', 'unique(program,adequacies_id)',
                         'The program code must be unique per Adequacies')]
