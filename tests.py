#!/usr/bin/python
import sys
import getopt
import cwtapitests
import unittest

def main(argv):
   inputfile = ''
   outputfile = ''
   try:
      opts, args = getopt.getopt(argv,"hi:s:",["ifile=","host="])
   except getopt.GetoptError:
      print('test.py -i <configfile> -s <servername>')
      sys.exit(2)

   conf = './config.cfg'
   host = 'all'

   for opt, arg in opts:
      if opt == '-h':
         print('test.py -i <configfile> -o <servername>')
         print("")
         print("Run compliance tests on remote servers.")
         sys.exit()
      elif opt in ("-i", "--ifile"):
         conf = arg.strip()
      elif opt in ("-s", "--servername"):
         host = arg.strip()

   cwtapitests.conf.read_file(open(conf))

   suite = cwtapitests.tests.load_suite(host)
   unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == "__main__":
    main(sys.argv[1:])



