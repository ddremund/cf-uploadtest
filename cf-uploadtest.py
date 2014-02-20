#!/usr/bin/python -tt

# Copyright 2013 Derek Remund (derek.remund@rackspace.com)

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pyrax
import argparse
import os
import sys
import time
import subprocess
import re


def main():

	parser = argparse.ArgumentParser(description = 'Tests uploads  to '
		'various Cloud Files regions.')
	parser.add_argument('-c', '--container', 
		default = pyrax.utils.random_ascii(), 
		help="Name of container to use/create; random name is used if unspecified.")
	parser.add_argument('-u', '--user', help = 'Cloud Files username')
	parser.add_argument('-p', '--password', help = 'Cloud Files Password')
	parser.add_argument('-f', '--credsfile', help = 'Cloud credentials file in INI format',
		default = "")
	parser.add_argument('-d', '--directory', help = 'Directory to upload')
	args = parser.parse_args()

	pyrax.set_setting("identity_type", "rackspace")
	creds_file = args.credsfile
	if creds_file == "":
		pyrax.set_credentials(args.user, args.password)
	else:
		pyrax.set_credential_file(creds_file)

	regions = [('DFW', 'storage101.dfw1.clouddrive.com'),
	('ORD', 'storage101.ord1.clouddrive.com'),
	('IAD', 'storage101.iad3.clouddrive.com'),
	('SYD', 'storage101.syd2.clouddrive.com'),
	('HKG', 'storage101.hkg1.clouddrive.com')]

	print 'Using container "{}"'.format(args.container)

	for region, endpoint in regions:
		print '\n\nTesting region {}\n'.format(region)
		print 'Testing Upload...'
		cf = pyrax.connect_to_cloudfiles(region)
		try:
			container = cf.get_container(args.container)
		except:
			try:
				container = cf.create_container(args.container)
			except Exception, e:
				print "Container exception:", e
				sys.exit(1)

		directory = os.path.abspath(os.path.expanduser(args.directory))
		uuid, total_bytes = cf.upload_folder(directory, container)
		start_time = time.time()
		uploaded = 0
		while uploaded < total_bytes:
			uploaded = cf.get_uploaded(uuid)
			print '{}% completed - {} of {} bytes uploaded'.format(float(uploaded) * 100 / total_bytes, 
				uploaded, total_bytes)
			time.sleep(2)
		elapsed_time = time.time() - start_time
		print '{} bytes uploaded in {} seconds.'.format(total_bytes, elapsed_time)
		MBps = total_bytes / (1024*1024) / elapsed_time
		print 'Approximate Data rate: {} MBps | {} Mbps\n'.format(MBps, MBps * 8)

		print 'Testing Ping...'
		p = subprocess.Popen(['ping', '-c', '10', endpoint], stdout = subprocess.PIPE)
		lines = p.communicate()[0].split('\n')
		latencies = lines[-2].split()[3]
		avg_latency = latencies.split('/')[1]
		#matcher = re.compile("round-trip min/avg/max/stddev = (\d+.\d+)/(\d+.\d+)/(\d+.\d+)/(\d+.\d+)")
		#ping_results = matcher.match(lines[-2]).groups()
		avg_latency = ping_results[1]
		theoretical_bw_Mbps = 524.288 / float(avg_latency)
		print 'Latency results:', lines[-2]
		print 'Theoretical max bandwith with 64KB TCP Window: {} Mbps'.format(theoretical_bw_Mbps)





if __name__ == '__main__':
	main()