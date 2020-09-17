# -*- coding: utf-8 -*-
{
    'name': "Captivea Custom Sitemap",

    'summary': """
        Generates a custom sitemap.
        """,

    'description': """
        Iterates through all web pages, including blogs and events, and generates a stylized sitemap available on the website.
        Each website has associated settings page under Website > Configuration > Sitemap Settings
    """,

    'author': "Joe Hill Captivea",
    'website': "https://www.Captivea.us/",

    'category': 'Uncategorized',
    'version': '1.0',

    'depends': ['base','website'],

    'data': [
        'security/ir.model.access.csv',
        'views/sitemap_webpage.xml',
        'views/settings_page.xml',
        'data/data.xml',
        'images': 'images/main_screenshot.png',
    ]
}
