# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.


from collections import Counter
from datetime import datetime

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_round

class MrpProductProduce(models.TransientModel):
	_inherit = 'mrp.product.produce'

	lot_id = fields.Many2one('stock.production.lot', string='Lot',required=False)


	# @api.multi
	def do_produce(self):
		self._check_company()
		company = self.env.company
		result = self.env['res.config.settings'].search([],order="id desc", limit=1)

		if result.apply_method == "global":
			digit = result.digits_serial_no
			prefix = result.prefix_serial_no
		else:
			digit = self.product_id.digits_serial_no
			prefix = self.product_id.prefix_serial_no

		serial_no = company.serial_no + 1
		serial_no_digit=len(str(company.serial_no))


		diffrence = abs(serial_no_digit - digit)
		if diffrence > 0:
			no = "0"
			for i in range(diffrence-1) :
				no = no + "0"
		else :
			no = ""

		if prefix != False:
			lot_no = prefix+no+str(serial_no)
		else:
			lot_no = str(serial_no)
		company.sudo().update({'serial_no' : serial_no})
		lot_serial_no = self.env['stock.production.lot'].create({'name' : lot_no,'product_id':self.product_id.id,'company_id': self.env.company.id})
		print('lot_serial_nooooooooooooooooooooooooooooooooooooooo',lot_serial_no.name)
		self.finished_lot_id = lot_serial_no

		""" Save the current wizard and go back to the MO. """
		# self.ensure_one()
		self._record_production()

		return {
				'type': 'ir.actions.act_window_close'

				}

	def create_all_qty(self):
		""" to create all qty using batch serial number """
		count = self.qty_producing
		self.qty_producing = 1
		for i in range(int(count)):
			self.do_produce()
