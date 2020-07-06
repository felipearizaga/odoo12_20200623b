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

        pages = round(len(budget_lines) / 500)
        line_list = []
        for page in range(1, pages + 1):
            line_list.append(page)

        list_labels = self._context.get('lines_data', line_list)
        counter = 1

        if previous_options and previous_options.get('line_pages'):
            line_pages_map = dict((opt['id'], opt['selected'])
                                  for opt in previous_options['line_pages'] if
                                  opt['id'] != 'divider' and 'selected' in opt)
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
        if self.env.user.lang == 'es_MX':
            list_labels = ['Partida', 'Autorizado', 'Total Asignado Anual', 'Asignado 1er Trimestre',
                           'Asignado 2do Trimestre', 'Asignado 3er Trimestre',
                           'Asignado 4to Trimestre', 'Modificado Anual',
                           'Por Ejercer', 'Comprometido', 'Devengado', 'Ejercido', 'Pagado', 'Disponible']
        else:
            list_labels = ['Expense Item', 'Authorized', 'Assigned Total Annual', 'Assigned 1st Trimester',
                           'Assigned 2nd Trimester', 'Assigned 3rd Trimester',
                           'Assigned 4th Trimester', 'Annual Modified',
                           'Per Exercise', 'Committed', 'Accrued', 'Exercised', 'Paid', 'Available']
        counter = 1

        if previous_options and previous_options.get('budget_control'):
            budget_control_map = dict((opt['id'], opt['selected'])
                                      for opt in previous_options['budget_control'] if
                                      opt['id'] != 'divider' and 'selected' in opt)
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
        b_line_obj = self.env['expenditure.budget.line']
        adequacies_line_obj = self.env['adequacies.lines']
        item_list = {'1': [], '2': [], '3': [], '4': [], '5': [], '6': [], '7': [], '8': [], '9': []}
        budget_lines = self.env['expenditure.budget.line'].search(
            [('expenditure_budget_id.state', '=', 'validate'),
             ('start_date', '>=', start), ('end_date', '<=', end)])
        for li in budget_lines:
            if li.program_code_id and li.program_code_id.item_id:
                key_i = int(li.program_code_id.item_id.item)
                if key_i >= 100 and key_i <= 199:
                    item_list.update({'1': item_list.get('1') + [li]})
                elif key_i >= 200 and key_i <= 299:
                    item_list.update({'2': item_list.get('2') + [li]})
                elif key_i >= 300 and key_i <= 399:
                    item_list.update({'3': item_list.get('3') + [li]})
                elif key_i >= 400 and key_i <= 499:
                    item_list.update({'4': item_list.get('4') + [li]})
                elif key_i >= 500 and key_i <= 599:
                    item_list.update({'5': item_list.get('5') + [li]})
                elif key_i >= 600 and key_i <= 699:
                    item_list.update({'6': item_list.get('6') + [li]})
                elif key_i >= 700 and key_i <= 799:
                    item_list.update({'7': item_list.get('7') + [li]})
                elif key_i >= 800 and key_i <= 899:
                    item_list.update({'8': item_list.get('8') + [li]})
                elif key_i >= 900 and key_i <= 999:
                    item_list.update({'9': item_list.get('9') + [li]})
        program_code_list = []
        need_total = False
        for fc, budget_lines in item_list.items():
            if budget_lines:
                main_id = False
                main_list = []
                for b_line in budget_lines:
                    if not main_id:
                        main_id = b_line
                    if b_line.program_code_id in program_code_list:
                        continue
                    columns = []
                    if len(options['selected_programs']) > 0 and str(b_line.program_code_id.program_id.key_unam) not in \
                            options['selected_programs']:
                        continue
                    if len(options['selected_sub_programs']) > 0 and str(
                            b_line.program_code_id.sub_program_id.sub_program) not in options['selected_sub_programs']:
                        continue
                    if len(options['selected_dependency']) > 0 and str(
                            b_line.program_code_id.dependency_id.dependency) not in options['selected_dependency']:
                        continue
                    if len(options['selected_sub_dependency']) > 0 and str(
                            b_line.program_code_id.sub_dependency_id.sub_dependency) not in options[
                        'selected_sub_dependency']:
                        continue
                    if len(options['selected_items']) > 0 and str(b_line.program_code_id.item_id.item) not in options[
                        'selected_items']:
                        continue
                    if len(options['selected_or']) > 0 and str(
                            b_line.program_code_id.resource_origin_id.key_origin) not in options['selected_or']:
                        continue
                    if len(options['selected_ai']) > 0 and str(
                            b_line.program_code_id.institutional_activity_id.number) not in options['selected_ai']:
                        continue
                    if len(options['selected_conpp']) > 0 and str(
                            b_line.program_code_id.budget_program_conversion_id.shcp.name) not in options[
                        'selected_conpp']:
                        continue
                    if len(options['selected_conpa']) > 0 and str(
                            b_line.program_code_id.conversion_item_id.federal_part) not in options['selected_conpa']:
                        continue
                    if len(options['selected_expenses']) > 0 and str(
                            b_line.program_code_id.expense_type_id.key_expenditure_type) not in options[
                        'selected_expenses']:
                        continue
                    if len(options['selected_ug']) > 0 and str(b_line.program_code_id.location_id.state_key) not in \
                            options['selected_ug']:
                        continue
                    if len(options['selected_wallets']) > 0 and str(
                            b_line.program_code_id.portfolio_id.wallet_password) not in options['selected_wallets']:
                        continue
                    if len(options['selected_tp']) > 0 and str(
                            b_line.program_code_id.project_type_id.project_type_identifier) not in options[
                        'selected_tp']:
                        continue
                    if len(options['selected_pn']) > 0 and str(b_line.program_code_id.project_number) not in options[
                        'selected_pn']:
                        continue
                    if len(options['selected_stage']) > 0 and str(
                            b_line.program_code_id.stage_id.stage_identifier) not in options['selected_stage']:
                        continue
                    if len(options['selected_type']) > 0 and str(
                            b_line.program_code_id.agreement_type_id.agreement_type) not in options['selected_type']:
                        continue
                    if len(options['selected_agreement_number']) > 0 and str(
                            b_line.program_code_id.number_agreement) not in options['selected_agreement_number']:
                        continue

                    # Program code struture view fields
                    need_to_skip = 0
                    for column in options['selected_program_fields']:
                        if column == 'Year':
                            year = b_line.program_code_id.year and b_line.program_code_id.year.name or ''
                            columns.append({'name': str(year)})
                            need_to_skip += 1
                        if column == 'Program':
                            program = b_line.program_code_id.program_id and b_line.program_code_id.program_id.key_unam or ''
                            columns.append({'name': str(program)})
                            need_to_skip += 1
                        if column == 'Sub Program':
                            subprogram = b_line.program_code_id.sub_program_id and b_line.program_code_id.sub_program_id.sub_program or ''
                            columns.append({'name': str(subprogram)})
                            need_to_skip += 1
                        if column == 'Dependency':
                            dependency = b_line.program_code_id.dependency_id and b_line.program_code_id.dependency_id.dependency or ''
                            columns.append({'name': str(dependency)})
                            need_to_skip += 1
                        if column == 'Sub Dependency':
                            subdependency = b_line.program_code_id.sub_dependency_id and b_line.program_code_id.sub_dependency_id.sub_dependency or ''
                            columns.append({'name': str(subdependency)})
                            need_to_skip += 1
                        if column == 'Expenditure Item':
                            item = b_line.program_code_id.item_id and b_line.program_code_id.item_id.item or ''
                            columns.append({'name': str(item)})
                            need_to_skip += 1
                        if column == 'Check Digit':
                            check_digit = b_line.program_code_id.check_digit or ''
                            columns.append({'name': str(check_digit)})
                            need_to_skip += 1
                        if column == 'Source of Resource':
                            sor = b_line.program_code_id.resource_origin_id and b_line.program_code_id.resource_origin_id.key_origin or ''
                            columns.append({'name': str(sor)})
                            need_to_skip += 1
                        if column == 'Institutional Activity':
                            ai = b_line.program_code_id.institutional_activity_id and b_line.program_code_id.institutional_activity_id.number or ''
                            columns.append({'name': str(ai)})
                            need_to_skip += 1
                        if column == 'Conversion of Budgetary Program':
                            conversion = b_line.program_code_id.budget_program_conversion_id and b_line.program_code_id.budget_program_conversion_id.shcp and b_line.program_code_id.budget_program_conversion_id.shcp.name or ''
                            columns.append({'name': str(conversion)})
                            need_to_skip += 1
                        if column == 'SHCP items':
                            shcp = b_line.program_code_id.conversion_item_id and b_line.program_code_id.conversion_item_id.federal_part or ''
                            columns.append({'name': str(shcp)})
                            need_to_skip += 1
                        if column == 'Type of Expenditure':
                            expense_type = b_line.program_code_id.expense_type_id and b_line.program_code_id.expense_type_id.key_expenditure_type or ''
                            columns.append({'name': str(expense_type)})
                            need_to_skip += 1
                        if column == 'Geographic Location':
                            location = b_line.program_code_id.location_id and b_line.program_code_id.location_id.state_key or ''
                            columns.append({'name': str(location)})
                            need_to_skip += 1
                        if column == 'Wallet Key':
                            wallet_key = b_line.program_code_id.portfolio_id and b_line.program_code_id.portfolio_id.wallet_password or ''
                            columns.append({'name': str(wallet_key)})
                            need_to_skip += 1
                        if column == 'Type of Project':
                            project_type = b_line.program_code_id.project_type_id and b_line.program_code_id.project_type_id.project_type_identifier or ''
                            columns.append({'name': str(project_type)})
                            need_to_skip += 1
                        if column == 'Project Number':
                            project_number = b_line.program_code_id.project_number or ''
                            columns.append({'name': str(project_number)})
                            need_to_skip += 1
                        if column == 'Stage':
                            stage = b_line.program_code_id.stage_id and b_line.program_code_id.stage_id.stage_identifier or ''
                            columns.append({'name': str(stage)})
                            need_to_skip += 1
                        if column == 'Type of Agreement':
                            agreement_type = b_line.program_code_id.agreement_type_id and b_line.program_code_id.agreement_type_id.agreement_type or ''
                            columns.append({'name': str(agreement_type)})
                            need_to_skip += 1
                        if column == 'Agreement Number':
                            agreement_number = b_line.program_code_id.number_agreement or ''
                            columns.append({'name': str(agreement_number)})
                            need_to_skip += 1

                    all_b_lines = b_line_obj.search([('program_code_id', '=', b_line.program_code_id.id),
                                                     ('start_date', '>=', start), ('end_date', '<=', end)])
                    annual_modified = 0
                    adequacies_lines = adequacies_line_obj.search([('program', '=', b_line.program_code_id.id),
                                                                   ('adequacies_id.state', '=', 'accepted')])
                    for ad_line in adequacies_lines:
                        if ad_line.line_type == 'increase':
                            annual_modified += ad_line.amount
                        elif ad_line.line_type == 'decrease':
                            annual_modified -= ad_line.amount
                    authorized = sum(x.authorized for x in all_b_lines)
                    annual_modified = annual_modified + authorized
                    for column in options['selected_budget_control']:
                        if column in ('Partida', 'Expense Item'):
                            year = b_line.item_id and b_line.item_id.item or ''
                            columns.append({'name': str(year)})
                            need_total = True
                        elif column in ('Authorized', 'Autorizado'):
                            columns.append({'name': authorized})
                        elif column in ('Assigned Total Annual', 'Total Asignado Anual'):
                            columns.append({'name': sum(x.assigned for x in all_b_lines)})
                        elif column in ('Annual Modified', 'Modificado Anual'):
                            columns.append({'name': annual_modified})
                        elif column in ('Assigned 1st Trimester', 'Asignado 1er Trimestre'):
                            columns.append({'name': sum(x.assigned if x.start_date.month == 1 and \
                                                                      x.start_date.day == 1 and x.end_date.month == 3 and x.end_date.day == 31 \
                                                            else 0 for x in all_b_lines)})
                        elif column in ('Assigned 2nd Trimester', 'Asignado 2do Trimestre'):
                            columns.append({'name': sum(x.assigned if x.start_date.month == 4 and \
                                                                      x.start_date.day == 1 and x.end_date.month == 6 and x.end_date.day == 30 \
                                                            else 0 for x in all_b_lines)})
                        elif column in ('Assigned 3rd Trimester', 'Asignado 3er Trimestre'):
                            columns.append({'name': sum(x.assigned if x.start_date.month == 7 and \
                                                                      x.start_date.day == 1 and x.end_date.month == 9 and x.end_date.day == 30 \
                                                            else 0 for x in all_b_lines)})
                        elif column in ('Assigned 4th Trimester', 'Asignado 4to Trimestre'):
                            columns.append({'name': sum(x.assigned if x.start_date.month == 10 and \
                                                                      x.start_date.day == 1 and x.end_date.month == 12 and x.end_date.day == 31 \
                                                            else 0 for x in all_b_lines)})
                        elif column in ('Per Exercise', 'Por Ejercer'):
                            columns.append({'name': sum(x.available for x in all_b_lines)})
                        elif column in ('Committed', 'Comprometido'):
                            columns.append({'name': 0})
                        elif column in ('Accrued', 'Devengado'):
                            columns.append({'name': 0})
                        elif column in ('Exercised', 'Ejercido'):
                            columns.append({'name': 0})
                        elif column in ('Paid', 'Pagado'):
                            columns.append({'name': 0})
                        elif column in ('Available', 'Disponible'):
                            columns.append({'name': sum(x.available for x in all_b_lines)})
                    if need_total:
                        main_list.append(columns)

                    lines.append({
                        'id': b_line.id,
                        'name': b_line.program_code_id.program_code,
                        'columns': columns,
                        'level': 0,
                        'unfoldable': False,
                        'unfolded': True,
                    })
                    program_code_list.append(b_line.program_code_id)
                if need_total:
                    main_list_new = main_list
                    list_with_data = []
                    for l in main_list_new:
                        new_list = []
                        for d in l:
                            new_list.append(d.get('name'))
                        list_with_data.append(new_list)
                    list_tot_data = list(map(sum, map(lambda l: map(float, l), zip(*list_with_data))))
                    main_cols = []
                    counter = 0
                    for l in list_tot_data:
                        if counter != 0:
                            main_cols.append({'name': l})
                        else:
                            main_cols.append({'name': ''})
                        counter += 1
                    if main_cols:
                        lines.append({
                            'id': main_id,
                            'name': _('Total'),
                            'class': 'total',
                            'level': 2,
                            'columns': main_cols,
                        })
        selected_line_pages = options['selected_line_pages']
        all_list = []
        for s in selected_line_pages:
            s = int(s)
            start = (s - 1) * 500 + 1
            end = s * 500
            for i in range(start - 1, end):
                try:
                    all_list.append(lines[i])
                except:
                    pass
        if need_total:
            new_total_list = []
            for al in all_list:
                if al.get('name') == 'Total':
                    if new_total_list:
                        list_with_data = []
                        for l in new_total_list:
                            new_list = []
                            for d in l:
                                new_list.append(d.get('name'))
                            list_with_data.append(new_list)
                        list_tot_data = list(map(sum, map(lambda l: map(float, l), zip(*list_with_data))))
                        main_cols = []
                        counter = 0
                        for l in list_tot_data:
                            if counter > need_to_skip:
                                main_cols.append({'name': l})
                            else:
                                main_cols.append({'name': ''})
                            counter += 1
                        al.update({
                            'id': 0,
                            'name': _('Total'),
                            'class': 'total',
                            'level': 2,
                            'columns': main_cols,
                        })
                    new_total_list = []
                else:
                    new_total_list.append(al.get('columns'))

            if new_total_list:
                list_with_data = []
                for l in new_total_list:
                    new_list = []
                    for d in l:
                        new_list.append(d.get('name'))
                    list_with_data.append(new_list)

                list_tot_data = list(map(sum, map(lambda l: map(float, l), zip(*list_with_data))))
                main_cols = []
                counter = 0

                for l in list_tot_data:
                    if counter > need_to_skip:
                        main_cols.append({'name': l})
                    else:
                        main_cols.append({'name': ''})
                    counter += 1
                all_list.append({
                    'id': 0,
                    'name': _('Total'),
                    'class': 'total',
                    'level': 2,
                    'columns': main_cols,
                })
            if len(all_list) > 0:
                return all_list
            new_lines = []
            need_to_add = 0
            new_total_list = []
            for al in lines[:500]:
                if al.get('name') == 'Total':
                    if new_total_list:
                        list_with_data = []
                        for l in new_total_list:
                            new_list = []
                            for d in l:
                                new_list.append(d.get('name'))
                            list_with_data.append(new_list)
                        list_tot_data = list(map(sum, map(lambda l: map(float, l), zip(*list_with_data))))
                        main_cols = []
                        counter = 0
                        for l in list_tot_data:
                            if counter > need_to_skip:
                                main_cols.append({'name': l})
                            else:
                                main_cols.append({'name': ''})
                            counter += 1
                        al.update({
                            'id': 0,
                            'name': _('Total'),
                            'class': 'total',
                            'level': 2,
                            'columns': main_cols,
                        })
                    new_total_list = []
                    new_lines.append(al)
                else:
                    new_total_list.append(al.get('columns'))
                    new_lines.append(al)
            if new_total_list:
                need_to_add += 1
                list_with_data = []
                for l in new_total_list:
                    new_list = []
                    for d in l:
                        new_list.append(d.get('name'))
                    list_with_data.append(new_list)
                list_tot_data = list(map(sum, map(lambda l: map(float, l), zip(*list_with_data))))
                main_cols = []
                counter = 0
                for l in list_tot_data:
                    if counter > need_to_skip:
                        main_cols.append({'name': l})
                    else:
                        main_cols.append({'name': ''})
                    counter += 1
                new_lines.append({
                    'id': 0,
                    'name': _('Total'),
                    'class': 'total',
                    'level': 2,
                    'columns': main_cols,
                })
            return new_lines[:501]
        else:
            if len(all_list) > 0:
                return all_list
            return lines[:500]

    def _get_report_name(self):
        context = self.env.context
        date_report = fields.Date.from_string(context['date_from']) if context.get(
            'date_from') else fields.date.today()
        return '%s_%s_Summary_Report' % (
            date_report.year,
            str(date_report.month).zfill(2))
