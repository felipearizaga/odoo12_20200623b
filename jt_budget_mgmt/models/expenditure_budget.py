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
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class ExpenditureBudget(models.Model):

    _name = 'expenditure.budget'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Expenditure Budget'
    _rec_name = 'name'

    def _get_count(self):
        for record in self:
            record.record_number = len(record.success_line_ids)
            record.import_record_number = len(
                record.success_line_ids.filtered(lambda l: l.imported == True))

    # Fields For Header
    name = fields.Text(string='Budget name', required=True, tracking=True,
                       states={'validate': [('readonly', True)]})

    _sql_constraints = [
        ('uniq_budget_name', 'unique(name)',
         'The Budget name must be unique!'),
    ]

    user_id = fields.Many2one('res.users', string='Responsible',
                              default=lambda self: self.env.user, tracking=True,
                              states={'validate': [('readonly', True)]})

    # Date Periods
    from_date = fields.Date(string='From', states={
                            'validate': [('readonly', True)]}, tracking=True)
    to_date = fields.Date(string='To', states={
                          'validate': [('readonly', True)]}, tracking=True)

    def _compute_total_budget(self):
        for budget in self:
            budget.total_budget = sum(
                budget.success_line_ids.mapped('assigned'))

    total_budget = fields.Float(
        string='Total budget', tracking=True, compute="_compute_total_budget")
    record_number = fields.Integer(
        string='Number of records', compute='_get_count')
    import_record_number = fields.Integer(
        string='Number of imported records', readonly=True, compute='_get_count')

    def _compute_total_quarter_budget(self):
        for budget in self:
            total_quarter_budget = 0
            for line in budget.success_line_ids:
                if line.start_date and line.start_date.day == 1 and line.start_date.month == 1 and line.end_date and line.end_date.month == 3:
                    total_quarter_budget += line.assigned
            budget.total_quarter_budget = total_quarter_budget

    total_quarter_budget = fields.Float(
        string='Total 1st Quarter', tracking=True, compute="_compute_total_quarter_budget")
    journal_id = fields.Many2one('account.journal')
    move_line_ids = fields.One2many('account.move.line', 'budget_id', string="Journal Items")

    @api.model
    def default_get(self, fields):
        res = super(ExpenditureBudget, self).default_get(fields)
        budget_app_jou = self.env.ref('jt_conac.budget_appr_jour')
        if budget_app_jou:
            res.update({'journal_id': budget_app_jou.id})
        return res


    def _get_imported_lines_count(self):
        for record in self:
            record.imported_lines_count = len(record.line_ids)
            record.success_lines_count = len(record.success_line_ids)

    @api.depends('success_line_ids','success_line_ids.assigned', 'success_line_ids.authorized','success_line_ids.available')
    def _compute_amt_total(self):
        """
        This function will count the total of all success rows
        :return:
        """
        for budget in self:
            assigned_total = 0
            authorised_total = 0
            available_total = 0
            for line in budget.success_line_ids:
                assigned_total += line.assigned
                authorised_total += line.authorized
                available_total += line.available

            budget.assigned_total = assigned_total
            budget.authorised_total = authorised_total
            budget.available_total = available_total

    assigned_total = fields.Float("Assigned Total", tracking=True, compute="_compute_amt_total", store=True)
    authorised_total = fields.Float("Authorised Total", tracking=True, compute="_compute_amt_total", store=True)
    available_total = fields.Float("Available Total", tracking=True, compute="_compute_amt_total", store=True)
    # Budget Lines
    line_ids = fields.One2many(
        'expenditure.budget.line', 'expenditure_budget_id',
        string='Expenditure Budget Lines', states={'validate': [('readonly', True)]}, domain=[('state', '!=', 'success')])
    success_line_ids = fields.One2many(
        'expenditure.budget.line', 'expenditure_budget_id',
        string='Expenditure Budget Lines', domain=[('state', '=', 'success')])

    state = fields.Selection([
        ('draft', 'Draft'),
        ('previous', 'Previous'),
        ('confirm', 'Confirm'),
        ('validate', 'Validate'),
        ('done', 'Done')], default='draft', required=True, string='State', tracking=True)

    imported_lines_count = fields.Integer(
        string='Imported Lines', compute='_get_imported_lines_count')
    success_lines_count = fields.Integer(
        string='Success Lines', compute='_get_imported_lines_count')

    def _compute_total_rows(self):
        for budget in self:
            budget.draft_rows = self.env['expenditure.budget.line'].search_count(
                [('expenditure_budget_id', '=', budget.id), ('state', 'in', ['draft', 'manual'])])
            budget.failed_rows = self.env['expenditure.budget.line'].search_count(
                [('expenditure_budget_id', '=', budget.id), ('state', '=', 'fail')])
            budget.success_rows = self.env['expenditure.budget.line'].search_count(
                [('expenditure_budget_id', '=', budget.id), ('state', '=', 'success')])
            budget.total_rows = self.env['expenditure.budget.line'].search_count(
                [('expenditure_budget_id', '=', budget.id)])

    # Rows Progress Tracking Details
    cron_running = fields.Boolean(string='Running CRON?')
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

    @api.constrains('from_date', 'to_date')
    def _check_dates(self):
        if self.from_date and self.to_date:
            if self.from_date > self.to_date:
                raise ValidationError("Please select correct date")

    def import_lines(self):
        ctx = self.env.context.copy()
        if self._context.get('reimport'):
            ctx['reimport'] = True
        return {
            'name': "Import Budget Lines",
            'type': 'ir.actions.act_window',
            'res_model': 'import.line',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(False, 'form')],
            'target': 'new',
            'context': ctx,
        }

    def send_notification_msg(self, user, failed, successed):
        ch_obj = self.env['mail.channel']
        base_user = self.env.ref('base.user_root')
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = base_url + '/web#id=%s&view_type=form&model=expenditure.budget' % (self.id)
        body = (_("Budget Validation Process is Completed for \
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

    def validate_and_add_budget_line(self, record_id=False, cron_id=False):
        if record_id:
            self = self.env['expenditure.budget'].browse(int(record_id))

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
                    lines_to_execute = self.env['expenditure.budget.line'].search(
                        [('cron_id', '=', cron.id)])

            for line in lines_to_execute:
                if counter == 5000:
                    break
                counter += 1
                line_vals = [line.year, line.program, line.subprogram, line.dependency, line.subdependency, line.item,
                             line.dv, line.origin_resource, line.ai, line.conversion_program,
                             line.departure_conversion, line.expense_type, line.location, line.portfolio,
                             line.project_type, line.project_number, line.stage, line.agreement_type,
                             line.agreement_number, line.exercise_type]

                if line.state == 'manual' or line.program_code_id:
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
                    try:
                        authorized_amount = float(line.authorized)
                        if authorized_amount <= 0:
                            failed_row += str(line_vals) + \
                                "------>> Authorized Amount should be greater than 0!"
                            failed_line_ids.append(line.id)
                            continue
                    except:
                        failed_row += str(line_vals) + \
                            "------>> Invalid Authorized Amount Format"
                        failed_line_ids.append(line.id)
                        continue
                    line.state = 'success'

                if line.state in ['fail', 'draft']:

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
                        # if asigned_amount == 0:
                        #     failed_row += str(line_vals) + \
                        #         "------>> Assigned Amount should be greater than 0!"
                        #     failed_line_ids.append(line.id)
                        #     continue
                    except:
                        failed_row += str(line_vals) + \
                            "------>> Invalid Asigned Amount Format \n"
                        failed_line_ids.append(line.id)
                        continue

                    # Validation Authorized Amount
                    authorized_amount = 0
                    try:
                        authorized_amount = float(line.authorized)
                        if authorized_amount == 0:
                            failed_row += str(line_vals) + \
                                "------>> Authorized Amount should be greater than 0! \n"
                            failed_line_ids.append(line.id)
                            continue
                    except:
                        failed_row += str(line_vals) + \
                            "------>> Invalid Authorized Amount Format \n"
                        failed_line_ids.append(line.id)
                        continue


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

                            if program_code and program_code.state == 'validated':
                                failed_row += str(line_vals) + \
                                    "------>> Duplicated Program Code Found!"
                                failed_line_ids.append(line.id)
                                continue
                            if program_code and program_code.state == 'draft':
                                budget_line = self.env['expenditure.budget.line'].search([('program_code_id', '=', program_code.id), (
                                    'start_date', '=', line.start_date), ('end_date', '=', line.end_date)], limit=1)
                                if budget_line:
                                    failed_row += str(line_vals) + \
                                        "------>> Program Code Already Linked With Budget Line With Selected Start/End Date! \n"
                                    failed_line_ids.append(line.id)
                                    continue

                        if not program_code:
                            program_vals = {
                                'year': year.id,
                                'program_id': program.id,
                                'sub_program_id': subprogram.id,
                                'dependency_id': dependency.id,
                                'sub_dependency_id': subdependency.id,
                                'item_id': item.id,
                                'resource_origin_id': origin_resource.id,
                                'institutional_activity_id': institutional_activity.id,
                                'budget_program_conversion_id': shcp.id,
                                'conversion_item_id': conversion_item.id,
                                'expense_type_id': expense_type.id,
                                'location_id': geo_location.id,
                                'portfolio_id': wallet_key.id,
                                'project_type_id': project_type.id,
                                'stage_id': stage.id,
                                'agreement_type_id': agreement_type.id,
                            }
                            program_code = self.env['program.code'].sudo().create(
                                program_vals)
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
                            "------>> Row Data Are Not Corrected or Duplicated Program Code Found! \n"
                        failed_line_ids.append(line.id)
                        continue

            failed_lines = self.env['expenditure.budget.line'].search(
                [('expenditure_budget_id', '=', self.id), ('id', 'in', failed_line_ids)])
            success_lines = self.env['expenditure.budget.line'].search(
                [('expenditure_budget_id', '=', self.id), ('id', 'in', success_line_ids)])
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
                if cron:
                    content = ''
                content += "\n"
                content += "...................Failed Rows " + \
                    str(datetime.today()) + "...............\n"
                content += str(failed_row)
                failed_data = base64.b64encode(content.encode('utf-8'))
                vals['failed_row_file'] = failed_data

            if cron:
                lines_to_execute.write({'cron_id': False})
                model_id = self.env.ref(
                    'jt_budget_mgmt.model_expenditure_budget').id
                next_cron = self.env['ir.cron'].sudo().search([('prev_cron_id', '=', cron.id),
                                                               ('active', '=', False),
                                                               ('model_id', '=', model_id)], limit=1)
                if next_cron:
                    nextcall = datetime.now()
                    nextcall = nextcall + timedelta(seconds=10)
                    next_cron.write({'nextcall': nextcall, 'active': True})
                else:
                    failed_count = sucess_count = 0
                    if self.line_ids:
                        failed_count = len(self.line_ids.ids)
                    if self.success_line_ids:
                        sucess_count = len(self.success_line_ids)
                    self.send_notification_msg(self.user_id, failed_count, sucess_count)
                    self.user_id.notify_info(
                        message='Budget - ' + str(self.name) + ' Lines validation process completed. \
                                                               Please verify and correct lines, if any failed!',
                        title="Budget Line Validation", sticky=True)
                    self.write({'cron_running': False})
                    if len(self.line_ids.ids) == 0:
                        self.write({'state': 'previous'})
                    msg = (_("Budget Validation Process Ended at %s" % datetime.strftime(
                    datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)))
                    self.env['mail.message'].create({'model': 'expenditure.budget', 'res_id': self.id,
                                                     'body': msg})

            if vals.get('failed_row_file'):
                self.write(vals)


    def remove_cron_records(self):
        crons = self.env['ir.cron'].sudo().search(
            [('model_id', '=', self.env.ref('jt_budget_mgmt.model_expenditure_budget').id)])
        for cron in crons:
            if cron.budget_id and not cron.budget_id.cron_running:
                try:
                    cron.sudo().unlink()
                except:
                    pass

    def verify_data(self):
        total = sum(self.success_line_ids.mapped('assigned'))
        if total <= 0:
            raise ValidationError("Budget amount should be greater than 0")
        if len(self.success_line_ids.ids) == 0:
            raise ValidationError("Please correct failed rows")
        # if self.total_rows > 0 and self.success_rows != self.total_rows:
        #     raise ValidationError("Please correct failed rows")
        return True

    def previous_budget(self):
        # Total CRON to create
        msg = (_("Budget Validation Process Started at %s" % datetime.strftime(
            datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)))
        self.env['mail.message'].create({'model': 'expenditure.budget', 'res_id': self.id,
                             'body': msg})
        if self.line_ids:
            total_cron = math.ceil(len(self.line_ids.ids) / 5000)
        else:
            total_cron = math.ceil(len(self.success_line_ids.ids) / 5000)
        if total_cron != 0:
            if total_cron == 1:
                if self.success_rows != self.total_rows:
                    self.validate_and_add_budget_line()
                total_lines = len(self.success_line_ids.filtered(
                    lambda l: l.state == 'success'))
                if total_lines == self.total_rows:
                    self.state = 'previous'
                msg = (_("Budget Validation Process Ended at %s" % datetime.strftime(
                    datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)))
                self.env['mail.message'].create({'model': 'expenditure.budget', 'res_id': self.id,
                                                 'body': msg})
            else:
                self.write({'cron_running': True})
                prev_cron_id = False
                line_ids = self.line_ids.ids
                for seq in range(1, total_cron + 1):

                    # Create CRON JOB
                    cron_name = str(self.name).replace(' ', '') + \
                        "_" + str(datetime.now()).replace(' ', '')
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
                        'model_id': self.env.ref('jt_budget_mgmt.model_expenditure_budget').id,
                        'user_id': self.env.user.id,
                        'budget_id': self.id
                    }

                    # Final process
                    cron = self.env['ir.cron'].sudo().create(cron_vals)
                    cron.write({'code': "model.validate_and_add_budget_line(" +
                                str(self.id) + "," + str(cron.id) + ")"})
                    if prev_cron_id:
                        cron.write({'prev_cron_id': prev_cron_id, 'active': False})
                    line_records = self.env['expenditure.budget.line'].browse(
                        lines)
                    line_records.write({'cron_id': cron.id})
                    del line_ids[:5000]
                    prev_cron_id = cron.id

    def confirm(self):
        self.verify_data()
        self.write({'state': 'confirm'})

    def approve(self):
        self.verify_data()
        if self.journal_id:
            move_obj = self.env['account.move']
            journal = self.journal_id
            today = datetime.today().date()
            budget_id = self.id
            user = self.env.user
            partner_id = user.partner_id.id
            amount = sum(self.success_line_ids.mapped('authorized'))
            company_id = user.company_id.id
            if not journal.default_debit_account_id or not journal.default_credit_account_id \
                or not journal.conac_debit_account_id or not journal.conac_credit_account_id:
                raise ValidationError(_("Please configure UNAM and CONAC account in budget journal!"))
            unam_move_val = {'ref': self.name, 'budget_id': budget_id, 'conac_move': True,
                             'date': today, 'journal_id': journal.id, 'company_id': company_id,
                             'line_ids': [(0, 0, {
                                 'account_id': journal.default_credit_account_id.id,
                                 'coa_conac_id': journal.conac_credit_account_id.id,
                                 'credit': amount, 'budget_id': budget_id,
                                 'partner_id': partner_id
                             }), (0, 0, {
                                 'account_id': journal.default_debit_account_id.id,
                                 'coa_conac_id': journal.conac_debit_account_id.id,
                                 'debit': amount, 'budget_id': budget_id,
                                 'partner_id': partner_id
                             })]}
            unam_move = move_obj.create(unam_move_val)
            unam_move.action_post()
        self.success_line_ids.mapped('program_code_id').write(
            {'state': 'validated', 'budget_id': self.id})
        self.write({'state': 'validate'})

    def reject(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'reject',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(False, 'form')],
            'target': 'new',
        }

    def unlink(self):
        if not self._context.get('from_wizard'):
            for budget in self:
                if budget.state not in ('draft', 'previous'):
                    raise ValidationError(
                        'You can not delete processed budget!')
        return super(ExpenditureBudget, self).unlink()

    def show_imported_lines(self):
        action = self.env.ref(
            'jt_budget_mgmt.action_expenditure_budget_imported_line').read()[0]
        action['limit'] = 1000
        action['domain'] = [('id', 'in', self.line_ids.ids)]
        action['search_view_id'] = (self.env.ref(
            'jt_budget_mgmt.expenditure_budget_imported_line_search_view').id, )
        return action

    def show_success_lines(self):
        action = self.env.ref(
            'jt_budget_mgmt.action_expenditure_budget_success_line').read()[0]
        action['limit'] = 1000
        action['domain'] = [('id', 'in', self.success_line_ids.ids)]
        action['search_view_id'] = (self.env.ref(
            'jt_budget_mgmt.expenditure_budget_success_line_search_view').id, )
        return action


class ExpenditureBudgetLine(models.Model):

    _name = 'expenditure.budget.line'
    _description = 'Expenditure Budget Line'
    _rec_name = 'program_code_id'

    expenditure_budget_id = fields.Many2one(
        'expenditure.budget', string='Expenditure Budget', ondelete="cascade")

    start_date = fields.Date(
        string='Start date')
    end_date = fields.Date(
        string='End date')

    authorized = fields.Float(
        string='Authorized')
    assigned = fields.Float(
        string='Assigned')
    available = fields.Float(
        string='Available')
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id)

    program_code_id = fields.Many2one('program.code', string='Program code')
    program_id = fields.Many2one(
        'program', string='Program', related="program_code_id.program_id")
    dependency_id = fields.Many2one(
        'dependency', string='Dependency', related="program_code_id.dependency_id")
    sub_dependency_id = fields.Many2one(
        'sub.dependency', string='Sub-Dependency', related="program_code_id.sub_dependency_id")
    item_id = fields.Many2one(
        'expenditure.item', string='Item', related="program_code_id.item_id")

    imported = fields.Boolean()
    state = fields.Selection([('manual', 'Manual'), ('draft', 'Draft'), (
        'fail', 'Fail'), ('success', 'Success')], string='Status', default='manual')
    imported_sessional = fields.Boolean()

    # Fields for imported data
    year = fields.Char(string='Year')
    program = fields.Char(string='Program')
    subprogram = fields.Char(string='Sub-Program')
    dependency = fields.Char(string='Dependency')
    subdependency = fields.Char(string='Sub-Dependency')
    item = fields.Char(string='Expense Item')
    dv = fields.Char(string='Digit Verification')
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

    _sql_constraints = [
        ('uniq_quarter', 'unique(program_code_id,start_date,end_date)',
         'The Program code must be unique per quarter!'),
    ]

    @api.onchange('assigned')
    def onchange_assigned(self):
        if self.assigned:
            self.available = self.assigned

    def write(self, vals):
        if vals.get('assigned'):
            for line in self:
                line.available = vals.get('assigned')
        return super(ExpenditureBudgetLine, self).write(vals)

    @api.model
    def create(self, vals):
        res = super(ExpenditureBudgetLine, self).create(vals)
        if res and res.assigned:
            res.available = res.assigned
        return res

    # ALTER TABLE expenditure_budget_line DROP CONSTRAINT expenditure_budget_line_uniq_program_code_id;
