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


def main():

	parser = argparse.ArgumentParser(description = 'Tests uploads  to '
		'various Cloud Files regions.')
	parser.add_argument('-c', '--container', 
		default = pyrax.utils.random_name(8, ascii_only = True), 
        help="Name of container to use/create; random name is used if unspecified.")
	parser.add_argument('-u', '--user', 'Cloud Files username')
	parser.add_argument('-p', '--password', 'Cloud Files Password')
	parser.add_argument('-f', '--credfile', 'Cloud credentials file in INI format')
	parser.add_argument('-d', '--directory', 'Directory to upload')
	args = parser.parse_args()

    pyrax.set_setting("identity_type", "rackspace")
    creds_file = args.get('credfile')
    if creds_file is None:
    	pyrax.set_credentials(args['user'], args['password'])

    regions = list(pyrax.regions())

    print 'Using container "{}"'.format(args.container)

    for region in regions:
    	print 'Testing region', region
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
    	while cf.get_uploaded(uuid) < total_bytes:
    		uploaded_bytes = cf.get_uploaded(uuid)
    		print '{}% completed - {} of {} bytes uploaded'.format(float(uploaded_bytes / total_bytes, 
    			uploaded_bytes, total_bytes))
    		time.sleep(2)
    	elapsed_time = time.time() - start_time
    	print '{} bytes uploaded in {} seconds.'.format(total_bytes, elapsed_time)
    	print 'Data rate: {} MBps'.format(total_bytes / 1024 / elapsed_time)



if __name__ == '__main__':
    main()