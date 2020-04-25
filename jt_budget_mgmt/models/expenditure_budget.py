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
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


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
                            'validate': [('readonly', True)]})
    to_date = fields.Date(string='To', states={
                          'validate': [('readonly', True)]})

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

    # Budget Lines
    line_ids = fields.One2many(
        'expenditure.budget.line', 'expenditure_budget_id',
        string='Expenditure Budget Lines', states={'validate': [('readonly', True)]}, domain=[('state', '!=', 'success')])
    success_line_ids = fields.One2many(
        'expenditure.budget.line', 'expenditure_budget_id',
        string='Expenditure Budget Lines', states={'validate': [('readonly', True)]}, domain=[('state', '=', 'success')])

    state = fields.Selection([
        ('draft', 'Draft'),
        ('previous', 'Previous'),
        ('confirm', 'Confirm'),
        ('validate', 'Validate'),
        ('done', 'Done')], default='draft', required=True, string='State', tracking=True)

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

    def validate_and_add_budget_line(self):
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

            for line in self.line_ids:
                if counter == 10000:
                    break
                counter += 1
                line_vals = [line.year, line.program, line.subprogram, line.dependency, line.subdependency, line.item, line.dv, line.origin_resource, line.ai, line.conversion_program,
                             line.departure_conversion, line.expense_type, line.location, line.portfolio, line.project_type, line.project_number, line.stage, line.agreement_type, line.agreement_number, line.exercise_type]

                if line.state == 'manual' or line.program_code_id:
                    # Validation Importe 1a Asignacion
                    asigned_amount = 0
                    try:
                        asigned_amount = float(line.assigned)
                        if asigned_amount == 0:
                            failed_row += str(line_vals) + \
                                "------>> Assigned Amount should be greater than 0!"
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
                        if authorized_amount == 0:
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
                        if asigned_amount == 0:
                            failed_row += str(line_vals) + \
                                "------>> Assigned Amount should be greater than 0!"
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
                        if authorized_amount == 0:
                            failed_row += str(line_vals) + \
                                "------>> Authorized Amount should be greater than 0!"
                            failed_line_ids.append(line.id)
                            continue
                    except:
                        failed_row += str(line_vals) + \
                            "------>> Invalid Authorized Amount Format"
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
                                # ('state', '=', 'validated'),
                            ], limit=1)

                            if program_code and program_code.state == 'validated':
                                failed_row += str(line_vals) + \
                                    "------>> Duplicated Program Code Found!"
                                failed_line_ids.append(line.id)
                                continue
                            if program_code and program_code.state == 'draft':
                                budget_line = self.env['expenditure.budget.line'].search([('program_code_id', '=', program_code.id)], limit=1)
                                if budget_line:
                                    failed_row += str(line_vals) + \
                                        "------>> Program Code Already Linked With Budget Line!"
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
                            self._cr.commit()
                        if program_code:
                            line.program_code_id = program_code.id
                            success_line_ids.append(line.id)
                    except:
                        failed_row += str(line_vals) + \
                            "------>> Row Data Are Not Corrected or Duplicated Program Code Found!"
                        failed_line_ids.append(line.id)
                        continue

            failed_lines = self.env['expenditure.budget.line'].search(
                [('expenditure_budget_id', '=', self.id), ('id', 'in', failed_line_ids)])
            success_lines = self.env['expenditure.budget.line'].search(
                [('expenditure_budget_id', '=', self.id), ('id', 'in', success_line_ids)])
            success_lines.write({'state': 'success'})
            self._cr.commit()
            for l in failed_lines:
                if l.state == 'draft':
                    l.state = 'fail'

            failed_data = False
            if failed_row != "":
                vals = {}
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
                self.write(vals)

            if len(failed_line_ids) == 0:
                return{
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'All rows are imported successfully!',
                        'type': 'rainbow_man',
                    }
                }

    def verify_data(self):
        total = sum(self.success_line_ids.mapped('assigned'))
        if total <= 0:
            raise ValidationError("Budget amount should be greater than 0")
        if len(self.success_line_ids.ids) == 0:
            raise ValidationError("Please correct failed rows")
        if self.total_rows > 0 and self.success_rows != self.total_rows:
            raise ValidationError("Please correct failed rows")
        return True

    def previous_budget(self):
        if self.success_rows != self.total_rows:
            self.validate_and_add_budget_line()
        total_lines = len(self.success_line_ids.filtered(lambda l: l.state == 'success'))
        if total_lines == self.total_rows:
            # self.verify_data()
            self.write({'state': 'previous'})

    def confirm(self):
        self.verify_data()
        self.write({'state': 'confirm'})

    def approve(self):
        self.verify_data()
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


class ExpenditureBudgetLine(models.Model):

    _name = 'expenditure.budget.line'
    _description = 'Expenditure Budget Line'
    _rec_name = 'program_code_id'

    expenditure_budget_id = fields.Many2one(
        'expenditure.budget', string='Expenditure Budget', ondelete="cascade")

    start_date = fields.Date(
        string='Start date', related="expenditure_budget_id.from_date")
    end_date = fields.Date(
        string='End date', related="expenditure_budget_id.to_date")

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

    _sql_constraints = [
        ('uniq_program_code_id', 'unique(program_code_id)',
         'The Program code must be unique!'),
    ]
