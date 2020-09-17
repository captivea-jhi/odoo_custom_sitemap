# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo import models

import logging
_logger = logging.getLogger(__name__)

class GenerateSitemap(http.Controller):

    _inherit = 'website'

    @http.route('/sitemap', type='http', auth='public', website=True)
    def index(self, **kw):

        # Get website ID from 'website' module, then when I search, pass onto field
        website_id = request.website.id

        # Get name for display
        website_name = request.env['website'].sudo().search([('id','=', website_id)])['name']

        # use existing function to get all URLs. Will use to match URL to forum post and other missing pages
        enum_urls = []
        # for item in request.website.with_user(request.website.user_id).enumerate_pages(): v13
        for item in request.website.enumerate_pages(): # v12
            enum_urls.append(item['loc'])


        # Get all web pages for this website  with fields we want: name, url. Returns as a dictionary. Returns in order of creation.
        web_pages = request.env['website.page'].sudo().search([('is_published', '=', True), ('website_id', '=', website_id)], order="id asc")
        # Get rest of default app pages - if they exist.
        blog_posts = checkModule('website_blog', 'blog.post', website_id, 'blog_posts')
        event_posts = checkModule('website_event','event.event', website_id, 'events')
        forum_posts = checkModule('website_forum', 'forum.post',website_id, 'forum_posts', enum_urls)
        job_posts = checkModule('website_hr_recruitment', 'hr.job', website_id, 'jobs')
        products = checkModule('website_sale', 'product.product', website_id, 'products')
        ecourse_posts = checkModule('website_slides', 'slide.channel',website_id, 'ecourses')
        livechat_channels = checkModule('im_livechat', 'im_livechat.channel',website_id, 'livechat_channels')
        appointment_pages = checkModule('website_calendar', 'calendar.appointment.type',website_id, 'appointments')


        # Create a list of webapges (dictionaries) with display name and url
        clean_pages = []
        for page in web_pages:
            p = {'name': page['name'].title().replace('-', ' ').strip(), 'url': page['url']}
            if p not in clean_pages:
                clean_pages.append(p)

        # Add in the pages not found under website.page
        clean_pages = clean_pages + getWebsitePages(clean_pages, enum_urls)

        #remove duplicates
        cleaner_pages = []
        for x in clean_pages:
            _logger.info('Clean Page: ' + str(x))
            if x not in cleaner_pages:
                cleaner_pages.append(x)
        # Do settings check
        if request.env['website.sitemap.settings'].sudo().search([('website_id', '=', website_id)])[0]['webpages'] == False:
            cleaner_pages = []

        clean_forums, clean_blogs = getForumsBlogs(enum_urls, website_id)
        clean_blog_posts = clean_blogs + cleanPosts(blog_posts)
        clean_events = cleanPosts(event_posts)
        clean_forum_posts = clean_forums + cleanPosts(forum_posts)
        clean_jobs = cleanPosts(job_posts)
        clean_products = cleanPosts(products)
        clean_ecourses = cleanPosts(ecourse_posts)
        clean_livechannels = cleanPosts(livechat_channels)
        clean_appointments = cleanPosts(appointment_pages)
        all_pages = cleaner_pages + clean_events + clean_jobs + clean_products + clean_ecourses + clean_livechannels + clean_appointments + clean_forums + clean_blogs

        return http.request.render("custom_sitemap.captivea_sitemap",
								   {'web_pages': cleaner_pages, 'blog_posts': clean_blog_posts,
                                    'event_pages': clean_events, 'website_name': website_name,
                                     'job_posts' : clean_jobs, 'products' : clean_products, 'livechat_channels' : clean_livechannels, 'ecourses' : clean_ecourses,
                                     'appointments' : clean_appointments, 'forum_posts' : clean_forum_posts,

                                    } )

# ==============================================================================================================================
# Helper functions below.
# ==============================================================================================================================
def checkModuleInstall():
    # this function returns a dict, 0 if the module is installed, 1 if not - used to show/hide fields on settings page.
    modules = {'website_forum':1, 'website_blog':1,  'website_event':1, 'website_hr_recruitment':1, 'website_sale':1, 'website_slides':1, 'im_livechat':1, 'website_calendar':1}
    for name,state in modules:
        if request.env['ir.module.module'].sudo().search_read([('name', '=', name)])[0]['state'] == 'installed':
            state = 0
    return modules


def matchEnumURLs(posts, enum_urls):
    # This function takes in forum posts and adds the url field to them from enum_urls_dicts
    return_posts = []
    for post in posts:
        return_posts.append({'name' : post['name'], 'website_url' : 'URL not set'})

    for url in enum_urls:
        split = url.split('/')
        # if its a forum post
        if split[1] == 'forum':
            # go thorugh each post in our list of posts
            for post in return_posts:
                # if the end of the url contains our post name (replacing - with a space for matching)
                if post['name'].lower() in split[-1].replace("-", " "):
                    # set current url as the url of forum post
                    post['website_url'] = url

    return return_posts

def getWebsitePages(clean_pages, enum_urls):
    # This function gets all the web pages not found under website.pages
    new_pages = []
    for url in enum_urls:
        split = url.split('/')
        if len(split) == 2 and split[1] != "":
            temp_dict = {'name' : split[1].title().replace('-', ' ').strip(), 'url' : url}
            #Fix ugly contactus and about us
            if temp_dict['name'] == 'Aboutus':
                temp_dict['name'] = 'About Us'
            if temp_dict['name'] == 'Contactus':
                temp_dict['name'] = 'Contact Us'
            if temp_dict not in clean_pages:
                new_pages.append(temp_dict)
    #remove weird /
    return new_pages

def getForumsBlogs(enum_urls, website_id):
    # This function gets all the blogs and forums (not posts)
    # Check the settings to see if user has disabled a module for display
    settings_check_blog = request.env['website.sitemap.settings'].sudo().search([('website_id', '=', website_id)])[0]['blog_posts']
    settings_check_forum = request.env['website.sitemap.settings'].sudo().search([('website_id', '=', website_id)])[0]['forum_posts']
    blogs = []
    forums = []
    for url in enum_urls:
        split = url.split('/')
        if 'forum' in url and len(split) == 3 and settings_check_forum:
            f = {'name' : split[2][:-2].title().replace("-", " "), 'url' : url}
            if f not in forums:
                forums.append(f)
        if 'blog' in url and len(split) == 3 and settings_check_blog:
            b = {'name' : split[2][:-2].title().replace("-", " "), 'url' : url}
            if b not in blogs:
                blogs.append(b)

    return forums,blogs

def cleanPosts(posts):
    clean_posts = []
    if posts != False:
        for post in posts:
            clean_posts.append({'name' : post['name'], 'url' : post['website_url']})
    return clean_posts

def coursesAreSiteSpecific():
    # Check if any eCourses are assigned to a website.  By default they are not.
    courses = request.env['slide.channel'].sudo().search([])
    for course in courses:
        if course['website_id']:
            return True
    return False

def checkModule(website_name, module_name, website_id, settings_name, enum_urls=[]):
    # This function checks if the module is installed, and returns its items if its installed. otherwise returns false.
    check = request.env['ir.module.module'].sudo().search_read([('name', '=', website_name)])
    # Check the settings to see if user has disabled a module for display
    settings_check = request.env['website.sitemap.settings'].sudo().search([('website_id', '=', website_id)])[0][settings_name]

    if check[0]['state'] == "installed" and settings_check:
        if module_name == "forum.post":
            raw_posts = request.env[module_name].sudo().search([('website_id', '=', website_id)], order="id asc")
            # match URL to forum post name
            posts = matchEnumURLs(raw_posts, enum_urls)

        elif module_name == "im_livechat.channel" or module_name == 'calendar.appointment.type' or module_name == 'hr.job' or module_name == 'blog.post' or module_name == 'product.product':
            posts = request.env[module_name].sudo().search([('is_published', '=', True)], order="id asc")
        elif module_name == 'slide.channel':
            # if any course is set to a website
            if coursesAreSiteSpecific():
                #seach with website_id
                posts = request.env[module_name].sudo().search([('is_published', '=', True), ('website_id', '=', website_id)], order="id asc")
            else:
                #no courses were found assigned to a site - search without website_id
                posts = request.env[module_name].sudo().search([('is_published', '=', True)], order="id asc")
        else:
            posts = request.env[module_name].sudo().search([('is_published', '=', True), ('website_id', '=', website_id)], order="id asc")
    else:
        _logger.info('Module Name ' + website_name + ' is returning false for getting all posts.')
        posts = False
    return posts
