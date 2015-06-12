
from inspect import currentframe, getframeinfo
import pprint
from amara.bindery import html
import requests
import Queue
from optparse import OptionParser
import re
import sys


__version__ = "1.0"

pp = pprint.PrettyPrinter(depth=6)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    YELLOW = '\033[33m'
    FAIL = '\033[31m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

##############################################################################################################################

class Crawler():
	"""docstring for Crawler"""
	def __init__(self, baseurl, verbose, limit, output_filename=None, print_sublinks=True, keep_inpage_ref=False, recrawl_pages=False, keep_duplicate_links=False):

		if not baseurl.startswith("http://"):
			baseurl = "http://"+baseurl						

		self.baseurl = baseurl
		self.verbose =  verbose
		self.limit = limit
		self.keep_inpage_ref = keep_inpage_ref
		self.recrawl_pages = recrawl_pages
		self.keep_duplicate_links = keep_duplicate_links

		self.seeds_queue = Queue.Queue()
		self.seeds_queue.put(baseurl)
		
		self.crawled_list = list()
		self.sites_already_crawled = list()

		self.error_code = None
		self.error_message = "No Error"
		self.output_filename = output_filename
		self.write_fd = None
		self.print_sublinks=print_sublinks

##############################################################################################################################

	def crawl(self):

		number_of_pages_to_crawl = self.limit
		crawl_limit = self.limit

		if self.output_filename is not None:
			self.write_fd = open(self.output_filename,"w")


		if self.limit is None:
			crawl_limit = "Infinite"
			number_of_pages_to_crawl = 2**20



		for i in range(0,number_of_pages_to_crawl):

			try:
				url = self.seeds_queue.get(block=False)				
			except Queue.Empty:
				break

			try:
				html_output =  requests.get(url).text   			

			except (requests.exceptions.ConnectionError,requests.exceptions.InvalidURL) as e:
				frameinfo = getframeinfo(currentframe())
				self.error_code = 1
				self.error_message = "Exception:"+frameinfo.filename + ":%d."%(frameinfo.lineno)+ "  Invalid base url: " + url
				if self.verbose and url == self.baseurl:
					print bcolors.FAIL + "Exception:"+frameinfo.filename, "line number:%d."%(frameinfo.lineno),"Invalid base url: "+url + bcolors.ENDC
				continue


			

			html_output = html_output.encode('utf-8')
			source = html.inputsource(arg=html_output, sourcetype=1)
			self.sites_already_crawled.append(url)

			if self.verbose:
				print "Crawling %s, %d of %s."%(url, i+1, str(crawl_limit))


			if self.write_fd:
				self.write_fd.write("Crawling %s, %d of %s."%(url, i+1, str(crawl_limit)) + "\n")


			try:
				doc = html.parse(html_output)			
			except ValueError:										
				continue


			href_repo_list = list()
			
			hrefs=doc.xml_select(u"//a/@href")

			for href in hrefs:
				if ( not self.keep_inpage_ref ) and href.xml_value.startswith("#"):				  
					continue

				if not href.xml_value.startswith("http") or href.xml_value.startswith("/"):  
					href.xml_value=self.baseurl+href.xml_value
				

				if href.xml_value.endswith("/"):				 
					href.xml_value = href.xml_value[:-1]


			 
				if (not self.keep_duplicate_links) and ( href.xml_value not in href_repo_list):   	
					href_repo_list.append(href.xml_value)

				if self.keep_duplicate_links:														
					href_repo_list.append(href.xml_value)

				if (not self.recrawl_pages)  and (href.xml_value not in self.sites_already_crawled): 
					self.seeds_queue.put(href.xml_value)

				if self.recrawl_pages:																	 
					self.seeds_queue.put(href.xml_value)


			page_href_dict = dict()
			page_href_dict["url"]=url
			page_href_dict["href_repo_list"]=href_repo_list	
			self.crawled_list.append(page_href_dict)

		#End of for loop


			
##############################################################################################################################

	def print_results(self):
		linebreak =  "\n________________________________________________________________________________________________________________________\n"

		string1 = linebreak + "Number of web pages crawled: " + str(len(self.crawled_list)) 
		
		if self.verbose:
			print bcolors.OKGREEN + bcolors.BOLD +string1+ bcolors.ENDC
		if self.write_fd:
			self.write_fd.write(string1+"\n" )


		
		for index, page_href_dict in enumerate(self.crawled_list):
			string2 = linebreak + str((index+1)) + ") " + page_href_dict["url"] + ",Found %d sublinks"%(len(page_href_dict["href_repo_list"]))
			
			if self.verbose:
				print bcolors.OKGREEN+string2+bcolors.ENDC
			if self.write_fd:
				self.write_fd.write(string2+"\n" )


			for url in page_href_dict["href_repo_list"]:
				string3 = "\t** "+url 

				if self.verbose and self.print_sublinks:
					print bcolors.YELLOW + string3 + bcolors.ENDC
				if self.write_fd:
					self.write_fd.write(string3+"\n" )




##############################################################################################################################


def main():
	"""Main function:  Grabs command-line arguments and runs the program."""
	usage = 'usage: %prog [options] "[command1]" "[command2]" ...'
	parser = OptionParser(usage=usage, version=__version__)
	parser.disable_interspersed_args()
	parser.add_option("-o", "--output_filename", dest="output_filename", default=None, help="Location of the file where the results will be saved.", metavar="<file>")
	parser.add_option("-q", "--quiet", action="store_false", dest="verbose", default=True, help="Don't print messages to screen. Disable verbose.")	
	parser.add_option("-i", "--inpage_references",action="store_true", dest="keep_inpage_ref", default=False, help="Consider in page references, eg:-#section .  Defaults to False.")
	parser.add_option("-r", "--recrawl_pages", action="store_true", dest="recrawl_pages", default=False, help="Recrawl already crawled links.  Defaults to False.")
	parser.add_option("-d", "--duplicate_links", action="store_true", dest="keep_duplicate_links", default=False, help="Consider duplicate links within a page.  Defaults to False.")
	parser.add_option("-b", "--baseurl", dest="baseurl", default=None, help="Base URL to start crawling.")
	parser.add_option("-n", "--maxnumberoflinks", dest="maxnumberoflinks", default=None, help="Max number of links to crawl.")
	parser.add_option("-k", "--hide_sublinks", dest="print_sublinks", action="store_false", default=True, help="Don't print sublinks.")


	(options, args) = parser.parse_args()
	baseurl = options.baseurl
	verbose = options.verbose
	output_filename = options.output_filename
	keep_inpage_ref = options.keep_inpage_ref
	recrawl_pages = options.recrawl_pages
	keep_duplicate_links = options.keep_duplicate_links
	print_sublinks = options.print_sublinks

	
	if baseurl == None:
		baseurl = raw_input(bcolors.WARNING +"Enter Base URL: "+ bcolors.ENDC)



	if options.maxnumberoflinks is not None:
		maxnumberoflinks = int(options.maxnumberoflinks)

	elif options.maxnumberoflinks is None:
		try:
			maxnumberoflinks = int(raw_input(bcolors.WARNING + "Enter number of pages to crawl (Non-whole number for Infinite): "+ bcolors.ENDC))

		except ValueError:
			maxnumberoflinks = None


	if (maxnumberoflinks is None) and verbose:
		print "Press CTRL-C to stop!!!"


	crawler = Crawler(baseurl=baseurl, verbose=verbose, limit=maxnumberoflinks, output_filename=output_filename, print_sublinks = print_sublinks, keep_inpage_ref=keep_inpage_ref, recrawl_pages=recrawl_pages,keep_duplicate_links=keep_duplicate_links)

	try:
		crawler.crawl()
	except KeyboardInterrupt:
		crawler.print_results()	
		sys.exit()	

	crawler.print_results()



if __name__ == '__main__':
	main()