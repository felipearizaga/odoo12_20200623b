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
from datetime import datetime
from odoo import models, fields, api, _


class ProformaBudgetSummaryReport(models.AbstractModel):
    _name = "proforma.budget.summary.report"
    _inherit = "account.report"
    _description = "Proforma Budget Summary"

    filter_journals = None
    filter_multi_company = True
    filter_date = {'mode': 'range', 'filter': 'this_month'}
    filter_all_entries = None
    filter_comparison = None
    filter_journals = None
    filter_analytic = None
    filter_unfold_all = None
    filter_hierarchy = None
    filter_partner = None

    # Custom filters
    filter_line_pages = None
    filter_budget_control = None
    filter_program_code_section = None

    # Set columns based on dynamic options
    def _get_columns_name(self, options):
        column_list = []
        column_list.append({'name': _("Program Code")})

        # Add program code structure fields
        for column in options['selected_program_fields']:
            column_list.append({'name': _(column)})

        for column in options['selected_budget_control']:
            column_list.append({'name': _(column)})
        return column_list

    @api.model
    def _init_filter_line_pages(self, options, previous_options=None):
        options['line_pages'] = []
        budget_lines = self.env['expenditure.budget.line'].search(
            [('expenditure_budget_id.state', '=', 'validate')])

        pages = round(len(budget_lines) / 3)
        line_list = []
        for page in range(1, pages + 1):
            line_list.append(page)

        list_labels = self._context.get('lines_data', line_list)
        counter = 1

        if previous_options and previous_options.get('line_pages'):
            line_pages_map = dict((opt['id'], opt['selected'])
                                  for opt in previous_options['line_pages'] if opt['id'] != 'divider' and 'selected' in opt)
        else:
            line_pages_map = {}

        options['selected_line_pages'] = []
        for label in list_labels:
            options['line_pages'].append({
                'id': str(counter),
                'name': str(label),
                'code': str(label),
                'selected': line_pages_map.get(str(counter)),
            })
            if line_pages_map.get(str(counter)):
                options['selected_line_pages'].append(str(label))
            counter += 1

    @api.model
    def _init_filter_budget_control(self, options, previous_options=None):
        options['budget_control'] = []
        list_labels = ['Authorized', 'Assigned', 'Annual Modified',
                       'Per Exercise', 'Committed', 'Accrued', 'Exercised', 'Paid', 'Available']
        counter = 1

        if previous_options and previous_options.get('budget_control'):
            budget_control_map = dict((opt['id'], opt['selected'])
                                      for opt in previous_options['budget_control'] if opt['id'] != 'divider' and 'selected' in opt)
        else:
            budget_control_map = {}

        options['selected_budget_control'] = []
        for label in list_labels:
            options['budget_control'].append({
                'id': str(counter),
                'name': str(label),
                'code': str(label),
                'selected': budget_control_map.get(str(counter)),
            })
            if budget_control_map.get(str(counter)):
                options['selected_budget_control'].append(str(label))
            counter += 1

    @api.model
    def _init_filter_program_code_section(self, options, previous_options=None):
        options['code_sections'] = previous_options and previous_options.get(
            'code_sections') or []
        program_fields_ids = [int(acc) for acc in options['code_sections']]
        selected_program_fields = program_fields_ids \
            and self.env['report.program.fields'].browse(program_fields_ids) \
            or self.env['report.program.fields']
        options['selected_program_fields'] = selected_program_fields.mapped(
            'name')

        # Program Section filter
        options['section_program'] = previous_options and previous_options.get(
            'section_program') or []
        program_ids = [int(acc) for acc in options['section_program']]
        selected_programs = program_ids \
            and self.env['program'].browse(program_ids) \
            or self.env['program']
        options['selected_programs'] = selected_programs.mapped('key_unam')

        # Sub Program Section filter
        options['section_sub_program'] = previous_options and previous_options.get(
            'section_sub_program') or []
        sub_program_ids = [int(acc) for acc in options['section_sub_program']]
        selected_sub_programs = sub_program_ids \
            and self.env['sub.program'].browse(sub_program_ids) \
            or self.env['sub.program']
        options['selected_sub_programs'] = selected_sub_programs.mapped(
            'sub_program')

        # Dependency Section filter
        options['section_dependency'] = previous_options and previous_options.get(
            'section_dependency') or []
        dependency_ids = [int(acc) for acc in options['section_dependency']]
        selected_dependency = dependency_ids \
            and self.env['dependency'].browse(dependency_ids) \
            or self.env['dependency']
        options['selected_dependency'] = selected_dependency.mapped(
            'dependency')

        # Sub Dependency Section filter
        options['section_sub_dependency'] = previous_options and previous_options.get(
            'section_sub_dependency') or []
        sub_dependency_ids = [int(acc)
                              for acc in options['section_sub_dependency']]
        selected_sub_dependency = sub_dependency_ids \
            and self.env['sub.dependency'].browse(sub_dependency_ids) \
            or self.env['sub.dependency']
        options['selected_sub_dependency'] = selected_sub_dependency.mapped(
            'sub_dependency')

        # Expense Item filter
        options['section_expense_item'] = previous_options and previous_options.get(
            'section_expense_item') or []
        item_ids = [int(acc) for acc in options['section_expense_item']]
        selected_items = item_ids \
            and self.env['expenditure.item'].browse(item_ids) \
            or self.env['expenditure.item']
        options['selected_items'] = selected_items.mapped('item')

        # Origin Resource filter
        options['section_or'] = previous_options and previous_options.get(
            'section_or') or []
        or_ids = [int(acc) for acc in options['section_or']]
        selected_origins = or_ids \
            and self.env['resource.origin'].browse(or_ids) \
            or self.env['resource.origin']
        options['selected_or'] = selected_origins.mapped('key_origin')

        # Institutional Activity filter
        options['section_ai'] = previous_options and previous_options.get(
            'section_ai') or []
        ai_ids = [int(acc) for acc in options['section_ai']]
        selected_acitvities = ai_ids \
            and self.env['institutional.activity'].browse(ai_ids) \
            or self.env['institutional.activity']
        options['selected_ai'] = selected_acitvities.mapped('number')

        # Budget Program Conversion (CONPP) filter
        options['section_conpp'] = previous_options and previous_options.get(
            'section_conpp') or []
        conpp_ids = [int(acc) for acc in options['section_conpp']]
        selected_conpp = conpp_ids \
            and self.env['budget.program.conversion'].browse(conpp_ids) \
            or self.env['budget.program.conversion']
        options['selected_conpp'] = selected_conpp.mapped(
            'shcp').mapped('name')

        # SHCP Games (CONPA) filter
        options['section_conpa'] = previous_options and previous_options.get(
            'section_conpa') or []
        conpa_ids = [int(acc) for acc in options['section_conpa']]
        selected_conpa = conpa_ids \
            and self.env['departure.conversion'].browse(conpa_ids) \
            or self.env['departure.conversion']
        options['selected_conpa'] = selected_conpa.mapped('federal_part')

        # Type of Expense (TG) filter
        options['section_expense'] = previous_options and previous_options.get(
            'section_expense') or []
        expense_ids = [int(acc) for acc in options['section_expense']]
        selected_expenses = expense_ids \
            and self.env['expense.type'].browse(expense_ids) \
            or self.env['expense.type']
        options['selected_expenses'] = selected_expenses.mapped(
            'key_expenditure_type')

        # Geographic Location (UG) filter
        options['section_ug'] = previous_options and previous_options.get(
            'section_ug') or []
        ug_ids = [int(acc) for acc in options['section_ug']]
        selected_ug = ug_ids \
            and self.env['geographic.location'].browse(ug_ids) \
            or self.env['geographic.location']
        options['selected_ug'] = selected_ug.mapped('state_key')

        # Wallet Key (CC) filter
        options['section_wallet'] = previous_options and previous_options.get(
            'section_wallet') or []
        wallet_ids = [int(acc) for acc in options['section_wallet']]
        selected_wallets = wallet_ids \
            and self.env['key.wallet'].browse(wallet_ids) \
            or self.env['key.wallet']
        options['selected_wallets'] = selected_wallets.mapped(
            'wallet_password')

        # Project Type (TP) filter
        options['section_tp'] = previous_options and previous_options.get(
            'section_tp') or []
        tp_ids = [int(acc) for acc in options['section_tp']]
        selected_tp = tp_ids \
            and self.env['project.type'].browse(tp_ids) \
            or self.env['project.type']
        options['selected_tp'] = selected_tp.mapped('project_type_identifier')

        # Project Number filter
        options['section_pn'] = previous_options and previous_options.get(
            'section_pn') or []
        pn_ids = [int(acc) for acc in options['section_pn']]
        selected_pn = pn_ids \
            and self.env['project.type'].browse(pn_ids) \
            or self.env['project.type']
        options['selected_pn'] = selected_pn.mapped('number')

        # Stage filter
        options['section_stage'] = previous_options and previous_options.get(
            'section_stage') or []
        stage_ids = [int(acc) for acc in options['section_stage']]
        selected_stage = stage_ids \
            and self.env['stage'].browse(stage_ids) \
            or self.env['stage']
        options['selected_stage'] = selected_stage.mapped('stage_identifier')

        # Agreement Type filter
        options['section_agreement_type'] = previous_options and previous_options.get(
            'section_agreement_type') or []
        type_ids = [int(acc) for acc in options['section_agreement_type']]
        selected_type = type_ids \
            and self.env['agreement.type'].browse(type_ids) \
            or self.env['agreement.type']
        options['selected_type'] = selected_type.mapped('agreement_type')

        # Agreement Number filter
        options['section_agreement_number'] = previous_options and previous_options.get(
            'section_agreement_number') or []
        agreement_number_ids = [int(acc)
                                for acc in options['section_agreement_number']]
        selected_agreement_number = agreement_number_ids \
            and self.env['agreement.type'].browse(agreement_number_ids) \
            or self.env['agreement.type']
        options['selected_agreement_number'] = selected_agreement_number.mapped(
            'number_agreement')

    def _get_lines(self, options, line_id=None):
        start = datetime.strptime(
            str(options['date'].get('date_from')), '%Y-%m-%d').date()
        end = datetime.strptime(
            options['date'].get('date_to'), '%Y-%m-%d').date()

        lines = []
        budget_lines = self.env['expenditure.budget.line'].search(
            [('expenditure_budget_id.state', '=', 'validate'), ('start_date', '>=', start), ('end_date', '<=', end)])

        for b_line in budget_lines:
            annual_modified = b_line.authorized + b_line.assigned
            columns = []

            if len(options['selected_programs']) > 0 and str(b_line.program_code_id.program_id.key_unam) not in options['selected_programs']:
                continue
            if len(options['selected_sub_programs']) > 0 and str(b_line.program_code_id.sub_program_id.sub_program) not in options['selected_sub_programs']:
                continue
            if len(options['selected_dependency']) > 0 and str(b_line.program_code_id.dependency_id.dependency) not in options['selected_dependency']:
                continue
            if len(options['selected_sub_dependency']) > 0 and str(b_line.program_code_id.sub_dependency_id.sub_dependency) not in options['selected_sub_dependency']:
                continue
            if len(options['selected_items']) > 0 and str(b_line.program_code_id.item_id.item) not in options['selected_items']:
                continue
            if len(options['selected_or']) > 0 and str(b_line.program_code_id.resource_origin_id.key_origin) not in options['selected_or']:
                continue
            if len(options['selected_ai']) > 0 and str(b_line.program_code_id.institutional_activity_id.number) not in options['selected_ai']:
                continue
            if len(options['selected_conpp']) > 0 and str(b_line.program_code_id.budget_program_conversion_id.shcp.name) not in options['selected_conpp']:
                continue
            if len(options['selected_conpa']) > 0 and str(b_line.program_code_id.conversion_item_id.federal_part) not in options['selected_conpa']:
                continue
            if len(options['selected_expenses']) > 0 and str(b_line.program_code_id.expense_type_id.key_expenditure_type) not in options['selected_expenses']:
                continue
            if len(options['selected_ug']) > 0 and str(b_line.program_code_id.location_id.state_key) not in options['selected_ug']:
                continue
            if len(options['selected_wallets']) > 0 and str(b_line.program_code_id.portfolio_id.wallet_password) not in options['selected_wallets']:
                continue
            if len(options['selected_tp']) > 0 and str(b_line.program_code_id.project_type_id.project_type_identifier) not in options['selected_tp']:
                continue
            if len(options['selected_pn']) > 0 and str(b_line.program_code_id.project_number) not in options['selected_pn']:
                continue
            if len(options['selected_stage']) > 0 and str(b_line.program_code_id.stage_id.stage_identifier) not in options['selected_stage']:
                continue
            if len(options['selected_type']) > 0 and str(b_line.program_code_id.agreement_type_id.agreement_type) not in options['selected_type']:
                continue
            if len(options['selected_agreement_number']) > 0 and str(b_line.program_code_id.number_agreement) not in options['selected_agreement_number']:
                continue

            # Program code struture view fields
            for column in options['selected_program_fields']:
                if column == 'Year':
                    year = b_line.program_code_id.year and b_line.program_code_id.year.name or ''
                    columns.append({'name': str(year)})
                if column == 'Program':
                    program = b_line.program_code_id.program_id and b_line.program_code_id.program_id.key_unam or ''
                    columns.append({'name': str(program)})
                if column == 'Sub Program':
                    subprogram = b_line.program_code_id.sub_program_id and b_line.program_code_id.sub_program_id.sub_program or ''
                    columns.append({'name': str(subprogram)})
                if column == 'Dependency':
                    dependency = b_line.program_code_id.dependency_id and b_line.program_code_id.dependency_id.dependency or ''
                    columns.append({'name': str(dependency)})
                if column == 'Sub Dependency':
                    subdependency = b_line.program_code_id.sub_dependency_id and b_line.program_code_id.sub_dependency_id.sub_dependency or ''
                    columns.append({'name': str(subdependency)})
                if column == 'Expenditure Item':
                    item = b_line.program_code_id.item_id and b_line.program_code_id.item_id.item or ''
                    columns.append({'name': str(item)})
                if column == 'Check Digit':
                    check_digit = b_line.program_code_id.check_digit or ''
                    columns.append({'name': str(check_digit)})
                if column == 'Source of Resource':
                    sor = b_line.program_code_id.resource_origin_id and b_line.program_code_id.resource_origin_id.key_origin or ''
                    columns.append({'name': str(sor)})
                if column == 'Institutional Activity':
                    ai = b_line.program_code_id.institutional_activity_id and b_line.program_code_id.institutional_activity_id.number or ''
                    columns.append({'name': str(ai)})
                if column == 'Conversion of Budgetary Program':
                    conversion = b_line.program_code_id.budget_program_conversion_id and b_line.program_code_id.budget_program_conversion_id.shcp and b_line.program_code_id.budget_program_conversion_id.shcp.name or ''
                    columns.append({'name': str(conversion)})
                if column == 'SHCP items':
                    shcp = b_line.program_code_id.conversion_item_id and b_line.program_code_id.conversion_item_id.federal_part or ''
                    columns.append({'name': str(shcp)})
                if column == 'Type of Expenditure':
                    expense_type = b_line.program_code_id.expense_type_id and b_line.program_code_id.expense_type_id.key_expenditure_type or ''
                    columns.append({'name': str(expense_type)})
                if column == 'Geographic Location':
                    location = b_line.program_code_id.location_id and b_line.program_code_id.location_id.state_key or ''
                    columns.append({'name': str(location)})
                if column == 'Wallet Key':
                    wallet_key = b_line.program_code_id.portfolio_id and b_line.program_code_id.portfolio_id.wallet_password or ''
                    columns.append({'name': str(wallet_key)})
                if column == 'Type of Project':
                    project_type = b_line.program_code_id.project_type_id and b_line.program_code_id.project_type_id.project_type_identifier or ''
                    columns.append({'name': str(project_type)})
                if column == 'Project Number':
                    project_number = b_line.program_code_id.project_number or ''
                    columns.append({'name': str(project_number)})
                if column == 'Stage':
                    stage = b_line.program_code_id.stage_id and b_line.program_code_id.stage_id.stage_identifier or ''
                    columns.append({'name': str(stage)})
                if column == 'Type of Agreement':
                    agreement_type = b_line.program_code_id.agreement_type_id and b_line.program_code_id.agreement_type_id.agreement_type or ''
                    columns.append({'name': str(agreement_type)})
                if column == 'Agreement Number':
                    agreement_number = b_line.program_code_id.number_agreement or ''
                    columns.append({'name': str(agreement_number)})

            for column in options['selected_budget_control']:
                if column == 'Authorized':
                    columns.append({'name': b_line.authorized})
                elif column == 'Assigned':
                    columns.append({'name': b_line.assigned})
                elif column == 'Annual Modified':
                    columns.append({'name': annual_modified})
                elif column == 'Per Exercise':
                    columns.append({'name': 0})
                elif column == 'Committed':
                    columns.append({'name': 0})
                elif column == 'Accrued':
                    columns.append({'name': 0})
                elif column == 'Exercised':
                    columns.append({'name': 0})
                elif column == 'Paid':
                    columns.append({'name': 0})
                elif column == 'Available':
                    columns.append({'name': b_line.available})
            lines.append({
                'id': b_line.id,
                'name': b_line.program_code_id.program_code,
                'columns': columns,
                'level': 0,
                'unfoldable': False,
                'unfolded': True,
            })

        selected_line_pages = options['selected_line_pages']
        all_list = []
        for s in selected_line_pages:
            s = int(s)
            start = (s - 1) * 3 + 1
            end = s * 3
            for i in range(start - 1, end):
                try:
                    all_list.append(lines[i])
                except:
                    pass
        if len(all_list) > 0:
            return all_list
        return lines

    def _get_report_name(self):
        context = self.env.context
        date_report = fields.Date.from_string(context['date_from']) if context.get(
            'date_from') else fields.date.today()
        return '%s_%s_Summary_Report' % (
            date_report.year,
            str(date_report.month).zfill(2))
