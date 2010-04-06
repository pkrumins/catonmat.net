This is the new catonmat.net website.

I have around 100 ideas of what a modern, state of the art, personal website
should have.

I will explain all my ideas in an article series "Designing the new
catonmat.net together with me." I have all the ideas on 4 A4 sheets I'll scan
and digitalize them as I start writing the articles.

Update:
    I wrote more than 50 of them down in ideas.txt, take a look.
    I also published them to catonmat.net as an article:
    http://www.catonmat.net/blog/50-ideas-for-the-new-catonmat-website/

This readme.txt file will be updated as I go to reflect full history of making
the new catonmat.net

I am starting to push code today 2009.12.09.

The new catonmat.net is written in Python and reuses the following Python
modules (list is not complete):

    * Werkzeug   for WSGI and local development HTTP server.
    * SQLAlchemy for ORM.
    * Memcached  for caching.
    * Pygments   for parsing posts and syntax highlighting.
    * Mako       for HTML templates.
    * SimpleJSON for JSON.
    * jQuery     for AJAX and visual effects.

2010.04.06:
    * improved /tag list and individual post list in /tag/<name>
    * improved /category list and individual post list in /category/<name>
    * /archive, /archive/<year>, /archive/<year>/<month>
2010.04.05:
    * /feedback now fully works.
    * /sitemap now fully works.
2010.04.04:
    * added categories to the sidebar
    * added post archive to the sidebar
2010.04.02:
    * added page-stuff - views, comment count, tags, short url
    * added Google Buzz to 'meet me on'
    * added /sitemap, /projects and /feedback pages
    * added exception table to log Python exceptions
    * 404 log now logs also http headers
2010.04.01:
    * added atom feed
2010.03.31:
    * added progress screenshot screenshot_2010-03-31.png
    * added top ten {articles,downloads} and recent articles to the sidebar
2010.03.30:
    * added caching
2010.03.25:
    * /download/<file> now works
    * lexer now handles [download#id] and converts it to <a> download link
2010.03.23:
    * rewrote the state based comment parser with a recursive descent one
    * added tests for comments
    * added a script that generates pygments code highlighting css
2010.03.22:
    * page parser now doesn't <p> contents of certain block tags
    * added 3 more tests for page parser for <pre>, <pre lang> and above test
2010.03.16:
    * added syntax highlighting for <pre lang="...">...</pre> tags
2010.03.15:
    * added tests for the new page parser
    * added "this space reserved for jelly stains" banner
2010.03.12:
    * replaced the state based article parser with a recursive descent one
2010.03.02:
    * added pagination for front page
    * fixed individual pages that was broken after refactoring
2010.03.01:
    * refactored individual page
2010.02.25:
    * added wordpress_to_catonmat.py script that converts wordpress to cm db
2010.02.10:
    * added page_meta table
2010.02.05:
    * front page now works
    * added tags icon
2010.02.04:
    * factored out individual pages to individual_page.tmpl.html
    * worked on front page
2010.02.03:
    * added visitors and rss tables
    * adding a comment now stores user's info in visitors table
2010.02.02:
    * minor css changes
2010.02.01:
    * added 301 redirection for broken links via url_maps table
2010.01.31:
    * added tags
    * all <a> links now have title="" attributes
    * added category list and tag list
2010.01.30:
    * added comment count and publish time for articles and comments
2010.01.29:
    * added categories
2010.01.28:
    * short-urls /p/ now fully work
    * code style changes
2010.01.27:
    * comments now work with and without ajax
    * added a message that reminds to submit comment after clicking preview
2010.01.26:
    * refactored comment code
2010.01.25:
    * comments now work without ajax
    * comment permalinks now work
2010.01.24:
    * factored code for ajax comments
    * worked on comment preview and submit to work without javascript enabled
2010.01.21-2010.01.23:
    * didn't do much, added linear comment view
2010.01.20:
    * comment textarea box now resizes horizontally via css when replying
    * comments can now be submitted via ajax
2010.01.19:
    * added /c/ short-url for comments and /p/ short-url for pages
2010.01.18:
    * more work on threaded comments
    * added basic latex via google charts api
    * screenshot_2010-01-18.png
2010.01.17:
    * threaded comments now work
    * a newline in comments now gets converted into a <br>
    * factored preview comment out from html to javascript to catonmat.js file
2010.01.16:
    * worked on comment parser
    * added stricter comment validation for twitter name and website
2010.01.15:
    * 'reply comment' and 'cancel comment' buttons now work
    * added a darker border on comment text field focus
    * screenshot_2010-01-15.png
2010.01.14:
    * factored out javascript code from html to catonmat.js
    * added icons for 'reply comment' and 'cancel comment'
2010.01.12-2010.01.13:
    * didn't do anything, rested.
2010.01.11:
    * worked on threaded comments
2010.01.10:
    * worked on displaying comments
    * added gravatars for comments
    * improved comment validation
    * added comment form tabindexes for input elements for better user exp'
    * added permalinks for comments
    * screenshot_2010-01-10.png
2010.01.09:
    * added an explanation why I need your email
    * now can submit comment and it gets put in database
    * screenshot_2010-01-09.png
2010.01.08:
    * redesigned comment form
    * added icons for name, email, twitter, website and comment fields
2010.01.07:
    * celebrated my birthday
2010.01.06:
    * more work on comments, added twitter field for comments
2010.01.05:
    * finished comment error checking
    * added error and info icons
    * worked on comment parser
2010.01.04:
    * worked on comment error checking and preview
2010.01.03:
    * added comments table, form and worked on comment css
    * progress screenshot: screenshot_2010-01-03.png
2010.01.02:
    * added page parser: parser.py
    * css changes for page content
2009.12.31-2010.01.01:
    * new year holidays
2009.12.30:
    * added category, calendar and comments icons
    * improved how a single page looks
    * screenshot of a single page: screenshot_2009-12-30.png
2009.12.22-2009.12.29:
    * christmas holidays
2009.12.21:
    * made "meet me on" expandable by up/down arrow
    * lots of css changes to make "meet me on" look precise to pixel
    * added screenshot_2009-12-21.png
2009.12.20:
    * added "meet me on: github, linkedin, friendfeed, irc"
    * added icons for all these "meet me on" sites.
2009.12.19:
    * added excerpt for posts that goes into meta description
    * worked on css
2009.12.18:
    * a new idea about comment emails
    * worked on individual page css and added a border to faux column
2009.12.17:
    * now displays individual page from database.
    * added a new idea about skribit.
2009.12.16:
    * added a new idea about rss.
    * added blog_pages table, did some refactoring.
2009.12.15:
    * added urlmapper table that maps urls to pages or views
    * progress so far: screenshot_2009-12-15.png
2009.12.14:
    * added orm tables and 404 logging
2009.12.13:
    * more ideas, updates to templates.
2009.11.12:
    * added random quotes
    * added "meet me on" twitter, plurk, facebook.
2009.12.11:
    * created templates/
2009.12.10:
    * added ideas.txt with most of the ideas I have for the new catonmat.
2009.12.09:
    * updated readme with what Python modules it uses.
    * start.

