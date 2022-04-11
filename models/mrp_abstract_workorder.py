# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class MrpAbstractWorkorderLineInherit(models.AbstractModel):
    _inherit = "mrp.abstract.workorder.line"
    _description = "Abstract model to implement product_produce_line as well as\
    workorder_line"
    _check_company_auto = True
    lot_id = fields.Many2one(
        'stock.production.lot', 'Lot/Serial Number',
        check_company=True, readonly=False,
        domain="[('product_id', '=', product_id), '|', ('company_id', '=', False), ('company_id', '=', parent.company_id)]")
