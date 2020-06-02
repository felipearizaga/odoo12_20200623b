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
import math
from datetime import datetime, timedelta
from xlrd import open_workbook
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class Standardization(models.Model):

    _name = 'standardization'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Re-standardization'
    _rec_name = 'folio'

    def _get_count(self):
        for record in self:
            record.record_number = len(record.line_ids)
            record.all_line_count = len(record.line_ids)
            record.imported_record_number = len(
                record.line_ids.filtered(lambda l: l.imported == True))
            record.draft_count = len(
                record.line_ids.filtered(lambda l: l.state == 'draft'))
            record.received_count = len(
                record.line_ids.filtered(lambda l: l.state == 'received'))
            record.in_process_count = len(
                record.line_ids.filtered(lambda l: l.state == 'in_process'))
            record.authorized_count = len(
                record.line_ids.filtered(lambda l: l.state == 'authorized'))
            record.cancelled_count = len(
                record.line_ids.filtered(lambda l: l.state == 'cancelled'))

    cron_running = fields.Boolean(string='Running CRON?')
    folio = fields.Char(string='Folio', states={
        'confirmed': [('readonly', True)], 'cancelled': [('readonly', True)]}, tracking=True)
    record_number = fields.Integer(
        string='Number of records', compute='_get_count')
    imported_record_number = fields.Integer(
        string='Number of imported records', compute='_get_count')
    observations = fields.Text(string='Observations', tracking=True)
    select_box = fields.Boolean(string='Select Box')
    line_ids = fields.One2many(
        'standardization.line', 'standardization_id', string='Standardization lines', states={'cancelled': [('readonly', True)]})
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'),
                              ('cancelled', 'Cancelled')], default='draft', required=True, string='State')

    # Counter fields for line stage
    draft_count = fields.Integer(string='Draft', compute='_get_count')
    received_count = fields.Integer(string='Received', compute='_get_count')
    in_process_count = fields.Integer(
        string='In process', compute='_get_count')
    authorized_count = fields.Integer(
        string='Authorized', compute='_get_count')
    cancelled_count = fields.Integer(string='Cancelled', compute='_get_count')
    all_line_count = fields.Integer(string='Cancelled', compute='_get_count')
    check_line_state = fields.Boolean(
        compute="_compute_check_line_state", store=True)

    @api.depends('line_ids', 'line_ids.state')
    def _compute_check_line_state(self):
        for standardization in self:
            standardization.check_line_state = False
            lines = standardization.line_ids.filtered(
                lambda l: l.amount_effected == False and l.state == 'authorized')
            for line in lines:
                if line.origin_id and line.quarter:
                    budget_lines = self.env['expenditure.budget.line'].search(
                        [('program_code_id', '=', line.code_id.id), ('expenditure_budget_id', '=', line.budget_id.id)])

                    origin_start_date_day = False
                    origin_start_date_month = False
                    origin_end_date_day = False
                    origin_end_date_month = False

                    date_start = str(line.origin_id.start_date).split('/')
                    if len(date_start) > 1:
                        origin_start_date_day = date_start[0]
                        origin_start_date_month = date_start[1]
                    date_end = str(line.origin_id.end_date).split('/')
                    if len(date_end) > 1:
                        origin_end_date_day = date_end[0]
                        origin_end_date_month = date_end[1]

                    origin_budget_line = False
                    for budget_line in budget_lines:
                        if budget_line.start_date and str(budget_line.start_date.day).zfill(2) == origin_start_date_day and str(budget_line.start_date.month).zfill(2) == origin_start_date_month and budget_line.end_date and str(budget_line.end_date.day).zfill(2) == origin_end_date_day and str(budget_line.end_date.month).zfill(2) == origin_end_date_month:
                            origin_budget_line = budget_line
                            break

                    quarter_start_date_day = False
                    quarter_start_date_month = False
                    quarter_end_date_day = False
                    quarter_end_date_month = False

                    date_start = str(line.quarter.start_date).split('/')
                    if len(date_start) > 1:
                        quarter_start_date_day = date_start[0]
                        quarter_start_date_month = date_start[1]
                    date_end = str(line.quarter.end_date).split('/')
                    if len(date_end) > 1:
                        quarter_end_date_day = date_end[0]
                        quarter_end_date_month = date_end[1]

                    quarter_budget_line = False
                    for budget_line in budget_lines:
                        if budget_line.start_date and str(budget_line.start_date.day).zfill(2) == quarter_start_date_day and str(budget_line.start_date.month).zfill(2) == quarter_start_date_month and budget_line.end_date and str(budget_line.end_date.day).zfill(2) == quarter_end_date_day and str(budget_line.end_date.month).zfill(2) == quarter_end_date_month:
                            quarter_budget_line = budget_line
                            break

                    if origin_budget_line and quarter_budget_line and origin_budget_line.assigned >= line.amount:
                        amount = origin_budget_line.assigned - line.amount
                        origin_budget_line.write({'assigned': amount})
                        increase_amount = quarter_budget_line.assigned + line.amount
                        quarter_budget_line.write({'assigned': increase_amount})
                        line.amount_effected = True

    _sql_constraints = [
        ('folio_uniq_const', 'unique(folio)', 'The folio must be unique.')]

    @api.constrains('folio')
    def _check_folio(self):
        if not str(self.folio).isnumeric():
            raise ValidationError('Folio Must be numeric value!')
        folio = self.search(
            [('id', '!=', self.id), ('folio', '=', self.folio)], limit=1)
        if folio:
            raise ValidationError('Folio Must be unique!')

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
    budget_file = fields.Binary(string='Uploaded File', states={
        'confirmed': [('readonly', True)], 'cancelled': [('readonly', True)]})
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

    def validate_and_add_budget_line(self, record_id=False, cron_id=False):
        if record_id:
            self = self.env['standardization'].browse(int(record_id))

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

            cron = False
            if cron_id:
                cron = self.env['ir.cron'].sudo().browse(int(cron_id))

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
            lines_to_iterate = self.pointer_row + 5000
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

                if not result_dict.get('Digito Verificador'):
                    failed_row += str(list(result_dict.values())) + \
                                  "------>> Digito Verificador is not added!\n"
                    failed_row_ids.append(pointer)
                    continue

                if result_dict.get('Digito Verificador'):
                    p_code += str(result_dict.get('Digito Verificador')).zfill(2)

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
                    amount = float(result_dict.get('Amount', ''))
                    if float(amount) <= 0:
                        failed_row += str(list(result_dict.values())) + \
                            "------>> Amount should be greater than 0"
                        failed_row_ids.append(pointer)
                        continue
                except:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Amount Format or Amount should be 0"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Folio
                folio = result_dict.get('Folio', '')
                if folio:
                    try:
                        folio = int(float(folio))
                    except:
                        failed_row += str(list(result_dict.values())) + \
                            "------>> Folio Must Be Numeric"
                        failed_row_ids.append(pointer)
                        continue
                    line_standardization = self.env['standardization.line'].search(
                        [('folio', '=', str(folio))], limit=1)
                    if line_standardization:
                        failed_row += str(list(result_dict.values())) + \
                            "------>> Folio Must Be Unique"
                        failed_row_ids.append(pointer)
                        continue
                else:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Folio Format"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Budget
                budget_str = result_dict.get('Budget', '')
                budget = budget_obj.search(
                    [('name', '=', budget_str)], limit=1)
                if not budget:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Budget Not Found"
                    failed_row_ids.append(pointer)
                    continue

                # Validate Origin
                origin = self.env['quarter.budget'].search(
                    [('name', '=', result_dict.get('Origin', ''))], limit=1)
                if not origin:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Origin Not Found\n"
                    failed_row_ids.append(pointer)
                    continue

                quarter = self.env['quarter.budget'].search(
                    [('name', '=', result_dict.get('Quarter', ''))], limit=1)
                if not quarter:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Quarter Not Found\n"
                    failed_row_ids.append(pointer)
                    continue

                try:
                    program_code = False
                    if stage and origin and budget and year and program and subprogram and dependency and subdependency and item and origin_resource and institutional_activity and shcp and conversion_item and expense_type and geo_location and wallet_key and project_type and stage and agreement_type:
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
                                [('program_code_id', '=', program_code.id), ('expenditure_budget_id', '=', budget.id)], limit=1)
                            if not budget_line:
                                failed_row += str(list(result_dict.values())) + \
                                    "------>> Budget line not found for selected program code!"
                                failed_row_ids.append(pointer)
                                continue

                            pc = program_code
                            dv_obj = self.env['verifying.digit']
                            if pc.program_id and pc.sub_program_id and pc.dependency_id and \
                                    pc.sub_dependency_id and pc.item_id:
                                vd = dv_obj.check_digit_from_codes(
                                    pc.program_id, pc.sub_program_id, pc.dependency_id, pc.sub_dependency_id,
                                    pc.item_id)
                                if vd and p_code and vd != p_code:
                                    failed_row += str(list(result_dict.values())) + \
                                                  "------>> Digito Verificador is not matched! \n"
                                    failed_row_ids.append(pointer)
                                    continue

                    if not program_code:
                        failed_row += str(list(result_dict.values())) + \
                            "------>> Program code not found!"
                        failed_row_ids.append(pointer)
                        continue
                    success_row_ids.append(pointer)

                    if self._context.get('re_scan_failed'):
                        failed_row_ids_eval_refill = eval(self.failed_row_ids)
                        failed_row_ids_eval_refill.remove(pointer)
                        self.write({'failed_row_ids': str(
                            list(set(failed_row_ids_eval_refill)))})

                    line_vals = {
                        'folio': folio,
                        'code_id': program_code.id,
                        'budget_id': budget.id,
                        'amount': amount,
                        'origin_id': origin.id,
                        'quarter': quarter.id,
                        'imported': True,
                    }
                    self.write({'line_ids': [(0, 0, line_vals)]})
                except:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Row Data Are Not Corrected or Validated Program Code Not Found or Program Code not associated with selected budget!"
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

            if pointer == sheet.nrows and len(failed_row_ids_eval) > 0:
                self.write({'allow_upload': True})

            if self.failed_row_ids == 0 or len(failed_row_ids_eval) == 0:
                self.write({'allow_upload': False})

            if cron:
                next_cron = self.env['ir.cron'].sudo().search([('prev_cron_id', '=', cron.id), ('active', '=', False), ('model_id', '=', self.env.ref('jt_budget_mgmt.model_standardization').id)], limit=1)
                if next_cron:
                    nextcall = datetime.now()
                    nextcall = nextcall + timedelta(seconds=10)
                    next_cron.write({'nextcall': nextcall, 'active': True})
                else:
                    self.write({'cron_running': False})
                    failed_count = success_count = 0
                    if self.line_ids:
                        success_count = len(self.line_ids)
                    failed_count = self.total_rows - success_count
                    self.send_notification_msg(self.create_uid, failed_count, success_count)
                    self.create_uid.notify_info(message='Standardization - ' + str(self.folio) +
                        ' Lines validation process completed. Please verify and correct lines, if any failed!',
                        title="Re-standardization", sticky=True)
                    msg = (_("Re-standardization Validation Process Ended at %s" % datetime.strftime(
                        datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)))
                    self.env['mail.message'].create({'model': 'standardization', 'res_id': self.id,
                                                     'body': msg})
            if vals:
                self.write(vals)

            # if len(failed_row_ids) == 0:
            #     return{
            #         'effect': {
            #             'fadeout': 'slow',
            #             'message': 'All rows are imported successfully!',
            #             'type': 'rainbow_man',
            #         }
            #     }

    def remove_cron_records(self):
        crons = self.env['ir.cron'].sudo().search([('model_id', '=', self.env.ref('jt_budget_mgmt.model_standardization').id)])
        for cron in crons:
            if cron.standardization_id and not cron.standardization_id.cron_running:
                try:
                    cron.sudo().unlink()
                except:
                    pass

    def send_notification_msg(self, user, failed, successed):
        ch_obj = self.env['mail.channel']
        base_user = self.env.ref('base.user_root')
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = base_url + '/web#id=%s&view_type=form&model=standardization' % (self.id)
        body = (_("Re-standardization Validation Process is Completed for \
                    <a href='%s' target='new'>%s</a>" % (url, self.folio)))
        body += (_("<ul><li>Total Successed Lines: %s </li>\
            <li>Total Failed Lines: %s </li></ul>") % (str(successed), str(failed)))
        if user:
            ch = ch_obj.sudo().search([('name', '=', str(base_user.name + ', ' + user.name)),
                                       ('channel_type', '=', 'chat')], limit=1)
            if not ch:
                ch = ch_obj.create({
                    'name': 'OdooBot, ' + user.name,
                    'public': 'private',
                    'channel_type': 'chat',
                    'channel_last_seen_partner_ids': [(0, 0, {'partner_id': user.partner_id.id,
                                                              'partner_email': user.partner_id.email}),
                                                      (0, 0, {'partner_id': base_user.partner_id.id,
                                                              'partner_email': base_user.partner_id.email})
                                                      ]
                })
            ch.message_post(attachment_ids=[], body=body, content_subtype='html',
                            message_type='comment', partner_ids=[], subtype='mail.mt_comment',
                            email_from=base_user.partner_id.email, author_id=base_user.partner_id.id)
        return True

    def validate_draft_lines(self):
        if self.budget_file:
            # Total CRON to create
            data = base64.decodestring(self.budget_file)
            book = open_workbook(file_contents=data or b'')
            sheet = book.sheet_by_index(0)
            total_sheet_rows = sheet.nrows - 1
            total_cron = math.ceil(total_sheet_rows / 5000)
            msg = (_("Re-standardization Validation Process Started at %s" % datetime.strftime(
                datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)))
            self.env['mail.message'].create({'model': 'standardization', 'res_id': self.id,
                                             'body': msg})
            if total_cron == 1:
                self.validate_and_add_budget_line()
                msg = (_("Re-standardization Validation Process Ended at %s" % datetime.strftime(
                    datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)))
                self.env['mail.message'].create({'model': 'standardization', 'res_id': self.id,
                                                 'body': msg})
            else:
                self.write({'cron_running': True})
                prev_cron_id = False
                for seq in range(1, total_cron + 1):
                    # Create CRON JOB
                    cron_name = str(self.folio).replace(' ', '') + "_" + str(datetime.now()).replace(' ', '')
                    nextcall = datetime.now()
                    nextcall = nextcall + timedelta(seconds=10)

                    cron_vals = {
                        'name': cron_name,
                        'state': 'code',
                        'nextcall': nextcall,
                        'nextcall_copy': nextcall,
                        'numbercall': -1,
                        'code': "model.validate_and_add_budget_line()",
                        'model_id': self.env.ref('jt_budget_mgmt.model_standardization').id,
                        'user_id': self.env.user.id,
                        'standardization_id': self.id
                    }

                    # Final process
                    cron = self.env['ir.cron'].sudo().create(cron_vals)
                    cron.write({'code': "model.validate_and_add_budget_line(" + str(self.id) + "," + str(cron.id) + ")"})
                    if prev_cron_id:
                        cron.write({'prev_cron_id': prev_cron_id, 'active': False})
                    prev_cron_id = cron.id

    def validate_data(self):
        if len(self.line_ids.ids) == 0:
            raise ValidationError("Please Add Standardization Lines")
        if self.failed_rows > 0:
            raise ValidationError("Please correct failed rows!")

        lines = self.line_ids.filtered(lambda l: l.amount == 0)
        if lines:
            raise ValidationError("Row Amount must be greater than 0!")

        if self.total_rows > 0 and len(self.line_ids.ids) != self.total_rows:
            raise ValidationError(
                "Total imported rows not matched with total standardization lines!")

        bugdet_l_obj = self.env['expenditure.budget.line']
        for line in self.line_ids:
            if line.amount and line.origin_id and line.code_id and line.budget_id:
                budget_lines = bugdet_l_obj.search([('expenditure_budget_id', '=', line.budget_id.id),
                                                    ('program_code_id', '=', line.code_id.id)])
                origin_start_date_day = False
                origin_start_date_month = False
                origin_end_date_day = False
                origin_end_date_month = False

                date_start = str(line.origin_id.start_date).split('/')
                if len(date_start) > 1:
                    origin_start_date_day = date_start[0]
                    origin_start_date_month = date_start[1]
                date_end = str(line.origin_id.end_date).split('/')
                if len(date_end) > 1:
                    origin_end_date_day = date_end[0]
                    origin_end_date_month = date_end[1]
                origin_budget_line = False
                for budget_line in budget_lines:
                    if not origin_budget_line:
                        if budget_line.start_date and str(budget_line.start_date.day).zfill(
                                2) == origin_start_date_day and str(budget_line.start_date.month).zfill(
                                2) == origin_start_date_month and budget_line.end_date and str(
                                budget_line.end_date.day).zfill(2) == origin_end_date_day and str(
                                budget_line.end_date.month).zfill(2) == origin_end_date_month:
                            origin_budget_line = budget_line
                if origin_budget_line and line.amount > origin_budget_line.assigned:
                    raise ValidationError(_("The amount is greater than the one assigned in the budget. \n"
                            "Budget: %s \nProgram Code: %s" % (line.budget_id.name, line.code_id.program_code)))

    def confirm(self):
        self.validate_data()
        self.state = 'confirmed'
        self.line_ids.write({'state': 'draft'})

    def cancel(self):
        self.state = 'cancelled'

    def import_lines(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'import.standardization.line',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(False, 'form')],
            'target': 'new',
        }

    def action_draft(self):
        lines = self.line_ids.filtered(lambda l: l.selected == True and l.state == False)
        for line in lines:
            line.state = 'draft'

    def action_received(self):
        lines = self.line_ids.filtered(
            lambda l: l.selected == True and l.state == 'draft')
        for line in lines:
            line.state = 'received'

    def action_in_process(self):
        lines = self.line_ids.filtered(
            lambda l: l.selected == True and l.state == 'received')
        for line in lines:
            line.state = 'in_process'

    def action_authorized(self):
        lines = self.line_ids.filtered(
            lambda l: l.selected == True and l.state == 'in_process')
        for line in lines:
            line.state = 'authorized'

    def action_cancelled(self):
        lines = self.line_ids.filtered(lambda l: l.selected == True)
        for line in lines:
            line.state = 'cancelled'
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'reject.standardization.line',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(False, 'form')],
            'target': 'new',
            'context': {'parent_id': self.id, }
        }

    def draft_button(self):
        action = self.env.ref(
            'jt_budget_mgmt.action_standardization_lines').read()[0]
        action['view_mode'] = 'tree'
        action['domain'] = [
            ('standardization_id', '=', self.id), ('state', '=', 'draft')]
        return action

    def received_button(self):
        action = self.env.ref(
            'jt_budget_mgmt.action_standardization_lines').read()[0]
        action['view_mode'] = 'tree'
        action['domain'] = [
            ('standardization_id', '=', self.id), ('state', '=', 'received')]
        return action

    def in_process_button(self):
        action = self.env.ref(
            'jt_budget_mgmt.action_standardization_lines').read()[0]
        action['view_mode'] = 'tree'
        action['domain'] = [
            ('standardization_id', '=', self.id), ('state', '=', 'in_process')]
        return action

    def authorized_button(self):
        action = self.env.ref(
            'jt_budget_mgmt.action_standardization_lines').read()[0]
        action['view_mode'] = 'tree'
        action['domain'] = [
            ('standardization_id', '=', self.id), ('state', '=', 'authorized')]
        return action

    def cancelled_button(self):
        action = self.env.ref(
            'jt_budget_mgmt.action_standardization_lines').read()[0]
        action['view_mode'] = 'tree'
        action['domain'] = [
            ('standardization_id', '=', self.id), ('state', '=', 'cancelled')]
        return action

    def all_lines_button(self):
        action = self.env.ref(
            'jt_budget_mgmt.action_standardization_lines').read()[0]
        action['view_mode'] = 'tree'
        action['domain'] = [
            ('standardization_id', '=', self.id)]
        return action

    def select_deselect_checkbox(self):
        if self.select_box:
            self.select_box = False
        else:
            self.select_box = True

        self.line_ids.write({'selected': self.select_box})

    def unlink(self):
        for budget in self:
            if budget.state != 'draft':
                raise ValidationError(
                    'You can not delete confirmed Re-standardization!')
        return super(Standardization, self).unlink()


class StandardizationLine(models.Model):

    _name = 'standardization.line'
    _description = 'Re-standardization Lines'
    _rec_name = 'folio'

    folio = fields.Char(string='Folio')
    budget_id = fields.Many2one('expenditure.budget', string='Budget', domain="[('state', '=', 'validate')]")
    code_id = fields.Many2one(
        'program.code', string='Code', domain="[('budget_id', '=', budget_id)]")
    amount = fields.Monetary(string='Amount', currency_field='currency_id')
    origin_id = fields.Many2one('quarter.budget', string='Origin')
    quarter = fields.Many2one('quarter.budget', string='Quarter')
    reason = fields.Text(string='Reason for rejection')
    standardization_id = fields.Many2one(
        'standardization', string='Standardization', ondelete="cascade")
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.user.company_id.currency_id)
    imported = fields.Boolean(default=False)
    amount_effected = fields.Boolean(string='Amount Effected?')
    selected = fields.Boolean(default=False)
    state = fields.Selection([('draft', 'Draft'), ('received', 'Received'),
                              ('in_process', 'In process'),
                              ('authorized', 'Authorized'),
                              ('cancelled', 'Cancelled')],
                             string='State')

    _sql_constraints = [('uniq_program_per_standardization_id', 'unique(code_id,standardization_id)',
                         'The program code must be unique per Standardization'),
                        ('folio_uniq', 'unique(folio)', 'The folio must be unique.')]

    @api.constrains('folio')
    def _check_folio(self):
        for line in self:
            if not str(line.folio).isnumeric():
                raise ValidationError('Folio Must be numeric value!')

    @api.onchange('state')
    def _onchange_state(self):
        state = self._origin.state
        if state and state == 'draft' and self.state not in ['draft', 'received', 'cancelled']:
            raise ValidationError(
                "You can only select Cancel or Received status")
        if state and state == 'received' and self.state not in ['received', 'in_process', 'cancelled']:
            raise ValidationError(
                "You can only select Cancel or In Progress status")
        if state and state == 'in_process' and self.state not in ['in_process', 'authorized', 'cancelled']:
            raise ValidationError(
                "You can only select Cancel or Authorized status")
        if state and state == 'authorized' and self.state not in ['authorized', 'cancelled']:
            raise ValidationError("You can only select Cancel status")
        if state and state == 'cancelled' and self.state not in ['cancelled']:
            raise ValidationError("You can only not select any status")
