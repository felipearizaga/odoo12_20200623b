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
from odoo import models, api, _
import unicodedata
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class AnalyticalStatusOfTheExpenditureBudgetExercise(models.AbstractModel):
    _name = "jt_conac.status.of.expenditure.report"
    _inherit = "account.coa.report"
    _description = "Analytical Status of the Expenditure Budget Exercise"

    filter_date = {'mode': 'range', 'filter': 'this_month'}
    filter_comparison = {'date_from': '', 'date_to': '', 'filter': 'no_comparison', 'number_period': 1}
    filter_all_entries = False
    filter_journals = False
    filter_analytic = False
    filter_unfold_all = False
    filter_cash_basis = None
    filter_hierarchy = False
    filter_unposted_in_period = False
    MAX_LINES = None

    def _get_templates(self):
        templates = super(AnalyticalStatusOfTheExpenditureBudgetExercise, self)._get_templates()
        templates['main_table_header_template'] = 'jt_budget_mgmt.template_analytic_status_header'
        templates['main_template'] = 'account_reports.main_template'
        return templates

    def _get_columns_name(self, options):
        columns = [{'name': _('Concepto')}]
        if options.get('comparison') and options['comparison'].get('periods'):
            comparison = options.get('comparison')
            period_list = comparison.get('periods')
            period_list.reverse()
            columns += [
                           {'name': _('Aprobado')},
                           {'name': _('Ampliaciones/ (Reducciones)')},
                           {'name': _('Modificado')},
                           {'name': _('Devengado')},
                           {'name': _('Pagado')},
                           {'name': _('Subejercicio')},
                       ] * (len(period_list) + 1)
        else:
            columns = [
                {'name': _('Concepto')}, {'name': _('Aprobado')},
            {'name': _('Ampliaciones/ (Reducciones)')},
            {'name': _('Modificado')},
            {'name': _('Devengado')},
            {'name': _('Pagado')},
            {'name': _('Subejercicio')},
            ]
        return columns

    @api.model
    def _get_filter_journals(self):
        # OVERRIDE to filter only bank / cash journals.
        return []

    def strip_accents(self, text):
        return ''.join(char for char in
                       unicodedata.normalize('NFKD', text)
                       if unicodedata.category(char) != 'Mn')

    def _get_lines(self, options, line_id=None):
        exp_obj = self.env['status.expen']
        bud_obj = self.env['expenditure.budget']
        adeq_obj = self.env['adequacies']

        comparison = options.get('comparison')
        periods = []
        if comparison and comparison.get('filter') != 'no_comparison':
            period_list = comparison.get('periods')
            period_list.reverse()
            periods = [period for period in period_list]
        periods.append(options.get('date'))

        period_item_auth_dict = {}

        for period in periods:
            period_name = period.get('string')
            date_start = datetime.strptime(str(period.get('date_from')), DEFAULT_SERVER_DATE_FORMAT).date()
            date_end = datetime.strptime(str(period.get('date_to')), DEFAULT_SERVER_DATE_FORMAT).date()
            budgets = bud_obj.search([('state', '=', 'validate'),
                                      ('from_date', '=', date_start),
                                      ('to_date', '=', date_end)])
            for budget in budgets:
                for line in budget.success_line_ids:
                    if line.item_id and line.item_id.heading and line.item_id.heading.name:
                        heading_name = line.item_id.heading.name.upper()
                        heading_name = self.strip_accents(heading_name)
                        if period_name in period_item_auth_dict.keys():
                            pe_dict = period_item_auth_dict.get(period_name)
                            if heading_name in pe_dict.keys():
                                pe_dict.update({heading_name: pe_dict.get(heading_name) + [line]})
                            else:
                                pe_dict.update({heading_name: [line]})
                        else:
                            period_item_auth_dict.update({period_name: {heading_name: [line]}})

        for period, section_data in period_item_auth_dict.items():
            for section, line_list in section_data.items():
                item_dict = {}
                for line in line_list:
                    item = line.item_id
                    if item not in item_dict:
                        item_dict.update({item: line.authorized})
                    else:
                        item_dict.update({item: item_dict.get(item) + line.authorized})
                sec_dict = period_item_auth_dict.get(period)
                sec_dict.update({section: item_dict})

        # adequacies = adeq_obj.search([('state', '=', 'accepted')])
        # item_dict_auth = {}
        # item_dict_adeq = {}
        # date_from = False
        # date_to = False
        # if options.get('date'):
        #     date_from = options.get('date').get('date_from')
        #     date_to = options.get('date').get('date_to')
        # if isinstance(date_from, str):
        #     date_from = datetime.strptime(date_from, DEFAULT_SERVER_DATE_FORMAT).date()
        # if isinstance(date_to, str):
        #     date_to = datetime.strptime(date_to, DEFAULT_SERVER_DATE_FORMAT).date()
        # for budget in budgets:
        #     for line in budget.success_line_ids:
        #         if line.item_id and line.item_id.heading and line.item_id.heading.name:
        #             heading_name = line.item_id.heading.name.upper()
        #             heading_name = self.strip_accents(heading_name)
        #             item = line.item_id
        #             if heading_name in item_dict_auth.keys():
        #                 heading_dict = item_dict_auth.get(heading_name)[0]
        #                 if item in heading_dict.keys():
        #                     amt = heading_dict.get(item)
        #                     heading_dict.update({item: amt + line.authorized})
        #                 else:
        #                     heading_dict.update({item: line.authorized})
        #             else:
        #                 item_dict_auth.update({heading_name: [{item: line.authorized}]})
        #
        # for ade in adequacies:
        #     if ade.adaptation_type == 'liquid' and ade.date_of_liquid_adu >= date_from and ade.date_of_liquid_adu <= date_to:
        #         for line in ade.adequacies_lines_ids:
        #             if line.program:
        #                 item = line.program.item_id.item
        #                 if item in item_dict_adeq.keys():
        #                     if line.line_type == 'increase':
        #                         item_dict_adeq.update({item: item_dict_adeq.get(item) + line.amount})
        #                     else:
        #                         item_dict_adeq.update({item: item_dict_adeq.get(item) - line.amount})
        #                 else:
        #                     if line.line_type == 'increase':
        #                         item_dict_adeq.update({item: line.amount})
        #                     else:
        #                         item_dict_adeq.update({item: -line.amount})
        #     elif ade.adaptation_type != 'liquid' and ade.date_of_budget_affected >= date_from and ade.date_of_budget_affected <= date_to:
        #         for line in ade.adequacies_lines_ids:
        #             if line.program:
        #                 item = line.program.item_id.item
        #                 if item in item_dict_adeq.keys():
        #                     if line.line_type == 'increase':
        #                         item_dict_adeq.update({item: item_dict_adeq.get(item) + line.amount})
        #                     else:
        #                         item_dict_adeq.update({item: item_dict_adeq.get(item) - line.amount})
        #                 else:
        #                     if line.line_type == 'increase':
        #                         item_dict_adeq.update({item: line.amount})
        #                     else:
        #                         item_dict_adeq.update({item: -line.amount})

        lines = []
        hierarchy_lines = exp_obj.sudo().search([('parent_id', '=', False)], order='id')

        main_period_total = {}
        for line in hierarchy_lines:
            lines.append({
                'id': 'hierarchy_' + str(line.id),
                'name': line.concept,
                'columns': [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}]
                                * len(periods),
                'level': 1,
                'unfoldable': False,
                'unfolded': True,
            })

            level_1_lines = exp_obj.search([('parent_id', '=', line.id)])
            for level_1_line in level_1_lines:
                lines.append({
                    'id': 'level_one_%s' % level_1_line.id,
                    'name': level_1_line.concept,
                    'columns': [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}] *
                                len(periods),
                    'level': 2,
                    'unfoldable': True,
                    'unfolded': True,
                    'parent_id': 'hierarchy_' + str(line.id),
                })
                line_concept = level_1_line.concept.upper()
                line_concept = self.strip_accents(line_concept)
                concept_dict  = {}
                item_list = []
                period_total = {}
                for period in periods:
                    period_name = period.get('string')
                    if period_name in period_item_auth_dict.keys():
                        if line_concept in period_item_auth_dict.get(period_name):
                            for item, amt in period_item_auth_dict.get(period_name).get(line_concept).items():
                                if period_name in concept_dict:
                                    item_dict = concept_dict.get(period_name)
                                    if item in item_dict:
                                        item_dict.update({item: item_dict.get(item) + amt})
                                    else:
                                        item_dict.update({item: amt})
                                else:
                                    concept_dict.update({period_name: {item: amt}})
                                if item not in item_list:
                                    item_list.append(item)

                for item in item_list:
                    line_cols = []
                    for period in periods:
                        period_name = period.get('string')
                        if period_name in concept_dict:
                            if item in concept_dict.get(period_name).keys():
                                amt = concept_dict.get(period_name).get(item)
                                if period_name in period_total:
                                    period_total.update({period_name: period_total.get(period_name) + amt})
                                else:
                                    period_total.update({period_name: amt})
                                if period_name in main_period_total:
                                    main_period_total.update({period_name: main_period_total.get(period_name) + amt})
                                else:
                                    main_period_total.update({period_name: amt})
                                line_cols += [{'name': '%.2f' % amt, 'style': 'margin-left:15px;'}, {'name': ''}, {'name': ''},{'name': ''},
                                              {'name': ''}, {'name': ''}]
                        else:
                            line_cols += [{'name': ''}] * 6
                    name = item.item
                    if item.description:
                        name += ' '
                        name += item.description
                    lines.append({
                        'id': 'level_two_%s' % item.id,
                        'name': name,
                        'columns': line_cols,
                        'level': 3,
                        'unfoldable': False,
                        'unfolded': False,
                        'parent_id': 'level_one_%s' % level_1_line.id,
                    })

                total_cols = []
                need_to_add = False
                for period in periods:
                    period_name = period.get('string')
                    if period_name in period_total:
                        total_cols += [{'name': '%.2f' %  period_total.get(period_name), 'style': 'margin-left:15px;'}, {'name': ''}, {'name': ''},
                                       {'name': ''},{'name': ''},{'name': ''}]
                        if not need_to_add:
                            need_to_add = True
                    else:
                        total_cols += [{'name': ''}] * 6
                if need_to_add:
                    lines.append({
                        'id': 'level_two',
                        'name': _('Total'),
                        'columns': total_cols,
                        'level': 4,
                        'class': 'total',
                        'unfoldable': False,
                        'unfolded': False,
                        'parent_id': 'level_one_%s' % level_1_line.id,
                    })
        main_total_cols = []
        need_to_add = False
        for period in periods:
            period_name = period.get('string')
            if period_name in main_period_total:
                main_total_cols += [{'name': '%.2f' % main_period_total.get(period_name), 'style': 'margin-left:15px;'}, {'name': ''}, {'name': ''},
                               {'name': ''}, {'name': ''}, {'name': ''}]
                if not need_to_add:
                    need_to_add = True
            else:
                main_total_cols += [{'name': ''}] * 6
        lines.append({
            'id': 'hierarchy_' + str(line.id),
            'name': 'Main Total',
            'columns': main_total_cols,
            'level': 1,
            'unfoldable': False,
            'unfolded': True,
        })
        return lines
