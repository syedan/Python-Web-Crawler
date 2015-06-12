# Python-Web-Crawler
    Simple web crawler for Python

<h2>Example usage</h2>

<h3>1. Comandline option </h3>

    $ python crawler.py --baseurl google.com -n 1
    $ python crawler.py -h                                   #For Help


<h3>2. As a module</h3>

    from crawler.crawler import Crawler 
    import pprint
    pp = pprint.PrettyPrinter(depth=6)
    
    crawl = Crawler(baseurl="google.com", verbose=True, limit=2, output_filename="results.txt")
    crawl.crawl()
    crawl.print_results()
    pp.pprint(crawl.crawled_list)   #List of dictionaries which contain the results

<h3>Installation</h3>
    1. Download the zip file and extract to a directory called crawler
     "crawler" directory
      --> __init__.py
      --> crawler.py

<h3>Dependencies</h3>
    1. Python Version 2.7
    2. Amara 
        pip install amara
    3. pip install requests[security]    (Optional)
  
<h3>Bugs</h3>
    Please report bugs to the github issue tracker.
    
 <h3>Contributing</h3>

    Fork it
    Create your feature branch (git checkout -b my-new-feature)
    Commit your changes (git commit -am 'Add some feature')
    Push to the branch (git push origin my-new-feature)
    Create new Pull Request

