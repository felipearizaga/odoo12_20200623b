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
import tempfile
import base64
import io
from datetime import datetime
from odoo.modules.module import get_resource_path
from xlrd import open_workbook
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ExpenditureBudget(models.Model):

    _name = 'expenditure.budget'
    _description = 'Expenditure Budget'
    _rec_name = 'budget_name'

    def _get_count(self):
        for record in self:
            record.record_number = len(record.line_ids)
            record.import_record_number = len(
                record.line_ids.filtered(lambda l: l.imported == True))

    budget_name = fields.Text(string='Budget name', required=True)
    responsible_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user)

    # Date Periods
    from_date = fields.Date(string='From')
    to_date = fields.Date(string='To')

    total_budget = fields.Float(string='Total budget')
    record_number = fields.Integer(
        string='Number of records', compute='_get_count')
    import_record_number = fields.Integer(
        string='Number of imported records', readonly=True, compute='_get_count')

    # Budget Lines
    line_ids = fields.One2many(
        'expenditure.budget.line', 'expenditure_budget_id',
        string='Expenditure Budget Lines')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('previous', 'Previous'),
        ('confirm', 'Confirm'),
        ('validate', 'Validate'),
        ('done', 'Done')], default='draft', required=True, string='State')

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

    budget_file = fields.Binary(string='Uploaded File')
    filename = fields.Char(string='File name')
    import_status = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Completed')], default='draft')
    failed_row_file = fields.Binary(string='Failed Rows File')
    fialed_row_filename = fields.Char(string='File name', default="Failed_Rows.txt")
    failed_rows = fields.Integer(string='Failed Rows', compute="_compute_failed_rows")
    success_rows = fields.Integer(string='Success Rows', compute="_compute_success_rows")
    success_row_ids = fields.Text(string='Success Row Ids', default="[]")
    failed_row_ids = fields.Text(string='Failed Row Ids', default="[]")
    pointer_row = fields.Integer(string='Current Pointer Row', default=1)

    # @api.constrains('total_budget', 'line_ids')
    # def _check_budget(self):
    #     total = sum(self.line_ids.mapped('assigned'))
    #     if total != self.total_budget:
    #         raise ValidationError("Budget amount not match with total lines assigned amount! \n Please first import/fill budget lines or compare amount total with file column")

    @api.constrains('from_date', 'to_date')
    def _check_dates(self):
        if self.from_date and self.to_date:
            if self.from_date > self.to_date:
                raise ValidationError("Please select correct date")

    def import_lines(self):
        return {
            'name': "Import Budget Lines",
            'type': 'ir.actions.act_window',
            'res_model': 'import.line',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(False, 'form')],
            'target': 'new',
        }

    def validate_year(self, year_string):
        if len(str(year_string)) > 3:
            year_str = str(year_string)[:4]
            if year_str.isnumeric():
                year = self.env['year.configuration'].search([('name', '=', year_str)], limit=1)
                if not year:
                    year = self.env['year.configuration'].create({'name': year_str})
                return year
        return False

    def validate_program(self, program_string):
        if len(str(program_string)) > 1:
            program_str = str(program_string).zfill(2)
            if program_str.isnumeric():
                program = self.env['program'].search([('key_unam', '=', program_str)], limit=1)
                if not program:
                    program = self.env['program'].create({'key_unam': program_str})
                return program
        return False

    def validate_subprogram(self, subprogram_string, program):
        if len(str(subprogram_string)) > 1:
            subprogram_str = str(subprogram_string).zfill(2)
            if subprogram_str.isnumeric():
                subprogram = self.env['sub.program'].search([('unam_key_id', '=', program.id), ('sub_program', '=', subprogram_str)], limit=1)
                if not subprogram:
                    subprogram = self.env['sub.program'].create({'unam_key_id': program.id, 'sub_program': subprogram_str})
                return subprogram
        return False

    def validate_dependency(self, dependency_string):
        if len(str(dependency_string)) > 2:
            dependency_str = str(dependency_string).zfill(3)
            if dependency_str.isnumeric():
                dependency = self.env['dependency'].search([('dependency', '=', dependency_str)], limit=1)
                if not dependency:
                    dependency = self.env['dependency'].create({'dependency': dependency_str})
                return dependency
        return False

    def validate_subdependency(self, subdependency_string, dependency):
        if len(str(subdependency_string)) > 1:
            subdependency_str = str(subdependency_string).zfill(2)
            if subdependency_str.isnumeric():
                subdependency = self.env['sub.dependency'].search([('dependency_id', '=', dependency.id), ('sub_dependency', '=', subdependency_string)], limit=1)
                if not subdependency:
                    subdependency = self.env['sub.dependency'].create({'dependency_id': dependency.id, 'sub_dependency': subdependency_string})
                return subdependency
        return False

    def validate_item(self, item_string, typee):
        if len(str(item_string)) > 2:
            item_str = str(item_string).zfill(3)
            typee = str(typee).lower()
            if typee not in ['r', 'c', 'd']:
                typee = 'r'
            if item_str.isnumeric():
                item = self.env['expenditure.item'].search([('item', '=', item_str), ('exercise_type', '=', typee)], limit=1)
                if not item:
                    item = self.env['expenditure.item'].search([('item', '=', item_str)], limit=1)
                if not item:
                    item = self.env['expenditure.item'].create({'item': item_str, 'exercise_type': typee})
                return item
        return False

    def validate_origin_resource(self, origin_resource_string):
        if len(str(origin_resource_string)) > 0:
            origin_resource_str = str(origin_resource_string).zfill(2)

            desc = 'subsidy'
            if origin_resource_str == '00':
                desc = 'subsidy'
            if origin_resource_str == '01':
                desc = 'income'
            if origin_resource_str == '02':
                desc = 'service'
            if origin_resource_str == '03':
                desc = 'financial'
            if origin_resource_str == '04':
                desc = 'other'
            if origin_resource_str == '05':
                desc = 'pef'

            if origin_resource_str.isnumeric():
                origin_resource = self.env['resource.origin'].search([('key_origin', '=', origin_resource_str)], limit=1)
                if not origin_resource:
                    origin_resource = self.env['resource.origin'].create({'key_origin': origin_resource_str, 'desc': desc})
                return origin_resource
        return False

    def validate_institutional_activity(self, institutional_activity_string):
        if len(str(institutional_activity_string)) > 2:
            institutional_activity_str = str(institutional_activity_string).zfill(5)
            if institutional_activity_str.isnumeric():
                institutional_activity = self.env['institutional.activity'].search([('number', '=', institutional_activity_str)], limit=1)
                if not institutional_activity:
                    institutional_activity = self.env['institutional.activity'].create({'number': institutional_activity_str})
                return institutional_activity
        return False

    def validate_shcp(self, shcp_string, program):
        if len(str(shcp_string)) > 3:
            shcp_str = str(shcp_string).zfill(4)
            if shcp_str.isnumeric():
                shcp = self.env['budget.program.conversion'].search([('shcp', '=', shcp_str)], limit=1)
                if not shcp:
                    shcp = self.env['budget.program.conversion'].create({'shcp': shcp_str})
                return shcp
        return False

    def validate_conversion_item(self, conversion_item_string):
        if len(str(conversion_item_string)) > 4:
            conversion_item_str = str(conversion_item_string).zfill(4)
            if conversion_item_str.isnumeric():
                conversion_item = self.env['departure.conversion'].search([('federal_part', '=', conversion_item_str)], limit=1)
                if not conversion_item:
                    conversion_item = self.env['departure.conversion'].create({'federal_part': conversion_item_str})
                return conversion_item
        return False

    def validate_expense_type(self, expense_type_string):
        if len(str(expense_type_string)) > 1:
            expense_type_str = str(expense_type_string).zfill(2)
            if expense_type_str.isnumeric():
                expense_type = self.env['expense.type'].search([('key_expenditure_type', '=', expense_type_str)], limit=1)
                if not expense_type:
                    expense_type = self.env['expense.type'].create({'key_expenditure_type': expense_type_str})
                return expense_type
        return False

    def validate_geo_location(self, location_string):
        if len(str(location_string)) > 1:
            location_str = str(location_string).zfill(2)
            if location_str.isnumeric():
                location = self.env['geographic.location'].search([('state_key', '=', location_str)], limit=1)
                if not location:
                    location = self.env['geographic.location'].create({'state_key': location_str})
                return location
        return False

    def validate_wallet_key(self, wallet_key_string):
        if len(str(wallet_key_string)) > 3:
            wallet_key_str = str(wallet_key_string).zfill(4)
            if wallet_key_str.isnumeric():
                wallet_key = self.env['key.wallet'].search([('wallet_password', '=', wallet_key_str)], limit=1)
                if not wallet_key:
                    wallet_key = self.env['key.wallet'].create({'wallet_password': wallet_key_str})
                return wallet_key
        return False

    def validate_project_type(self, project_type_string):
        if len(str(project_type_string)) > 1:
            project_type_str = str(project_type_string).zfill(2)
            if project_type_str.isnumeric():
                # Find Project
                project = self.env['project.project'].sudo().search([('project_type_identifier', '=', project_type_str)], limit=1)
                if not project:
                    project = self.env['project.project'].sudo().create({'name': project_type_str, 'project_type_identifier': project_type_str})
                if project:
                    # Find Project Type
                    project_type = self.env['project.type'].search([('project_id', '=', project.id)], limit=1)
                    if not project_type:
                        project_type = self.env['project.type'].create({'project_id': project.id})
                    return project_type
        return False

    def validate_project_number(self, project_number_string, project_type):
        if len(str(project_number_string)) > 5:
            project_number_str = str(project_number_string).zfill(6)
            if project_number_str.isnumeric():
                project = project_type.project_id
                if project and project.number == project_number_str:
                    return project_number_str
                else:
                    project1 = self.env['project.project'].sudo().search([('number', '=', project_number_str)], limit=1)
                    if project1:
                        project_type = self.env['project.type'].search([('project_id', '=', project1.id)], limit=1)
                        if project_type:
                            return project1.number
                project.number = project_number_str
                return project_number_str
        return False

    def validate_stage(self, stage_string, project):
        if len(str(stage_string)) > 1:
            stage_str = str(stage_string).zfill(2)
            if stage_str.isnumeric():
                if project and project.stage_identifier == stage_str:
                    # Check stage
                    stage = self.env['stage'].search([('project_id', '=', project.id)], limit=1)
                    if stage:
                        return stage
                else:
                    project1 = self.env['project.project'].sudo().search([('stage_identifier', '=', stage_str)], limit=1)
                    if project1:
                        stage = self.env['stage'].search([('project_id', '=', project1.id)], limit=1)
                        if stage:
                            return stage
                        else:
                            project = project1
                stage = self.env['stage'].search([('project_id', '=', project.id)], limit=1)
                if not stage:
                    stage = self.env['stage'].create({'project_id': project.id})
                    project.stage_identifier = stage_str
                return stage
        return False

    def validate_agreement_type(self, agreement_type_string, project, agreement_number):
        if len(str(agreement_type_string)) > 1:
            agreement_type_str = str(agreement_type_string).zfill(2)
            if agreement_type_str.isnumeric():
                validated_agreement_number = self.validate_agreement_number(agreement_number, project)
                if project and project.agreement_type == agreement_type_str and project.number_agreement == validated_agreement_number:
                    # Check agreement type
                    agreement_type = self.env['agreement.type'].search([('project_id', '=', project.id)], limit=1)
                    if agreement_type:
                        return agreement_type
                else:
                    project1 = self.env['project.project'].sudo().search([('agreement_type', '=', agreement_type_str),('number_agreement', '=', validated_agreement_number)], limit=1)
                    if project1:
                        agreement_type = self.env['agreement.type'].search([('project_id', '=', project1.id),('number_agreement', '=', validated_agreement_number)], limit=1)
                        if agreement_type:
                            return agreement_type
                        else:
                            project = project1
                agreement_type = self.env['agreement.type'].search([('project_id', '=', project.id),('number_agreement', '=', validated_agreement_number)], limit=1)
                if not agreement_type:
                    agreement_type = self.env['agreement.type'].create({'project_id': project.id, 'number_agreement': validated_agreement_number})
                return agreement_type

            validated_number = self.validate_agreement_number(agreement_number, project)
            if validated_number:
                project.number_agreement = validated_number
                project.number_agreement = validated_agreement_number
        return False

    def validate_agreement_number(self, agreement_number_string, project):
        if len(str(agreement_number_string)) > 5:
            agreement_number_str = str(agreement_number_string).zfill(6)
            if agreement_number_str.isnumeric():
                # project.number_agreement = agreement_number_str
                return agreement_number_str
        return False

    def validate_asigned_amount(self, asigned_amount_string):
        if len(str(asigned_amount_string)) > 0:
            if asigned_amount_string.isnumeric():
                return float(asigned_amount_string)
        return False

    def validate_authorized_amount(self, authorized_amount_string):
        if len(str(authorized_amount_string)) > 0:
            if authorized_amount_string.isnumeric():
                return float(authorized_amount_string)
        return False

    def validate_and_add_budget_line(self):
        if self.budget_file:
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
            lines_to_iterate = self.pointer_row + 100
            total_sheet_rows = sheet.nrows - 1
            if total_sheet_rows < lines_to_iterate:
                lines_to_iterate = total_sheet_rows + 1
            failed_row = ""
            for rowx, row in enumerate(map(sheet.row, range(self.pointer_row, lines_to_iterate)), 1):
                cnt += 1
                pointer = self.pointer_row + cnt

                result_dict = {}
                counter = 0
                for colx, cell in enumerate(row, 1):
                    result_dict.update({headers[counter]: cell.value})
                    counter += 1
                result_vals.append(result_dict)

                final_dict = {}
                # Validate year format
                year = self.validate_year(result_dict.get('AÑO', ''))
                if year:
                    final_dict['year'] = year.id
                else:
                    failed_row += str(list(result_dict.values())) + "------>> Invalid Year Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validate Program(PR)
                program = self.validate_program(result_dict.get('Programa', ''))
                if program:
                    final_dict['program_id'] = program.id
                else:
                    failed_row += str(list(result_dict.values())) + "------>> Invalid Program(PR) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validate Sub-Program
                subprogram = self.validate_subprogram(result_dict.get('SubPrograma', ''), program)
                if program:
                    final_dict['sub_program_id'] = subprogram.id
                else:
                    failed_row += str(list(result_dict.values())) + "------>> Invalid SubProgram(SP) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validate Dependency
                dependency = self.validate_dependency(result_dict.get('Dependencia', ''))
                if dependency:
                    final_dict['dependency_id'] = dependency.id
                else:
                    failed_row += str(list(result_dict.values())) + "------>> Invalid Dependency(DEP) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validate Sub-Dependency
                subdependency = self.validate_subdependency(result_dict.get('SubDependencia', ''), dependency)
                if subdependency:
                    final_dict['sub_dependency_id'] = subdependency.id
                else:
                    failed_row += str(list(result_dict.values())) + "------>> Invalid Sub Dependency(DEP) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validate Item
                item = self.validate_item(result_dict.get('Partida', ''), result_dict.get('Cve Ejercicio', ''))
                if item:
                    final_dict['item_id'] = item.id
                else:
                    failed_row += str(list(result_dict.values())) + "------>> Invalid Expense Item(PAR) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validate Origin Of Resource
                origin_resource = self.validate_origin_resource(result_dict.get('Digito Centraliador', ''))
                if origin_resource:
                    final_dict['resource_origin_id'] = origin_resource.id
                else:
                    failed_row += str(list(result_dict.values())) + "------>> Invalid Origin Of Resource(OR) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Institutional Activity Number
                institutional_activity = self.validate_institutional_activity(result_dict.get('Actividad Institucional', ''))
                if institutional_activity:
                    final_dict['institutional_activity_id'] = institutional_activity.id
                else:
                    failed_row += str(list(result_dict.values())) + "------>> Invalid Institutional Activity Number(AI) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Conversion Program SHCP
                shcp = self.validate_shcp(result_dict.get('Conversion Programa', ''), program)
                if shcp:
                    final_dict['budget_program_conversion_id'] = shcp.id
                else:
                    failed_row += str(list(result_dict.values())) + "------>> Invalid Conversion Program SHCP(CONPP) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Federal Item
                conversion_item = self.validate_conversion_item(result_dict.get('Conversion Partida', ''))
                if conversion_item:
                    final_dict['conversion_item_id'] = conversion_item.id
                else:
                    failed_row += str(list(result_dict.values())) + "------>> Invalid SHCP Games(CONPA) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Expense Type
                expense_type = self.validate_expense_type(result_dict.get('Tipo de gasto', ''))
                if expense_type:
                    final_dict['expense_type_id'] = expense_type.id
                else:
                    failed_row += str(list(result_dict.values())) + "------>> Invalid Expense Type(TG) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Expense Type
                geo_location = self.validate_geo_location(result_dict.get('Ubicación geografica', ''))
                if geo_location:
                    final_dict['location_id'] = geo_location.id
                else:
                    failed_row += str(list(result_dict.values())) + "------>> Invalid Geographic Location (UG) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Wallet Key
                wallet_key = self.validate_wallet_key(result_dict.get('Clave Cartera', ''))
                if wallet_key:
                    final_dict['portfolio_id'] = wallet_key.id
                else:
                    failed_row += str(list(result_dict.values())) + "------>> Invalid Wallet Key(CC) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Project Type
                project_type = self.validate_project_type(result_dict.get('Tipo de Proyecto', ''))
                if project_type:
                    final_dict['project_type_id'] = project_type.id
                else:
                    failed_row += str(list(result_dict.values())) + "------>> Invalid Project Type(TP) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Project Number
                project_number = self.validate_project_number(result_dict.get('No. de Proyecto', ''), project_type)
                if not project_number:
                    failed_row += str(list(result_dict.values())) + "------>> Invalid Project Number Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Stage
                stage = self.validate_stage(result_dict.get('Etapa', ''), project_type.project_id)
                if stage:
                    final_dict['stage_id'] = stage.id
                else:
                    failed_row += str(list(result_dict.values())) + "------>> Invalid Stage(E) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Agreement Number
                agreement_number = self.validate_agreement_number(result_dict.get('No. de Convenio', ''), project_type.project_id)
                if not agreement_number:
                    failed_row += str(list(result_dict.values())) + "------>> Invalid Agreement Number Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Agreement Type
                agreement_type = self.validate_agreement_type(result_dict.get('Tipo de Convenio', ''), project_type.project_id, result_dict.get('No. de Convenio', ''))
                if agreement_type:
                    final_dict['agreement_type_id'] = agreement_type.id
                else:
                    failed_row += str(list(result_dict.values())) + "------>> Invalid Agreement Type(TC) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Importe 1a Asignacion
                asigned_amount = self.validate_asigned_amount(result_dict.get('Importe 1a Asignacion', ''))
                if not asigned_amount:
                    failed_row += str(list(result_dict.values())) + "------>> Invalid Asigned Amount Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Authorized Amount
                authorized_amount = self.validate_authorized_amount(result_dict.get('Importe Autorizado', ''))
                if not authorized_amount:
                    failed_row += str(list(result_dict.values())) + "------>> Invalid Authorized Amount Format\n"
                    failed_row_ids.append(pointer)
                    continue

                try:
                    program_code = self.env['program.code'].sudo().create(final_dict)
                    success_row_ids.append(pointer)
                    line_vals = {
                        'program_code_id': program_code.id,
                        'authorized': asigned_amount,
                        'assigned': authorized_amount,
                        'imported': True,
                    }
                    self.write({'line_ids': [(0, 0, line_vals)]})
                except:
                    failed_row += str(list(result_dict.values())) + "------>> Row Data Are Not Corrected\n"
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
                content += "...................Failed Rows " + str(datetime.today()) + "...............\n"
                content += str(failed_row)
                failed_data = base64.b64encode(content.encode('utf-8'))
                vals['failed_row_file'] = failed_data
            if pointer == sheet.nrows:
                vals['import_status'] = 'done'
            self.write(vals)

    # def confirm(self):
    #     if self.total_budget <= 0:
    #         raise UserError(_('Please enter amount greater than zero.'))
    #     # elif self.line_ids:
    #     #     for line in self.line_ids:
    #     #         if line.available < 5000:
    #     #             raise UserError(_('Please enter amount greater than or equal to 5000.'))
    #     else:
    #         self.state = 'confirm'

    # def approve(self):
    #     self.state = 'validate'

    # def reject(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'reject',
    #         'view_mode': 'form',
    #         'view_type': 'form',
    #         'views': [(False, 'form')],
    #         'target': 'new',
    #     }


class ExpenditureBudgetLine(models.Model):

    _name = 'expenditure.budget.line'
    _description = 'Expenditure Budget Line'
    _rec_name = 'program_code_id'

    expenditure_budget_id = fields.Many2one(
        'expenditure.budget', string='Expenditure Budget')
    program_code_id = fields.Many2one('program.code', string='Program code')
    start_date = fields.Date(string='Start date', related="expenditure_budget_id.from_date")
    end_date = fields.Date(string='End date', related="expenditure_budget_id.to_date")
    paid_date = fields.Date(string='Paid Date')
    authorized = fields.Float(
        string='Authorized')
    assigned = fields.Float(
        string='Assigned')
    available = fields.Float(
        string='Available')

    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id)
    imported = fields.Boolean()
    dependency_id = fields.Many2one('dependency', string='Dependency', related="program_code_id.dependency_id")
    sub_dependency_id = fields.Many2one('sub.dependency', string='Sub-Dependency', related="program_code_id.sub_dependency_id")
    program_id = fields.Many2one('program', string='Program', related="program_code_id.program_id")
    item_id = fields.Many2one('expenditure.item', string='Item', related="program_code_id.item_id")

    _sql_constraints = [
        ('uniq_program_code_id', 'unique(program_code_id)', 'The Program code must be unique!'),
    ]
