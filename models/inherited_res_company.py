# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools import float_compare, float_round
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta



class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    use_next_on_work_order_id = fields.Many2one('mrp.workorder',
        string="Next Work Order to Use",
        help='Technical: used to figure out default serial number on work orders')


class Company(models.Model):
    _inherit = 'res.company'


    serial_no = fields.Integer(default = 0)
    digits_serial_no = fields.Integer(string='Digits :')
    prefix_serial_no = fields.Char(string="Prefix :")

class ProductProductInherit(models.Model):
    _inherit = "product.template"

    digits_serial_no = fields.Integer(string='Digits :')
    prefix_serial_no = fields.Char(string="Prefix :")

class MrpProductionInherit(models.Model):
    """ Manufacturing Orders """
    _inherit = 'mrp.production'

    # lot_numbr = fields.Char(string="lot number")

    def create_all_qty(self):
        """ create batch serial no for Manufacturing Orders with work order """
        count = self.product_qty
        if len(self.workorder_ids) == 0:
            raise UserError(_('There is no work order for this product'))
        for wo in self.workorder_ids:
            wo.button_start()
            for i in range(int(count)):
                wo.record_production()

    def create_custom_lot_no(self,wo):
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
        company.update({'serial_no' : serial_no})
        lot_serial_no = self.env['stock.production.lot'].create({'name' : lot_no,'product_id':self.product_id.id,'company_id': company.id,'use_next_on_work_order_id' : wo.id})
        return lot_serial_no

    def _workorders_create(self, bom, bom_data):

        res = super(MrpProductionInherit, self)._workorders_create(bom,bom_data)
        if self.product_id.tracking == 'serial' :
            lot_id_list = []
            for i in range(0,int(self.product_qty)) :
                lot_id = self.create_custom_lot_no(res[0])
                lot_id_list.append(lot_id.id)
            res[0].finished_lot_id = lot_id_list[0]
                #lot.lot_numbr = lot_id.id

        elif self.product_id.tracking == 'lot' :
            lot_id = self.create_custom_lot_no(res[0])
            for lot in res:
                lot.finished_lot_id = lot_id.id
        return res

class MrpWorkorder(models.Model):
    """ Manufacturing Orders """
    _inherit = 'mrp.workorder'



    


    def _assign_default_final_lot_id(self):
        
        lot_id_list = self.env['stock.production.lot'].search([('use_next_on_work_order_id', '=', self.id)],
                                                                    order='create_date, id')

        finished_lot = []
        for line in self.finished_workorder_line_ids :
            finished_lot.append(line.lot_id.id)


       

        for lot in lot_id_list :

            if lot.id in finished_lot :
                continue


            else :
                self.finished_lot_id = lot
                
                break




        
    def record_production(self):

        
        res = super(MrpWorkorder, self).record_production()



        
        if self.qty_produced == self.qty_production :

            for line in self.finished_workorder_line_ids :

                if self.production_id.product_id.tracking == 'serial':
                    
                    line.lot_id.use_next_on_work_order_id = self.next_work_order_id.id

            
            return res

            #self.finished_lot_id = False
        if self.production_id.product_id.tracking == 'serial':
            self._assign_default_final_lot_id()

        return res

    def create_all_qty(self):
        """ to create all qty using batch serial number """

        count = self.qty_producing
        for i in range(int(count)):
            self.button_start()

