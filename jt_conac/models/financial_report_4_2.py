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


class StatusOfActivities(models.AbstractModel):
    _name = "jt_conac.status.of.activities.report"
    _inherit = "jt_conac.coa.conac.report"
    _description = "Status of Activities"

    def _get_columns_name(self, options):
        return [
            {'name': _('Account Name')},
        ]

    def _get_lines(self, options, line_id=None):
        conac_obj = self.env['coa.conac']
        lines = []
        hierarchy_lines = conac_obj.sudo().search(
            [('parent_id', '=', False)], order='code')

        for line in hierarchy_lines:
            if line.code in ('4.0.0.0', '5.0.0.0'):
                lines.append({
                    'id': 'hierarchy_' + line.code,
                    'name': line.display_name,
                    'columns': [],
                    'level': 1,
                    'unfoldable': False,
                    'unfolded': True,
                })

                level_1_lines = conac_obj.search([('parent_id', '=', line.id)])
                for level_1_line in level_1_lines:
                    lines.append({
                        'id': 'level_one_%s' % level_1_line.id,
                        'name': level_1_line.display_name,
                        'columns': [],
                        'level': 2,
                        'unfoldable': True,
                        'unfolded': True,
                        'parent_id': 'hierarchy_' + line.code,
                    })

                    level_2_lines = conac_obj.search(
                        [('parent_id', '=', level_1_line.id)])
                    for level_2_line in level_2_lines:
                        lines.append({
                            'id': 'level_two_%s' % level_2_line.id,
                            'name': level_2_line.display_name,
                            'columns': [],
                            'level': 3,
                            'unfoldable': True,
                            'unfolded': True,
                            'parent_id': 'level_one_%s' % level_1_line.id,
                        })

                        level_3_lines = conac_obj.search(
                            [('parent_id', '=', level_2_line.id)])
                        for level_3_line in level_3_lines:
                            lines.append({
                                'id': 'level_three_%s' % level_3_line.id,
                                'name': level_3_line.display_name,
                                'columns': [],
                                'level': 4,
                                'parent_id': 'level_two_%s' % level_2_line.id,
                            })
        return lines
