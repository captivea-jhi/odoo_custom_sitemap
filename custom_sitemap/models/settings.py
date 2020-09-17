# -*- coding: utf-8 -*-
# Part of CAPTIVEA. Odoo 12 EE.

from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class Website(models.Model):
    _inherit = 'website'

    # extend website create() so creates an assoc. sitemap
    @api.model
    def create(self, vals):
        res = super(Website,self).create(vals)
        res.create_sitemap_settings()
        _logger.info("New Website being created")
        return res # Once returned, site is created.


    # function that creates a sitemap and links this website to it
    def create_sitemap_settings(self):
        self.env['website.sitemap.settings'].create({'website' : self.id, 'website_id': self.id, 'name' : self.name })

    # function specifically for when we install module
    def create_sitemap_settings_init(self):
        # Get list of all websites, then call create_sitemap_settings for each one
        websites = self.env['website'].search([])
        for website in websites:
            website.create_sitemap_settings()

class settings_page(models.Model):
    _name = 'website.sitemap.settings'
    _description = 'Sitemap Settings'

    #init settings
    website = fields.Many2one()
    name = fields.Char()
    website_id = fields.Integer()
    # Booleans for users to select or deselect - will show or hide related section on sitemap page. Default is true for all.
    webpages = fields.Boolean(default=True)
    blog_posts = fields.Boolean("Blogs",default=True)
    events = fields.Boolean(default=True)
    jobs = fields.Boolean(default=True)
    livechat_channels = fields.Boolean(default=True)
    ecourses = fields.Boolean(default=True)
    appointments = fields.Boolean(default=True)
    products = fields.Boolean(default=True)
    forum_posts = fields.Boolean("Forums",default=True)
