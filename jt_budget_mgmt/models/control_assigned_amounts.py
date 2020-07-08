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
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ControlAssignedAmounts(models.Model):

    _name = 'control.assigned.amounts'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Control of Assigned Amounts'
    _rec_name = 'folio'

    def _get_count(self):
        for record in self:
            record.record_number = len(record.success_line_ids)
            record.import_record_number = len(
                record.success_line_ids.filtered(lambda l: l.imported == True))

    name = fields.Char(string="Name", tracking=True)
    cron_running = fields.Boolean(string='Running CRON?')
    record_number = fields.Integer(
        string='Number of records', compute='_get_count')
    import_record_number = fields.Integer(
        string='Number of imported records', readonly=True, compute='_get_count')

    folio = fields.Char(string='Folio', states={'validated': [('readonly', True)], 'rejected': [
                        ('readonly', True)], 'canceled': [('readonly', True)]}, tracking=True)
    budget_id = fields.Many2one('expenditure.budget', string='Budget', states={'validated': [(
        'readonly', True)], 'rejected': [('readonly', True)], 'canceled': [('readonly', True)]}, tracking=True)
    user_id = fields.Many2one(
        'res.users', string='Made by', default=lambda self: self.env.user, tracking=True)
    import_date = fields.Date(string='Import date', states={'validated': [(
        'readonly', True)], 'rejected': [('readonly', True)], 'canceled': [('readonly', True)]})
    observations = fields.Text(string='Observations', tracking=True)
    state = fields.Selection([('draft', 'Draft'), ('process', 'In process'),
                              ('validated', 'Validated'),
                              ('rejected', 'Rejected'),
                              ('canceled', 'Canceled')], default='draft', required=True, string='Status')

    # Budget Lines
    line_ids = fields.One2many('control.assigned.amounts.lines',
                               'assigned_amount_id', string='Assigned amount lines', domain=[('state', '!=', 'success')], states={'validated': [('readonly', True)], 'rejected': [('readonly', True)], 'canceled': [('readonly', True)]})
    success_line_ids = fields.One2many(
        'control.assigned.amounts.lines', 'assigned_amount_id',
        string='Assigned amount lines', domain=[('state', '=', 'success')], states={'validated': [('readonly', True)], 'rejected': [('readonly', True)], 'canceled': [('readonly', True)]})

    def _compute_total_rows(self):
        for assigned_amount in self:
            assigned_amount.draft_rows = self.env['control.assigned.amounts.lines'].search_count(
                [('assigned_amount_id', '=', assigned_amount.id), ('state', 'in', ['draft', 'manual'])])
            assigned_amount.failed_rows = self.env['control.assigned.amounts.lines'].search_count(
                [('assigned_amount_id', '=', assigned_amount.id), ('state', '=', 'fail')])
            assigned_amount.success_rows = self.env['control.assigned.amounts.lines'].search_count(
                [('assigned_amount_id', '=', assigned_amount.id), ('state', '=', 'success')])
            assigned_amount.total_rows = self.env['control.assigned.amounts.lines'].search_count(
                [('assigned_amount_id', '=', assigned_amount.id)])

    # Rows Progress Tracking Details
    import_status = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Completed')], default='draft', copy=False)
    failed_row_file = fields.Binary(string='Failed Rows File')
    fialed_row_filename = fields.Char(
        string='File name', default="Failed_Rows.txt")
    draft_rows = fields.Integer(
        string='Failed Rows', compute="_compute_total_rows")
    failed_rows = fields.Integer(
        string='Failed Rows', compute="_compute_total_rows")
    success_rows = fields.Integer(
        string='Success Rows', compute="_compute_total_rows")
    total_rows = fields.Integer(
        string="Total Rows", compute="_compute_total_rows")
    assigned_total = fields.Float(
        string="Total Assigned", compute="_compute_amt_total", store=True)

    _sql_constraints = [
        ('folio', 'unique(folio)', 'The folio must be unique.')]

    @api.depends('success_line_ids', 'success_line_ids.assigned')
    def _compute_amt_total(self):
        for seasonality in self:
            assigned_total = 0
            for line in seasonality.success_line_ids:
                assigned_total += line.assigned

            seasonality.assigned_total = assigned_total

    @api.constrains('folio')
    def _check_folio(self):
        if not str(self.folio).isnumeric():
            raise ValidationError('Folio Must be numeric value!')

    def import_lines(self):
        ctx = self.env.context.copy()
        if self._context.get('reimport'):
            ctx['reimport'] = True
        return {
            'name': _("Import Lines"),
            'type': 'ir.actions.act_window',
            'res_model': 'import.assigned.amount.line',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(False, 'form')],
            'target': 'new',
            'context': ctx,
        }

    def validate_and_add_budget_line(self, record_id=False, cron_id=False):
        if record_id:
            self = self.env['control.assigned.amounts'].browse(int(record_id))

        if len(self.line_ids.ids) > 0:
            counter = 0
            failed_row = ""
            failed_line_ids = []
            success_line_ids = []

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

            lines_to_execute = self.line_ids
            cron = False
            if cron_id:
                cron = self.env['ir.cron'].sudo().browse(int(cron_id))
                if cron:
                    lines_to_execute = self.env['control.assigned.amounts.lines'].search([('cron_id', '=', cron.id)])

            for line in lines_to_execute:
                if counter == 5000:
                    break
                counter += 1
                line_vals = [line.year, line.program, line.subprogram, line.dependency, line.subdependency, line.item,
                             line.dv, line.origin_resource, line.ai, line.conversion_program,
                             line.departure_conversion, line.expense_type, line.location, line.portfolio,
                             line.project_type, line.project_number, line.stage, line.agreement_type,
                             line.agreement_number, line.exercise_type]

                if line.state != 'success':

                    # Validate start date
                    if line.start_date and line.start_date.day == 1 and line.start_date.month in [1, 4, 7, 10]:
                        pass
                    else:
                        failed_row += str(line_vals) + \
                            "------>> Invalid start date based on quarter rules\n"
                        failed_line_ids.append(line.id)
                        continue

                    # Validate end date
                    if line.end_date:
                        flag = False
                        if line.end_date.month not in [3, 6, 9, 12] or line.end_date.day not in [31, 30]:
                            flag = True
                        if line.end_date.month == 3 and line.end_date.day != 31:
                            flag = True
                        if line.end_date.month == 6 and line.end_date.day != 30:
                            flag = True
                        if line.end_date.month == 9 and line.end_date.day != 30:
                            flag = True
                        if line.end_date.month == 12 and line.end_date.day != 31:
                            flag = True
                        if flag:
                            failed_row += str(line_vals) + \
                                "------>> Invalid end date based on quarter rules\n"
                            failed_line_ids.append(line.id)
                            continue

                    # Validate year format
                    year = year_obj.validate_year(line.year)
                    if not year:
                        failed_row += str(line_vals) + \
                            "------>> Invalid Year Format\n"
                        failed_line_ids.append(line.id)
                        continue

                    # Validate Program(PR)
                    program = program_obj.validate_program(line.program)
                    if not program:
                        failed_row += str(line_vals) + \
                            "------>> Invalid Program(PR) Format\n"
                        failed_line_ids.append(line.id)
                        continue

                    # Validate Sub-Program
                    subprogram = subprogram_obj.validate_subprogram(
                        line.subprogram, program)
                    if not subprogram:
                        failed_row += str(line_vals) + \
                            "------>> Invalid SubProgram(SP) Format\n"
                        failed_line_ids.append(line.id)
                        continue

                    # Validate Dependency
                    dependency = dependancy_obj.validate_dependency(
                        line.dependency)
                    if not dependency:
                        failed_row += str(line_vals) + \
                            "------>> Invalid Dependency(DEP) Format\n"
                        failed_line_ids.append(line.id)
                        continue

                    # Validate Sub-Dependency
                    subdependency = subdependancy_obj.validate_subdependency(
                        line.subdependency, dependency)
                    if not subdependency:
                        failed_row += str(line_vals) + \
                            "------>> Invalid Sub Dependency(DEP) Format\n"
                        failed_line_ids.append(line.id)
                        continue

                    # Validate Item
                    item = item_obj.validate_item(
                        line.item, line.exercise_type)
                    if not item:
                        failed_row += str(line_vals) + \
                            "------>> Invalid Expense Item(PAR) Format\n"
                        failed_line_ids.append(line.id)
                        continue

                    # Validate Origin Of Resource
                    origin_resource = origin_obj.validate_origin_resource(
                        line.origin_resource)
                    if not origin_resource:
                        failed_row += str(line_vals) + \
                            "------>> Invalid Origin Of Resource(OR) Format\n"
                        failed_line_ids.append(line.id)
                        continue

                    # Validation Institutional Activity Number
                    institutional_activity = activity_obj.validate_institutional_activity(
                        line.ai)
                    if not institutional_activity:
                        failed_row += str(line_vals) + \
                            "------>> Invalid Institutional Activity Number(AI) Format\n"
                        failed_line_ids.append(line.id)
                        continue

                    # Validation Conversion Program SHCP
                    shcp = shcp_obj.validate_shcp(
                        line.conversion_program, program)
                    if not shcp:
                        failed_row += str(line_vals) + \
                            "------>> Invalid Conversion Program SHCP(CONPP) Format\n"
                        failed_line_ids.append(line.id)
                        continue

                    # Validation Federal Item
                    conversion_item = dpc_obj.validate_conversion_item(
                        line.departure_conversion)
                    if not conversion_item:
                        failed_row += str(line_vals) + \
                            "------>> Invalid SHCP Games(CONPA) Format\n"
                        failed_line_ids.append(line.id)
                        continue

                    # Validation Expense Type
                    expense_type = expense_type_obj.validate_expense_type(
                        line.expense_type)
                    if not expense_type:
                        failed_row += str(line_vals) + \
                            "------>> Invalid Expense Type(TG) Format\n"
                        failed_line_ids.append(line.id)
                        continue

                    # Validation Expense Type
                    geo_location = location_obj.validate_geo_location(
                        line.location)
                    if not geo_location:
                        failed_row += str(line_vals) + \
                            "------>> Invalid Geographic Location (UG) Format\n"
                        failed_line_ids.append(line.id)
                        continue

                    # Validation Wallet Key
                    wallet_key = wallet_obj.validate_wallet_key(line.portfolio)
                    if not wallet_key:
                        failed_row += str(line_vals) + \
                            "------>> Invalid Wallet Key(CC) Format\n"
                        failed_line_ids.append(line.id)
                        continue

                    # Validation Project Type
                    project_type = project_type_obj.validate_project_type(
                        line.project_type, line)
                    if not project_type:
                        failed_row += str(project_type) + \
                            "------>> Invalid Project Type(TP) or Project Number Format\n"
                        failed_line_ids.append(line.id)
                        continue

                    # Validation Stage
                    stage = stage_obj.validate_stage(
                        line.stage, project_type.project_id)
                    if not stage:
                        failed_row += str(line_vals) + \
                            "------>> Invalid Stage(E) Format\n"
                        failed_line_ids.append(line.id)
                        continue

                    # Validation Agreement Type
                    agreement_type = agreement_type_obj.validate_agreement_type(
                        line.agreement_type, project_type.project_id, line.agreement_number)
                    if not agreement_type:
                        failed_row += str(line_vals) + \
                            "------>> Invalid Agreement Type(TC) or Agreement Number Format\n"
                        failed_line_ids.append(line.id)
                        continue

                    # Validation Importe 1a Asignacion
                    asigned_amount = 0
                    try:
                        asigned_amount = float(line.assigned)
                        if asigned_amount < 0:
                            failed_row += str(line_vals) + \
                                "------>> Assigned Amount should be greater than or 0!"
                            failed_line_ids.append(line.id)
                            continue
                    except:
                        failed_row += str(line_vals) + \
                            "------>> Invalid Asigned Amount Format"
                        failed_line_ids.append(line.id)
                        continue

                    # Validation Authorized Amount
                    authorized_amount = 0
                    # try:
                    #     authorized_amount = float(line.authorized)
                    #     if authorized_amount == 0:
                    #         failed_row += str(line_vals) + \
                    #             "------>> Authorized Amount should be greater than 0!"
                    #         failed_line_ids.append(line.id)
                    #         continue
                    # except:
                    #     failed_row += str(line_vals) + \
                    #         "------>> Invalid Authorized Amount Format"
                    #     failed_line_ids.append(line.id)
                    #     continue

                    if not line.dv:
                        failed_row += str(line_vals) + \
                            "------>> Digito Verificador is not added! \n"
                        failed_line_ids.append(line.id)
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
                            ], limit=1)

                            # if program_code and program_code.state == 'validated':
                            #     failed_row += str(line_vals) + \
                            #         "------>> Duplicated Program Code Found!"
                            #     failed_line_ids.append(line.id)
                            #     continue
                            if program_code:
                                budget_line = self.env['expenditure.budget.line'].search([('expenditure_budget_id', '=', self.budget_id.id), ('program_code_id', '=', program_code.id), (
                                    'start_date', '=', line.start_date), ('end_date', '=', line.end_date)], limit=1)
                                if budget_line:
                                    failed_row += str(line_vals) + \
                                        "------>> Program Code Already Linked With Budget Line with same quarter!"
                                    failed_line_ids.append(line.id)
                                    continue

                        if not program_code:
                            failed_row += str(line_vals) + \
                                "-------> Program Code is not created. \n"
                            failed_line_ids.append(line.id)
                            continue
                        if program_code and not program_code.budget_id:
                            failed_row += str(line_vals) + \
                                          "-------> Program Code is not created in selected budget. \n"
                            failed_line_ids.append(line.id)
                            continue
                        if program_code and program_code.budget_id and program_code.budget_id.id != self.budget_id.id:
                            failed_row += str(line_vals) + \
                                          "-------> Program Code is not created in selected budget. \n"
                            failed_line_ids.append(line.id)
                            continue
                        #     program_vals = {
                        #         'year': year.id,
                        #         'program_id': program.id,
                        #         'sub_program_id': subprogram.id,
                        #         'dependency_id': dependency.id,
                        #         'sub_dependency_id': subdependency.id,
                        #         'item_id': item.id,
                        #         'resource_origin_id': origin_resource.id,
                        #         'institutional_activity_id': institutional_activity.id,
                        #         'budget_program_conversion_id': shcp.id,
                        #         'conversion_item_id': conversion_item.id,
                        #         'expense_type_id': expense_type.id,
                        #         'location_id': geo_location.id,
                        #         'portfolio_id': wallet_key.id,
                        #         'project_type_id': project_type.id,
                        #         'stage_id': stage.id,
                        #         'agreement_type_id': agreement_type.id,
                        #     }
                        #     program_code = self.env['program.code'].sudo().create(
                        #         program_vals)
                        if program_code:
                            pc = program_code
                            dv_obj = self.env['verifying.digit']
                            if pc.program_id and pc.sub_program_id and pc.dependency_id and \
                                    pc.sub_dependency_id and pc.item_id:
                                vd = dv_obj.check_digit_from_codes(
                                    pc.program_id, pc.sub_program_id, pc.dependency_id, pc.sub_dependency_id,
                                    pc.item_id)
                                if vd and line.dv:
                                    line_dv = line.dv
                                    if len(line.dv) == 1:
                                        line_dv = '0' + line.dv
                                    if vd != line_dv:
                                        failed_row += str(line_vals) + \
                                                      "------>> Digito Verificador is not matched! \n"
                                        failed_line_ids.append(line.id)
                                        continue
                        if program_code:
                            line.program_code_id = program_code.id
                            success_line_ids.append(line.id)
                            line.available = line.assigned
                    except:
                        failed_row += str(line_vals) + \
                            "------>> Row Data Are Not Corrected or Duplicated Program Code Found!"
                        failed_line_ids.append(line.id)
                        continue

            failed_lines = self.env['control.assigned.amounts.lines'].search(
                [('assigned_amount_id', '=', self.id), ('id', 'in', failed_line_ids)])
            success_lines = self.env['control.assigned.amounts.lines'].search(
                [('assigned_amount_id', '=', self.id), ('id', 'in', success_line_ids)])
            success_lines.write({'state': 'success'})
            for l in failed_lines:
                if l.state == 'draft':
                    l.state = 'fail'

            failed_data = False
            vals = {}
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

            if cron:
                lines_to_execute.write({'cron_id': False})
                next_cron = self.env['ir.cron'].sudo().search([('prev_cron_id', '=', cron.id), ('active', '=', False), ('model_id', '=', self.env.ref('jt_budget_mgmt.model_control_assigned_amounts').id)], limit=1)
                if next_cron:
                    nextcall = datetime.now()
                    nextcall = nextcall + timedelta(seconds=10)
                    next_cron.write({'nextcall': nextcall, 'active': True})
                else:
                    self.write({'cron_running': False})
                    if len(self.line_ids.ids) == 0:
                        self.write({'state': 'process'})
                    failed_count = success_count = 0
                    if self.success_line_ids:
                        success_count = len(self.success_line_ids)
                    if self.line_ids:
                        failed_count = len(self.line_ids)
                    self.send_notification_msg(self.user_id, failed_count, success_count)
                    self.user_id.notify_info(message='Control of Assigned Amounts - ' + str(self.folio) +
                    ' Lines Validation process completed. Please verify and correct lines, if any failed!',
                                    title='Control of Assigned Amounts', sticky=True)
                    msg = (_("Control of Assigned Amounts Validation Process Ended at %s" % datetime.strftime(
                        datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)))
                    self.env['mail.message'].create({'model': 'control.assigned.amounts', 'res_id': self.id,
                                                     'body': msg})
            if vals:
                self.write(vals)

            # if len(failed_line_ids) == 0:
            #     return{
            #         'effect': {
            #             'fadeout': 'slow',
            #             'message': 'All rows are imported successfully!',
            #             'type': 'rainbow_man',
            #         }
            #     }

    def send_notification_msg(self, user, failed, successed):
        ch_obj = self.env['mail.channel']
        base_user = self.env.ref('base.user_root')
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = base_url + '/web#id=%s&view_type=form&model=control.assigned.amounts' % (self.id)
        body = (_("Control of Assigned Amounts Validation Process is Completed for \
                       <a href='%s' target='new'>%s</a>" % (url, self.name)))
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

    def remove_cron_records(self):
        crons = self.env['ir.cron'].sudo().search([('model_id', '=', self.env.ref('jt_budget_mgmt.model_control_assigned_amounts').id)])
        for cron in crons:
            if cron.control_assigned_id and not cron.control_assigned_id.cron_running:
                try:
                    cron.sudo().unlink()
                except:
                    pass

    def confirm(self):
        # Total CRON to create
        total_cron = math.ceil(len(self.line_ids.ids) / 5000)
        msg = (_("Control of Assigned Amounts Validation Process Started at %s" % datetime.strftime(
            datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)))
        self.env['mail.message'].create({'model': 'control.assigned.amounts', 'res_id': self.id,
                                         'body': msg})
        if total_cron == 1:
            if self.success_rows != self.total_rows:
                self.validate_and_add_budget_line()
            total_lines = len(self.success_line_ids.filtered(
                lambda l: l.state == 'success'))
            if total_lines == self.total_rows:
                self.import_date = datetime.today().date()
                self.state = 'process'
            msg = (_("Control of Assigned Amounts Validation Process Ended at %s" % datetime.strftime(
                datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)))
            self.env['mail.message'].create({'model': 'control.assigned.amounts', 'res_id': self.id,
                                             'body': msg})
        else:
            self.write({'cron_running': True})
            prev_cron_id = False
            line_ids = self.line_ids.ids
            for seq in range(1, total_cron + 1):

                # Create CRON JOB
                cron_name = str(self.folio).replace(' ', '') + "_" + str(datetime.now()).replace(' ', '')
                nextcall = datetime.now()
                nextcall = nextcall + timedelta(seconds=10)
                lines = line_ids[:5000]

                cron_vals = {
                    'name': cron_name,
                    'state': 'code',
                    'nextcall': nextcall,
                    'nextcall_copy': nextcall,
                    'numbercall': -1,
                    'code': "model.validate_and_add_budget_line()",
                    'model_id': self.env.ref('jt_budget_mgmt.model_control_assigned_amounts').id,
                    'user_id': self.env.user.id,
                    'control_assigned_id': self.id
                }

                # Final process
                cron = self.env['ir.cron'].sudo().create(cron_vals)
                cron.write({'code': "model.validate_and_add_budget_line(" + str(self.id) + "," + str(cron.id) + ")"})
                if prev_cron_id:
                    cron.write({'prev_cron_id': prev_cron_id, 'active': False})
                line_records = self.env['control.assigned.amounts.lines'].browse(lines)
                line_records.write({'cron_id': cron.id})
                del line_ids[:5000]
                prev_cron_id = cron.id

    def validate(self):
        vals_list = []
        # total_assigned_amount = sum(self.success_line_ids.mapped('authorized'))
        # total_budget_amount = sum(self.budget_id.success_line_ids.mapped('authorized'))
        # if total_assigned_amount != total_budget_amount:
        #     raise ValidationError("Authorized amount not matched with budget!")
        for line in self.success_line_ids:
            vals = {
                'program_code_id': line.program_code_id.id,
                'start_date': line.start_date,
                'end_date': line.end_date,
                # 'authorized': line.authorized,
                'assigned': line.assigned,
                # 'available': line.available,
                'imported': line.imported,
                'imported_sessional': True,
                'state': line.state,
                'year': line.year,
                'program': line.program,
                'subprogram': line.subprogram,
                'dependency': line.dependency,
                'subdependency': line.subdependency,
                'item': line.item,
                'dv': line.dv,
                'origin_resource': line.origin_resource,
                'ai': line.ai,
                'conversion_program': line.conversion_program,
                'departure_conversion': line.departure_conversion,
                'expense_type': line.expense_type,
                'location': line.location,
                'portfolio': line.portfolio,
                'project_type': line.project_type,
                'project_number': line.project_number,
                'stage': line.stage,
                'agreement_type': line.agreement_type,
                'agreement_number': line.agreement_number,
                'exercise_type': line.exercise_type,
            }
            vals_list.append((0, 0, vals))
        self.budget_id.write({'success_line_ids': vals_list})
        self.state = 'validated'

    def reject(self):
        self.state = 'rejected'

    def unlink(self):
        for Camount in self:
            if Camount.state not in ('draft', 'process'):
                raise ValidationError(
                    'You can not delete processed Control of Assigned Amounts!')
        return super(ControlAssignedAmounts, self).unlink()


class ControlAssignedAmountsLines(models.Model):

    _name = 'control.assigned.amounts.lines'
    _description = 'Control Assigned Amounts Lines'
    _rec_name = 'program_code_id'

    program_code_id = fields.Many2one('program.code', string='Code program')

    start_date = fields.Date(string='Start date')
    end_date = fields.Date(string='End date')

    # authorized = fields.Integer(string='Authorized')
    assigned = fields.Integer(string='Assigned')
    available = fields.Integer(string='Available')
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id)

    assigned_amount_id = fields.Many2one(
        'control.assigned.amounts', string='Assigned amount')
    budget_id = fields.Many2one('expenditure.budget', string='Budget')

    imported = fields.Boolean()
    state = fields.Selection([('manual', 'Manual'), ('draft', 'Draft'), (
        'fail', 'Fail'), ('success', 'Success')], string='Status', default='manual')

    # Fields for imported data
    year = fields.Char(string='Year')
    program = fields.Char(string='Program')
    subprogram = fields.Char(string='Sub-Program')
    dependency = fields.Char(string='Dependency')
    subdependency = fields.Char(string='Sub-Dependency')
    item = fields.Char(string='Expense Item')
    dv = fields.Char(string='Digit Varification')
    origin_resource = fields.Char(string='Origin Resource')
    ai = fields.Char(string='Institutional Activity')
    conversion_program = fields.Char(string='Conversion Program')
    departure_conversion = fields.Char(string='Federal Item')
    expense_type = fields.Char(string='Expense Type')
    location = fields.Char(string='State Code')
    portfolio = fields.Char(string='Key portfolio')
    project_type = fields.Char(string='Type of Project')
    project_number = fields.Char(string='Project Number')
    stage = fields.Char(string='Stage Identifier')
    agreement_type = fields.Char(string='Type of Agreement')
    agreement_number = fields.Char(string='Agreement number')
    exercise_type = fields.Char(string='Exercise type')
    cron_id = fields.Many2one('ir.cron', string="CRON ID")

    @api.onchange('program_code_id')
    def onchange_program_code_id(self):
        if self.program_code_id:
            code = self.program_code_id
            self.year = code.year and code.year.name or ''
            self.program = code.program_id and code.program_id.key_unam or ''
            self.subprogram = code.sub_program_id and code.sub_program_id.sub_program or ''
            self.dependency = code.dependency_id and code.dependency_id.dependency or ''
            self.subdependency = code.sub_dependency_id and code.sub_dependency_id.sub_dependency or ''
            self.item = code.item_id and code.item_id.item or ''
            self.dv = code.check_digit
            self.ai = code.institutional_activity_id and code.institutional_activity_id.number or ''
            self.origin_resource = code.resource_origin_id and code.resource_origin_id.key_origin or ''
            self.conversion_program = code.budget_program_conversion_id and code.budget_program_conversion_id.shcp.name or ''
            self.departure_conversion = code.conversion_item_id and code.conversion_item_id.federal_part or ''
            self.expense_type = code.expense_type_id and code.expense_type_id.key_expenditure_type or ''
            self.location = code.location_id and code.location_id.state_key or ''
            self.portfolio = code.portfolio_id and code.portfolio_id.wallet_password or ''
            self.project_type = code.project_type_id and code.project_type_id.project_type_identifier or ''
            self.project_number = code.project_number
            if code.stage_id and code.stage_id.stage_identifier:
                self.stage = code.stage_id.stage_identifier
            if code.agreement_type_id and code.agreement_type_id.agreement_type:
                self.agreement_type = code.agreement_type_id.agreement_type
            self.agreement_number = code.number_agreement

    _sql_constraints = [
        ('unique_assigned_amount_id_program_code', 'unique(program_code_id,assigned_amount_id)', 'The program code must be unique per Control of Assigned Amounts')]

    @api.onchange('assigned')
    def onchange_assigned(self):
        if self.assigned:
            self.available = self.assigned

    def write(self, vals):
        if vals.get('assigned'):
            for line in self:
                line.available = vals.get('assigned')
        return super(ControlAssignedAmountsLines, self).write(vals)
