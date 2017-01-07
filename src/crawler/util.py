import re
import lxml.html as html
import urllib
import newspaper
import datetime

def download_html(url):
    '''
    Takes a url, downloads and returns the html for that page.
    '''
    url = url
    url = clean_url(url)
    url = add_prefix(url)
    f = urllib.urlopen(url)
    text = f.read()
    return text

def extract_links(html_text, base_url):
    '''
    Takes the html from a page and the base url,
    and extracts any links from within the html text.
    Filters only for internal links.
    '''
    base_url = extract_base(base_url)
    root = html.fromstring(html_text)
    found_links = root.xpath('//a/@href')
    found_links = filter(lambda link: len(link) > 0, found_links)
    # prepend relative links with the base url
    for i in range(len(found_links)):
        if re.match(r'//', found_links[i]):
            found_links[i] = found_links[i][2:]
        if re.match(r'/', found_links[i]):
            found_links[i] = base_url + found_links[i]
    found_links = [clean_url(url) for url in found_links]
    found_links = filter(lambda link: len(link) > 0, found_links)
    found_links = list(set(found_links))
    found_links = filter(lambda link: is_internal_link(base_url,link), found_links)
    return found_links

def is_internal_link(base_url, url):
    '''
    Returns whether or not url starts with base_url
    '''
    return bool(re.match(base_url, url))

def add_prefix(url):
    '''
    Takes a clean url (prefix/suffix removed),
    and adds 'http://www.' to the start of the url.
    '''
    url = 'http://www.%s' % url
    return url

def clean_url(url):
    '''
    Returns the original url, but with
    both the prefix and the suffix cleaned.
    '''
    url = clean_prefix(url)
    url = clean_suffix(url)
    return url

def clean_prefix(url):
    '''
    Returns the original url, but with any
    https://, http://, or www. removed
    '''
    subs = ['https://', 'http://', 'www.']
    for sub in subs:
        if re.match('%s' % sub, url):
            url = url[len(sub):]
    return url

def clean_suffix(url):
    '''
    Returns the original url, but with everything after a
    question mark (?) or pound symbol (#) removed.
    Also removes any trailing slashes.
    '''
    regexps = [r'(.*)(\?.*)', r'(.*)(#.*)', r'(.*)/$']
    for regexp in regexps:
        m = re.search(regexp, url)
        if m:
            url = m.groups()[0]
    return url

def extract_base(url):
    '''
    Returns everything between the www. and the first forward slash
    '''
    url = clean_url(url)
    regexp = r'(.*)/.*'
    m = re.match(regexp, url)
    if m:
        base = m.groups()[0]
    else:
        base = url
    return base

def robots_url(url):
    url = clean_url(url)
    url = add_prefix(url)
    url = '{0}/robots.txt'.format(url)
    return url

def extract_source(url):
    '''
    Returns everything in between the www. and the first dot
    '''
    url = clean_url(url)
    regexp = r'(.*)(\..*)'
    m = re.search(regexp, url)
    if m:
        url = m.groups()[0]
    return url

def extract_article(html_text, url):
    '''
    Returns a newspaper.Article instance from the given html and url
    '''
    article = newspaper.Article(url)
    article.download(html=html_text)
    article.parse()
    return article

def time_string(t):
    dt = datetime.datetime.fromtimestamp(t)
    return dt.strftime('%m.%d.%y_%H.%M.%S')
