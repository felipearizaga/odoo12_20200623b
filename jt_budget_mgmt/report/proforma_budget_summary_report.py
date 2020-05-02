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

    def _get_columns_name(self, options):
        return [
            {'name': _('Code program')},
            {'name': _('Authorized')},
            {'name': _('Assigned')},
            {'name': _('Annual Modified')},
            {'name': _('Per Exercise')},
            {'name': _('Committed')},
            {'name': _('Accrued')},
            {'name': _('Exercised')},
            {'name': _('Paid')},
            {'name': _('Available')},
        ]

    @api.model
    def _get_filter_program_code(self):
        # print("program code filter..........")
        return self.env['program.code'].search([])

    @api.model
    def _init_filter_budget_control(self, options, previous_options=None):
        options['budget_control'] = []
        list_labels = ['Authorized', 'Assigned', 'Annual Modified',
                       'Per Exercise', 'Committed', 'Accrued', 'Exercised', 'Paid', 'Available']
        counter = 1
        for label in list_labels:
            options['budget_control'].append({
                'id': str(counter),
                'name': str(label),
                'code': str(counter),
            })
            counter += 1
        # print("init filter budget_control..........",
        #       options, self._context, previous_options)

    def _get_lines(self, options, line_id=None):
        lines = []

        budget_lines = self.env['expenditure.budget.line'].search(
            [('expenditure_budget_id.state', '=', 'validate')])

        for b_line in budget_lines:
            annual_modified = b_line.authorized + b_line.assigned
            columns = [
                {'name': b_line.authorized},
                {'name': b_line.assigned},
                {'name': annual_modified},
                {'name': 0},
                {'name': 0},
                {'name': 0},
                {'name': 0},
                {'name': 0},
                {'name': b_line.available}
            ]
            lines.append({
                'id': b_line.id,
                'name': b_line.program_code_id.program_code,
                'columns': columns,
                'level': 0,
                'unfoldable': False,
                'unfolded': True,
            })

        return lines
    #     conac_obj = self.env['coa.conac']
    #     lines = []
    #     hierarchy_lines = conac_obj.sudo().search(
    #         [('parent_id', '=', False)], order='code')

    #     for line in hierarchy_lines:

    #         # Root Level
    #         lines.append({
    #             'id': 'hierarchy_' + line.code,
    #             'name': line.display_name,
    #             'columns': [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}],
    #             'level': 1,
    #             'unfoldable': False,
    #             'unfolded': True,
    #         })

    #         # Level-1 lines
    #         level_1_lines = conac_obj.search([('parent_id', '=', line.id)])
    #         for level_1_line in level_1_lines:
    #             lines.append({
    #                 'id': 'level_one_%s' % level_1_line.id,
    #                 'name': level_1_line.display_name,
    #                 'columns': [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}],
    #                 'level': 2,
    #                 'unfoldable': True,
    #                 'unfolded': True,
    #                 'parent_id': 'hierarchy_' + line.code,
    #             })

    #             # Level-2 Lines
    #             level_2_lines = conac_obj.search(
    #                 [('parent_id', '=', level_1_line.id)])
    #             for level_2_line in level_2_lines:
    #                 lines.append({
    #                     'id': 'level_two_%s' % level_2_line.id,
    #                     'name': level_2_line.display_name,
    #                     'columns': [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}],
    #                     'level': 3,
    #                     'unfoldable': True,
    #                     'unfolded': True,
    #                     'parent_id': 'level_one_%s' % level_1_line.id,
    #                 })

    #                 # Level-3 Lines
    #                 level_3_lines = conac_obj.search(
    #                     [('parent_id', '=', level_2_line.id)])
    #                 for level_3_line in level_3_lines:
    #                     nature = ''
    #                     acc_type = ''
    #                     if level_3_line == 'debtor':
    #                         nature = 'Debitable account'
    #                         acc_type = 'Debtor'
    #                     elif level_3_line == 'creditor':
    #                         nature = 'Creditable account'
    #                         acc_type = 'Creditor'
    #                     elif nature == 'debtor_creditor':
    #                         nature = 'Debitable/Creditable account'
    #                         acc_type = 'Debtoror/Creditor'
    #                     lines.append({
    #                         'id': 'level_three_%s' % level_3_line.id,
    #                         'name': level_3_line.display_name,
    #                         'columns': [{'name': nature}, {'name': acc_type}, {'name': level_3_line.gender}, {'name': level_3_line.group}, {'name': level_3_line.item}],
    #                         'level': 4,
    #                         'parent_id': 'level_two_%s' % level_2_line.id,
    #                     })
    #     return lines

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
