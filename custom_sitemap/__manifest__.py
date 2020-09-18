# -*- coding: utf-8 -*-
{
    'name': "Custom Sitemap",

    'summary': """
        Generates a customizable sitemap for each website on your Odoo.
        """,

    'description': """
        Iterates through all web pages and generates a stylized sitemap available on the website under /sitemap
        Each website has associated settings page under Website > Configuration > Sitemap Settings where the user can include or ignore certain page types.
    """,

    'author': "Captivea",
    'website': "https://www.Captivea.us/",
    'license': 'LGPL-3',

    'category': 'Website',
    'version': '1.0',

    'depends': ['base','website'],

    'images': ['images/main_screenshot.png'],

    'data': [
        'security/ir.model.access.csv',
        'views/sitemap_webpage.xml',
        'views/settings_page.xml',
        'data/data.xml',
        ]
}
