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
from odoo import models, _
import unicodedata
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class AnalyticalStatusOfTheExpenditureBudgetExercise(models.AbstractModel):
    _name = "jt_conac.status.of.expenditure.report"
    _inherit = "account.coa.report"
    _description = "Analytical Status of the Expenditure Budget Exercise"

    def _get_templates(self):
        templates = super(
            AnalyticalStatusOfTheExpenditureBudgetExercise, self)._get_templates()
        templates[
            'main_table_header_template'] = 'account_reports.main_table_header'
        templates['main_template'] = 'account_reports.main_template'
        return templates

    def _get_columns_name(self, options):
        return [
            {'name': _('Concepto')},
            {'name': _('Aprobado')},
            {'name': _('Ampliaciones/ (Reducciones)')},
            {'name': _('Modificado')},
            {'name': _('Devengado')},
            {'name': _('Pagado')},
            {'name': _('Subejercicio')},
        ]

    def strip_accents(self, text):
        return ''.join(char for char in
                       unicodedata.normalize('NFKD', text)
                       if unicodedata.category(char) != 'Mn')

    def _get_lines(self, options, line_id=None):
        print ("Options =-=-=", options)
        exp_obj = self.env['status.expen']
        bud_obj = self.env['expenditure.budget']
        adeq_obj = self.env['adequacies']
        budgets = bud_obj.search([('state', '=', 'validate')])
        adequacies = adeq_obj.search([('state', '=', 'accepted')])
        item_dict_auth = {}
        item_dict_adeq = {}
        date_from = False
        date_to = False
        if options.get('date'):
            date_from = options.get('date').get('date_from')
            date_to = options.get('date').get('date_to')
        if isinstance(date_from, str):
            date_from = datetime.strptime(date_from, DEFAULT_SERVER_DATE_FORMAT).date()
        if isinstance(date_to, str):
            date_to = datetime.strptime(date_to, DEFAULT_SERVER_DATE_FORMAT).date()
        for budget in budgets:
            for line in budget.success_line_ids:
                if line.item_id and line.item_id.heading and line.item_id.heading.name:
                    heading_name = line.item_id.heading.name.upper()
                    heading_name = self.strip_accents(heading_name)
                    item = line.item_id
                    if heading_name in item_dict_auth.keys():
                        heading_dict = item_dict_auth.get(heading_name)[0]
                        if item in heading_dict.keys():
                            amt = heading_dict.get(item)
                            heading_dict.update({item: amt + line.authorized})
                        else:
                            heading_dict.update({item: line.authorized})
                    else:
                        item_dict_auth.update({heading_name: [{item: line.authorized}]})

        for ade in adequacies:
            if ade.adaptation_type == 'liquid' and ade.date_of_liquid_adu >= date_from and ade.date_of_liquid_adu <= date_to:
                for line in ade.adequacies_lines_ids:
                    if line.program:
                        item = line.program.item_id.item
                        if item in item_dict_adeq.keys():
                            if line.line_type == 'increase':
                                item_dict_adeq.update({item: item_dict_adeq.get(item) + line.amount})
                            else:
                                item_dict_adeq.update({item: item_dict_adeq.get(item) - line.amount})
                        else:
                            if line.line_type == 'increase':
                                item_dict_adeq.update({item: line.amount})
                            else:
                                item_dict_adeq.update({item: -line.amount})
            elif ade.adaptation_type != 'liquid' and ade.date_of_budget_affected >= date_from and ade.date_of_budget_affected <= date_to:
                for line in ade.adequacies_lines_ids:
                    if line.program:
                        item = line.program.item_id.item
                        if item in item_dict_adeq.keys():
                            if line.line_type == 'increase':
                                item_dict_adeq.update({item: item_dict_adeq.get(item) + line.amount})
                            else:
                                item_dict_adeq.update({item: item_dict_adeq.get(item) - line.amount})
                        else:
                            if line.line_type == 'increase':
                                item_dict_adeq.update({item: line.amount})
                            else:
                                item_dict_adeq.update({item: -line.amount})

        lines = []
        hierarchy_lines = exp_obj.sudo().search(
            [('parent_id', '=', False)], order='id')

        for line in hierarchy_lines:
            lines.append({
                'id': 'hierarchy_' + str(line.id),
                'name': line.concept,
                'columns': [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}],
                'level': 1,
                'unfoldable': False,
                'unfolded': True,
            })

            level_1_lines = exp_obj.search([('parent_id', '=', line.id)])
            for level_1_line in level_1_lines:
                lines.append({
                    'id': 'level_one_%s' % level_1_line.id,
                    'name': level_1_line.concept,
                    'columns': [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}],
                    'level': 2,
                    'unfoldable': True,
                    'unfolded': True,
                    'parent_id': 'hierarchy_' + str(line.id),
                })
                total_auth = 0
                total_ade = 0
                total_mod = 0
                total_sub = 0
                line_concept = level_1_line.concept.upper()
                line_concept = self.strip_accents(line_concept)
                if line_concept in item_dict_auth.keys():
                    concept_dict = item_dict_auth.get(line_concept)[0]
                    item_dict_con = dict(sorted(concept_dict.items()))
                    for item, authorized in item_dict_con.items():
                        name = item.item
                        if item.description:
                            name += ' '
                            name += item.description
                        adeq_amt = item_dict_adeq.get(item.item) if item_dict_adeq.get(item.item) else 0
                        modi_amt = authorized + adeq_amt
                        lines.append({
                            'id': 'level_two_%s' % item.id,
                            'name': name,
                            'columns': [{'name': '%.2f' % authorized, 'style': 'margin-left:15px;'},
                                        {'name': '%.2f' % adeq_amt, 'style': 'margin-left:15px;'},
                                        {'name': '%.2f' % modi_amt, 'style': 'margin-left:15px;'},
                                        {'name': ''},
                                        {'name': ''}, {'name': '%.2f' % modi_amt, 'style': 'margin-left:15px;'}],
                            'level': 3,
                            'unfoldable': False,
                            'unfolded': False,
                            'parent_id': 'level_one_%s' % level_1_line.id,
                        })
                        total_auth += authorized
                        total_ade += adeq_amt
                        total_mod += modi_amt
                        total_sub += modi_amt

                    lines.append({
                        'id': 'level_two_%s' % item.id,
                        'name': _('Total'),
                        'columns': [{'name': '%.2f' % total_auth},
                                    {'name': '%.2f' % total_ade},
                                    {'name': '%.2f' % total_mod}, {'name': ''},
                                    {'name': ''}, {'name': '%.2f' % total_sub}],
                        'level': 4,
                        'class': 'total',
                        'unfoldable': False,
                        'unfolded': False,
                        'parent_id': 'level_one_%s' % level_1_line.id,
                    })
                level_2_lines = exp_obj.search(
                    [('parent_id', '=', level_1_line.id)])
                for level_2_line in level_2_lines:
                    lines.append({
                        'id': 'level_two_%s' % level_2_line.id,
                        'name': level_2_line.concept,
                        'columns': [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}],
                        'level': 3,
                        'unfoldable': True,
                        'unfolded': True,
                        'parent_id': 'level_one_%s' % level_1_line.id,
                    })

                    level_3_lines = exp_obj.search(
                        [('parent_id', '=', level_2_line.id)])
                    for level_3_line in level_3_lines:
                        lines.append({
                            'id': 'level_three_%s' % level_3_line.id,
                            'name': level_3_line.concept,
                            'columns': [{'name': level_3_line.approved}, {'name': level_3_line.ext_and_red}, {'name': level_3_line.modified}, {'name': level_3_line.accrued}, {'name': level_3_line.paid_out}, {'name': level_3_line.sub_exercise}],
                            'level': 4,
                            'parent_id': 'level_two_%s' % level_2_line.id,
                        })
        return lines
