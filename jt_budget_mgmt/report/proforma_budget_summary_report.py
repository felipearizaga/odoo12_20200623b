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
    filter_budget_control = None

    # Set columns based on dynamic options
    def _get_columns_name(self, options):
        column_list = []
        column_list.append({'name': _("Program Code")})
        for column in options['selected_budget_control']:
            column_list.append({'name': _(column)})
        return column_list

    @api.model
    def _init_filter_budget_control(self, options, previous_options=None):
        options['budget_control'] = []
        list_labels = ['Authorized', 'Assigned', 'Annual Modified',
                       'Per Exercise', 'Committed', 'Accrued', 'Exercised', 'Paid', 'Available']
        counter = 1

        if previous_options and previous_options.get('budget_control'):
            budget_control_map = dict((opt['id'], opt['selected']) for opt in previous_options['budget_control'] if opt['id'] != 'divider' and 'selected' in opt)
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

    def _get_lines(self, options, line_id=None):
        lines = []
        budget_lines = self.env['expenditure.budget.line'].search(
            [('expenditure_budget_id.state', '=', 'validate')])

        for b_line in budget_lines:
            annual_modified = b_line.authorized + b_line.assigned
            columns = []
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

        return lines

    def _get_report_name(self):
        context = self.env.context
        date_report = fields.Date.from_string(context['date_from']) if context.get(
            'date_from') else fields.date.today()
        return '%s_%s_Summary_Report' % (
            date_report.year,
            str(date_report.month).zfill(2))

    def get_html(self, options, line_id=None, additional_context=None):
        '''
        return the html value of report, or html value of unfolded line
        * if line_id is set, the template used will be the line_template
        otherwise it uses the main_template. Reason is for efficiency, when unfolding a line in the report
        we don't want to reload all lines, just get the one we unfolded.
        '''
        # Check the security before updating the context to make sure the options are safe.
        self._check_report_security(options)

        # Prevent inconsistency between options and context.
        self = self.with_context(self._set_context(options))

        templates = self._get_templates()
        report_manager = self._get_report_manager(options)
        report = {'name': self._get_report_name(),
                  'summary': report_manager.summary,
                  'company_name': self.env.company.name, }
        lines = self._get_lines(options, line_id=line_id)

        if options.get('hierarchy'):
            lines = self._create_hierarchy(lines, options)
        if options.get('selected_column'):
            lines = self._sort_lines(lines, options)

        footnotes_to_render = []
        if self.env.context.get('print_mode', False):
            # we are in print mode, so compute footnote number and include them in lines values, otherwise, let the js compute the number correctly as
            # we don't know all the visible lines.
            footnotes = dict([(str(f.line), f)
                              for f in report_manager.footnotes_ids])
            number = 0
            for line in lines:
                f = footnotes.get(str(line.get('id')))
                if f:
                    number += 1
                    line['footnote'] = str(number)
                    footnotes_to_render.append(
                        {'id': f.id, 'number': number, 'text': f.text})

        rcontext = {'report': report,
                    'lines': {'columns_header': self.get_header(options), 'lines': lines},
                    'options': options,
                    'context': self.env.context,
                    'model': self,
                    }
        if additional_context and type(additional_context) == dict:
            rcontext.update(additional_context)
        if self.env.context.get('analytic_account_ids'):
            rcontext['options']['analytic_account_ids'] = [
                {'id': acc.id, 'name': acc.name} for acc in self.env.context['analytic_account_ids']
            ]

        render_template = templates.get(
            'main_template', 'account_reports.main_template')
        if line_id is not None:
            render_template = templates.get(
                'line_template', 'account_reports.line_template')
        html = self.env['ir.ui.view'].render_template(
            render_template,
            values=dict(rcontext),
        )
        if self.env.context.get('print_mode', False):
            for k, v in self._replace_class().items():
                html = html.replace(k, v)
            # append footnote as well
            html = html.replace(b'<div class="js_account_report_footnotes"></div>',
                                self.get_html_footnotes(footnotes_to_render))
        return html



    #     ####################################################
    # # OPTIONS: hierarchy
    # ####################################################
    # MOST_SORT_PRIO = 0
    # LEAST_SORT_PRIO = 99

    # # Create codes path in the hierarchy based on account.
    # def get_account_codes(self, account):
    #     # A code is tuple(sort priority, actual code)
    #     codes = []
    #     if account.group_id:
    #         group = account.group_id
    #         while group:
    #             code = '%s %s' % (group.code_prefix or '', group.name)
    #             codes.append((self.MOST_SORT_PRIO, code))
    #             group = group.parent_id
    #     else:
    #         # Limit to 3 levels.
    #         code = account.code[:3]
    #         while code:
    #             codes.append((self.MOST_SORT_PRIO, code))
    #             code = code[:-1]
    #     return list(reversed(codes))

    # @api.model
    # def _sort_lines(self, lines, options):
    #     def merge_tree(line):
    #         sorted_list.append(line)
    #         for l in sorted(tree[line['id']], key=lambda k: selected_sign * k['columns'][selected_column - k.get('colspan', 1)]['no_format']):
    #             merge_tree(l)

    #     sorted_list = []
    #     selected_column = abs(options['selected_column']) - 1
    #     selected_sign = -copysign(1, options['selected_column'])
    #     tree = defaultdict(list)
    #     if 'sortable' not in self._get_columns_name(options)[selected_column].get('class', ''):
    #         return lines  # Nothing to do here
    #     for line in lines:
    #         tree[line.get('parent_id')].append(line)
    #     for line in sorted(tree[None], key=lambda k: ('total' in k.get('class', ''), selected_sign * k['columns'][selected_column - k.get('colspan', 1)]['no_format'])):
    #         merge_tree(line)

    #     return sorted_list

    # @api.model
    # def _create_hierarchy(self, lines, options):
    #     """This method is called when the option 'hiearchy' is enabled on a report.
    #     It receives the lines (as computed by _get_lines()) in argument, and will add
    #     a hiearchy in those lines by using the account.group of accounts. If not set,
    #     it will fallback on creating a hierarchy based on the account's code first 3
    #     digits.
    #     """
    #     is_number = ['number' in c.get('class', []) for c in self.get_header(options)[-1][1:]]
    #     # Avoid redundant browsing.
    #     accounts_cache = {}

    #     # Retrieve account either from cache, either by browsing.
    #     def get_account(id):
    #         if id not in accounts_cache:
    #             accounts_cache[id] = self.env['account.account'].browse(id)
    #         return accounts_cache[id]

    #     # Add the report line to the hierarchy recursively.
    #     def add_line_to_hierarchy(line, codes, level_dict, depth=None):
    #         # Recursively build a dict where:
    #         # 'children' contains only subcodes
    #         # 'lines' contains the lines at this level
    #         # This > lines [optional, i.e. not for topmost level]
    #         #      > children > [codes] "That" > lines
    #         #                                  > metadata
    #         #                                  > children
    #         #      > metadata(depth, parent ...)

    #         if not codes:
    #             return
    #         if not depth:
    #             depth = line.get('level', 1)
    #         level_dict.setdefault('depth', depth)
    #         level_dict.setdefault('parent_id', 'hierarchy_' + codes[0][1] if codes[0][0] != 'root' else codes[0][1])
    #         level_dict.setdefault('children', {})
    #         code = codes[1]
    #         codes = codes[1:]
    #         level_dict['children'].setdefault(code, {})

    #         if len(codes) > 1:
    #             add_line_to_hierarchy(line, codes, level_dict['children'][code], depth=depth + 1)
    #         else:
    #             level_dict['children'][code].setdefault('lines', [])
    #             level_dict['children'][code]['lines'].append(line)
    #             for l in level_dict['children'][code]['lines']:
    #                 l['parent_id'] = 'hierarchy_' + code[1]

    #     # Merge a list of columns together and take care about str values.
    #     def merge_columns(columns):
    #         return [('n/a' if any(i != '' for i in x) else '') if any(isinstance(i, str) for i in x) else sum(x) for x in zip(*columns)]

    #     # Get_lines for the newly computed hierarchy.
    #     def get_hierarchy_lines(values, depth=1):
    #         lines = []
    #         sum_sum_columns = []
    #         unfold_all = self.env.context.get('print_mode') and len(options.get('unfolded_lines')) == 0
    #         for base_line in values.get('lines', []):
    #             lines.append(base_line)
    #             sum_sum_columns.append([c.get('no_format_name', c['name']) for c in base_line['columns']])

    #         # For the last iteration, there might not be the children key (see add_line_to_hierarchy)
    #         for key in sorted(values.get('children', {}).keys()):
    #             sum_columns, sub_lines = get_hierarchy_lines(values['children'][key], depth=values['depth'])
    #             id = 'hierarchy_' + key[1]
    #             header_line = {
    #                 'id': id,
    #                 'name': key[1] if len(key[1]) < 30 else key[1][:30] + '...',  # second member of the tuple
    #                 'title_hover': key[1],
    #                 'unfoldable': True,
    #                 'unfolded': id in options.get('unfolded_lines') or unfold_all,
    #                 'level': values['depth'],
    #                 'parent_id': values['parent_id'],
    #                 'columns': [{'name': self.format_value(c) if not isinstance(c, str) else c} for c in sum_columns],
    #             }
    #             if key[0] == self.LEAST_SORT_PRIO:
    #                 header_line['style'] = 'font-style:italic;'
    #             lines += [header_line] + sub_lines
    #             sum_sum_columns.append(sum_columns)
    #         return merge_columns(sum_sum_columns), lines

    #     def deep_merge_dict(source, destination):
    #         for key, value in source.items():
    #             if isinstance(value, dict):
    #                 # get node or create one
    #                 node = destination.setdefault(key, {})
    #                 deep_merge_dict(value, node)
    #             else:
    #                 destination[key] = value

    #         return destination

    #     # Hierarchy of codes.
    #     accounts_hierarchy = {}

    #     new_lines = []
    #     no_group_lines = []
    #     # If no account.group at all, we need to pass once again in the loop to dispatch
    #     # all the lines across their account prefix, hence the None
    #     for line in lines + [None]:
    #         # Only deal with lines grouped by accounts.
    #         # And discriminating sections defined by account.financial.html.report.line
    #         is_grouped_by_account = line and line.get('caret_options') == 'account.account'
    #         if not is_grouped_by_account or not line:

    #             # No group code found in any lines, compute it automatically.
    #             no_group_hierarchy = {}
    #             for no_group_line in no_group_lines:
    #                 codes = [('root', str(line.get('parent_id')) or 'root'), (self.LEAST_SORT_PRIO, _('(No Group)'))]
    #                 if not accounts_hierarchy:
    #                     account = get_account(no_group_line.get('account_id', no_group_line.get('id')))
    #                     codes = [('root', str(line.get('parent_id')) or 'root')] + self.get_account_codes(account)
    #                 add_line_to_hierarchy(no_group_line, codes, no_group_hierarchy, line.get('level', 0) + 1)
    #             no_group_lines = []

    #             deep_merge_dict(no_group_hierarchy, accounts_hierarchy)

    #             # Merge the newly created hierarchy with existing lines.
    #             if accounts_hierarchy:
    #                 new_lines += get_hierarchy_lines(accounts_hierarchy)[1]
    #                 accounts_hierarchy = {}

    #             if line:
    #                 new_lines.append(line)
    #             continue

    #         # Exclude lines having no group.
    #         account = get_account(line.get('account_id', line.get('id')))
    #         if not account.group_id:
    #             no_group_lines.append(line)
    #             continue

    #         codes = [('root', str(line.get('parent_id')) or 'root')] + self.get_account_codes(account)
    #         add_line_to_hierarchy(line, codes, accounts_hierarchy, line.get('level', 0) + 1)

    #     return new_lines
